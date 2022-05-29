"""
Test SRI Testing reporting code snippets
"""
import pytest
from os import linesep
from app.util import SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN


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
def test_pattern(query):
    assert SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.search(query)


def test_pattern_splitting():
    query = f"Pytest report prefix{linesep}== short test summary info =={linesep}Pytest Report Suffix"
    part = SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.split(query)
    assert len(part) == 2
    assert part[0] == f"Pytest report prefix{linesep}"
    assert part[1] == "Pytest Report Suffix"
