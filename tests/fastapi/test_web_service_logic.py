"""
Unit tests for the backend logic of the web services application
"""

import logging
from app.util import run_onehop_test_harness

logger = logging.getLogger()


def test_run_local_onehop_test_harness():
    report = run_onehop_test_harness(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    assert report
    logger.debug(f"test_run_local_onehop_test_harness() 'report':\n{report}")


def test_run_registry_onehop_test_harness():
    report = run_onehop_test_harness(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    assert report
    logger.debug(f"test_run_registry_onehop_test_harness() 'report':\n{report}")
