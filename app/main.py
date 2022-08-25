"""
FastAPI web service wrapper for SRI Testing harness
(i.e. for reports to a Translator Runtime Status Dashboard)
"""
from typing import Optional, Dict, List, Generator, Union

from os.path import dirname, abspath

from pydantic import BaseModel

import uvicorn

import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
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

favicon_path = f"{abspath(dirname(__file__))}/img/favicon.ico"


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


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
async def run_tests(test_parameters: Optional[TestRunParameters] = None) -> TestRunSession:
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

    trapi_version: Optional[str] = None
    biolink_version: Optional[str] = None
    log: Optional[str] = None
    timeout: int = DEFAULT_WORKER_TIMEOUT

    errors: List[str] = list()
    if test_parameters:

        if test_parameters.trapi_version:
            trapi_version = test_parameters.trapi_version
            if not _is_valid_version(trapi_version):
                errors.append(f"'trapi_version' parameter '{trapi_version}' is not a valid SemVer string!")
            else:
                trapi_version = latest.get(test_parameters.trapi_version)

        if test_parameters.biolink_version:
            biolink_version = test_parameters.biolink_version
            if not _is_valid_version(biolink_version):
                errors.append(f"'biolink_version' parameter '{biolink_version}' is not a valid SemVer string!")

        if test_parameters.log:
            log = test_parameters.log
            try:
                logging.getLogger().setLevel(log)
            except (ValueError, TypeError):
                errors.append(f"'log' parameter '{log}' is not a valid Logging level!")

        timeout = test_parameters.timeout if test_parameters.timeout else DEFAULT_WORKER_TIMEOUT

    if errors:
        return TestRunSession(test_run_id="Invalid Parameters - test run not started...", errors=errors)

    # Constructor initializes a fresh
    # test run with a new identifier
    test_harness = OneHopTestHarness()

    test_harness.run(
        trapi_version=trapi_version,
        biolink_version=biolink_version,
        log=log,
        timeout=timeout
    )

    return TestRunSession(test_run_id=test_harness.get_test_run_id())


class TestRunStatus(BaseModel):
    test_run_id: str
    percent_complete: int


@app.get(
    "/status",
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

    percent_complete: int = OneHopTestHarness(test_run_id=test_run_id).get_status()

    return TestRunStatus(test_run_id=test_run_id, percent_complete=percent_complete)


class TestRunList(BaseModel):
    test_runs: List[str]


@app.get(
    "/test_runs",
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


class Message(BaseModel):
    message: str


class TestRunSummary(BaseModel):
    test_run_id: str
    summary: Dict


@app.get(
    "/index",
    tags=['report'],
    response_model=TestRunSummary,
    summary="Retrieve the index - KP and ARA resource tags - of a completed specified OneHopTestHarness test run.",
    responses={404: {"model": Message}}
)
async def get_index(test_run_id: str) -> Union[TestRunSummary, JSONResponse]:
    """
    Returns a JSON index  - KP and ARA resource tags - for a completed OneHopTestHarness test run.

    \f
    :param test_run_id: test_run_id: test run identifier (as returned by /run_tests endpoint).

    :return: TestRunSummary, with fields 'test_run_id' and 'summary', the latter being a
                             JSON document summary of available unit test results.
    :raises: HTTPException(404) if the summary is not (yet?) available.
    """

    index: Optional[Dict] = OneHopTestHarness(test_run_id=test_run_id).get_index()

    if index is not None:
        return TestRunSummary(test_run_id=test_run_id, summary=index)
    else:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Index for test run '{test_run_id}' is not (yet) available?"
            }
        )

@app.get(
    "/summary",
    tags=['report'],
    response_model=TestRunSummary,
    summary="Retrieve the summary of a completed specified OneHopTestHarness test run.",
    responses={404: {"model": Message}}
)
async def get_summary(test_run_id: str) -> Union[TestRunSummary, JSONResponse]:
    """
    Returns a JSON summary report of results for a completed OneHopTestHarness test run.

    \f
    :param test_run_id: test_run_id: test run identifier (as returned by /run_tests endpoint).

    :return: TestRunSummary, with fields 'test_run_id' and 'summary', the latter being a
                             JSON document summary of available unit test results.
    :raises: HTTPException(404) if the summary is not (yet?) available.
    """

    summary: Optional[Dict] = OneHopTestHarness(test_run_id=test_run_id).get_summary()

    if summary is not None:
        return TestRunSummary(test_run_id=test_run_id, summary=summary)
    else:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Summary for test run '{test_run_id}' is not (yet) available?"
            }
        )


@app.get(
    "/resource",
    tags=['report'],
    response_model=TestRunSummary,
    summary="Retrieve the test result summary for a specified resource from a specified SRI Testing Run.",
    responses={400: {"model": Message}, 404: {"model": Message}}
)
async def get_kp_resource_summary(
        test_run_id: str,
        ara_id: Optional[str] = None,
        kp_id: Optional[str] = None
) -> Union[TestRunSummary, JSONResponse]:
    """
    Return result summary for a specific KP resource in an
    identified test run, identified by a specific set of query parameters:
    - **test_run_id**: test run being accessed.
    - **ara_id**: identifier of the ARA resource whose indirect KP test results are being accessed
    - **kp_id**: identifier of the KP resource whose test results are specifically being accessed.
        - Case 1 - non-empty kp_id, empty ara_id == just return the summary of the one directly tested KP resource
        - Case 2 - non-empty ara_id, non-empty kp_id == return the one specific KP tested via the specified ARA
        - Case 3 - non-empty ara_id, empty kp_id == return all the KPs being tested under the specified ARA
        - Case 4 - empty ara_id and kp_id == error ...at least one of 'ara_id' and 'kp_id' needs to be provided.

    - **kp_id**: identifier of the KP resource being tested.

    \f
    :param test_run_id: test run identifier (as returned by /run_tests endpoint).
    :param ara_id: identifier of the ARA resource whose indirect KP test results are being accessed
    :param kp_id: identifier of the KP resource whose test results are specifically being accessed.
        - Case 1 - non-empty kp_id, empty ara_id == just return the summary of the one directly tested KP resource
        - Case 2 - non-empty ara_id, non-empty kp_id == return the one specific KP tested via the specified ARA
        - Case 3 - non-empty ara_id, empty kp_id == return all the KPs being tested under the specified ARA
        - Case 4 - empty ara_id and kp_id == error ...at least one of 'ara_id' and 'kp_id' needs to be provided.

    :return: TestRunResourceSummary, echoing input parameters alongside the requested 'details', the latter which is a
                                 details JSON document for the specified unit test.

    :raises: HTTPException(404) if the requested edge unit test details are not (yet?) available.
    """
    # TODO: maybe we can validate the ara_id and kp_id against the /index catalog?
    summary: Optional[Dict]
    if ara_id:
        if kp_id:
            # Case 2: return the one specific KP tested via the specified ARA
            summary = OneHopTestHarness(test_run_id=test_run_id).get_resource_summary(
                component="ARA",
                ara_id=ara_id,
                kp_id=kp_id
            )
        else:
            # Case 3: return all the KPs being tested under the specified ARA
            # TODO: Merged ARA implementation without a specific kp_id, needs a bit more thought.
            return JSONResponse(status_code=400, content={"message": "Null kp_id parameter is not yet supported?"})
    else:  # empty 'ara_id'
        if kp_id:
            # Case 1: just return the summary of the one directly tested KP resource
            summary: Optional[Dict] = OneHopTestHarness(test_run_id=test_run_id).get_resource_summary(
                component="KP",
                kp_id=kp_id
            )
        else:
            # Case 4: error...at least one of 'ara_id' and 'kp_id' needs to be provided.
            return JSONResponse(
                status_code=400,
                content={"message": "The 'ara_id' and 'kp_id' cannot both be empty parameters!"}
            )
    if summary is not None:
        return TestRunSummary(test_run_id=test_run_id, summary=summary)
    else:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Resource summary, for ara_id '{str(ara_id)}' and kp_id '{str(kp_id)}', " +
                           f"is not (yet) available from test run '{test_run_id}'?"
            }
        )


class TestRunEdgeDetails(BaseModel):
    details: Dict


@app.get(
    "/details",
    tags=['report'],
    response_model=TestRunEdgeDetails,
    summary="Retrieve the test result details for a specified SRI Testing Run input edge.",
    responses={400: {"model": Message}, 404: {"model": Message}}
)
async def get_details(
    test_run_id: str,
    edge_num: str,
    ara_id: Optional[str] = None,
    kp_id: Optional[str] = None
) -> Union[TestRunEdgeDetails, JSONResponse]:
    """
    Retrieve the test result details for a specified ARA or KP resource
    in a given test run defined by the following query path parameters:
    - **test_run_id**: test run being accessed.
    - **edge_num**: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.

    - **ara_id**: identifier of the ARA resource whose indirect KP test results are being accessed
    - **kp_id**: identifier of the KP resource whose test results are specifically being accessed.
        - Case 1 - non-empty kp_id, empty ara_id == just return the summary of the one directly tested KP resource
        - Case 2 - non-empty ara_id, non-empty kp_id == return the one specific KP tested via the specified ARA
        - Case 3 - non-empty ara_id, empty kp_id == return all the KPs being tested under the specified ARA
        - Case 4 - empty ara_id and kp_id == error ...at least one of 'ara_id' and 'kp_id' needs to be provided.

    \f
    :param test_run_id: test run identifier (as returned by /run_tests endpoint).
    :param edge_num: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.

    :param ara_id: identifier of the ARA resource whose indirect KP test results are being accessed
    :param kp_id: identifier of the KP resource whose test results are specifically being accessed.
        - Case 1 - non-empty kp_id, empty ara_id == just return the summary of the one directly tested KP resource
        - Case 2 - non-empty ara_id, non-empty kp_id == return the one specific KP tested via the specified ARA
        - Case 3 - non-empty ara_id, empty kp_id == return all the KPs being tested under the specified ARA
        - Case 4 - empty ara_id and kp_id == error ...at least one of 'ara_id' and 'kp_id' needs to be provided.

    :return: TestRunEdgeDetails, echoing input parameters alongside the requested 'details', the latter which is a
                                 details JSON document for the specified unit test.
             or HTTP Status Code(400) unsupported parameter configuration.
             or HTTP Status Code(404) if the requested TRAPI response JSON text data file is not (yet?) available.
    """
    # TODO: maybe we can validate the ara_id and kp_id against the /index catalog?
    details: Optional[Dict]
    if ara_id:
        if kp_id:
            # Case 2: return the one specific KP tested via the specified ARA
            details = OneHopTestHarness(test_run_id=test_run_id).get_details(
                component="ARA",
                ara_id=ara_id,
                kp_id=kp_id,
                edge_num=edge_num
            )
        else:
            # Case 3: return all the KPs being tested under the specified ARA
            # TODO: Merged ARA implementation without a specific kp_id, needs a bit more thought.
            return JSONResponse(status_code=400, content={"message": "Null kp_id parameter is not yet supported?"})
    else:  # empty 'ara_id'
        if kp_id:
            # Case 1: just return the summary of the one directly tested KP resource
            details: Optional[Dict] = OneHopTestHarness(test_run_id=test_run_id).get_details(
                component="KP",
                kp_id=kp_id,
                edge_num=edge_num
            )
        else:
            # Case 4: error...at least one of 'ara_id' and 'kp_id' needs to be provided.
            return JSONResponse(status_code=400, content={"message": "At least a 'kp_id' must be specified!"})

    if details is not None:
        return TestRunEdgeDetails(details=details)
    else:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"Edge details, for ara_id '{str(ara_id)}' and kp_id '{str(kp_id)}', " +
                           f"are not (yet) available from test run '{test_run_id}'?"
            }
        )


@app.get(
    "/response",
    tags=['report'],
    summary="Directly stream the TRAPI response JSON message for a " +
            "specified SRI Testing unit test of a given input edge.",
    responses={400: {"model": Message}, 404: {"model": Message}}
)
async def get_response(
        test_run_id: str,
        edge_num: str,
        test_id: str,
        ara_id: Optional[str] = None,
        kp_id: Optional[str] = None
) -> Union[StreamingResponse, JSONResponse]:
    """
    Return full TRAPI response message as a streamed downloadable text file, if available, for a specified unit test
    of an edge, as identified test run defined by the following query path parameters:

    - **test_run_id**: test run being accessed.
    - **edge_num**: target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.
    - **test_id**: target unit test identifier, one of the values noted in the edge leaf nodes of the test run summary.

    - **ara_id**: identifier of the ARA resource whose indirect KP test results are being accessed
    - **kp_id**: identifier of the KP resource whose test results are specifically being accessed.
        - Case 1 - non-empty kp_id, empty ara_id == just return the summary of the one directly tested KP resource
        - Case 2 - non-empty ara_id, non-empty kp_id == return the one specific KP tested via the specified ARA
        - Case 3 - non-empty ara_id, empty kp_id == error... option not provided here ... too much bandwidth!
        - Case 4 - empty ara_id and kp_id == error ...At least a 'kp_id' must be specified!

    \f
    :param test_run_id: str, test run identifier (as returned by /run_tests endpoint)
    :param edge_num: str, target input 'edge_num' edge number, as found in edge leaf nodes of the JSON test run summary.
    :param test_id: str, target unit test identifier, one of the values noted in the
                         edge leaf nodes of the JSON test run summary (e.g. 'by_subject', etc.).

    :param ara_id: identifier of the ARA resource whose indirect KP test results are being accessed
    :param kp_id: identifier of the KP resource whose test results are specifically being accessed.
        - Case 1 - non-empty kp_id, empty ara_id == just return the summary of the one directly tested KP resource
        - Case 2 - non-empty ara_id, non-empty kp_id == return the one specific KP tested via the specified ARA
        - Case 3 - non-empty ara_id, empty kp_id == error... option not provided here ... too much bandwidth!
        - Case 4 - empty ara_id and kp_id == error ...At least a 'kp_id' must be specified!

    :return: StreamingResponse, HTTP status code 200 with downloadable text file of TRAPI response
             or HTTP Status Code(400) unsupported parameter configuration.
             or HTTP Status Code(404) if the requested TRAPI response JSON text data file is not (yet?) available.
    """
    # TODO: maybe we can validate the ara_id and kp_id against the /index catalog?
    try:
        content_generator: Generator
        if ara_id:
            if kp_id:
                # Case 2: return the one specific KP tested via the specified ARA
                content_generator = OneHopTestHarness(test_run_id=test_run_id).get_streamed_response_file(
                    component="ARA",
                    ara_id=ara_id,
                    kp_id=kp_id,
                    edge_num=edge_num,
                    test_id=test_id
                )
            else:
                # Case 3: error... option not provided here ... too much bandwidth!
                return JSONResponse(
                    status_code=400,
                    content={"message": "Null 'kp_id' is not supported with a non-null 'ara_id'!"}
                )
        else:  # empty 'ara_id'
            if kp_id:
                # Case 1: just return the summary of the one directly tested KP resource
                content_generator = OneHopTestHarness(test_run_id=test_run_id).get_streamed_response_file(
                    component="KP",
                    kp_id=kp_id,
                    edge_num=edge_num,
                    test_id=test_id
                )
            else:
                # Case 4: error...at least 'kp_id' needs to be provided.
                return JSONResponse(status_code=400, content={"message": "At least a 'kp_id' must be specified!"})

        return StreamingResponse(
            content=content_generator,
            media_type="application/json"
        )
    except RuntimeError:
        return JSONResponse(
            status_code=404,
            content={
                "message": f"TRAPI Response JSON text file for unit test {test_id} for edge {edge_num} " +
                           f"for ara_id '{str(ara_id)}' and kp_id '{str(kp_id)}', " +
                           f"from test run '{test_run_id}', is not (yet) available?"
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
