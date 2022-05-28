"""
Unit tests for the backend logic of the web services application
"""
from sys import stderr
from typing import Optional
import logging
from uuid import UUID

from translator.sri.testing.processor import run_command, CMD_DELIMITER
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()


def _report_outcome(label: str, session_id: UUID, report: str, expected_report: Optional[str] = None):
    assert session_id
    print(f"{label}() worker 'session_id': {session_id}", file=stderr)
    assert report
    msg = '\n'.join(report.split('\r\n'))
    spacer = '\n' + '#'*80 + '\n'
    print(f"{label}() worker process 'report':{spacer}{msg}{spacer}", file=stderr)
    if expected_report:
        assert report == expected_report


def test_run_command():
    session_id, report = run_command(f"dir .* {CMD_DELIMITER} python --version")
    _report_outcome("test_run_command", session_id, report)


def test_cd_path():
    session_id, report = run_command(f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} cd")
    _report_outcome("test_cd_path", session_id, report)


def test_run_pytest_command():
    session_id, report = run_command(f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} pytest --version")
    _report_outcome("test_run_pytest_command", session_id, report)


def test_run_process_timeout():
    session_id, report = run_command(
        command_line=f"PING -n 10 127.0.0.1 > nul",
        timeout=1  # one second, very short?
    )
    _report_outcome("test_run_process_timeout", session_id, report, 'Worker process still executing?')
