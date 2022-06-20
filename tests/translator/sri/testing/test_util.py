"""
Unit tests for OneHop unit test processing functions
"""
import pytest
import shutil

from tests.onehop.util import clean_up_unit_test_filename, unit_test_report_filepath


@pytest.mark.parametrize(
    "query",
    [
        (
            "test_onehops.py::test_trapi_kps[Test_KP_1#0-inverse_by_new_subject]",
            "test_onehops-test_trapi_kps-Test_KP_1-0-inverse_by_new_subject"
        )
    ]
)
def test_clean_up_unit_test_filename(query):
    # name = source.split('/')[-1][:-1]
    # name = name.strip("[]")
    # name = name.replace(".py::", "-")
    # name = sub(r"[:\[\]|#/]+", "-", name)
    # return name
    assert clean_up_unit_test_filename(query[0]) == query[1]


@pytest.mark.parametrize(
    "query",
    [
        (
            "test_triples/KP/Unit_Test_KP/Test_KP_1.json",
            "test_onehops.py::test_trapi_kps[Test_KP_1#0-inverse_by_new_subject]",
            "test_results",
            "failed",
            "test_results/KP/Unit_Test_KP/" +
            "test_onehops-test_trapi_kps-Test_KP_1-0-inverse_by_new_subject_FAILED"
        ),
        (
            "test_triples/KP/Unit_Test_KP/Test_KP_1.json",
            "test_onehops.py::test_trapi_kps[Test_KP_1#0-by_subject]",
            "d6098879-d791-4c77-a300-f60d95f48ee1",
            "passed",
            "d6098879-d791-4c77-a300-f60d95f48ee1/KP/Unit_Test_KP/" +
            "test_onehops-test_trapi_kps-Test_KP_1-0-by_subject_PASSED"
        ),
        (
            None,
            "test_onehops.py::test_trapi_kps[Test_KP_1#0-by_subject]",
            "d6098879-d791-4c77-a300-f60d95f48ee1",
            "passed",
            "d6098879-d791-4c77-a300-f60d95f48ee1/test_onehops-test_trapi_kps-Test_KP_1-0-by_subject_PASSED"
        )
    ]
)
def test_unit_test_report_filepath(query):
    assert unit_test_report_filepath(
       location=query[0],
       unit_test_key=query[1],
       test_run_id=query[2],
       status=query[3]
    ) == query[4]
    if query[0]:
        shutil.rmtree(query[2], ignore_errors=True)
