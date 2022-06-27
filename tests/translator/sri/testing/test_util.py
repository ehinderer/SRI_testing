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
            "test_onehops.py::test_trapi_kps[Test_KP_1#1-raise_object_by_subject]",
            "KP/Test_KP_1/1/raise_object_by_subject_FAILED"
        ),
        (
            "test_onehops.py::test_trapi_aras[Test_ARA|Test_KP_1#1-raise_object_by_subject]",
            "ARA/Test_ARA/Test_KP_1/1/raise_object_by_subject_FAILED"
        )
    ]
)
def test_clean_up_unit_test_filename(query):
    assert cleaned_up_unit_test_name(query[0], 'failed') == query[1]


@pytest.mark.parametrize(
    "query",
    [
        (
            "test_results/d6098879-d791-4c77-a300-f60d95f48ee1",
            "KP/Test_KP_1/1/raise_object_by_subject_FAILED",
            "test_results/d6098879-d791-4c77-a300-f60d95f48ee1" +
            "/KP/Test_KP_1/1/raise_object_by_subject_FAILED.json"
        ),
    (
            "test_results/d6098879-d791-4c77-a300-f60d95f48ee1",
            "ARA/Test_ARA/Test_KP_1/1/raise_object_by_subject_FAILED",
            "test_results/d6098879-d791-4c77-a300-f60d95f48ee1" +
            "/ARA/Test_ARA/Test_KP_1/1/raise_object_by_subject_FAILED.json"
        )
    ]
)
def test_unit_test_report_filepath(query):
    assert unit_test_report_filepath(
        test_run_root_path=query[0],
        unit_test_file_path=query[1]
    ) == query[2]
    # shutil.rmtree(query[0], ignore_errors=True)
