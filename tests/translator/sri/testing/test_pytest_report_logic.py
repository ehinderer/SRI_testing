"""
Unit tests for the backend logic of the web services application.

Note: the nature of these unit tests, even with sample data,
      means that they may take over five minutes to run each one.
"""
from sys import stderr
from typing import Optional, Dict
from time import sleep

from translator.sri.testing.onehops_test_runner import OneHopTestHarness

import logging

logger = logging.getLogger()

SPACER = '\n' + '#'*120 + '\n'

MAX_TRIES = 5  # we'll try just 5 x api.util.DEFAULT_WORKER_TIMEOUT


def _report_outcome(
        test_name: str,
        session_id: str,
        expecting_report: bool = True
):
    print(f"Processing {test_name}() from {session_id}", file=stderr)
    summary: Optional[str] = None
    tries: int = 0
    while not summary:
        tries += 1
        if tries > MAX_TRIES:
            break

        summary: Optional[Dict] = OneHopTestHarness(session_id).get_summary()

        if summary:
            # got something back?!
            break

        if expecting_report:
            # nothing yet? sleep a bit?
            sleep(120)
        else:
            sleep(20)  # Should be long enough for a short timeout aborted test
            summary = OneHopTestHarness(session_id).get_summary()
            break

    if expecting_report:

        assert summary, f"{test_name}() from {session_id} is missing an expected summary?"

        print(f"{test_name}() test run 'summary':\n\t{summary}\n", file=stderr)

        details: Optional[str] = None
        tries = 0
        while not details:

            tries += 1
            if tries > MAX_TRIES:
                break

            details = OneHopTestHarness(session_id).get_details(
                component="ARA",
                edge_num="1",
                ara_id="Test_ARA",
                kp_id="-Test_KP_2"
            )

        assert details, \
            f"{test_name}() from test run '{session_id}' is missing expected details for " + \
            f"ARA tests of edge number '1' of resource 'Test_ARA-Test_KP_2'?"

        print(
            f"{test_name}() test run '{session_id}' details for ARA tests of " +
            f"edge number '1' of resource 'Test_ARA-Test_KP_2' for test run:\n\t{details}\n",
            file=stderr
        )

    else:
        assert not summary, \
            f"{test_name}() test run '{session_id}' has unexpected non-empty report with contents: {summary}?"


def test_run_local_onehop_tests_one_only():
    onehop_test = OneHopTestHarness()
    onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP_1.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json",
        one=True
    )
    _report_outcome(
        "test_run_local_onehop_tests",
        session_id=onehop_test.get_test_run_id()
    )


def test_run_local_onehop_tests_all():
    onehop_test = OneHopTestHarness()
    onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP_1.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    _report_outcome(
        "test_run_local_onehop_tests",
        session_id=onehop_test.get_test_run_id()
    )


def test_run_local_onehop_tests_all_older_trapi_version():
    onehop_test = OneHopTestHarness()
    onehop_test.run(
        trapi_version="1.0.0",
        biolink_version="2.2.16",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP_1.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )

    _report_outcome(
        "test_run_local_onehop_tests",
        session_id=onehop_test.get_test_run_id()
    )


def test_run_local_onehop_tests_all_older_blm_version():
    onehop_test = OneHopTestHarness()
    onehop_test.run(
        trapi_version="1.2.0",
        biolink_version="1.8.2",
        triple_source="test_triples/KP/Unit_Test_KP/Test_KP_1.json",
        ara_source="test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
    )
    _report_outcome(
        "test_run_local_onehop_tests",
        session_id=onehop_test.get_test_run_id()
    )


def test_run_onehop_tests_from_registry():
    onehop_test = OneHopTestHarness()
    onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True
    )
    _report_outcome(
        "test_run_onehop_tests_from_registry",
        session_id=onehop_test.get_test_run_id()
    )


def test_run_onehop_tests_from_registry_with_default_versioning():
    onehop_test = OneHopTestHarness()
    onehop_test.run(one=True)
    _report_outcome(
        "test_run_onehop_tests_from_registry_with_default_versioning",
        session_id=onehop_test.get_test_run_id()
    )


def test_run_onehop_tests_with_timeout():
    # 1 second timeout is much too short for this test to run
    # to completion, so a WorkerProcess timeout is triggered
    onehop_test = OneHopTestHarness()
    onehop_test.run(
        trapi_version="1.2",
        biolink_version="2.2.16",
        one=True,
        timeout=1
    )
    _report_outcome(
        "test_run_onehop_tests_with_timeout",
        session_id=onehop_test.get_test_run_id(),
        expecting_report=False
    )
