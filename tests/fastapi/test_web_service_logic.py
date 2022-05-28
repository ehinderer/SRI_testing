"""
Unit tests for the backend logic of the web services application
"""

import logging
from translator.sri.testing.processor import run_command, CMD_DELIMITER
from app.util import run_onehop_test_harness
from tests.onehop import ONEHOP_TEST_DIRECTORY

logger = logging.getLogger()


def test_run_command():
    process_id = run_command(f"dir .* {CMD_DELIMITER} python --version")
    assert process_id
    logger.debug(f"test_run_test_harness() worker process_id: {process_id}")


def test_cd_path():
    process_id = run_command(f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} cd")
    assert process_id


def test_run_pytest_command():
    process_id = run_command(f"cd {ONEHOP_TEST_DIRECTORY} {CMD_DELIMITER} pytest --version")
    assert process_id


def test_run_onehop_test_harness():
    process_id = run_onehop_test_harness(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    assert process_id
