"""
Test SRI Testing reporting code snippets
"""
import pytest
from os import linesep, path

from app.util import (
    SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN,
    PASSED_SKIPPED_FAILED_PATTERN,
    PYTEST_SUMMARY_PATTERN,
    SRITestReport,
    parse_result
)
from tests import TEST_DATA_DIR


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
def test_stsi_header_pattern_search(query):
    assert SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.search(query)


def test_stsi_header_pattern_splitting():
    query = f"Pytest report prefix{linesep}== short test summary info =={linesep}Pytest Report Suffix"
    part = SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN.split(query)
    assert len(part) == 2
    assert part[0] == f"Pytest report prefix{linesep}"
    assert part[1] == "Pytest Report Suffix"


_SAMPLE_BIOLINK_ERRORS = [
    "BLM Version 1.8.2 Error in Knowledge Graph: 'biolink:SmallMolecule' for node " +
    "'PUBCHEM.COMPOUND:597' is not a recognized Biolink Model category?",

    "BLM Version 2.2.16 Error in Knowledge Graph: Edge 'NCBIGene:29974--biolink:interacts_with->" +
    "PUBCHEM.COMPOUND:597' has missing or empty attributes?"
]


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
            "onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json] KP test for all test case S-P-O triples from this " +
            "location or just for the test case S-P-O triple '(PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily)--" +
            "[biolink:part_of]->(PANTHER.FAMILY:PTHR34921:biolink:GeneFamily)'?",

            "SKIPPED",

            None,  # not a 'component' test

            "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/" +
            "main/tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json",

            " KP test for all test case S-P-O triples from this location or just for the test case S-P-O triple " +
            "'(PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily)--[biolink:part_of]->" +
            "(PANTHER.FAMILY:PTHR34921:biolink:GeneFamily)'?"

        ),
        (   # Query 5 - Another really complex Pytest output line
            "SKIPPED [1] test_onehops.py:38: [https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/tests/" +
            "onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json] ARA test case S-P-O triple " +
            "'(PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily)--[biolink:part_of]->" +
            "(PANTHER.FAMILY:PTHR34921:biolink:GeneFamily)', since it is not Biolink Model compliant " +
            f"with model version 2.2.16:",

            "SKIPPED",

            None,  # not a 'component' test

            "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/tests/" +
            "onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json",

            " ARA test case S-P-O triple " +
            "'(PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily)--[biolink:part_of]->" +
            "(PANTHER.FAMILY:PTHR34921:biolink:GeneFamily)', since it is not Biolink Model compliant " +
            f"with model version 2.2.16:"
        )
    ]
)
def test_stsi_header_pattern_match(query):
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


TPS = "test_pytest_summary():"


@pytest.mark.parametrize(
    "query",
    [
        ("============= 40 passed, 9 failed, 2 skipped, 4 warning in 83.33s (0:01:23) ==============", 40, 9, 2, 4),
        ("============= 9 failed, 2 skipped, 4 warning in 83.33s (0:01:23) ==============", None, 9, 2, 4),
        ("============= 40 passed, 2 skipped, 4 warning in 83.33s (0:01:23) ==============", 40, None, 2, 4),
        ("============= 40 passed, 9 failed, 4 warning in 83.33s (0:01:23) ==============", 40, 9, None, 4),
        ("============= 40 passed, 9 failed, 2 skipped in 83.33s (0:01:23) ==============", 40, 9, 2, None)
    ]
)
def test_pytest_summary(query):
    match = PYTEST_SUMMARY_PATTERN.match(query[0])
    assert match, f"{TPS} no match?"
    if query[1]:
        assert match["passed"], f"{TPS} 'passed' field not matched?"
        assert match["passed"] == '40', f"{TPS} 'passed' value not matched?"
    if query[2]:
        assert match["failed"], f"{TPS} 'failed' field not matched?"
        assert match["failed"] == '9', f"{TPS} 'failed' value not matched?"
    if query[3]:
        assert match["skipped"], f"{TPS} 'skipped' field not matched?"
        assert match["skipped"] == '2', f"{TPS} 'skipped' field not matched?"
    if query[4]:
        assert match["warning"], f"{TPS} 'warning' field not matched?"
        assert match["warning"] == '4', f"{TPS} 'warning' field not matched?"


SAMPLE_CASE = "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/" + \
              "main/tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json"


@pytest.mark.parametrize(
    "query",
    [
        (
                "sample_pytest_report_1.txt",
                "FAILED",
                "0", "9", "57", "1"
        ),
        (
                "sample_pytest_report_2.txt",
                "PASSED",
                "9", "0", "57", "1"
        )
    ]
)
def test_report(query):
    sample_file_path = path.join(TEST_DATA_DIR, query[0])
    with open(sample_file_path, "r") as sf:

        raw_result = sf.read()

        # The function assumes that you are
        # processing the file as a monolithic text blob
        report: SRITestReport = parse_result(raw_result)

    assert report

    assert "INPUT" in report
    assert "SKIPPED" in report["INPUT"]
    assert SAMPLE_CASE in report["INPUT"]["SKIPPED"]
    sample_tail = report["INPUT"]["SKIPPED"][SAMPLE_CASE]
    assert any([tail.startswith("KP test case S-P-O triple") for tail in sample_tail])

    assert "KP" in report
    assert "ARA" in report

    for outcome in ["PASSED", "FAILED"]:
        if outcome == query[1]:
            assert outcome in report["KP"]
            assert outcome in report["ARA"]
        else:
            assert outcome not in report["KP"]
            assert outcome not in report["ARA"]

    assert "SUMMARY" in report
    assert "PASSED" in report["SUMMARY"]
    assert report["SUMMARY"]["PASSED"] == query[2]
    assert "FAILED" in report["SUMMARY"]
    assert report["SUMMARY"]["FAILED"] == query[3]
    assert "SKIPPED" in report["SUMMARY"]
    assert report["SUMMARY"]["SKIPPED"] == query[4]
    assert "WARNING" in report["SUMMARY"]
    assert report["SUMMARY"]["WARNING"] == query[5]
