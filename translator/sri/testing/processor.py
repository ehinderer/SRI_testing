"""
Utility module to support SRI Testing harness background processing

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from multiprocessing import Process
from multiprocessing.context import BaseContext
from sys import platform, stdout, stderr
from encodings.utf_8 import decode

from typing import Optional, Union, Tuple, Dict
import multiprocessing as mp
from queue import Empty
from subprocess import run, CompletedProcess, CalledProcessError, TimeoutExpired
import os
import logging
from uuid import uuid4, UUID

logger = logging.getLogger()


if platform == "win32":
    # Windoze
    CMD_DELIMITER = "&&"
elif platform in ["linux", "linux1", "linux2", "darwin"]:
    # *nix
    CMD_DELIMITER = ";"
else:
    print(f"Warning: other OS platform '{platform}' encountered?")
    CMD_DELIMITER = ";"


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
        result = run(
            command_line,
            shell=True,
            check=True,
            capture_output=True,

            # running test harnesses may take a very long time
            # so maybe a bit challenge to set a sensible timeout here
            # timeout=100,
        )

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


class WorkerProcess:
    
    # Bidirectional(?) WorkerProcess class map
    # between Process and Session identifiers
    _worker_pid_2_sid: Dict[int, UUID] = dict()
    # _worker_sid_2_pid: Dict[UUID, int] = dict()
    
    def _create_session_id(self):
        # encapsulate process identifier with a UUID session identifier
        session_id = uuid4()
        self._worker_pid_2_sid[self._process_id] = session_id
        # self._worker_sid_2_pid[session_id] = self.process_id

    def get_session_id(self) -> Optional[UUID]:
        if self._process_id and self._process_id in self._worker_pid_2_sid:
            return self._worker_pid_2_sid[self._process_id]
        else:
            return None
    
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

    def run_command(self, command_line: str) -> Optional[UUID]:
        """
        Run a provided command line string, as a background process.

        :param command_line: str, command line string to run as a shell command in a background worker process.

        :return: Optional[UUID], session identifier for this background Worker Process executing the command line.
                 If the method returns None, then the process is considered inaccessible; otherwise, the returned
                 UUID may be used to access background worker process results using the 'output()' method.
        """
        assert command_line  # should not be empty?

        logger.debug(f"run_command() command: {command_line}")

        # TODO: might need to manage several worker processes, therefore, may need to use multiprocessing Pools? see
        #       https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing
        try:
            # Sanity check: WorkProcess is a singleton?
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
                self._process.kill()
                self._process = None
                self._process_id = 0
                self._output = "Background process did not start up properly?"
            else:
                self._create_session_id()

        except Exception as ex:

            logger.warning(f"run_command() command: '{command_line}' raised an exception: {str(ex)}?")

            if self._process:
                self._process.kill()
                self._process = None
            
            self._output = f"Background process start-up exception: {str(ex)}?"

        return self.get_session_id()

    def get_output(self, session_id: UUID) -> Optional[str]:
        """
        Retrieves the raw STDOUT output or (alternately) error messages
        from the WorkerProcess, when it is complete.
        
        :param session_id: UUID, Universally Unique IDentifier assigned to a worker process
        :return: Optional[str], output which may be a raw worker process result,
                                an error message or None if not yet available.
        """
        # Sanity check
        assert session_id

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
                    self._output = decode(self._result.stdout)[0]  # sending back full raw process standard output
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
                    self._output = decode(self._result.stdout)[0]
                    if self._process:
                        self._process.kill()
                        self._process = None
                else:
                    raise RuntimeError(
                        f"ERROR: Unexpected result type encountered from worker process: {type(self._result)}"
                    )
            
        return self._output
