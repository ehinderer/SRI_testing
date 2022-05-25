"""
Utility module to support SRI Testing web service.

The module launches the SRT Testing test harness using the Python 'multiprocessor' library.
See https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing for details.
"""
from typing import Optional
from uuid import uuid4
import multiprocessing as mp
import os
import logging

logger = logging.getLogger()


def test_harness(lock: mp.Lock, queue: mp.Queue, cmd: str):
    lock.acquire()
    try:
        msg = f"Executing Test Harness command: '{cmd}'"
        queue.put(msg)
        print(f"{msg}!")
        print('module name:', __name__)
        print('parent process:', os.getppid())
        print('process id:', os.getpid())
    finally:
        lock.release()


def run_test_harness(
    trapi_version: Optional[str] = None,
    biolink_version: Optional[str] = None,
    triple_source: Optional[str] = None,
    ara_source:  Optional[str] = None,
    one: bool = False
) -> Optional[str]:
    """
    Run the SRT Testing test harness as a separate process.

    TODO: First iteration is a "blocking" call. We need to run this as a background child process?

    :param trapi_version: Optional[str], TRAPI version assumed for test run (default: None)

    :param biolink_version: Optional[str], Biolink Model version used in test run (default: None)

    :param triple_source: Optional[str], 'REGISTRY', directory or file from which to retrieve triples
                                         (Default: 'REGISTRY', which triggers the use of metadata, in KP entries
                                          from the Translator SmartAPI Registry, to configure the tests).

    :param ara_source: Optional[str], 'REGISTRY', directory or file from which to retrieve ARA Config.
                                         (Default: 'REGISTRY', which triggers the use of metadata, in ARA entries
                                         from the Translator SmartAPI Registry, to configure the tests).

    :param one: bool, Only use first edge from each KP file (default: False).

    :return: str, session identifier for this testing run
    """
    session_id = str(uuid4())

    cmd = "pytest test_onehops.py"
    cmd += f" --TRAPI_Version={trapi_version}" if trapi_version else ""
    cmd += f" --Biolink_Release={biolink_version}" if biolink_version else ""
    cmd += f" --triple_source={triple_source}" if triple_source else ""
    cmd += f" --ara_source={ara_source}" if ara_source else ""
    cmd += " --one" if one else ""

    logger.debug(f"run_test_harness() cmd: {cmd}")

    # TODO: if I need to manage several worker processes, then look at Pools, see
    #       https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing
    try:
        ctx = mp.get_context('spawn')
        queue = ctx.Queue()
        lock = ctx.Lock()
        p = ctx.Process(target=test_harness, args=(lock, queue, cmd))
        p.start()
        msg = queue.get()
        print(f"{msg} inside child process!")
        p.join()

    except RuntimeWarning:
        logger.warning(f"run_test_harness() cmd: {cmd} raised an exception?")
        return None

    return session_id
