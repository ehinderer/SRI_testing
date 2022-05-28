"""
Unit tests for the backend logic of the web services application
"""

import logging
from uuid import UUID

from translator.sri.testing.processor import run_command, CMD_DELIMITER
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()


def _report_outcome(label: str, session_id: UUID, report: str):
    assert session_id
    logger.debug(f"{label}() worker 'session_id': {session_id}")
    assert report
    msg = '\n'.join(report.split('\r\n'))
    spacer = '\n' + '#'*80 + '\n'
    logger.debug(f"{label}() worker 'report':\n{spacer}{msg}{spacer}")


def test_run_command():
    session_id, report = run_command(f"dir .* {CMD_DELIMITER} python --version")
    _report_outcome("test_run_command", session_id, report)


def test_cd_path():
    session_id, report = run_command(f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} cd")
    _report_outcome("test_cd_path", session_id, report)


def test_run_pytest_command():
    session_id, report = run_command(f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} pytest --version")
    _report_outcome("test_run_pytest_command", session_id, report)
