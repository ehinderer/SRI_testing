"""
Utility module to support SRI Testing harness background processing

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from sys import platform, stdout, stderr
from queue import Empty
from typing import Optional, Union, List
import multiprocessing as mp
from subprocess import run, CompletedProcess, CalledProcessError, TimeoutExpired
import os
import logging
logger = logging.getLogger()


if platform == "win32":
    # Windoze
    CMD_DELIMITER = "&&"
elif platform in ["linux1", "linux2", "darwin"]:
    # *nix
    CMD_DELIMITER = ";"
else:
    print(f"Warning: other OS platform '{platform}' encountered?")
    CMD_DELIMITER = ";"


def worker_process(lock: mp.Lock, queue: mp.Queue, command_line: str):
    """
    Wrapper for a background worker process which runs a specified command.

    :param lock: Lock, process lock used to synchronize background output
    :param queue: Queue, used for communication of worker process to caller
    :param command_line: str, the worker process command to execute
    :return:
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


def run_command(command_line: str) -> Optional[str]:
    """
    Run a SRT Testing test harness command as a background process.

    TODO: First iteration is a "blocking" call. We need to run this as a background child process?

    :param command_line: List[str], command line interface sequence to run as a background child process.

    :return: str, process identifier for this background command
    """
    assert command_line  # should not be empty?

    logger.debug(f"run_test_harness() command: {command_line}")

    process_id: Optional[int] = None

    # TODO: might need to manage several worker processes, therefore, may need to use multiprocessing Pools? see
    #       https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing
    try:
        # Get things started...
        ctx = mp.get_context('spawn')
        queue = ctx.Queue()
        lock = ctx.Lock()
        p = ctx.Process(target=worker_process, args=(lock, queue, command_line))
        p.start()

        try:
            process_id = queue.get(block=True, timeout=10)
        except Empty:
            # TODO: something sensible here
            logger.debug("run_test_harness() 'process_id' not available (yet) in the interprocess Queue?")

        try:
            result: Union[CompletedProcess, CalledProcessError, TimeoutExpired] = queue.get(block=True, timeout=10)
            logger.debug(f"run_test_harness() result:\n\t{result}")
        except Empty:
            # TODO: something sensible here... maybe fall through and try again later in another handler call
            logger.debug("run_test_harness() 'result' not available (yet) in the interprocess Queue?")

        # TODO: first iteration is "blocking" join, but we want to split
        #       this out for web service polling of the background process
        p.join()

    except Exception as ex:
        logger.warning(f"run_test_harness() command: '{command_line}' raised an exception: {str(ex)}?")

    return process_id
