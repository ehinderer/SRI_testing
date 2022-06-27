"""
FastAPI web service wrapper for SRI Testing harness
(i.e. for reports to a Translator Runtime Status Dashboard)
"""
from typing import Optional, Dict, List
from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from reasoner_validator.util import latest
from translator.sri.testing.report import (
    OneHopTestHarness,
    DEFAULT_WORKER_TIMEOUT,
    get_edge_details_file_path
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


@app.post("/run_tests")
async def run_tests(test_parameters: TestRunParameters) -> Dict:

    trapi_version: Optional[str] = latest.get(test_parameters.trapi_version) if test_parameters.trapi_version else None
    biolink_version: Optional[str] = test_parameters.biolink_version
    log: Optional[str] = test_parameters.log

    testrun = OneHopTestHarness(test_parameters.timeout)
    testrun.run(
        trapi_version=trapi_version,
        biolink_version=biolink_version,
        log=log
    )

    return {
        "test_run_id": testrun.get_test_run_id(),

        # TODO: user specified TRAPI version...
        #       we should somehow try to report the
        #       actual version used by the system
        # "trapi_version": trapi_version,

        # TODO: user specified Biolink Model version...
        #       we should somehow try to report the
        #       actual version used by the system
        # "biolink_version": biolink_version,
    }


@app.get("/results/{test_run_id}")
async def get_summary(test_run_id: str):
    """
    Returns a summary list of test results for a given session ID.

    :param test_run_id: test_run_id: test run identifier (as returned by /run_tests endpoint).

    :return: Dict, with keys 'test_run_id' and 'summary', the latter being a
                   JSON indexed summary of available unit test results.
    """
    summary: Optional[str] = OneHopTestHarness.get_summary(test_run_id)

    if summary is None:
        summary = f"Test summary for session is not yet available?"

    return {
        "test_run_id": test_run_id,
        "summary": summary
    }


@app.get("/results/{test_run_id}/{component}/{resource_id}/{edge_num}")
async def get_details(test_run_id: str, component: str, resource_id: str, edge_num: str):
    """
    Return details for a specified unit test in a given test session.

    :param test_run_id: test run identifier (as returned by /run_tests endpoint)
    :param component: Translator component being tested: 'ARA' or 'KP'
    :param resource_id: identifier of the resource being tested (may be single KP identifier (i.e. 'Some_KP') or a
                        hyphen-delimited 2-Tuple composed of an ARA and an associated KP identifier
                        (i.e. 'Some_ARA-Some_KP') as found in the JSON hierarchy of the test run summary.
    :param edge_num: Identifier of the unit test of interest, for retrieval of details, path like

    :return: Dict, with keys 'test_run_id', 'unit_test_id' and 'details', the latter which are the
                   details relating to the specified unit test, encoded as a JSON data structure.
    """
    assert test_run_id, "Null or empty Session Identifier?"
    assert component, "Null or empty Translator Component?"
    assert resource_id, "Null or empty Resource Identifier?"
    assert edge_num, "Null or empty Edge Number?"

    rid_part: List[str] = resource_id.split("-")
    if len(rid_part) > 1:
        ara_id = rid_part[0]
        kp_id = rid_part[1]
    else:
        ara_id = None
        kp_id = rid_part[0]

    edge_details_file_path: str = get_edge_details_file_path(component, ara_id, kp_id, edge_num)

    details: Optional[str] = OneHopTestHarness.get_details(test_run_id, edge_details_file_path)
    if details is None:
        details = f"Test details for edge are not (yet) available?"

    return {
        "test_run_id": test_run_id,
        "component": component,
        "resource_id": resource_id,
        "edge_num": edge_num,
        "details": details
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
