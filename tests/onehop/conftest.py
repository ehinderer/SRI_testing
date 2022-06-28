"""
Configure one hop tests
"""
from typing import Optional, Union, List, Set, Dict, Any
from sys import stdout, stderr
from os import path, walk, makedirs
from collections import defaultdict
from datetime import datetime

from uuid import uuid4

import json

import logging

from pytest_harvest import get_session_results_dct

from reasoner_validator.biolink import check_biolink_model_compliance_of_input_edge

from translator.registry import (
    get_remote_test_data_file,
    get_the_registry_data,
    extract_component_test_metadata_from_registry
)
from translator.trapi import (
    set_trapi_version,
    get_trapi_version,
    generate_edge_id
)

from tests.onehop import util as oh_util
from tests.onehop.util import (
    get_unit_test_codes
)
from translator.sri.testing.report import (
    TEST_RESULTS_DIR,
    unit_test_report_filepath,
    parse_unit_test_name
)

logger = logging.getLogger(__name__)


def pytest_sessionfinish(session):
    """ Gather all results and save them to a csv.
    Works both on worker and master nodes, and also with xdist disabled"""

    test_run_id: str
    if "test_run_id" in session.config.option and session.config.option.test_run_id:
        test_run_id = session.config.option.test_run_id
    else:
        # Generate a fake UUID test id for local runs
        test_run_id = str(uuid4())

    # subdirectory for local run output data
    test_run_root_path: str = f"{TEST_RESULTS_DIR}/{test_run_id}"
    makedirs(test_run_root_path)

    session_results = get_session_results_dct(session)

    test_summary: Dict = dict()

    current_time = datetime.now()
    test_summary['timestamp'] = current_time.strftime("%d-%m-%Y, %H:%M:%S")

    case_details: Dict = dict()

    for unit_test_key, details in session_results.items():

        rb: Dict = details['fixtures']['results_bag']

        # sanity check: clean up MS Windoze EOL characters, when present in results_bag keys
        rb = {key.strip("\r\n"): value for key, value in rb.items()}

        # clean up the name for safe file system usage
        component, ara_id, kp_id, edge_num, test_id, edge_details_file_path = parse_unit_test_name(
            unit_test_key=unit_test_key
        )

        ##############################################################
        # Summary file indexed by component, resources and edge cases
        ##############################################################

        if component not in test_summary:
            test_summary[component] = dict()

        case_summary: List[Dict]
        if ara_id:
            if ara_id not in test_summary[component]:
                test_summary[component][ara_id] = dict()
            if kp_id not in test_summary[component][ara_id]:
                test_summary[component][ara_id][kp_id] = list()
            case_summary = test_summary[component][ara_id][kp_id]
        else:
            if kp_id not in test_summary[component]:
                test_summary[component][kp_id] = list()
            case_summary = test_summary[component][kp_id]

        while edge_num >= len(case_summary):
            case_summary.append(dict())

        if 'edge_num' not in case_summary[edge_num]:
            case_summary[edge_num]['edge_num'] = edge_num

        if test_id not in case_summary[edge_num]:
            # Top level summary reporting 'PASSED, FAILED, SKIPPED' for each unit test
            case_summary[edge_num][test_id] = details['status']

        ################################################
        # Print out unit details as separate files
        # relative to TEST_RESULTS_DIR and 'test_run_id'
        ################################################

        if edge_details_file_path not in case_details:

            # TODO: this is a bit memory intensive...
            #      may need another strategy for capturing details
            case_details[edge_details_file_path] = dict()

            if 'case' in rb and 'case' not in case_details[edge_details_file_path]:
                case_details[edge_details_file_path] = rb['case']

            if 'results' not in case_details[edge_details_file_path]:
                case_details[edge_details_file_path]['results'] = dict()

        if test_id not in case_details[edge_details_file_path]['results']:
            case_details[edge_details_file_path]['results'][test_id] = dict()

        test_details = case_details[edge_details_file_path]['results'][test_id]

        # Replicating 'PASSED, FAILED, SKIPPED' test status
        # for each unit test, here in the detailed report
        test_details['outcome'] = details['status']

        # Print out errors - we assume they are only reported once for any given test?
        if 'errors' in rb and len(rb['errors']) > 0:
            test_details['errors'] = rb['errors']

        # Capture more request/response details for test failures
        if details['status'] == 'failed':

            if 'request' in rb:
                test_details['request'] = rb['request']
            else:
                test_details['request'] = "No 'request' generated for this unit test?"

            if 'response' in rb:
                test_details['http_status_code'] = rb["response"]["status_code"]
                test_details['response'] = rb['response']['response_json']
            else:
                test_details['response'] = "No 'response' generated for this unit test?"

    for edge_details_file_path in case_details:
        # Print out the test case details

        test_details_file_path = unit_test_report_filepath(
            test_run_id=test_run_id,
            unit_test_file_path=edge_details_file_path
        )
        with open(test_details_file_path, 'w') as details_file:
            test_details = case_details[edge_details_file_path]
            json.dump(test_details, details_file, indent=4)

    # Write out the whole List[str] of unit test identifiers, into one JSON summary file
    summary_filepath = f"{test_run_root_path}/test_summary.json"
    with open(summary_filepath, 'w') as summary_file:
        json.dump(test_summary, summary_file, indent=4)


def pytest_addoption(parser):
    """
    :param parser:
    """
    parser.addoption("--teststyle", action="store", default='all', help='Which Test to Run?')
    parser.addoption("--one", action="store_true", help="Only use first edge from each KP file")
    parser.addoption(
        "--triple_source", action="store", default='REGISTRY',  # 'test_triples/KP',
        help="'REGISTRY', directory or file from which to retrieve triples (Default: 'REGISTRY', which triggers " +
             "the use of metadata, in KP entries from the Translator SmartAPI Registry, to configure the tests)."
    )
    parser.addoption(
        "--ARA_source", action="store", default='REGISTRY',  # 'test_triples/ARA',
        help="'REGISTRY', directory or file from which to retrieve ARA Config (Default: 'REGISTRY', which triggers " +
             "the use of metadata, in ARA entries from the Translator SmartAPI Registry, to configure the tests)."
    )
    # We hard code a 'current' version (1.2 as of March 2022)
    # but we'll eventually use an endpoint's SmartAPI published value 'x-trapi' published metadata value
    parser.addoption(
        "--TRAPI_Version", action="store", default=None,
        help='TRAPI API Version to use for the tests '
             '(Default: latest public release or REGISTRY metadata value).'
    )
    # We could eventually use a TRAPI/meta_knowledge_graph 'x-translator' published metadata value,
    # but we'll use the Biolink Model Toolkit default for now?
    parser.addoption(
        "--Biolink_Version", action="store", default=None,
        help='Biolink Model Version to use for the tests ' +
             '(Default: latest Biolink Model Toolkit default or REGISTRY metadata value).'
    )
    #  Mostly used when the SRI Testing harness is run by a web service
    parser.addoption(
        "--test_run_id", action="store", default="",
        help='Optional Test Run Identifier for internal use to index test results.'
    )


def _fix_path(file_path: str) -> str:
    """
    Fixes OS specific path string issues (especially, for MS Windows)
    
    :param file_path: file path to be repaired
    """
    file_path = file_path.replace("\\", "/")
    return file_path


def _build_filelist(entry):
    filelist = []
    if path.isfile(entry):
        filelist.append(entry)
    else:
        dtrips = walk(entry)
        for dirpath, dirnames, filenames in dtrips:
            # SKIP specific test folders, if so tagged
            if dirpath and dirpath.endswith("SKIP"):
                continue
            # Windows OS quirk - fix path
            real_dirpath = _fix_path(dirpath)
            for f in filenames:
                # SKIP specific test files, if so tagged
                if f.endswith("SKIP"):
                    continue
                kpfile = f'{real_dirpath}/{f}'
                filelist.append(kpfile)
    
    return filelist


def get_test_data_sources(source: str, component_type: str) -> Dict[str, Dict[str, Optional[str]]]:
    """
    Retrieves a dictionary of metadata of 'component_type', indexed by name.

    If the 'source' is specified to be the string 'REGISTRY', then
    this dictionary is populated from the Translator SmartAPI Registry,
    using published 'test_data_location' values as keys.

    Otherwise, a local file source of the metadata is assumed,
    using the local data file name as a key (these should be unique).

    :param source: str, specific remote or local source from which the test data sources are to be retrieved.
    :param component_type: str, component type 'KP' or 'ARA'
    :return:
    """
    """

    """
    service_metadata: Dict[str, Dict[str, Optional[str]]]

    if source == "REGISTRY":
        # Access service metadata from the Translator SmartAPI Registry,
        # indexed using the "test_data_location" field as the unique key
        registry_data: Dict = get_the_registry_data()
        service_metadata = extract_component_test_metadata_from_registry(registry_data, component_type)
    else:
        # Access local set of test data triples
        if not path.exists(source):
            print("No such location:", source, flush=True, file=stderr)
            return dict()

        filelist: List[str] = _build_filelist(source)

        # Create an empty "mock" service metadata structure
        # indexed using the local file name as the unique key
        # We will try to populate this metadata later, from
        # the file contents or from default test conditions
        metadata_template = {
            "service_title": None,
            "service_version": None,
            "component": component_type,
            "infores": None,
            "biolink_version": None,
            "trapi_version": None
        }
        service_metadata = {name: metadata_template.copy() for name in filelist}

    return service_metadata


def load_test_data_source(
        source: str,
        metadata: Dict[str, Optional[str]],
        trapi_version: Optional[str] = None,
        biolink_version: Optional[str] = None
) -> Optional[Dict]:
    """
    Load one specified component test data source.

    :param source: source string, URL if from "remote"; file path if local
    :param metadata: metadata associated with source
    :param trapi_version: SemVer caller override of TRAPI release target for validation (Default: None)
    :param biolink_version: SemVer caller override of Biolink Model release target for validation (Default: None)
    :return: json test data with (some) metadata; 'None' if unavailable
    """
    # sanity check
    assert metadata is not None

    if not source.endswith('json'):
        # Source file, whatever its origin -
        # local or Translator SmartAPI Registry x-trapi
        # specified test_data_location - should be a JSON file.
        # Ignore this test data source...
        return None

    test_data: Optional[Dict] = None
    if source.startswith('http'):
        # Source is an online test data repository, likely harvested
        # from the Translator SmartAPI Registry 'test_data_location'
        test_data = get_remote_test_data_file(source)
    else:
        # Source is a local data file
        with open(source, 'r') as local_file:
            try:
                test_data = json.load(local_file)
            except (json.JSONDecodeError, TypeError):
                logger.error(f"load_test_data_source(): input file '{source}': Invalid JSON")

    if test_data is not None:

        # append test data to metadata
        metadata.update(test_data)

        metadata['location'] = source

        api_name: str = source.split('/')[-1]
        # remove the trailing file extension
        metadata['api_name'] = api_name.replace(".json", "")

        # Possible CLI override of the metadata value of
        # TRAPI and Biolink Model releases used for data validation
        if trapi_version:
            metadata['trapi_version'] = trapi_version

        if biolink_version:
            metadata['biolink_version'] = biolink_version

    return metadata


# Key is a resource identifier a.k.a. 'api_name'
# Value is associated Translator SmartAPI Registry metadata dictionary
component_catalog: Dict[str, Dict[str, Any]] = dict()


def cache_resource_metadata(metadata: Dict[str, Any]):
    component = metadata['component']
    assert component in ["KP", "ARA"]
    resource_id: str = metadata['api_name']
    component_catalog[resource_id] = metadata


def get_metadata_by_resource(resource_id: str) -> Optional[Dict[str, Any]]:
    if resource_id in component_catalog:
        metadata: Dict = component_catalog[resource_id]
        return metadata
    else:
        return None


def get_component_by_resource(resource_id: str) -> Optional[str]:
    metadata: Dict = get_metadata_by_resource(resource_id)
    if metadata and "component" in metadata:
        return metadata['component']
    else:
        return None


kp_edges_catalog: Dict[str, Dict[str,  Union[int, str]]] = dict()


def add_kp_edge(resource_id: str, edge_idx: int, edge: Dict[str, Any]):
    metadata: Dict = get_metadata_by_resource(resource_id)
    assert metadata
    if "edges" not in metadata:
        metadata['edges'] = list()
    while len(metadata['edges']) <= edge_idx:
        metadata['edges'].append(None)
    metadata['edges'][edge_idx] = edge


def get_kp_edge(resource_id: str, edge_idx: int) -> Optional[Dict[str, Any]]:
    metadata: Dict = get_metadata_by_resource(resource_id)
    if metadata:
        edges = metadata['edges']
        if 0 <= edge_idx < len(edges):
            return edges[edge_idx]
        logger.warning(f"get_kp_edge(resource_id: {resource_id}, edge_idx: {edge_idx}) out-of-bounds 'edge_idx'?")
    else:
        logger.warning(f"get_kp_edge(resource_id: {resource_id}, edge_idx: {edge_idx}) 'metadata' unavailable?")
    return None


def generate_trapi_kp_tests(metafunc, trapi_version: str, biolink_version: str) -> List:
    """
    Generate set of TRAPI Knowledge Provider unit tests with test data edges.

    :param metafunc: Dict, diverse One Step Pytest metadata
    :param trapi_version, str, TRAPI release set to be used in the validation
    :param biolink_version, str, Biolink Model release set to be used in the validation
    """
    edges = []
    idlist = []

    # optional user session identifier for test (maybe be an empty string)
    test_run_id = metafunc.config.getoption('test_run_id')

    triple_source = metafunc.config.getoption('triple_source')

    kp_metadata: Dict[str, Dict[str, Optional[str]]] = get_test_data_sources(triple_source, component_type="KP")

    for source, metadata in kp_metadata.items():

        # User CLI may override here the target Biolink Model version during KP test data preparation
        kpjson = load_test_data_source(source, metadata, trapi_version, biolink_version)

        cache_resource_metadata(kpjson)

        dataset_level_test_exclusions: Set = set()
        if "exclude_tests" in kpjson:
            dataset_level_test_exclusions.update(
                [test for test in kpjson["exclude_tests"] if test in get_unit_test_codes()]
            )

        if not ('url' in kpjson and kpjson['url'].startswith("http")):
            err_msg = f"generate_trapi_kp_tests(): source '{source}' url "
            err_msg += f"{str(kpjson['url'])} is invalid" if 'url' in kpjson else "field is missing"
            err_msg += "... Skipping test data source?"
            logger.error(err_msg)
            continue

        # TODO: see below about echoing the edge input data to the Pytest stdout
        print(f"### Start of Test Input Edges for KP '{kpjson['api_name']}' ###")

        if 'url' in kpjson:

            for edge_i, edge in enumerate(kpjson['edges']):

                # We tag each edge internally with its
                # sequence number, for later convenience
                edge['idx'] = edge_i

                # We can already do some basic Biolink Model validation here of the
                # S-P-O contents of the edge being input from the current triples file?
                model_version, errors = \
                    check_biolink_model_compliance_of_input_edge(
                        edge,
                        biolink_version=kpjson['biolink_version']
                    )
                if errors:
                    # defer reporting of errors to higher level of test harness
                    edge['biolink_errors'] = model_version, errors

                edge['location'] = kpjson['location']

                edge['url'] = kpjson['url']

                edge['kp_api_name'] = kpjson['api_name']

                edge['trapi_version'] = kpjson['trapi_version']
                edge['biolink_version'] = kpjson['biolink_version']

                if 'infores' in kpjson:
                    edge['kp_source'] = f"infores:{kpjson['infores']}"
                else:
                    logger.warning(
                        f"generate_trapi_kp_tests(): input file '{source}' "
                        "is missing its 'infores' field value? Inferred from its API name?"
                    )
                    kp_api_name: str = edge['kp_api_name']
                    edge['kp_source'] = f"infores:{kp_api_name.lower()}"

                if 'source_type' in kpjson:
                    edge['kp_source_type'] = kpjson['source_type']
                else:
                    # If not specified, we assume that the KP is a "primary_knowledge_source"
                    edge['kp_source_type'] = "primary"

                if 'query_opts' in kpjson:
                    edge['query_opts'] = kpjson['query_opts']
                else:
                    edge['query_opts'] = {}

                if dataset_level_test_exclusions:
                    if 'exclude_tests' not in edge:
                        edge['exclude_tests']: Set = dataset_level_test_exclusions
                    else:
                        # converting List internally to a set
                        edge['exclude_tests'] = set(edge['exclude_tests'])
                        edge['exclude_tests'].update(dataset_level_test_exclusions)

                # convert back to List for JSON serialization safety later
                if 'exclude_tests' in edge:
                    edge['exclude_tests'] = list(edge['exclude_tests'])

                edges.append(edge)

                resource_id = edge['kp_api_name']

                #
                # TODO: caching the edge here doesn't help parsing of the results into a report since
                #       the cache is not shared with the parent process.
                #       Instead, we will try to echo the edge directly to stdout, for later parsing for the report.
                #
                # add_kp_edge(resource_id, edge_i, edge)
                json.dump(edge, stdout)

                edge_id = generate_edge_id(resource_id, edge_i)
                idlist.append(edge_id)

                if metafunc.config.getoption('one', default=False):
                    break

        print(f"### End of Test Input Edges for KP '{kpjson['api_name']}' ###")

    if "kp_trapi_case" in metafunc.fixturenames:

        metafunc.parametrize('kp_trapi_case', edges, ids=idlist)

        teststyle = metafunc.config.getoption('teststyle')

        # Runtime specified (CLI) constraints on test scope,
        # which will be overridden by file set and specific
        # test triple-level exclude_tests scoping, as captured above
        if teststyle == 'all':
            global_test_inclusions = [
                    oh_util.by_subject,
                    oh_util.inverse_by_new_subject,
                    oh_util.by_object,
                    oh_util.raise_subject_entity,
                    oh_util.raise_object_by_subject,
                    oh_util.raise_predicate_by_subject
            ]
        else:
            global_test_inclusions = [getattr(oh_util, teststyle)]

        metafunc.parametrize("trapi_creator", global_test_inclusions)

    return edges


# Once the smartapi tests are up, we'll want to pass them in here as well
def generate_trapi_ara_tests(metafunc, kp_edges, trapi_version, biolink_version):
    """
    Generate set of TRAPI Autonomous Relay Agents (ARA) unit tests with KP test data edges.

    :param metafunc: Dict, diverse One Step Pytest metadata
    :param kp_edges: List, list of knowledge provider test edges from knowledge providers associated
    :param trapi_version, str, TRAPI release set to be used in the validation
    :param biolink_version, str, Biolink Model release set to be used in the validation
    """
    kp_dict = defaultdict(list)
    for e in kp_edges:
        kp_dict[e['kp_api_name']].append(e)

    ara_edges = []
    idlist = []

    ara_source = metafunc.config.getoption('ARA_source')

    ara_metadata: Dict[str, Dict[str, Optional[str]]] = get_test_data_sources(ara_source, component_type="ARA")

    for source, metadata in ara_metadata.items():

        # User CLI may override here the target Biolink Model version during KP test data preparation
        arajson = load_test_data_source(source, metadata, trapi_version, biolink_version)

        cache_resource_metadata(arajson)

        for kp in arajson['KPs']:

            # By replacing spaces in name with underscores,
            # should give get the KP "api_name" indexing the edges.
            kp = '_'.join(kp.split())

            for edge_i, kp_edge in enumerate(kp_dict[kp]):

                edge: dict = kp_edge.copy()

                edge['url'] = arajson['url']

                edge['ara_api_name'] = arajson['api_name']

                edge['trapi_version'] = arajson['trapi_version']
                edge['biolink_version'] = arajson['biolink_version']

                if 'infores' in arajson:
                    edge['ara_source'] = f"infores:{arajson['infores']}"
                else:
                    logger.warning(
                        f"generate_trapi_ara_tests(): input file '{source}' " +
                        "is missing its ARA 'infores' field.  We infer one from "
                        "the ARA 'api_name', but edge provenance may not be properly tested?"
                    )
                    ara_api_name: str = edge['ara_api_name']
                    edge['ara_source'] = f"infores:{ara_api_name.lower()}"

                if 'kp_source' in kp_edge:
                    edge['kp_source'] = kp_edge['kp_source']
                else:
                    logger.warning(
                        f"generate_trapi_ara_tests(): KP '{kp}' edge is missing its 'kp_source' infores." +
                        "Inferred from KP name, but KP provenance may not be properly tested?"
                    )
                    edge['kp_source'] = f"infores:{kp}"
                edge['kp_source_type'] = kp_edge['kp_source_type']

                if 'query_opts' in arajson:
                    edge['query_opts'] = arajson['query_opts']
                else:
                    edge['query_opts'] = {}

                idlist.append(f"{edge['ara_api_name']}|{edge['kp_api_name']}#{edge_i}")

                ara_edges.append(edge)

    metafunc.parametrize('ara_trapi_case', ara_edges, ids=idlist)


def pytest_generate_tests(metafunc):
    """This hook is run at test generation time.  These functions look at the configured triples on disk
    and use them to parameterize inputs to the test functions. Note that this gets called multiple times, once
    for each test_* function, and you can only parameterize an argument to that specific test_* function.
    However, for the ARA tests, we still need to get the KP data, since that is where the triples live."""
    trapi_version = metafunc.config.getoption('TRAPI_Version')
    logger.debug(f"pytest_generate_tests(): TRAPI_Version == {trapi_version}")
    set_trapi_version(version=trapi_version)

    # Bug or feature? The Biolink Model release may be overridden on the command line
    biolink_version = metafunc.config.getoption('Biolink_Version')
    logger.debug(f"pytest_generate_tests(): Biolink_Version == {biolink_version}")
    trapi_kp_edges = generate_trapi_kp_tests(metafunc, trapi_version=get_trapi_version(), biolink_version=biolink_version)

    if metafunc.definition.name == 'test_trapi_aras':
        generate_trapi_ara_tests(metafunc, trapi_kp_edges, trapi_version=get_trapi_version(), biolink_version=biolink_version)
