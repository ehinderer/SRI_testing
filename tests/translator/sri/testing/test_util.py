"""
Unit tests for OneHop unit test processing functions
"""
import pytest
import shutil

from translator.sri.testing.report import (
    unit_test_report_filepath,
    parse_unit_test_name,
    build_edge_details_file_path
)


@pytest.mark.parametrize(
    "query",
    [
        (
            "KP",
            None,
            "Some_KP",
            "2",
            "KP/Some_KP/Some_KP-2"
        ),
        (
            "ARA",
            "Some_ARA",
            "Some_KP",
            "3",
            "ARA/Some_ARA/Some_KP/Some_KP-3"
        )
    ]
)
def test_get_edge_details_file_path(query):
    edge_details_file_path = build_edge_details_file_path(
        component=query[0], ara_id=query[1], kp_id=query[2], edge_num=query[3]
    )
    assert edge_details_file_path == query[4]


@pytest.mark.parametrize(
    "query",
    [
        (
            "test_onehops.py::test_trapi_kps[Test_KP_1#2-raise_object_by_subject]",
            "KP",
            None,
            "Test_KP_1",
            2,
            "raise_object_by_subject",
            "KP/Test_KP_1/Test_KP_1-2"
        ),
        (
            "test_onehops.py::test_trapi_aras[Test_ARA|Test_KP_1#3-raise_object_by_subject]",
            "ARA",
            "Test_ARA",
            "Test_KP_1",
            3,
            "raise_object_by_subject",
            "ARA/Test_ARA/Test_KP_1/Test_KP_1-3"
        )
    ]
)
def test_clean_up_unit_test_filename(query):
    # component, ara_id, kp_id, edge_num, test_id
    part = parse_unit_test_name(query[0])
    assert part[0] == query[1]  # component
    assert part[1] == query[2]  # ara_id
    assert part[2] == query[3]  # kp_id
    assert part[3] == query[4]  # int(edge_num)
    assert part[4] == query[5]  # test_id
    assert part[5] == query[6]  # edge_details_file_path


@pytest.mark.parametrize(
    "query",
    [
        (
            "d6098879-d791-4c77-a300-f60d95f48ee1",
            "KP/Test_KP_1/Test_KP_1-2",
            "test_results/d6098879-d791-4c77-a300-f60d95f48ee1" +
            "/KP/Test_KP_1/Test_KP_1-2"
        ),
    (
            "d6098879-d791-4c77-a300-f60d95f48ee1",
            "ARA/Test_ARA/Test_KP_1/Test_KP_1-3",
            "test_results/d6098879-d791-4c77-a300-f60d95f48ee1" +
            "/ARA/Test_ARA/Test_KP_1/Test_KP_1-3"
        )
    ]
)
def test_unit_test_report_filepath(query):
    assert unit_test_report_filepath(
        test_run_id=query[0],
        unit_test_file_path=query[1]
    ) == query[2]
    shutil.rmtree("test_results", ignore_errors=True)
