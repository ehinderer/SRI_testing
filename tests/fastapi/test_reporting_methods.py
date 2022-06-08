"""
Test SRI Testing reporting code snippets
"""
from typing import Optional, Union, Dict, Tuple, Set, List, Any
from os import linesep, path

import pytest

from app.util import (
    SUMMARY_ENTRY_TAGS,
    SHORT_TEST_SUMMARY_INFO_HEADER_PATTERN,
    PASSED_SKIPPED_FAILED_PATTERN,
    PYTEST_SUMMARY_PATTERN,
    TEST_CASE_IDENTIFIER_PATTERN,
    SRITestReport,
    parse_result,
    PYTEST_HEADER_START_PATTERN,
    PYTEST_HEADER_END_PATTERN,
    PYTEST_FOOTER_START_PATTERN,
    LOGGER_PATTERN,
    skip_header,
    skip_footer
)
from tests import TEST_DATA_DIR
from tests.onehop.conftest import cache_resource_metadata, add_kp_edge
from tests.translator.registry import MOCK_TRANSLATOR_SMARTAPI_REGISTRY_METADATA


def mock_pytest_setup():
    # need to fake a few Pytest preconditions
    # (i.e. which would normally be set in the conftest.py)
    mock_resources: List[Dict[str, Any]] = list()
    mock_hits: List[Dict] = MOCK_TRANSLATOR_SMARTAPI_REGISTRY_METADATA["hits"]
    for hit in mock_hits:
        hit_info = hit['info']
        x_translator = hit_info['x-translator']
        x_trapi = hit_info['x-trapi']
        mock_resources.append(
            {
                "title": hit_info['title'],
                "api_version": hit_info['version'],
                "component": x_translator['component'],
                "infores": x_translator['infores'],
                "team": x_translator['team'],
                "biolink_version": x_translator['biolink-version'],
                "trapi_version": x_trapi['version'],
                "test_data_location": x_trapi['test_data_location']
            }
        )

    mock_edge = {
        "subject_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
        "object_category": "PANTHER.FAMILY:PTHR34921:SF1:biolink:GeneFamily",
        "predicate": "biolink:part_of",
        "subject_id": "PANTHER.FAMILY:PTHR34921",
        "object_id": "PANTHER.FAMILY:PTHR34921"
    }
    for metadata in mock_resources:
        cache_resource_metadata(metadata=metadata)
        resource_id = metadata['api_name']
        for edge_idx in range(0, 6):
            edge: Dict = mock_edge.copy()
            edge["idx"] = edge_idx
            add_kp_edge(resource_id, edge_idx, edge)


def test_pytest_header_start_pattern():
    assert PYTEST_HEADER_START_PATTERN.search(
        "============================= test session starts ============================="
    )


@pytest.mark.parametrize(
    "query",
    [
        "collecting ... collected 88 items",
        "collected 88 items",
        " collected 88 items",
        "collected 88 items ",
        " collected 88 items ",
        "collected 88 items\n",
    ]
)
def test_pytest_header_end_pattern(query):
    assert PYTEST_HEADER_END_PATTERN.search(query)


@pytest.mark.parametrize(
    "query",
    [
        "CRITICAL    sometest.py:123 blah, blah, blah",
        "ERROR    sometest.py:123 blah, blah, blah",
        "WARNING    sometest.py:123 blah, blah, blah",
        "INFO    sometest.py:123 blah, blah, blah",
        "DEBUG    sometest.py:123 blah, blah, blah"
    ]
)
def test_pytest_logger_pattern(query):
    assert LOGGER_PATTERN.match(query)


TEST_HEADER = """
============================= test session starts =============================

platform win32 -- Python 3.9.7, pytest-7.1.1, pluggy-1.0.0 -- c:\\users\\sri_testing\py\scripts\python.exe

cachedir: .pytest_cache

rootdir: C:\\Users\richa\PycharmProjects\SRI_testing\tests\onehop

plugins: anyio-3.5.0, asyncio-0.18.2, harvest-1.10.3

asyncio: mode=legacy

collecting ... collected 88 items



test_onehops.py::test_trapi_kps[Test_KP_1#0-by_subject] PASSED           [  1%]
"""


def test_skip_header():
    lines = TEST_HEADER.split('\n')
    line: str
    for line in lines:

        line = line.strip()  # spurious leading and trailing whitespace removed
        if not line:
            continue  # ignore blank lines

        if skip_header(line):
            continue

        # if it makes it this far, then this line will be seen?
        assert line == "test_onehops.py::test_trapi_kps[Test_KP_1#0-by_subject] PASSED           [  1%]"


def test_pytest_footer_start_pattern():
    assert PYTEST_FOOTER_START_PATTERN.search(
        "=================================== FAILURES ==================================="
    )


TEST_FOOTER = """================================== FAILURES ===================================
C:\\Users\richa\PycharmProjects\SRI_testing\translator\trapi\__init__.py:163: AssertionError: Edge:
============================== warnings summary ===============================
..\..\py\lib\site-packages\pytest_asyncio\plugin.py:191
  c:\\users\\richa\pycharmprojects\sri_testing\py\lib\site-packages\pytest_asyncio\plugin.py:191: ...

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED test_onehops.py::test_trapi_aras[Test_ARA|Test_KP_2#0-by_object] - AssertionError: Edge:
======= 6 failed, 19 passed, 63 skipped, 1 warning in 738.86s (0:12:18) =======
"""


def test_skip_footer():
    lines = TEST_FOOTER.split('\n')
    line: str
    for line in lines:

        line = line.strip()  # spurious leading and trailing whitespace removed
        if not line:
            continue  # ignore blank lines

        psp = PYTEST_SUMMARY_PATTERN.match(line)
        if psp:
            assert line == "======= 6 failed, 19 passed, 63 skipped, 1 warning in 738.86s (0:12:18) ======="

        if skip_footer(line):
            continue

        assert False, "test_skip_footer() unit should not generally get here!"


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
    [   # Now generated by Pytest -vv format without summary
        (  # New Query 0
            "test_onehops.py::test_trapi_kps[Test_KP_1#4-by_subject] SKIPPED " +
            "(" +
            "test case S-P-O triple '(FOO:1234|biolink:GeneFamily)--[biolink:part_of]" +
            "->(PANTHER.FAMILY:PTHR34921|biolink:GeneFamily)', since it is not Biolink Model compliant" +
            ")" +
            " [ 1%]",
            "SKIPPED",
            "kp",
            "Test_KP_1#4-by_subject",
            "(test case S-P-O triple '(FOO:1234|biolink:GeneFamily)--[biolink:part_of]" +
            "->(PANTHER.FAMILY:PTHR34921|biolink:GeneFamily)', since it is not Biolink Model compliant)"
        ),
        (   # New Query 1 - generated by Pytest -vv format
            "test_onehops.py::test_trapi_kps[Test_KP#0-by_subject] FAILED [  5%]",
            "FAILED",
            "kp",
            "Test_KP#0-by_subject",
            None  # no descriptive 'tail' to the error message
        ),
        (   # New Query 2 - generated by Pytest -vv format
            "test_onehops.py::test_trapi_kps[Test_KP_1#0-inverse_by_new_subject] PASSED [ 10%]",
            "PASSED",
            "kp",
            "Test_KP_1#0-inverse_by_new_subject",
            None  # no descriptive 'tail' to the error message
        ),
        (  # New Query 3 - generated by Pytest -vv format
           "test_onehops.py::test_trapi_aras[Test_ARA|Test_KP#0-by_subject] FAILED    [100%]",
           "FAILED",
           "ara",
           "Test_ARA|Test_KP#0-by_subject",
           None  # no descriptive 'tail' to the error message
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
        ("============= 9 failed, 40 passed, 2 skipped, 4 warning in 83.33s (0:01:23) ==============", 9, 40, 2, 4),
        ("============= 9 failed, 2 skipped, 4 warning in 83.33s (0:01:23) ==============", 9, None, 2, 4),
        ("============= 40 passed, 2 skipped, 4 warning in 83.33s (0:01:23) ==============", None, 40, 2, 4),
        ("============= 9 failed, 40 passed, 4 warning in 83.33s (0:01:23) ==============", 9, 40, None, 4),
        ("============= 9 failed, 40 passed, 2 skipped in 83.33s (0:01:23) ==============", 9, 40, 2, None)
    ]
)
def test_pytest_summary(query):
    match = PYTEST_SUMMARY_PATTERN.match(query[0])
    assert match, f"{TPS} no match?"

    if query[1]:
        assert match["failed"], f"{TPS} 'failed' field not matched?"
        assert match["failed"] == '9', f"{TPS} 'failed' value not matched?"
    if query[2]:
        assert match["passed"], f"{TPS} 'passed' field not matched?"
        assert match["passed"] == '40', f"{TPS} 'passed' value not matched?"
    if query[3]:
        assert match["skipped"], f"{TPS} 'skipped' field not matched?"
        assert match["skipped"] == '2', f"{TPS} 'skipped' field not matched?"
    if query[4]:
        assert match["warning"], f"{TPS} 'warning' field not matched?"
        assert match["warning"] == '4', f"{TPS} 'warning' field not matched?"


TEST_COMPONENT: Dict[str, Set] = {
    "KP": {"Test_KP_1", "Test_KP_2"},
    "ARA": {"Test_ARA|Test_KP_1", "Test_ARA|Test_KP_2"}
}

EDGE_ENTRY_TAGS: Tuple = (
    "subject_category",
    "object_category",
    "predicate",
    "subject",
    "object",
    "tests"
)


@pytest.mark.parametrize(
    "query",
    [
        (
                "sample_pytest_report_1.txt",
                "FAILED",
                True,
                True,
                "6", "19", "63"
        ),
        (
                "sample_pytest_report_2.txt",
                "PASSED",
                True,
                False,
                "25", "0", "63"
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
        for resource_id in TEST_COMPONENT[component]:

            if resource_id not in output[component]:
                print(f"Resource {resource_id} not seen in {component} output? Ignoring...")
                continue

            edges = output[component][resource_id]

            # edges are only reported if FAILED or SKIPPED, not PASSED?
            assert (len(edges) > 0) is query[2 if component == "KP" else 3]

            edge: Dict
            for edge in edges:
                assert all([tag in edge for tag in EDGE_ENTRY_TAGS])
                tests = edge["tests"]
                for test in tests:
                    result: Dict = tests[test]
                    for outcome in result.keys():
                        assert outcome in SUMMARY_ENTRY_TAGS
                        # TODO: can we validate anything further here?

        assert all([tag in output["SUMMARY"] for tag in SUMMARY_ENTRY_TAGS])
        for i, outcome in enumerate(SUMMARY_ENTRY_TAGS):
            assert output["SUMMARY"][outcome] == query[i+4]

