"""
One Hops Testing Suite
"""
import pytest
import requests
from jsonschema.exceptions import ValidationError
from reasoner_validator import validate

from tests.onehop.util import (
    get_toolkit,
    get_trapi_version,
    by_subject,
    by_object,
    raise_subject_entity,
    raise_object_by_subject,
    raise_predicate_by_subject
)

import logging

from tests.onehop.util import create_one_hop_message

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def inverse_by_new_subject(request):
    """Given a known triple, create a TRAPI message that inverts the predicate, then looks up the new
    object by the new subject (original object)"""
    original_predicate_element = get_toolkit().get_element(request['predicate'])
    if original_predicate_element['symmetric']:
        transformed_predicate = request['predicate']
    else:
        transformed_predicate_name = original_predicate_element['inverse']
        if transformed_predicate_name is None:
            transformed_predicate = None
        else:
            tp = get_toolkit().get_element(transformed_predicate_name)
            transformed_predicate = tp.slot_uri
    # Not everything has an inverse (it should, and it will, but it doesn't right now)
    if transformed_predicate is None:
        return None, None, None
    transformed_request = {
        "url": "https://automat.renci.org/human-goa",
        "subject_category": request['object_category'],
        "object_category": request['subject_category'],
        "predicate": transformed_predicate,
        "subject": request['object'],
        "object": request['subject']
    }
    message = create_one_hop_message(transformed_request, look_up_subject=False)
    # We inverted the predicate, and will be querying by the new subject, so the output will be in node b
    # but, the entity we are looking for (now the object) was originally the subject because of the inversion.
    return message, 'subject', 'b'


##############################
# End TRAPI creating functions
##############################


def call_trapi(url, opts, trapi_message):
    """Given an url and a TRAPI message, post the message to the url and return the status and json response"""
    query_url = f'{url}/query'
    print(query_url)
    response = requests.post(query_url, json=trapi_message, params=opts)
    try:
        response_json = response.json()
    except RuntimeError:
        response_json = None
    return {'status_code': response.status_code, 'response_json': response_json}


def is_valid_trapi(instance, component="Query"):
    """Make sure that the Message is valid using reasoner_validator"""
    try:
        validate(
            instance=instance,
            component=component,
            trapi_version=get_trapi_version()
        )
        return True
    except ValidationError as e:
        import json
        # print(json.dumps(response_json,indent=4))
        print(e)
        return False


def check_provenance(ara_case, ara_response):
    """
    This is where we will check to see whether the edge
    in the ARA response is marked with the expected KP.
    But at the moment, there is not a standard way to do this.
    """
    logger.warning(
        f"check_provenance() not yet implemented to assess ara_response '{ara_response}' for the ara_case '{ara_case}'"
    )
    pass


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
        return None
    
    # is_valid_trapi(instance=trapi_response_json, component="Query", trapi_version=tests.DEFAULT_TRAPI_VERSION)
    if not is_valid_trapi(trapi_request):
        # This is a problem with the testing framework.
        exit()

    trapi_response = call_trapi(case['url'], case['query_opts'], trapi_request)
    # Successfully invoked the query endpoint
    rbag.request = trapi_request
    rbag.response = trapi_response
    assert trapi_response['status_code'] == 200
    
    # Validate that we got back valid TRAPI Response
    # is_valid_trapi(instance=trapi_response_json, component="Query", trapi_version=tests.DEFAULT_TRAPI_VERSION)
    assert is_valid_trapi(trapi_response['response_json'])
    
    response_message = trapi_response['response_json']['message']

    # Verify that the response had some results
    assert len(response_message['results']) > 0
    
    # The results contained the object of the query
    object_ids = [r['node_bindings'][output_node_binding][0]['id'] for r in response_message['results']]
    assert case[output_element] in object_ids
    
    return response_message


@pytest.mark.parametrize(
    "trapi_creator",
    [by_subject, by_object, raise_subject_entity, raise_object_by_subject, raise_predicate_by_subject]
)
def test_trapi_kps(kp_trapi_case, trapi_creator, results_bag):
    """Generic Test for TRAPI KPs. The kp_trapi_case fixture is created in conftest.py by looking at the test_triples
    These get successively fed to test_TRAPI.  This function is further parameterized by trapi_creator, which knows
    how to take an input edge and create some kind of TRAPI query from it.  For instance, by_subject removes the object,
    while raise_object_by_subject removes the object and replaces the object category with its biolink parent.
    This approach will need modification if there turn out to be particular elements we want to test for different
    creators.
    """
    execute_trapi_lookup(kp_trapi_case, trapi_creator, results_bag)


@pytest.mark.parametrize(
    "trapi_creator",
    [by_subject, by_object, raise_subject_entity, raise_object_by_subject, raise_predicate_by_subject]
)
def test_trapi_aras(ara_trapi_case, trapi_creator, results_bag):
    """Generic Test for ARA TRAPI.  It does the same thing as the KP trapi, calling an ARA that should be pulling
    data from the KP.
    Then it performs a check on the result to make sure that the source is correct.
    Currently, that provenance check is a short circuit since ARAs are not reporting this in a standard way yet.
    """
    response_message = execute_trapi_lookup(ara_trapi_case, trapi_creator, results_bag)
    if response_message is not None:
        check_provenance(ara_trapi_case, response_message)
