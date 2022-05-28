"""
Unit tests for the backend logic of the web services application
"""
from sys import stderr
import logging
from app.util import run_onehop_test_harness

logger = logging.getLogger()


def _report_outcome(label: str, report: str):
    assert report
    msg = '\n'.join(report.split('\r\n'))
    spacer = '\n' + '#'*120 + '\n'
    print(f"{label}() worker 'report':\n{spacer}{msg}{spacer}", file=stderr)


def test_run_local_onehop_test_harness():
    report = run_onehop_test_harness(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    _report_outcome("test_run_local_onehop_test_harness", report)


def test_run_registry_onehop_test_harness():
    report = run_onehop_test_harness(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    _report_outcome("test_run_registry_onehop_test_harness", report)
