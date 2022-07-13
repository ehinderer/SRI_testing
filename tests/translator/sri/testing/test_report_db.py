import pytest

from translator.sri.testing.report_db import TestReportDatabase


def test_create_test_report_db():
    try:
        trd = TestReportDatabase()
    except RuntimeError as rte:
        assert False, f"Failed to create TestReportDatabase(), exception: {str(rte)}"


@pytest.mark.parametrize(
    "query",
    [
        (),
        ()
    ]
)
def test_get_edge_details_file_path(query):
    assert query
