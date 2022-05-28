"""
Unit tests for the backend logic of the web services application
"""
from typing import Optional
from sys import stderr
import logging
from app.util import OneHopTestHarness

logger = logging.getLogger()


def _report_outcome(label: str, report: str, expected_report: Optional[str] = None):
    assert report
    msg = '\n'.join(report.split('\r\n'))
    spacer = '\n' + '#'*120 + '\n'
    print(f"{label}() worker process 'report':{spacer}{msg}{spacer}", file=stderr)
    if expected_report:
        assert report == expected_report


def test_run_local_onehop_test_harness():
    onehop_test = OneHopTestHarness()
    report = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    _report_outcome("test_run_local_onehop_test_harness", report)


def test_run_registry_onehop_test_harness():
    onehop_test = OneHopTestHarness()
    report = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    _report_outcome("test_run_registry_onehop_test_harness", report)


def test_run_onehop_test_harness_with_timeout():
    # 1 second timeout is much too short for this test
    onehop_test = OneHopTestHarness(timeout=1)
    report = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    _report_outcome("test_run_onehop_test_harness_with_timeout", report, 'Worker process still executing?')
