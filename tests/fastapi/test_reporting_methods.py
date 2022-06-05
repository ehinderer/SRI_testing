"""
Test SRI Testing reporting code snippets
"""
from typing import Optional, Union, Dict, List, Tuple

import pytest
from os import linesep, path

from app.util import (
    SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN,
    PASSED_SKIPPED_FAILED_PATTERN,
    PYTEST_SUMMARY_PATTERN,
    TEST_CASE_IDENTIFIER_PATTERN,
    SRITestReport,
    parse_result
)
from tests.onehop.conftest import set_resource_component, add_kp_edge, generate_edge_id
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
    assert part[1] == f"{linesep}Pytest Report Suffix"


@pytest.mark.parametrize(
    "query",
    [
        (
            "Some_KP#0-by_subject",
            "Some_KP",
            "0",
            "by_subject"
        ),
        (
            "Some_KP#0",
            "Some_KP",
            "0",
            None
        ),
        (
            "Some_KP",
            "Some_KP",
            None,
            None
        ),
        (
            "Some-KP#0-by_subject",
            "Some-KP",
            "0",
            "by_subject"
        ),
        (
            "Test_ARA|Test_KP#1-raise_subject_entity",
            "Test_ARA|Test_KP",
            "1",
            "raise_subject_entity"
        ),
        (
            "Test_ARA|Test_KP#1",
            "Test_ARA|Test_KP",
            "1",
            None
        ),
        (
            "Test_ARA|Test_KP",
            "Test_ARA|Test_KP",
            None,
            None
        ),
        (
            "Test_ARA",
            "Test_ARA",
            None,
            None
        )
    ]
)
def test_case_identifier_pattern(query):
    m = TEST_CASE_IDENTIFIER_PATTERN.search(query[0])
    assert m
    assert m["resource_id"] == query[1]
    assert m["edge_num"] == query[2]
    assert m["test_id"] == query[3]

@pytest.mark.parametrize(
    "query",
    [
        (
                "Test_ARA|Test_KP#2-raise_subject_entity",
                "Test_ARA|Test_KP",
                2,
                "raise_subject_entity"
        ),
        (
                "Test_KP#3-raise_subject_entity",
                "Test_KP",
                3,
                "raise_subject_entity"
        )
    ]
)
def test_parse_case_pattern(query):
    resource_id, edge_num, test_id = SRITestReport.parse_test_case_identifier(query[0])
    assert resource_id == query[1]
    assert edge_num == query[2]
    assert test_id == query[3]


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


def mock_pytest_setup():
    # need to fake a few Pytest preconditions
    # (i.e. which would normally be set in the conftest.py)
    resource_id = "Test_KP"
    set_resource_component(resource_id, "KP")
    mock_edge = {
        "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
        "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
        "predicate": "biolink:part_of",
        "subject_id": "PANTHER.FAMILY:PTHR34921",
        "object_id": "PANTHER.FAMILY:PTHR34921"
    }
    for edge_i in range(0, 6):
        edge_id: str = generate_edge_id(resource_id, edge_i)
        edge: Dict = mock_edge.copy()
        edge["#"] = edge_i
        add_kp_edge(edge_id, edge)


TEST_COMPONENT: Dict = {
    "KP": "Test_KP",
    "ARA": "Test_ARA|Test_KP"
}

EDGE_ENTRY_TAGS: Tuple = (
    "subject_category",
    "object_category",
    "predicate",
    "subject",
    "object",
    "tests"
)

SUMMARY_ENTRY_TAGS: List = ["PASSED", "FAILED", "SKIPPED", "WARNING"]


@pytest.mark.parametrize(
    "query",
    [
        (
                "sample_pytest_report_1.txt",
                "FAILED",
                {"KP": True, "ARA": True},
                "0", "9", "57", "1"
        ),
        (
                "sample_pytest_report_2.txt",
                "PASSED",
                {"KP": True, "ARA": False},
                "9", "0", "57", "1"
        )
    ]
)
def test_parse_test_output(query):
    mock_pytest_setup()
    sample_file_path = path.join(TEST_DATA_DIR, query[0])
    with open(sample_file_path, "r") as sf:
        raw_result = sf.read()

        # The function assumes that you are
        # processing the file as a monolithic text blob
        report: SRITestReport = parse_result(raw_result)

    assert report

    output: Optional[Union[str, Dict]] = report.output()
    assert output

    # Top level tags of report
    assert "KP" in output
    assert "ARA" in output
    assert "SUMMARY" in output

    # Core resources from report
    for component in ["KP", "ARA"]:
        assert TEST_COMPONENT[component] in output[component]
        edges = output[component][TEST_COMPONENT[component]]

        # edges are only reported if FAILED or SKIPPED?
        report_edges: Dict = query[2]
        assert (len(edges) > 0) is report_edges[component]

        for edge in edges:
            assert all([tag in edge for tag in EDGE_ENTRY_TAGS])
            tests = edge["tests"]
            # for outcome in ["PASSED", "FAILED"]:
            #     if outcome == query[1]:
            #         assert outcome in output["KP"]
            #         assert outcome in output["ARA"]
            #     else:
            #         assert outcome not in output["KP"]
            #         assert outcome not in output["ARA"]

    assert all([tag in output["SUMMARY"] for tag in SUMMARY_ENTRY_TAGS])
    for i, outcome in enumerate(SUMMARY_ENTRY_TAGS):
        assert output["SUMMARY"][outcome] == query[i+3]

