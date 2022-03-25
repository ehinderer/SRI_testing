from json import dumps
from typing import Optional

import logging

import requests
from jsonschema import ValidationError

from reasoner_validator import validate

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

_default_trapi_version = None

# TODO: We'd rather NOT hard code a default TRAPI here, but do it for now pending clarity on how to guide
#       the choice of TRAPI elsewhere, be it either in the input test data (from KP's and ARA's)
#       or perhaps, as detected as the 'latest' TRAPI version seen within the ReasonerAPI Validator module
DEFAULT_TRAPI_VERSION = "1"  # actually specifically 1.2.0 as of March 2022, but the ReasonerAPI should discern this


def set_trapi_version(version: str):
    global _default_trapi_version
    _default_trapi_version = version if version else DEFAULT_TRAPI_VERSION


def get_trapi_version() -> Optional[str]:
    global _default_trapi_version
    return _default_trapi_version


def is_valid_trapi(instance, trapi_version):
    """Make sure that the Message is valid using reasoner_validator"""
    try:
        validate(
            instance=instance,
            component="Query",
            trapi_version=trapi_version
        )
        return True
    except ValidationError as e:
        import json
        # print(dumps(response_json, sort_keys=False, indent=4))
        print(e)
        return False


def check_provenance(ara_case, ara_response):
    """
    This is where we will check to see whether the edge
    in the ARA response is marked with the expected KP.
    But at the moment, there is not a standard way to do this.
    """
    logger.warning(
        f"check_provenance() not yet implemented to assess ara_response '{ara_response}' for the test case '{ara_case}'"
    )
    pass


def call_trapi(url, opts, trapi_message):
    """Given an url and a TRAPI message, post the message to the url and return the status and json response"""

    query_url = f'{url}/query'

    # print(f"\ncall_trapi({query_url}):\n\t{dumps(trapi_message, sort_keys=False, indent=4)}", file=stderr, flush=True)

    response = requests.post(query_url, json=trapi_message, params=opts)
    try:
        response_json = response.json()
    except RuntimeError:
        response_json = None
    return {'status_code': response.status_code, 'response_json': response_json}


def execute_trapi_lookup(case, creator, rbag):
    """

    :param case:
    :param creator:
    :param rbag:
    """
    # Create TRAPI query/response
    rbag.location = case['location']
    rbag.case = case
    trapi_request, output_element, output_node_binding = creator(case)
    if trapi_request is None:
        # The particular creator cannot make a valid message from this triple
        assert False, f"\nCreator method '{creator.__name__}' for test case \n" + \
                      f"\t'{dumps(case, sort_keys=False, indent=4)}'\n" + \
                      f"could not generate a valid TRAPI query request object?"

    # query use cases pertain to a particular TRAPI version
    trapi_version = case['trapi_version']

    if not is_valid_trapi(trapi_request, trapi_version=trapi_version):
        # This is a problem with the testing framework.
        assert False, f"execute_trapi_lookup({case['url']}): Invalid TRAPI '{trapi_version}' " + \
                      f"query request {dumps(trapi_request, sort_keys=False, indent=4)}"

    trapi_response = call_trapi(case['url'], case['query_opts'], trapi_request)

    # Successfully invoked the query endpoint
    rbag.request = trapi_request
    rbag.response = trapi_response

    if trapi_response['status_code'] != 200:
        err_msg = f"execute_trapi_lookup({case['url']}): " + \
                  f"TRAPI call returned status code: {str(trapi_response['status_code'])} " + \
                  f"and response:\n\t '{dumps(trapi_response['response_json'], sort_keys=False, indent=4)}'"
        logger.warning(err_msg)
        assert False, err_msg

    # Validate that we got back valid TRAPI Response
    # TODO: add an error message
    assert is_valid_trapi(trapi_response['response_json'], trapi_version=trapi_version), \
           f"execute_trapi_lookup({case['url']}): invalid TRAPI '{trapi_version}' response:\n\t" \
           f"{dumps(trapi_response['response_json'], sort_keys=False, indent=4)}"

    response_message = trapi_response['response_json']['message']

    # Verify that the response had some results
    assert len(response_message['results']) > 0, \
           f"execute_trapi_lookup({case['url']}): empty TRAPI Result?"

    # The results contained the object of the query
    object_ids = [r['node_bindings'][output_node_binding][0]['id'] for r in response_message['results']]
    # TODO: add an error message
    assert case[output_element] in object_ids, \
           f"execute_trapi_lookup({case['url']}): missing or invalid TRAPI Result object ID bindings?"

    return response_message
