from typing import Optional, Dict, List
from json import dumps

import logging
from pprint import PrettyPrinter

import requests
from jsonschema import ValidationError

from reasoner_validator import validate
from reasoner_validator.util import latest
from requests import Timeout, Response

from translator.biolink import check_biolink_model_compliance_of_knowledge_graph

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

pp = PrettyPrinter(indent=4)

# For testing, set TRAPI API query POST timeouts to 10 minutes == 600 seconds
DEFAULT_TRAPI_POST_TIMEOUT = 600.0

# Maximum number of edges to scrutinize in
# TRAPI response knowledge graph, during edge content tests
MAX_NO_OF_EDGES = 10

# TODO: We'd rather NOT hard code a default TRAPI here,
#       but do it for now pending clarity on how to guide
#       the choice of TRAPI from a Translator SmartAPI entry
# Default is actually specifically 1.2.0 as of March 2022,
# but the ReasonerAPI should discern this
DEFAULT_TRAPI_VERSION = "1"
_current_trapi_version = None


def set_trapi_version(version: str):
    global _current_trapi_version
    version = version if version else DEFAULT_TRAPI_VERSION
    _current_trapi_version = latest.get(version)
    logger.debug(f"TRAPI Version set to {_current_trapi_version}")


def get_trapi_version() -> Optional[str]:
    global _current_trapi_version
    return _current_trapi_version


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
    kg = ara_response['knowledge_graph']
    edges: Dict[str, Dict] = kg['edges']

    # Every knowledge graph should always have at least *some* edges
    if not len(edges):
        assert False, f"Knowledge graph has no edges?"

    kp_source_type = f"biolink:{ara_case['kp_source_type']}_knowledge_source"
    kp_infores = f"infores:{ara_case['kp_infores']}" if ara_case['kp_infores'] else ""

    number_of_edges_viewed = 0
    for edge in edges.values():

        error_msg_prefix = f"Edge:\n{pp.pformat(edge)}\nfrom ARA 'infores:{ara_case['ara_infores']}' "

        # Every edge should always have at least *some* (provenance source) attributes
        if 'attributes' not in edge.keys():
            assert False, f"Edge '{pp.pformat(edge)}' has no 'attributes' key?"

        attributes = edge['attributes']
        if not attributes:
            assert False, f"Edge '{pp.pformat(edge)}' has no attributes?"

        # Expecting ARA and KP 'aggregator_knowledge_source' attributes?
        found_ara_knowledge_source = False
        found_kp_knowledge_source = False

        # TODO: is it acceptable to only have a 'knowledge_source' here?
        found_primary_or_original_knowledge_source = False

        for entry in attributes:

            attribute_type_id = entry['attribute_type_id']

            # Only examine provenance related attributes
            if attribute_type_id not in \
                    [
                        "biolink:aggregator_knowledge_source",
                        "biolink:primary_knowledge_source",
                        "biolink:original_knowledge_source"
                    ]:
                continue

            # TODO: there seems to be non-uniformity in provenance attribute values for some KP/ARA's
            #       in which a value is returned as a Python list (of at least one element?) instead of a string.
            #       Here, to ensure full coverage of the attribute values returned,
            #       we'll coerce scalar values into a list, then iterate.
            #
            value = entry['value']

            if isinstance(value, List):
                if not value:
                    assert False, f"{error_msg_prefix} value is an empty list?"

            elif isinstance(value, str):
                value = [value]
            else:
                assert False, f"{error_msg_prefix} value has an unrecognized data type for a provenance attribute?"

            for infores in value:

                if not infores.startswith("infores:"):
                    assert False, \
                        f"{error_msg_prefix} provenance value '{infores}' is not a well-formed InfoRes CURIE?"

                if attribute_type_id == "biolink:aggregator_knowledge_source":

                    # Checking specifically here whether both KP and ARA infores
                    # attribute values are published as aggregator_knowledge_sources
                    if ara_case['ara_infores'] and infores == f"infores:{ara_case['ara_infores']}":
                        found_ara_knowledge_source = True

                    # check for special case of a KP provenance
                    if ara_case['kp_infores'] and \
                            attribute_type_id == kp_source_type and \
                            infores == kp_infores:
                        found_kp_knowledge_source = True
                else:
                    # attribute_type_id is either a
                    # "biolink:primary_knowledge_source" or
                    # a "biolink:original_knowledge_source"

                    # TODO: not totally sure how mandatory having either a
                    #       'primary' or 'original' provenance is for TRAPI?
                    found_primary_or_original_knowledge_source = True

                    # check for special case of a KP provenance tagged this way
                    if ara_case['kp_infores'] and \
                            attribute_type_id == kp_source_type and \
                            infores == kp_infores:
                        found_kp_knowledge_source = True

        if ara_case['ara_infores'] and not found_ara_knowledge_source:
            assert False,  f"{error_msg_prefix} missing ARA knowledge source provenance?"

        if ara_case['kp_infores'] and not found_kp_knowledge_source:
            assert False, \
                f"{error_msg_prefix}, KP 'infores:{ara_case['kp_infores']}' attribute value as " +\
                f"'{kp_source_type}' is missing as expected knowledge source provenance?"

        if not found_primary_or_original_knowledge_source:
            assert False, f"{error_msg_prefix} has neither 'primary' nor 'original' KP knowledge source provenance?"

        # We are not likely to want to check the entire Knowledge Graph for
        # provenance but only sample a subset, making the assumption that
        # defects in provenance will be systemic, thus will show up early
        number_of_edges_viewed += 1
        if number_of_edges_viewed >= MAX_NO_OF_EDGES:
            break


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
    Method to execute a TRAPI lookup, using the 'creator' test template.

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
        assert False, f"\nexecute_trapi_lookup(): creator method '{creator.__name__}' " +\
                      f"for test case \n\t{_output(case)}\ncould not generate a valid TRAPI query request object?"

    err_msg_prefix = f"execute_trapi_lookup(test '{creator.__name__}' to endpoint {case['url']}): " +\
                     f"TRAPI query request\n{_output(trapi_request)}\n error: "

    # query use cases pertain to a particular TRAPI version
    trapi_version = get_trapi_version()

    if not is_valid_trapi(trapi_request, trapi_version=trapi_version):
        # This is a problem with the testing framework.
        assert False, f"{err_msg_prefix}: for expected TRAPI version '{trapi_version}', " +\
                      "the query request is not TRAPI compliant?"

    trapi_response = call_trapi(case['url'], case['query_opts'], trapi_request)

    # Successfully invoked the query endpoint
    rbag.request = trapi_request
    rbag.response = trapi_response

    if trapi_response['status_code'] != 200:
        err_msg = f"{err_msg_prefix} response:\n\t '{_output(trapi_response['response_json'])}'\n" +\
                  f"has '{str(trapi_response['status_code'])}' " +\
                  "as an unexpected HTTP status code?"
        logger.warning(err_msg)
        assert False, err_msg

    # Validate that we got back valid TRAPI Response
    assert is_valid_trapi(trapi_response['response_json'], trapi_version=trapi_version), \
           f"{err_msg_prefix} for expected TRAPI version '{trapi_version}', " +\
           f"TRAPI response:\n{_output(trapi_response['response_json'])}\n" +\
           "is not TRAPI compliant?"

    response_message = trapi_response['response_json']['message']

    assert len(response_message['knowledge_graph']) > 0, \
        f"{err_msg_prefix} returned an empty TRAPI Message Knowledge Graph?"

    # Verify that the TRAPI message output knowledge graph
    # is compliant to the applicable Biolink Model release
    model_version, errors = \
        check_biolink_model_compliance_of_knowledge_graph(response_message['knowledge_graph'])
    assert not errors, \
        f"{err_msg_prefix} TRAPI response:\n{_output(response_message)}\n" +\
        f"against Biolink Model version '{model_version}', given\n{_output(errors)}\n" +\
        f"the response is not Biolink Model compliant?"

    # Verify that the response had some results
    assert len(response_message['results']) > 0, \
        f"{err_msg_prefix} TRAPI response:\n{_output(response_message)}\nreturned an empty TRAPI Message Result?"

    # The results contained the object of the query
    object_ids = [r['node_bindings'][output_node_binding][0]['id'] for r in response_message['results']]
    assert case[output_element] in object_ids, \
           f"{err_msg_prefix} TRAPI response:\n{_output(response_message)}\n" +\
           "has missing or invalid TRAPI Result object ID bindings?"

    return response_message
