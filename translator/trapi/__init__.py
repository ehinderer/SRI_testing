from typing import Optional, Dict, List

from json import dumps

import requests
from jsonschema import ValidationError

from reasoner_validator import validate, DEFAULT_TRAPI_VERSION
from reasoner_validator.util import latest

from reasoner_validator.biolink import check_biolink_model_compliance_of_knowledge_graph
from translator.sri import get_aliases

import logging
logger = logging.getLogger(__name__)

# For testing, set TRAPI API query POST timeouts to 10 minutes == 600 seconds
DEFAULT_TRAPI_POST_TIMEOUT = 600.0

# Maximum number of edges to scrutinize in
# TRAPI response knowledge graph, during edge content tests
MAX_NO_OF_EDGES = 10

# Default is actually specifically 1.2.0 as of March 2022,
# but the reasoner_validator should discern this
_current_trapi_version = None


def _output(json, flat=False):
    return dumps(json, sort_keys=False, indent=None if flat else 4)


def set_trapi_version(version: Optional[str] = None):
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
        # import json
        # print(dumps(response_json, sort_keys=False, indent=4))
        print(e)
        return False


def check_provenance(ara_case, ara_response):
    """
    This is where we will check to see whether the edge
    in the ARA response is marked with the expected KP.
    But at the moment, there is not a standard way to do this.
    """
    error_msg_prefix = generate_test_error_msg_prefix(ara_case, test_name="check_provenance")

    kg = ara_response['knowledge_graph']
    edges: Dict[str, Dict] = kg['edges']

    # Every knowledge graph should always have at least *some* edges
    if not len(edges):
        assert False, f"{error_msg_prefix} knowledge graph has no edges?"

    kp_source_type = f"biolink:{ara_case['kp_source_type']}_knowledge_source"
    kp_source = ara_case['kp_source'] if ara_case['kp_source'] else ""

    number_of_edges_viewed = 0
    for edge in edges.values():

        error_msg_prefix = f"{error_msg_prefix} edge '{_output(edge, flat=True)}' from ARA '{ara_case['ara_api_name']}'"

        # Every edge should always have at least *some* (provenance source) attributes
        if 'attributes' not in edge.keys():
            assert False, f"{error_msg_prefix} has no 'attributes' key?"

        attributes = edge['attributes']
        if not attributes:
            assert False, f"{error_msg_prefix} has no attributes?"

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
                        "biolink:primary_knowledge_source"
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

                    # Checking specifically here whether the ARA infores
                    # attribute value is published as aggregator_knowledge_sources
                    if ara_case['ara_source'] and infores == ara_case['ara_source']:
                        found_ara_knowledge_source = True

                # check for special case of KP provenance tagged this way
                if ara_case['kp_source'] and \
                        attribute_type_id == kp_source_type and \
                        infores == kp_source:
                    found_kp_knowledge_source = True

        if ara_case['ara_source'] and not found_ara_knowledge_source:
            assert False,  f"{error_msg_prefix} missing ARA knowledge source provenance?"

        if ara_case['kp_source'] and not found_kp_knowledge_source:
            assert False, \
                f"{error_msg_prefix} Knowledge Provider '{ara_case['kp_source']}' attribute value as " +\
                f"'{kp_source_type}' is missing as expected knowledge source provenance?"

        # We are not likely to want to check the entire Knowledge Graph for
        # provenance but only sample a subset, making the assumption that
        # defects in provenance will be systemic, thus will show up early
        number_of_edges_viewed += 1
        if number_of_edges_viewed >= MAX_NO_OF_EDGES:
            break


def call_trapi(url: str, opts, trapi_message):
    """
    Given an url and a TRAPI message, post the message
    to the url and return the status and json response.

    :param url:
    :param opts:
    :param trapi_message:
    :return:
    """
    query_url = f'{url}/query'

    # print(f"\ncall_trapi({query_url}):\n\t{dumps(trapi_message, sort_keys=False, indent=4)}", file=stderr, flush=True)

    try:
        response = requests.post(query_url, json=trapi_message, params=opts, timeout=DEFAULT_TRAPI_POST_TIMEOUT)
    except requests.Timeout:
        # fake response object
        response = requests.Response()
        response.status_code = 408
    except requests.RequestException as re:
        # perhaps another unexpected Request failure?
        logger.error(
            f"call_trapi(\n\turl: '{url}',\n\topts: '{_output(opts)}',"
            f"\n\ttrapi_message: '{_output(trapi_message)}') - "
            f"Request POST exception:\n\t\t{str(re)}"
        )
        response = requests.Response()
        response.status_code = 408

    response_json = None
    if response.status_code == 200:
        try:
            response_json = response.json()
        except Exception as exc:
            logger.error(f"call_trapi({query_url}) JSON access error: {str(exc)}")

    return {'status_code': response.status_code, 'response_json': response_json}


def generate_edge_id(resource_id: str, edge_i: int) -> str:
    return f"{resource_id}#{str(edge_i)}"


def generate_test_error_msg_prefix(case: Dict, test_name: str) -> str:
    assert case
    test_msg_prefix: str = "test_onehops.py::test_trapi_"
    resource_id: str = ""
    component: str = "kp"
    if 'ara_api_name' in case and case['ara_api_name']:
        component = "ara"
        resource_id += case['ara_api_name'] + "|"
    test_msg_prefix += f"{component}s["
    resource_id += case['kp_api_name']
    edge_idx = case['idx']
    edge_id = generate_edge_id(resource_id, edge_idx)
    if not test_name:
        test_name = "input"
    test_msg_prefix += f"{edge_id}-{test_name}] FAILED"
    return test_msg_prefix


def execute_trapi_lookup(case, creator, rbag):
    """
    Method to execute a TRAPI lookup, using the 'creator' test template.

    :param case:
    :param creator:
    :param rbag:
    """
    error_msg_prefix = generate_test_error_msg_prefix(case, test_name=creator.__name__)

    # Create TRAPI query/response
    rbag.location = case['location']
    rbag.case = case

    trapi_request, output_element, output_node_binding = creator(case)

    if trapi_request is None:
        # The particular creator cannot make a valid message from this triple
        assert False, f"{error_msg_prefix} message creator could not generate a valid TRAPI query request object?"

    # query use cases pertain to a particular TRAPI version
    trapi_version = get_trapi_version()

    if not is_valid_trapi(trapi_request, trapi_version=trapi_version):
        # This is a problem with the testing framework.
        assert False, f"{error_msg_prefix} for the expected TRAPI version '{trapi_version}', " +\
                      "the query request is not TRAPI compliant?"

    trapi_response = call_trapi(case['url'], case['query_opts'], trapi_request)

    # Successfully invoked the query endpoint
    rbag.request = trapi_request
    rbag.response = trapi_response

    if trapi_response['status_code'] != 200:
        err_msg = f"{error_msg_prefix} TRAPI response has an " \
                  f"unexpected HTTP status code of '{str(trapi_response['status_code'])}'?"
        logger.warning(err_msg)
        assert False, err_msg

    # Validate that we got back valid TRAPI Response
    valid_trapi_response = is_valid_trapi(trapi_response['response_json'], trapi_version=trapi_version)
    if not valid_trapi_response:
        logger.error(f"TRAPI Response: {_output(trapi_response['response_json'])}")
        assert False,  \
            f"{error_msg_prefix} for expected TRAPI version '{trapi_version}', TRAPI response is not TRAPI compliant?"

    response_message = trapi_response['response_json']['message']

    # Verify that the response had some results...
    assert len(response_message['results']) > 0,\
        f"{error_msg_prefix} TRAPI response returned an empty TRAPI Message Result?"

    # ...Then, validate the associated Knowledge Graph...
    assert len(response_message['knowledge_graph']) > 0,\
        f"{error_msg_prefix} returned an empty TRAPI Message Knowledge Graph?"

    # Verify that the TRAPI message output knowledge graph
    # is compliant to the applicable Biolink Model release
    model_version, errors = \
        check_biolink_model_compliance_of_knowledge_graph(
            graph=response_message['knowledge_graph'],
            biolink_version=case['biolink_version']
        )
    assert not errors, \
        f"{error_msg_prefix} TRAPI response is not compliant to " \
        f"Biolink Model release '{model_version}':\n{_output(errors)}\n?"

    # Finally, check that the Results contained the object of the query
    object_ids = [r['node_bindings'][output_node_binding][0]['id'] for r in response_message['results']]
    if case[output_element] not in object_ids:
        # The 'get_aliases' method uses the Translator NodeNormalizer to check if any of
        # the aliases of the case[output_element] identifier are in the object_ids list
        output_aliases = get_aliases(case[output_element])
        if not any([alias == object_id for alias in output_aliases for object_id in object_ids]):
            assert False, f"{error_msg_prefix}: neither the input id '{case[output_element]}' nor resolved aliases " \
                          f"[{','.join(output_aliases)}] were returned in the Result object IDs " \
                          f"{_output(object_ids,flat=True)} for node '{output_node_binding}' binding?"

    return response_message
