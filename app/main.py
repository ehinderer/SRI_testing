"""
FastAPI web service wrapper for SRI Testing harness
(i.e. for reports to a Translator Runtime Status Dashboard)
"""
from typing import Optional, Dict, List, Generator
from pydantic import BaseModel

import uvicorn

import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from reasoner_validator.util import (
    latest,
    SemVer,
    SemVerError,
    SemVerUnderspecified
)

from translator.sri.testing.onehops_test_runner import (
    OneHopTestHarness,
    DEFAULT_WORKER_TIMEOUT
)
from translator.sri.testing.report_db import TestReportDatabase, FileReportDatabase

app = FastAPI()

origins = [
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#############################################################
# Here we globally configure and bind a TestReportDatabase
# to the OneHopTestHarness (use a FileReportDatabase for now)
#############################################################
test_report_database: TestReportDatabase = FileReportDatabase()
OneHopTestHarness.set_test_report_database(test_report_database)


###########################################################
# We don't instantiate the full TRAPI models here but
# just use an open-ended dictionary which should have
# query_graph, knowledge_graph and results JSON tag-values
###########################################################
class TestRunParameters(BaseModel):

    # TODO: we ignore the other SRI Testing parameters
    #       for the initial design of the web service
    #
    # # Which Test to Run?
    # teststyle: Optional[str] = "all"
    #
    # # Only use first edge from each KP file
    # one: bool = False
    #
    # # 'REGISTRY', directory or file from which to retrieve triples.
    # # (Default: 'REGISTRY', which triggers the use of metadata, in KP entries
    # # from the Translator SmartAPI Registry, to configure the tests).
    # triple_source: Optional[str] = 'REGISTRY'
    #
    # # 'REGISTRY', directory or file from which to retrieve ARA Config.
    # # (Default: 'REGISTRY', which triggers the use of metadata, in ARA entries
    # # from the Translator SmartAPI Registry, to configure the tests).
    # ara_source: Optional[str] = 'REGISTRY'

    # Optional TRAPI version override override against which
    # SRI Testing will be applied to Translator KPs and ARA's.
    # This version will override Translator SmartAPI Registry
    # KP or ARA entry specified 'x-trapi' metadata tag value
    # specified TRAPI version (Default: None).
    trapi_version: Optional[str] = None

    # optional Biolink Model version override against which
    # SRI Testing will be applied to Translator KPs and ARA's.
    # This version will override Translator SmartAPI Registry
    # KP entry specified 'x-translator' metadata tag value
    # specified Biolink Model version (Default: None)..
    biolink_version: Optional[str] = None

    # Worker Process data access timeout; defaults to DEFAULT_WORKER_TIMEOUT
    # which implies caller blocking until the data is available
    timeout: Optional[int] = DEFAULT_WORKER_TIMEOUT

    # Python Logger activation handed to Pytest
    # CLI argument '--log-cli-level', for debugging
    log: Optional[str] = None


class TestRunSession(BaseModel):

    test_run_id: str

    # TODO: user specified TRAPI version...
    #       we should somehow try to report the
    #       actual version used by the system
    # "trapi_version": trapi_version,

    # TODO: user specified Biolink Model version...
    #       we should somehow try to report the
    #       actual version used by the system
    # "biolink_version": biolink_version

    errors: Optional[List[str]] = None


def _is_valid_version(version_string: str):
    try:
        SemVer.from_string(version_string)
    except SemVerUnderspecified:
        # it's ok that it's underspecified?
        pass
    except SemVerError:
        return False

    return True


@app.post(
    "/run_tests",
    tags=['run'],
    response_model=TestRunSession,
    summary="Initiate an SRI Testing Run"
)
async def run_tests(test_parameters: TestRunParameters) -> TestRunSession:
    """
    Initiate an SRI Testing Run with TestRunParameters:

    - **trapi_version**: Optional[str]
    - **biolink_version**: Optional[str]
    - **timeout**: Optional[int]
    - **log**: Optional[str]
    \f
    :param test_parameters:
    :return: TestRunSession (just 'test_run_id' for now)
    """
    errors: List[str] = list()

    trapi_version: Optional[str] = None
    if test_parameters.trapi_version:
        trapi_version = test_parameters.trapi_version
        if not _is_valid_version(trapi_version):
            errors.append(f"'trapi_version' parameter '{trapi_version}' is not a valid SemVer string!")
        else:
            trapi_version = latest.get(test_parameters.trapi_version)

    biolink_version: Optional[str] = None
    if test_parameters.biolink_version:
        biolink_version = test_parameters.biolink_version
        if not _is_valid_version(biolink_version):
            errors.append(f"'biolink_version' parameter '{biolink_version}' is not a valid SemVer string!")

    log: Optional[str] = None
    if test_parameters.log:
        log = test_parameters.log
        try:
            logging.getLogger().setLevel(log)
        except (ValueError, TypeError):
            errors.append(f"'log' parameter '{log}' is not a valid Logging level!")

    if errors:
        return TestRunSession(test_run_id="Invalid Parameters - test run not started...", errors=errors)

    # Constructor initializes a fresh test run identifier with empty test run
    test_harness = OneHopTestHarness()

    test_harness.run(
        trapi_version=trapi_version,
        biolink_version=biolink_version,
        log=log,
        timeout=test_parameters.timeout if test_parameters.timeout else DEFAULT_WORKER_TIMEOUT
    )

    return TestRunSession(test_run_id=test_harness.get_test_run_id())


class TestRunStatus(BaseModel):
    test_run_id: str
    percent_complete: int


@app.get(
    "/status/{test_run_id}",
    tags=['report'],
    response_model=TestRunStatus,
    summary="Retrieve the summary of a specified SRI Testing run."
)
async def get_status(test_run_id: str) -> TestRunStatus:
    """
    Returns the percentage completion status of the current OneHopTestHarness test run.

    \f
    :param test_run_id: test_run_id: test run identifier (as returned by /run_tests endpoint).

    :return: TestRunStatus, with fields 'test_run_id' and 'percent_complete', the latter being
                             an integer 0..100 indicating the percentage completion of the test run.
    """
    assert test_run_id, "Null or empty Test Run Identifier?"

    percent_complete: int = OneHopTestHarness(test_run_id=test_run_id).get_status()

    return TestRunStatus(test_run_id=test_run_id, percent_complete=percent_complete)


class TestRunList(BaseModel):
    test_runs: List[str]


@app.get(
    "/list",
    tags=['report'],
    response_model=TestRunList,
    summary="Retrieve the list of completed test runs."
)
async def get_test_run_list() -> TestRunList:
    """
    Returns the catalog of completed OneHopTestHarness test runs.

    \f
    :return: TestRunList, list of timestamp identifiers of completed OneHopTestHarness test runs.
    """
    test_runs: List[str] = OneHopTestHarness.get_completed_test_runs()

    return TestRunList(test_runs=test_runs)


class TestRunSummary(BaseModel):
    test_run_id: str
    summary: Dict


@app.get(
    "/summary/{test_run_id}",
    tags=['report'],
    response_model=TestRunSummary,
    summary="Retrieve the summary of a completed specified OneHopTestHarness test run."
)
async def get_summary(test_run_id: str) -> TestRunSummary:
    """
    Returns a JSON summary report of results for a completed **test_run_id**-identified OneHopTestHarness test run.

    \f
    :param test_run_id: test_run_id: test run identifier (as returned by /run_tests endpoint).

    :return: TestRunSummary, with fields 'test_run_id' and 'summary', the latter being a
                             JSON document summary of available unit test results.
    :raises: HTTPException(404) if the summary is not (yet?) available.
    """
    assert test_run_id, "Null or empty Test Run Identifier?"

    summary: Optional[Dict] = OneHopTestHarness(test_run_id=test_run_id).get_summary()

    if summary is not None:
        return TestRunSummary(test_run_id=test_run_id, summary=summary)
    else:
        raise HTTPException(status_code=404, detail=f"Summary for test run '{test_run_id}' is not (yet) available?")


class TestRunEdgeDetails(BaseModel):
    details: Dict


@app.get(
    "/details/{test_run_id}/{component}/{resource_id}/{edge_num}",
    tags=['report'],
    response_model=TestRunEdgeDetails,
    summary="Retrieve the test result details for a specified SRI Testing Run input edge."
)
async def get_details(test_run_id: str, component: str, resource_id: str, edge_num: str) -> TestRunEdgeDetails:
    """
    Return edge details for a specified unit test in an
     identified test run defined by the following query path parameters:

    - **component**: Translator component being tested: 'ARA' or 'KP'.
    - **resource_id**: identifier of the resource being tested, may be single KP identifier (i.e. 'Some_KP')
                       or a hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                       (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    - **edge_num**: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.

    \f
    :param test_run_id: test run identifier (as returned by /run_tests endpoint).
    :param component: Translator component being tested: 'ARA' or 'KP'.
    :param resource_id: identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP') or a
                        hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                        (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    :param edge_num: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.

    :return: TestRunEdgeDetails, echoing input parameters alongside the requested 'details', the latter which is a
                                 details JSON document for the specified unit test.

    :raises: HTTPException(404) if the requested edge unit test details are not (yet?) available.
    """
    assert test_run_id, "Null or empty Test Run Identifier?"
    assert component, "Null or empty Translator Component?"
    assert resource_id, "Null or empty Resource Identifier?"
    assert edge_num, "Null or empty Edge Number?"

    details: Optional[Dict] = OneHopTestHarness(test_run_id=test_run_id).get_details(
        component=component,
        resource_id=resource_id,
        edge_num=edge_num
    )

    if details is not None:
        return TestRunEdgeDetails(details=details)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Details for edge {edge_num} of {component} '{resource_id}', " +
                   f"from test run '{test_run_id}', are not (yet) available?"
        )


@app.get(
    "/response/{test_run_id}/{component}/{resource_id}/{edge_num}/{test_id}",
    tags=['report'],
    summary="Directly stream the TRAPI response JSON message for a " +
            "specified SRI Testing unit test of a given input edge."
)
async def get_response(
        test_run_id: str,
        component: str,
        resource_id: str,
        edge_num: str,
        test_id: str
) -> StreamingResponse:
    """
    Return full TRAPI response message as a streamed downloadable text file, if available, for a specified unit test
    of an edge, as identified test run defined by the following query path parameters:

    - **component**: Translator component being tested: 'ARA' or 'KP'
    - **resource_id**: identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP') or a
                        hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                        (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    - **edge_num**: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.
    - **test_id**: target unit test identifier, one of the values noted in the edge leaf nodes of the test run summary.

    \f
    :param test_run_id: str, test run identifier (as returned by /run_tests endpoint)
    :param component: str, Translator component being tested: 'ARA' or 'KP'
    :param resource_id: str, identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP') or a
                        hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                        (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    :param edge_num: str, target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.
    :param test_id: str, target unit test identifier, one of the values noted in the
                         edge leaf nodes of the JSON test run summary (e.g. 'by_subject', etc.).

    :return: StreamingResponse, downloadable text file of TRAPI response

    :raise: HTTPException(404) if the requested TRAPI response JSON text data file is not (yet?) available.
    """
    assert test_run_id, "Null or empty Test Run Identifier?"
    assert component, "Null or empty Translator Component?"
    assert resource_id, "Null or empty Resource Identifier?"
    assert edge_num, "Null or empty Edge Number?"
    assert test_id, "Null or empty Unit Test Identifier?"

    try:
        content_generator: Generator = OneHopTestHarness(
            test_run_id=test_run_id
        ).get_streamed_response_file(
            component=component,
            resource_id=resource_id,
            edge_num=edge_num,
            test_id=test_id
        )
        return StreamingResponse(
            content=content_generator,
            media_type="application/json"
        )
    except RuntimeError:
        raise HTTPException(
            status_code=404,
            detail=f"TRAPI Response JSON text file for unit test {test_id} for edge {edge_num} of "
                   f"{component} '{resource_id}', from test run '{test_run_id}', is not (yet) available?"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
