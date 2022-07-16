"""
Utility module to support SRI Testing harness background processing

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
import sys
from sys import platform, stderr

from multiprocessing import Process, Pipe
from multiprocessing.context import BaseContext
from multiprocessing.connection import Connection

from typing import Optional, Generator, IO

import multiprocessing as mp
from queue import Empty
from subprocess import (
    Popen,
    PIPE,
    STDOUT,
    DEVNULL
)
import os
import logging

logger = logging.getLogger()


if platform == "win32":
    # Windoze
    CMD_DELIMITER = "&&"
    PWD_CMD = "cd"
    from pathlib import PureWindowsPath
    PYTHON_PATH = PureWindowsPath(sys.executable).as_posix()
elif platform in ["linux", "linux1", "linux2", "darwin"]:
    # *nix
    CMD_DELIMITER = ";"
    PWD_CMD = "pwd"
    PYTHON_PATH = sys.executable
else:
    print(f"Warning: other OS platform '{platform}' encountered?")
    CMD_DELIMITER = ";"
    PWD_CMD = "pwd"
    PYTHON_PATH = sys.executable


def _worker_process(
        pipe: mp.Pipe,
        lock: mp.Lock,
        queue: mp.Queue,
        command_line: str,
        log_file: Optional[str] = None
):
    """
    Wrapper for a background worker process which runs a specified command.

    :param pipe: Pipe, process pipe between the Worker and caller
    :param lock: Lock, process lock used to synchronize background output
    :param queue: Queue, used for communication of worker process to caller
    :param command_line: str, the worker process command to execute
    :param log_file: Optional[str], path to save process output (in parallel to pipe)

    :return: None (process state indirectly returned via Queue)
    """
    lock.acquire()
    try:
        print('Module:', __name__, flush=True, file=stderr)
        print('Parent process:', os.getppid(), flush=True, file=stderr)
        process_id: int = os.getpid()
        print(f"Background process id: {process_id}", flush=True, file=stderr)
        msg: str = f'Executing Test Harness command "{command_line}"'
        print(msg, flush=True, file=stderr)
    finally:
        lock.release()

    # send the child process ID back to
    # the caller, as a point of reference
    queue.put(process_id)

    return_code: int
    return_status: str

    log: Optional[IO] = None
    if log_file:
        log = open(log_file, "w")

    try:

        with Popen(
                args=command_line,
                shell=True,
                bufsize=1,
                universal_newlines=True,
                stdout=PIPE,
                stderr=STDOUT
        ) as proc:
            for line in proc.stdout:
                # Echo 'line' to 'log_file' (may be /dev/null)
                if log:
                    log.write(line)

                line = line.strip()
                if line:
                    # Simple-minded strategy of shoving all the
                    # Worker Process output into an interprocess pipe
                    pipe.send(line)

        return_code = proc.returncode
        return_status = "Worker Process Completed?"

    except RuntimeError as rte:
        logger.error(f"run_script({command_line}) exception: {str(rte)}")
        return_code = 1
        return_status = f"Worker Process Exception: {str(rte)}?"

    finally:
        if log:
            log.close()

    # propagate the result - successful or not - back to the caller
    queue.put(f"{WorkerProcess.COMPLETED} - Return Code: {return_code}\nStatus {return_status}")


class WorkerProcessException(Exception):
    pass


class WorkerProcess:

    def __init__(self, timeout: Optional[int] = None, log_file: Optional[str] = None):
        """
        Constructor for WorkerProcess.
        
        :param timeout: int, worker process data query access timeout (Default: None => queue data access is blocking?)
        :param log_file: Optional[str], log file (path) to which to save a copy of worker process output lines.
        """
        self._timeout: Optional[int] = timeout
        self._parent_conn: Optional[Connection] = None
        self._child_conn: Optional[Connection] = None
        self._ctx: BaseContext = mp.get_context('spawn')
        self._queue = self._ctx.Queue()
        self._lock = self._ctx.Lock()
        self._process: Optional[Process] = None
        self._process_id: int = 0
        self._status: Optional[str] = None
        self._log_file: Optional[str] = log_file

    def run_command(self, command_line: str):
        """
        Run a provided command line string, as a background process.

        :param command_line: str, command line string to run as a shell command in a background worker process.

        :return: None
        """
        assert command_line  # should not be empty?

        logger.debug(f"run_command() command: {command_line}")

        try:
            # Sanity check: Work Process is a singleton?
            # TODO: may need to manage several worker processes, therefore, may need to use multiprocessing Pools? see
            #    https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing
            assert not self._process

            # Directly access the internal Worker Process task
            # standard output/error, using an interprocess Pipe
            self._parent_conn, self._child_conn = Pipe()

            self._process = self._ctx.Process(
                target=_worker_process,
                args=(
                    self._child_conn,
                    self._lock,
                    self._queue,
                    command_line,
                    self._log_file
                )
            )

            self._process.start()

            pid_tries: int = 10
            while not self._process_id and pid_tries:
                try:
                    self._process_id = self._queue.get(block=True, timeout=self._timeout)

                except Empty:

                    logger.debug("run_command() 'process_id' not available (yet) in the interprocess Queue?")
                    self._process_id = 0  # return a zero PID to signal 'Empty'?

                pid_tries -= 1

            # for some reason, the worker process didn't send back a
            # 'process_id', with queue access timeouts after several retries
            if not self._process_id:
                raise RuntimeError("Worker process startup time-out?")

            # TODO: perhaps I need to initiate a lightweight background thread *here*, to monitor the PIPE for
            #       Worker Process progress, instead of relying on access to PIPE output in the /status endpoint?

        except Exception as ex:

            logger.warning(f"run_command() command: '{command_line}' raised an exception: {str(ex)}?")

            if self._process and self._process.is_alive():
                self._process.kill()

            self._process = None
            self._process_id = 0

    def get_output(self, timeout: float = 1.0) -> Generator:
        if self._parent_conn:
            print("\n", file=stderr)
            while True:
                try:
                    if self._parent_conn.poll(timeout):
                        line: str = self._parent_conn.recv()
                        yield line
                    else:
                        # The Generator iteration is stopped if
                        # the get_output polling timeout is hit
                        return None
                except (EOFError, BrokenPipeError) as exc:
                    # The caller has to distinguish in
                    # between polling timeouts and output EOF
                    logger.debug(f"WorkerProcess.get_output(): {exc}")
                    return None
        else:
            # Caller also gets nothing if there is no active connection
            return None

    NOT_RUNNING: str = "Worker Process Not Running"
    COMPLETED: str = "Worker Process Completed"
    RUNNING: str = "Worker Process Running"

    def status(self) -> str:

        if not self._status or self._status == self.RUNNING:

            # ... otherwise, check the process queue for a final message...
            try:
                self._status = self._queue.get(block=True, timeout=1)
            except Empty:
                # ... (hopefully) still running...
                self._status = self.RUNNING

            # Hacker assumption: that a missing process is one deemed "completed"
            if not (self._process or not self._process.is_alive() or self._process_id):
                self._status = self.NOT_RUNNING

        return self._status

    def close(self):
        # Job done, the parent, not the child, sets the connections to None
        # which closes the interprocess pipe, when ready?
        self._parent_conn = None
        self._child_conn = None
        if self._process:
            self._process.join()
