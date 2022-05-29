"""
Unit tests for the backend logic of the web services application
"""
from typing import List, Union
from sys import stderr
import logging
from app.util import OneHopTestHarness

logger = logging.getLogger()

SPACER = '\n' + '#'*120 + '\n'


def _report_outcome(
        test_name: str,
        session_id: str,
        expecting_report: bool = True
):
    report: List[Union[str, List[str]]] = OneHopTestHarness.get_report(session_id)
    if expecting_report:
        assert report, f"{test_name}() is missing an expected report?"
        msg = ""
        for item in report:
            if isinstance(item, List):
                for sub_item in item:
                    msg += "\t" + sub_item + "\n"
            else:
                msg += item+"\n"
        print(f"{test_name}() worker process 'report':{SPACER}{msg}{SPACER}", file=stderr)
    else:
        assert not report, f"{test_name}() has unexpected non-empty report: {report}?"


def test_run_local_onehop_tests_one_only():
    onehop_test = OneHopTestHarness()
    session_id: str = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    assert session_id
    _report_outcome("test_run_local_onehop_tests", session_id)


def test_run_local_onehop_tests_all():
    onehop_test = OneHopTestHarness()
    session_id: str = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    assert session_id
    _report_outcome("test_run_local_onehop_tests", session_id)


def test_run_local_onehop_tests_all_older_trapi_version():
    onehop_test = OneHopTestHarness()
    session_id: str = onehop_test.run(
        trapi_version="1.0.0",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    assert session_id
    _report_outcome("test_run_local_onehop_tests", session_id)


def test_run_local_onehop_tests_all_older_blm_version():
    onehop_test = OneHopTestHarness()
    session_id: str = onehop_test.run(
        trapi_version="1.2.0",
        biolink_version="1.8.2",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    assert session_id
    _report_outcome("test_run_local_onehop_tests", session_id)


def test_run_onehop_tests_from_registry():
    onehop_test = OneHopTestHarness()
    session_id: str = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    assert session_id
    _report_outcome("test_run_onehop_tests_from_registry", session_id)


def test_run_onehop_tests_from_registry_with_default_versioning():
    onehop_test = OneHopTestHarness()
    session_id: str = onehop_test.run(one=True)
    assert session_id
    _report_outcome("test_run_onehop_tests_from_registry_with_default_versioning", session_id)


def test_run_onehop_tests_with_timeout():
    # 1 second timeout is much too short for this test to run
    # to completion, so a WorkerProcess timeout is triggered
    onehop_test = OneHopTestHarness(timeout=1)
    session_id: str = onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    assert session_id
    _report_outcome("test_run_onehop_tests_with_timeout", session_id, expecting_report=False)
