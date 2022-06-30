"""
Utility module to support SRI Testing harness background processing

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from multiprocessing import Process
from multiprocessing.context import BaseContext
from sys import platform, stdout, stderr

from typing import Optional, Union
import multiprocessing as mp
from queue import Empty
from subprocess import (
    run,
    # PIPE,
    # STDOUT,
    CompletedProcess,
    CalledProcessError,
    TimeoutExpired
)
import os
import logging

logger = logging.getLogger()


if platform == "win32":
    # Windoze
    CMD_DELIMITER = "&&"
    PWD_CMD = "cd"
elif platform in ["linux", "linux1", "linux2", "darwin"]:
    # *nix
    CMD_DELIMITER = ";"
    PWD_CMD = "pwd"
else:
    print(f"Warning: other OS platform '{platform}' encountered?")
    CMD_DELIMITER = ";"
    PWD_CMD = "pwd"


def _worker_process(lock: mp.Lock, queue: mp.Queue, command_line: str):
    """
    Wrapper for a background worker process which runs a specified command.

    :param lock: Lock, process lock used to synchronize background output
    :param queue: Queue, used for communication of worker process to caller
    :param command_line: str, the worker process command to execute
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

    result: Union[CompletedProcess, CalledProcessError, TimeoutExpired]
    try:
        # do the heavy lifting here
        #     try:
        #         with Popen(
        #                 args=cmd,
        #                 # env=env,
        #                 bufsize=1,
        #                 universal_newlines=True,
        #                 stdout=PIPE,
        #                 stderr=STDOUT
        #         ) as proc:
        #             logger.info(f"run_script({script}) log:")
        #             for line in proc.stdout:
        #                 line = line.strip()
        #                 if line:
        #                     # propagate the line to the
        #                     # parent process, via the Queue?
        #                     queue.put(line)
        #
        #     except RuntimeError:
        #         logger.error(f"run_script({script}) exception: {exc_info()}")
        #         return -1
        result = run(
            command_line,
            shell=True,
            check=True,
            capture_output=True,
            # stdout=PIPE,
            # stderr=STDOUT,
            universal_newlines=True,
            text=True,

            # running test harnesses may take a very long time
            # so maybe a bit challenge to set a sensible timeout here
            # timeout=100,
        )

        # TODO: somehow read the stdout stream to parse the PyTest %completion as a progress monitor

    except CalledProcessError as cpe:
        result = cpe

    # except TimeoutExpired as toe:
    #     print(str(toe), flush=True, file=stderr)
    #     result = toe

    lock.acquire()
    try:
        print(f"Result: {str(result)}", flush=True, file=stderr)

        return_code = result.returncode
        print(f"Return Code: {return_code}", flush=True, file=stderr)

        output = result.stdout
        print(f"Output: {output}", flush=True, file=stdout)

        errors = result.stderr
        print(f"Errors: {errors}", flush=True, file=stderr)

    finally:
        lock.release()

    # propagate the result - successful or not - back to the caller
    queue.put(result)


class WorkerProcessException(Exception):
    pass


class WorkerProcess:

    def __init__(self, timeout: Optional[int] = None):
        """
        Constructor for WorkerProcess.
        
        :param timeout: int, worker process data query access timeout (Default: None => queue data access is blocking?)
        """
        self._timeout: Optional[int] = timeout
        self._result: Optional[Union[CompletedProcess, CalledProcessError, TimeoutExpired, Empty]] = None
        self._output: Optional[str] = None
        self._ctx: BaseContext = mp.get_context('spawn')
        self._queue = self._ctx.Queue()
        self._lock = self._ctx.Lock()
        self._process: Optional[Process] = None
        self._process_id: int = 0

    def run_command(self, command_line: str):
        """
        Run a provided command line string, as a background process.

        :param command_line: str, command line string to run as a shell command in a background worker process.

        :return: None
        """
        assert command_line  # should not be empty?

        logger.debug(f"run_command() command: {command_line}")

        try:
            # Sanity check: WorkProcess is a singleton?
            # TODO: may need to manage several worker processes, therefore, may need to use multiprocessing Pools? see
            #   https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing
            assert not self._process
            
            self._process = self._ctx.Process(target=_worker_process, args=(self._lock, self._queue, command_line))

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

        except Exception as ex:

            logger.warning(f"run_command() command: '{command_line}' raised an exception: {str(ex)}?")

            if self._process:
                self._process.kill()
                self._process = None
                self._process_id = 0
            
            self._output = f"Background process start-up exception: {str(ex)}?"

    def get_output(self) -> Optional[str]:
        """
        Retrieves the raw STDOUT output or (alternately) error messages
        from the WorkerProcess, when it is complete.

        :return: Optional[str], output which may be a raw worker process result,
                                an error message or None if not yet available.
        """
        # this method is idempotent: once a non-empty output is
        # retrieved the first time, it is deemed ached for future access
        if not self._output:
            try:
                self._result = self._queue.get(block=True, timeout=self._timeout)
                logger.debug(f"WorkerProcess.output() result:\n\t{self._result}")
            except Empty as empty:
                logger.debug("Worker Process output is not (yet) available?")
                self._result = empty

            if self._result:
                if isinstance(self._result, CompletedProcess):
                    self._output = self._result.stdout  # sending back full raw process standard output
                    if self._result.returncode != 0:
                        # A special warning is added to the output?
                        self._output = "WARNING: Worker Process returned a non-zero return code: " + \
                                      f"'{str(self._result.returncode)}': \n\t{self._output}"
                    self._process.join()

                elif isinstance(self._result, Empty) or isinstance(self._result, TimeoutExpired):
                    # Worker process still running, self.process likely still running and the 'process_id'
                    # is likely (still) valid. Data 'output' is left None for now? Try again later...
                    pass

                elif isinstance(self._result, CalledProcessError):
                    # process aborted by internal error?
                    self._output = self._result.stdout
                    if self._process:
                        self._process.kill()
                        self._process = None
                else:
                    raise WorkerProcessException(
                        f"ERROR: Unexpected result type encountered from worker process: {type(self._result)}"
                    )
            
        return self._output
