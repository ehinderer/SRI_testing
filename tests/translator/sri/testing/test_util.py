"""
Unit tests for OneHop unit test processing functions
"""
import pytest
import shutil

from tests.onehop.util import cleaned_up_unit_test_name, unit_test_report_filepath


@pytest.mark.parametrize(
    "query",
    [
        (
            "test_onehops.py::test_trapi_kps[Test_KP_1#0-inverse_by_new_subject]",
            "onehops_kps-Test_KP_1-0-inverse_by_new_subject_FAILED"
        )
    ]
)
def test_clean_up_unit_test_filename(query):
    assert cleaned_up_unit_test_name(query[0], 'failed') == query[1]


@pytest.mark.parametrize(
    "query",
    [
        (
            "test_results",
            "Test_KP_1-0-inverse_by_new_subject_FAILED",
            "test_triples/KP/Unit_Test_KP/Test_KP_1.json",
            "test_results/KP/Unit_Test_KP/" +
            "Test_KP_1-0-inverse_by_new_subject_FAILED"
        ),
        (
            "d6098879-d791-4c77-a300-f60d95f48ee1",
            "Test_KP_1-0-by_subject_PASSED",
            "test_triples/KP/Unit_Test_KP/Test_KP_1.json",
            "d6098879-d791-4c77-a300-f60d95f48ee1/KP/Unit_Test_KP/" +
            "Test_KP_1-0-by_subject_PASSED"
        ),
        (
            "d6098879-d791-4c77-a300-f60d95f48ee1",
            "Test_KP_1-0-by_subject_PASSED",
            None,
            "d6098879-d791-4c77-a300-f60d95f48ee1/Test_KP_1-0-by_subject_PASSED"
        )
    ]
)
def test_unit_test_report_filepath(query):
    assert unit_test_report_filepath(
        test_run_id=query[0],
        unit_test_name=query[1],
        location=query[2],
    ) == query[3]
    if query[2]:
        shutil.rmtree(query[0], ignore_errors=True)
