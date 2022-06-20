"""
Unit tests for the backend logic of the web services application
"""
from sys import stderr
from typing import Optional
import logging

from translator.sri.testing.processor import CMD_DELIMITER, PWD_CMD, WorkerProcess
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()


def _report_outcome(
        test_name: str,
        command_line: str,
        timeout: Optional[int] = None,
        expecting_output: bool = True,
        expected_output: Optional[str] = None
):
    wp = WorkerProcess(timeout)

    # we don't propagate the session id to the test commands here
    session_id = wp.run_command(command_line, has_session=False)
    assert session_id
    print(f"{test_name}() worker 'session_id': {session_id}", file=stderr)
    output = wp.get_output(session_id)
    if expecting_output:
        assert output, f"{test_name}() is missing Worker Process output?"
        msg = '\n'.join(output.split('\r\n'))
        spacer = '\n' + '#'*80 + '\n'
        print(f"{test_name}() worker process 'output':{spacer}{msg}{spacer}", file=stderr)
        if expected_output:
            # Strip leading and training whitespace of the report for the comparison
            assert output.strip() == expected_output
    else:
        assert not output, f"{test_name}() has unexpected non-empty Worker Process output: {output}?"


def test_run_command():
    _report_outcome("test_run_command", f"dir .* {CMD_DELIMITER} python --version")


def test_cd_path():
    _report_outcome(
        "test_cd_path", f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} {PWD_CMD}",
        expected_output=ONEHOP_TEST_DIRECTORY
    )


def test_run_pytest_command():
    _report_outcome("test_run_pytest_command", f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} pytest --version")


def test_run_process_timeout():
    # one second timeout, very short relative to
    # the runtime of the specified command line
    _report_outcome(
        "test_run_process_timeout",
        f"PING -n 10 127.0.0.1 > nul",
        timeout=1,
        expecting_output=False
    )
