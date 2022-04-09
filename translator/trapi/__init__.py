from typing import Optional
from json import dumps

import logging

import requests
from jsonschema import ValidationError

from reasoner_validator import validate
from requests import Timeout, Response

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

# TODO: We'd rather NOT hard code a default TRAPI here,
#       but do it for now pending clarity on how to guide
#       the choice of TRAPI from a Translator SmartAPI entry
# Default is actually specifically 1.2.0 as of March 2022,
# but the ReasonerAPI should discern this
DEFAULT_TRAPI_VERSION = "1"

_default_trapi_version = None

# For testing, set TRAPI API query POST timeouts to 10 minutes == 600 seconds
DEFAULT_TRAPI_POST_TIMEOUT = 600.0


def set_trapi_version(version: str):
    global _default_trapi_version
    _default_trapi_version = version if version else DEFAULT_TRAPI_VERSION
    logger.debug(f"TRAPI Version set to {_default_trapi_version}")


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

    try:
        response = requests.post(query_url, json=trapi_message, params=opts, timeout=DEFAULT_TRAPI_POST_TIMEOUT)
    except Timeout:
        # fake response object
        response = Response()
        response.status_code = 408

    response_json = None
    if response.status_code == 200:
        try:
            response_json = response.json()
        except Exception as exc:
            logger.error(f"call_trapi({query_url}) JSON access error: {str(exc)}")

    return {'status_code': response.status_code, 'response_json': response_json}


def _output(json):
    return dumps(json, sort_keys=False, indent=4)


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
                      f"\t{_output(case)}\n" + \
                      f"could not generate a valid TRAPI query request object?"

    # query use cases pertain to a particular TRAPI version
    trapi_version = get_trapi_version()

    if not is_valid_trapi(trapi_request, trapi_version=trapi_version):
        # This is a problem with the testing framework.
        assert False, f"execute_trapi_lookup({case['url']}): Invalid TRAPI '{trapi_version}' " + \
                      f"query request {_output(trapi_request)}"

    trapi_response = call_trapi(case['url'], case['query_opts'], trapi_request)

    # Successfully invoked the query endpoint
    rbag.request = trapi_request
    rbag.response = trapi_response

    if trapi_response['status_code'] != 200:
        err_msg = f"execute_trapi_lookup({case['url']}): " + \
                  f"TRAPI request:\n\t{_output(trapi_request)}\n " + \
                  f"returned status code: {str(trapi_response['status_code'])} " + \
                  f"and response:\n\t '{_output(trapi_response['response_json'])}'"
        logger.warning(err_msg)
        assert False, err_msg

    # Validate that we got back valid TRAPI Response
    assert is_valid_trapi(trapi_response['response_json'], trapi_version=trapi_version), \
           f"execute_trapi_lookup({case['url']}): " + \
           f"TRAPI request:\n\t{_output(trapi_request)}\n " + \
           f"had an invalid TRAPI '{trapi_version}' response:\n\t" + \
           f"{_output(trapi_response['response_json'])}"

    response_message = trapi_response['response_json']['message']

    # Verify that the response had some results
    assert len(response_message['results']) > 0, \
           f"execute_trapi_lookup({case['url']}): empty TRAPI Result from TRAPI request:\n\t" + \
           f"{_output(trapi_request)}"

    # The results contained the object of the query
    object_ids = [r['node_bindings'][output_node_binding][0]['id'] for r in response_message['results']]
    assert case[output_element] in object_ids, \
           f"execute_trapi_lookup({case['url']}): TRAPI request:\n\t{_output(trapi_request)}\n " + \
           f"had missing or invalid TRAPI Result object ID bindings in response method results:\n\t" \
           f"{_output(response_message)}"

    return response_message
