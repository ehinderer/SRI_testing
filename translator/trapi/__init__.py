from typing import Optional, Dict, List, Tuple

from json import dumps

import requests
from jsonschema import ValidationError

from reasoner_validator import validate, DEFAULT_TRAPI_VERSION
from reasoner_validator.util import latest

from reasoner_validator.biolink import check_biolink_model_compliance_of_knowledge_graph
from translator.sri import get_aliases

import pytest

import logging
logger = logging.getLogger(__name__)

# For testing, set TRAPI API query POST timeouts to 10 minutes == 600 seconds
DEFAULT_TRAPI_POST_TIMEOUT = 600.0

# Maximum number of edges to scrutinize in
# TRAPI response knowledge graph, during edge content tests
TEST_DATA_SAMPLE_SIZE = 10

# Default is actually specifically 1.2.0 as of March 2022,
# but the reasoner_validator should discern this
# TODO: this global variable is not thread safe across multiple tests
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


def get_latest_trapi_version() -> str:
    return latest.get(DEFAULT_TRAPI_VERSION)


def is_valid_trapi(instance, trapi_version: str, component: str = "Query") -> Tuple[bool, str]:
    """
    Make sure that the Message is valid using reasoner_validator.

    :param instance: Dict, data instance
    :param trapi_version: str, SemVer of target TRAPI version
    :param component: str, name of TRAPI Message schemata (sub)component to be validated

    :return: Tuple[bool,str], validation status (True / False) and (optional) validation message if 'False' status
    """
    try:
        validate(
            instance=instance,
            component=component,
            trapi_version=trapi_version
        )
        return True, ""
    except ValidationError as e:
        # import json
        # print(dumps(response_json, sort_keys=False, indent=4))
        print(e)
        return False, str(e)


class TestReport:

    def __init__(self, errors: List[str]):
        self.errors = errors

    def test(self, is_true: bool, message: str, data_dump: Optional[str] = None):
        """
        Error test report.

        :param is_true: test predicate, triggering error message report if False
        :param message: error message reported when 'is_true' is False
        :param data_dump: optional extra information about a test failure (e.g. details about the object that failed)
        :raises: AssertionError when 'is_true' flag has value False
        """
        if not is_true:
            logger.error(message)
            if data_dump:
                logger.debug(data_dump)
            self.errors.append(message)

    def skip(self, message: str):
        """
        Skip report wrapper.
        :param message: str, message explaining why the test is skipped
        :raises: AssertionError when 'is_true' flag has value False
        """
        self.errors.append(message)
        pytest.skip(message)

    def assert_errors(self):
        """
        Error failure report wrapper.
        :return:
        """
        if self.errors:
            pytest.fail(_output(self.errors))


def generate_test_error_msg_prefix(case: Dict, test_name: str) -> str:
    assert case
    test_msg_prefix: str = "test_onehops.py::test_trapi_"
    resource_id: str = ""
    component: str = "kp"
    if 'ara_source' in case and case['ara_source']:
        component = "ara"
        ara_id = case['ara_source'].replace("infores:", "")
        resource_id += ara_id + "|"
    test_msg_prefix += f"{component}s["
    if 'kp_source' in case and case['kp_source']:
        kp_id = case['kp_source'].replace("infores:", "")
        resource_id += kp_id
    edge_idx = case['idx']
    edge_id = generate_edge_id(resource_id, edge_idx)
    if not test_name:
        test_name = "input"
    test_msg_prefix += f"{edge_id}-{test_name}] FAILED"
    return test_msg_prefix


def check_provenance(ara_case, ara_response, test_report: TestReport):
    """
    Check to see whether the edge in the ARA response is marked with the expected KP.

    :param ara_case: ARA associated input data test case
    :param ara_response: TRAPI Response whose provenance is to be validated.
    :param test_report: ErrorReport, class wrapper object for asserting and reporting errors
    """
    error_msg_prefix = generate_test_error_msg_prefix(ara_case, test_name="check_provenance")

    kg = ara_response['knowledge_graph']
    edges: Dict[str, Dict] = kg['edges']

    # Every knowledge graph should always have at least *some* edges
    test_report.test(len(edges) > 0, f"{error_msg_prefix} knowledge graph has no edges?")

    kp_source_type = f"biolink:{ara_case['kp_source_type']}_knowledge_source"
    kp_source = ara_case['kp_source'] if ara_case['kp_source'] else ""

    number_of_edges_viewed = 0
    for edge in edges.values():

        error_msg_prefix = f"{error_msg_prefix} edge '{_output(edge, flat=True)}' from ARA '{ara_case['ara_api_name']}'"

        # Every edge should always have at least *some* (provenance source) attributes
        test_report.test('attributes' in edge.keys(), f"{error_msg_prefix} has no 'attributes' key?")

        attributes = edge['attributes']

        test_report.test(attributes, f"{error_msg_prefix} has no attributes?")

        # Expecting ARA and KP 'aggregator_knowledge_source' attributes?
        found_ara_knowledge_source = False
        found_kp_knowledge_source = False
        found_primary_or_original_knowledge_source = False

        for entry in attributes:

            attribute_type_id = entry['attribute_type_id']

            # Only examine provenance related attributes
            if attribute_type_id not in \
                    [
                        "biolink:aggregator_knowledge_source",
                        "biolink:primary_knowledge_source",
                        "biolink:original_knowledge_source"  # TODO: 'original' KS will be deprecated from Biolink 2.4.5
                    ]:
                continue

            if attribute_type_id in \
                    [
                        "biolink:primary_knowledge_source",
                        "biolink:original_knowledge_source"  # TODO: 'original' KS will be deprecated from Biolink 2.4.5
                    ]:
                found_primary_or_original_knowledge_source = True

            # TODO: there seems to be non-uniformity in provenance attribute values for some KP/ARA's
            #       in which a value is returned as a Python list (of at least one element?) instead of a string.
            #       Here, to ensure full coverage of the attribute values returned,
            #       we'll coerce scalar values into a list, then iterate.
            #
            value = entry['value']

            if isinstance(value, List):
                test_report.test(len(value) > 0, f"{error_msg_prefix} value is an empty list?")

            else:
                test_report.test(
                    isinstance(value, str),
                    f"{error_msg_prefix} value has an unrecognized data type for a provenance attribute?"
                )
                value = [value]

            for infores in value:

                test_report.test(
                    infores.startswith("infores:"),
                    f"{error_msg_prefix} provenance value '{infores}' is not a well-formed InfoRes CURIE?"
                )

                if attribute_type_id == "biolink:aggregator_knowledge_source":

                    # Checking specifically here whether the ARA infores
                    # attribute value is published as an aggregator_knowledge_source
                    if infores == ara_case['ara_source']:
                        found_ara_knowledge_source = True

                # check for special case of KP provenance tagged this way
                if attribute_type_id == kp_source_type and \
                        infores == kp_source:
                    found_kp_knowledge_source = True

        test_report.test(found_ara_knowledge_source, f"{error_msg_prefix} missing ARA knowledge source provenance?")

        test_report.test(
            found_kp_knowledge_source,
            f"{error_msg_prefix} Knowledge Provider '{ara_case['kp_source']}' attribute value as " +
            f"'{kp_source_type}' is missing as expected knowledge source provenance?"
        )

        test_report.test(
            found_primary_or_original_knowledge_source,
            f"{error_msg_prefix} has neither 'primary' nor 'original' knowledge source?"
        )

        # We are not likely to want to check the entire Knowledge Graph for
        # provenance but only sample a subset, making the assumption that
        # defects in provenance will be systemic, thus will show up early
        number_of_edges_viewed += 1
        if number_of_edges_viewed >= TEST_DATA_SAMPLE_SIZE:
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
        logger.error(
            f"call_trapi(\n\turl: '{url}',\n\topts: '{_output(opts)}',"
            f"\n\ttrapi_message: '{_output(trapi_message)}') - "
            f"Request POST TimeOut?"
        )
        response = requests.Response()
        response.status_code = 408
    except requests.RequestException as re:
        # perhaps another unexpected Request failure?
        logger.error(
            f"call_trapi(\n\turl: '{url}',\n\topts: '{_output(opts)}',"
            f"\n\ttrapi_message: '{_output(trapi_message)}') - "
            f"Request POST exception: {str(re)}"
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


def sample_results(results: List) -> List:
    sample_size = min(TEST_DATA_SAMPLE_SIZE, len(results))
    result_subsample = results[0:sample_size]
    return result_subsample


def sample_graph(graph: Dict) -> Dict:
    kg_sample: Dict = {
        "nodes": dict(),
        "edges": dict()
    }
    sample_size = min(TEST_DATA_SAMPLE_SIZE, len(graph["edges"]))
    n = 0
    for key, edge in graph['edges'].items():
        kg_sample['edges'][key] = edge
        if 'subject' in edge and edge['subject'] in graph['nodes']:
            kg_sample['nodes'][edge['subject']] = graph['nodes'][edge['subject']]
        if 'object' in edge and edge['object'] in graph['nodes']:
            kg_sample['nodes'][edge['object']] = graph['nodes'][edge['object']]
        n += 1
        if n > sample_size:
            break

    return kg_sample


def execute_trapi_lookup(case, creator, rbag, test_report: TestReport):
    """
    Method to execute a TRAPI lookup, using the 'creator' test template.

    :param case: input data test case
    :param creator: unit test-specific query message creator
    :param rbag: dictionary of results
    :param test_report: ErrorReport, class wrapper object for asserting and reporting errors

    """
    error_msg_prefix = generate_test_error_msg_prefix(case, test_name=creator.__name__)

    trapi_request, output_element, output_node_binding = creator(case)
    is_valid: bool = trapi_request is not None
    test_report.test(
        is_valid,
        f"{error_msg_prefix} message creator could not generate a valid TRAPI query request object?"
    )
    if not is_valid:
        return None

    # query use cases pertain to a particular TRAPI version
    trapi_version = case['trapi_version']  # get_trapi_version() - we now record TRAPI version within the 'case'

    is_valid, error = is_valid_trapi(trapi_request, trapi_version=trapi_version)
    test_report.test(
        is_valid,
        f"{error_msg_prefix} the input Query request is not compliant " +
        f"to TRAPI version '{trapi_version}'?",
        data_dump=f"TRAPI Request: {trapi_request},\nError: {error}"
    )
    if not is_valid:
        return None

    trapi_response = call_trapi(case['url'], case['query_opts'], trapi_request)

    # Successfully invoked the query endpoint
    rbag.request = trapi_request
    rbag.response = trapi_response

    is_valid = trapi_response['status_code'] == 200
    test_report.test(
        is_valid,
        f"{error_msg_prefix} TRAPI response has an unexpected HTTP status code: '{str(trapi_response['status_code'])}'?"
    )
    if not is_valid:
        return None

    response_message = trapi_response['response_json']['message']

    # Generally validate to top level structure of the Knowledge Graph...
    kg = response_message['knowledge_graph']
    is_valid = len(kg) > 0 and "nodes" in kg and len(kg["nodes"]) > 0 and "edges" in kg and len(kg["edges"]) > 0
    test_report.test(
        is_valid,
        f"{error_msg_prefix} returned an empty TRAPI Message Knowledge Graph?"
    )
    if not is_valid:
        return None

    # ...then if not empty, validate a sample subgraph of the associated Knowledge Graph...
    kg_sample = sample_graph(response_message['knowledge_graph'])
    is_valid, error = is_valid_trapi(
        instance=kg_sample,
        trapi_version=trapi_version,
        component="KnowledgeGraph"
    )
    test_report.test(
        is_valid,
        f"{error_msg_prefix} TRAPI response Knowledge Graph sample " +
        f"is not compliant to TRAPI '{trapi_version}'?",
        data_dump=f"Sample subgraph: {_output(kg_sample)}\nErrors: {error}"
    )
    if not is_valid:
        return None

    # Verify that the sample of the sample knowledge graph is
    # compliant to the currently applicable Biolink Model release
    model_version, errors = \
        check_biolink_model_compliance_of_knowledge_graph(
            graph=kg_sample,
            biolink_version=case['biolink_version']
        )
    test_report.test(
        not errors,
        f"{error_msg_prefix} TRAPI response Knowledge Graph sample is not compliant to " +
        f"Biolink Model release '{model_version}': {_output(errors, flat=True)}?",
        data_dump=_output(kg_sample)
    )

    # ...Verify that the response had some results...
    is_valid = len(response_message['results']) > 0
    test_report.test(
        is_valid,
        f"{error_msg_prefix} TRAPI response returned an empty TRAPI Message Result?"
    )

    if not is_valid:
        return None

    # Validate a subsample of the Message.Result data returned
    results_sample = sample_results(response_message['results'])
    is_valid, error = is_valid_trapi(results_sample, trapi_version=trapi_version, component="Result")
    test_report.test(
        is_valid,
        f"{error_msg_prefix} TRAPI response Results " +
        f"are not compliant to TRAPI '{trapi_version}'?",
        data_dump=f"Sample Results: {_output(results_sample)}\nError: {error}"
    )

    if not is_valid:
        return None

    # TODO: here, we might wish to compare the Results against the content of the KnowledgeGraph,
    #       but this is tricky to do solely with the subsamples, which may not completely overlap.

    # ...Finally, check that the sample Results contained the object of the query
    object_ids = [r['node_bindings'][output_node_binding][0]['id'] for r in results_sample]
    if case[output_element] not in object_ids:
        # The 'get_aliases' method uses the Translator NodeNormalizer to check if any of
        # the aliases of the case[output_element] identifier are in the object_ids list
        output_aliases = get_aliases(case[output_element])
        test_report.test(
            any([alias == object_id for alias in output_aliases for object_id in object_ids]),
            f"{error_msg_prefix}: neither the input id '{case[output_element]}' nor resolved aliases " +
            f"were returned in the Result object IDs for node '{output_node_binding}' binding?",
            data_dump=f"Resolved aliases:\n{','.join(output_aliases)}\n" +
                      f"Result object IDs:\n{_output(object_ids,flat=True)}"
        )

    return response_message
