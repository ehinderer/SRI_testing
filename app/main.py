"""
FastAPI web service wrapper for SRI Testing harness
(i.e. for reports to a Translator Runtime Status Dashboard)
"""
from typing import Optional, Dict
from pydantic import BaseModel

import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from reasoner_validator.util import latest
from translator.sri.testing.report import (
    OneHopTestHarness,
    DEFAULT_WORKER_TIMEOUT
)

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


#
# We don't instantiate the full TRAPI models here but
# just use an open-ended dictionary which should have
# query_graph, knowledge_graph and results JSON tag-values
#
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


@app.post(
    "/run_tests",
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
    trapi_version: Optional[str] = latest.get(test_parameters.trapi_version) if test_parameters.trapi_version else None
    biolink_version: Optional[str] = test_parameters.biolink_version
    log: Optional[str] = test_parameters.log

    testrun = OneHopTestHarness(test_parameters.timeout)

    testrun.run(
        trapi_version=trapi_version,
        biolink_version=biolink_version,
        log=log
    )

    return TestRunSession(test_run_id=testrun.get_test_run_id())


class TestRunSummary(BaseModel):
    test_run_id: str
    summary: Dict


@app.get(
    "/summary/{test_run_id}",
    response_model=TestRunSummary,
    summary="Retrieve the summary of a specified SRI Testing run."
)
async def get_summary(test_run_id: str) -> TestRunSummary:
    """
    Returns a JSON summary report of test results for a given **test_run_id**.

    \f
    :param test_run_id: test_run_id: test run identifier (as returned by /run_tests endpoint).

    :return: TestRunSummary, with fields 'test_run_id' and 'summary', the latter being a
                             JSON indexed summary of available unit test results.
    """
    summary: Optional[Dict] = OneHopTestHarness.get_summary(test_run_id)

    if summary is None:
        summary = {"status": "Test summary for testing run is not yet available?"}

    return TestRunSummary(
        test_run_id=test_run_id,
        summary=summary
    )


class TestRunEdgeDetails(BaseModel):
    details: Dict


@app.get(
    "/details/{test_run_id}/{component}/{resource_id}/{edge_num}",
    response_model=TestRunEdgeDetails,
    summary="Retrieve the test result details for a specified SRI Testing Run input edge."
)
async def get_details(test_run_id: str, component: str, resource_id: str, edge_num: str) -> TestRunEdgeDetails:
    """
    Return edge details for a specified unit test in an
     identified test run defined by the following query path parameters:

    - **component**: Translator component being tested: 'ARA' or 'KP'
    - **resource_id**: identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP') or a
                        hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                        (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    - **edge_num**: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.

    \f
    :param test_run_id: test run identifier (as returned by /run_tests endpoint)
    :param component: Translator component being tested: 'ARA' or 'KP'
    :param resource_id: identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP') or a
                        hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                        (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    :param edge_num: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.

    :return: TestRunEdgeDetails, echoing input parameters alongside the requested 'details', the latter which are the
                                 details relating to the specified unit test, encoded as a JSON data structure.
    """
    assert test_run_id, "Null or empty Session Identifier?"
    assert component, "Null or empty Translator Component?"
    assert resource_id, "Null or empty Resource Identifier?"
    assert edge_num, "Null or empty Edge Number?"

    details: Optional[Dict] = OneHopTestHarness.get_details(test_run_id, component, resource_id, edge_num)

    if details is None:
        details = {"status": "Test details for edge in specified testing run are not (yet) available?"}

    return TestRunEdgeDetails(
        details=details
    )


@app.get(
    "/response/{test_run_id}/{component}/{resource_id}/{edge_num}/{test_id}",
    summary="Retrieve the TRAPI response JSON message for a specified SRI Testing unit test of a given input edge."
)
async def get_response(
        test_run_id: str,
        component: str,
        resource_id: str,
        edge_num: str,
        test_id: str
) -> FileResponse:
    """
    Return full TRAPI response message in a downloadable text file, if available, for a specified unit test of
    an edge, as identified test run defined by the following query path parameters:

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

    :return: FileResponse, downloadable text file of TRAPI response
    """
    assert test_run_id, "Null or empty Session Identifier?"
    assert component, "Null or empty Translator Component?"
    assert resource_id, "Null or empty Resource Identifier?"
    assert edge_num, "Null or empty Edge Number?"
    assert test_id, "Null or empty Unit Test Identifier?"

    response_file_path: str = \
        OneHopTestHarness.get_response_file_path(
            test_run_id,
            component,
            resource_id,
            edge_num,
            test_id
        )

    try:
        return FileResponse(response_file_path)
    except RuntimeError:
        response_file_name = response_file_path.split("/")[-1]
        raise HTTPException(status_code=404, detail=f"File '{response_file_name}' does not exist?")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
