"""
Utility module to support SRI Testing harness background processing

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional
import multiprocessing as mp
import os
import logging
logger = logging.getLogger()


def test_harness(lock: mp.Lock, queue: mp.Queue, cmd: str):
    lock.acquire()
    try:
        print('Module:', __name__)
        print('Parent process:', os.getppid())
        process_id: int = os.getpid()
        print(f"Background process id: {process_id}")
        queue.put(process_id)
        msg = f'Executing Test Harness command "{cmd}"'
        print(f"{msg}!")
        queue.put(msg)
    finally:
        lock.release()


def run_test_harness(command: str) -> Optional[str]:
    """
    Run a SRT Testing test harness command as a background process.

    TODO: First iteration is a "blocking" call. We need to run this as a background child process?

    :param command: str, command line interface command to run as a background child process.

    :return: str, process identifier for this background command
    """
    logger.debug(f"run_test_harness() command: {command}")

    process_id: Optional[int] = None

    # TODO: if I need to manage several worker processes, then look at Pools, see
    #       https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing
    try:
        ctx = mp.get_context('spawn')
        queue = ctx.Queue()
        lock = ctx.Lock()
        p = ctx.Process(target=test_harness, args=(lock, queue, command))
        p.start()
        process_id = queue.get()
        msg = queue.get()
        print(f"{msg} inside the worker process!")
        p.join()

    except RuntimeWarning:
        logger.warning(f"run_test_harness() cmd: {command} raised an exception?")

    return process_id
