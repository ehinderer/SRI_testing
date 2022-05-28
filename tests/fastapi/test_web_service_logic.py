"""
Unit tests for the backend logic of the web services application
"""
from typing import Optional, List
from sys import stderr
import logging
from app.util import OneHopTestHarness

logger = logging.getLogger()


def _report_outcome(
        test_name: str,
        report: List[str],
        expecting_report: bool = True
):
    if expecting_report:
        assert report, f"{test_name}() is missing an expected report?"
        msg = '\n'.join(report)
        spacer = '\n' + '#'*120 + '\n'
        print(f"{test_name}() worker process 'report':{spacer}{msg}{spacer}", file=stderr)
    else:
        assert not report, f"{test_name}() has unexpected non-empty report: {report}?"


def test_run_local_onehop_tests_one_only():
    onehop_test = OneHopTestHarness()
    report: List[str] = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    _report_outcome("test_run_local_onehop_tests", report)


def test_run_local_onehop_tests_all():
    onehop_test = OneHopTestHarness()
    report: List[str] = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    _report_outcome("test_run_local_onehop_tests", report)


def test_run_onehop_tests_from_registry():
    test = OneHopTestHarness()
    report: List[str] = test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    _report_outcome("test_run_onehop_tests_from_registry", report)


def test_run_onehop_tests_with_timeout():
    # 1 second timeout is much too short for this test
    test = OneHopTestHarness(timeout=1)
    report = test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    _report_outcome("test_run_onehop_tests_with_timeout", report, expecting_report=False)
