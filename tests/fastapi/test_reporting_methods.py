"""
Test SRI Testing reporting code snippets
"""
import pytest
from os import linesep
from app.util import (
    SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN,
    PASSED_SKIPPED_FAILED_PATTERN
)


@pytest.mark.parametrize(
    "query",
    [
        f"=========================== short test summary info ============================{linesep}",
        f"===================== short test summary info ============================{linesep}",
        f"=========================== short test summary info ================================={linesep}",
        f"== short test summary info =={linesep}",
        f"{linesep}== short test summary info =={linesep}"
    ]
)
def test_stsi_header_pattern(query):
    assert SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.search(query)


def test_stsi_header_pattern_splitting():
    query = f"Pytest report prefix{linesep}== short test summary info =={linesep}Pytest Report Suffix"
    part = SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.split(query)
    assert len(part) == 2
    assert part[0] == f"Pytest report prefix{linesep}"
    assert part[1] == "Pytest Report Suffix"


@pytest.mark.parametrize(
    "query",
    [
        "PASSED test_onehops.py::test_trapi_aras[Test_ARA.json_Test KP_0-by_subject]",
        "SKIPPED [11] test_onehops.py:32: ",
        "FAILED test_onehops.py::test_trapi_aras[Test_ARA.json_Test KP_0-by_subject]"
    ]
)
def test_stsi_header_pattern(query):
    m = PASSED_SKIPPED_FAILED_PATTERN.match(query)
    assert m
    assert m[1] in ["PASSED", "SKIPPED", "FAILED"]
