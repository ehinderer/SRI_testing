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
        (   # Query 0
            "PASSED test_onehops.py::test_trapi_aras[Test_ARA.json_Test KP_0-by_subject]",
            "PASSED",
            "ara",
            "Test_ARA.json_Test KP_0-by_subject",
            None  # no descriptive 'tail' to the error message
        ),

        (   # Query 1
            "SKIPPED [11] test_onehops.py:32: ",
            "SKIPPED",
            None,  # not a 'component' test
            None,  # no 'case'
            None   # no descriptive 'tail' to the error message
        ),
        (   # Query 2
            "FAILED test_onehops.py::test_trapi_aras[Test_ARA.json_Test KP_0-by_subject]",
            "FAILED",
            "ara",
            "Test_ARA.json_Test KP_0-by_subject",
            None  # no descriptive 'tail' to the error message
        ),

        (   # Query 3 - Moderately complex Pytest output line
            "FAILED test_onehops.py::test_trapi_kps[https://raw.githubusercontent.com/TranslatorSRI/" +
            "SRI_testing/main/tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP.json_0-by_subject]",
            "FAILED",
            "kp",
            "https://raw.githubusercontent.com/TranslatorSRI/" +
            "SRI_testing/main/tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP.json_0-by_subject",
            None  # no descriptive 'tail' to the error message
        ),
        (   # Query 4 - Really complex Pytest output line
            "SKIPPED [1] test_onehops.py:38: [https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/tests/" +
            "onehop/test_triples/KP/Unit_Test_KP/Test_KP.json] KP test for all test case S-P-O triples from this " +
            "location or just for the test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily)--" +
            "[biolink:part_of]->(PANTHER.FAMILY:PTHR34921:biolink:GeneFamily)'?",

            "SKIPPED",

            None,  # not a 'component' test

            "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/" +
            "main/tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP.json",

            " KP test for all test case S-P-O triples from this location or just for the test case S-P-O triple " +
            "'(PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily)--[biolink:part_of]->" +
            "(PANTHER.FAMILY:PTHR34921:biolink:GeneFamily)'?"

        )
    ]
)
def test_stsi_header_pattern(query):
    m = PASSED_SKIPPED_FAILED_PATTERN.match(query[0])
    assert m
    if query[1]:
        assert m["outcome"]
        assert m["outcome"] in ["PASSED", "SKIPPED", "FAILED"]
        assert m["outcome"] == query[1]
    else:
        assert not m["outcome"]

    if query[2]:
        assert m["component"]
        assert m["component"] in ["kp", "ara"]
        assert m["component"] == query[2]
    else:
        assert not m["component"]

    if query[3]:
        assert m["case"]
        assert m["case"] == query[3]
    else:
        assert not m["component"]

    if query[4]:
        assert m["tail"]
        assert m["tail"] == query[4]
    else:
        assert not m["tail"]
