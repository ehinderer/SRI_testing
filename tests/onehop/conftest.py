"""
Configure one hop tests
"""
import os
import json
import logging
from collections import defaultdict
from json import JSONDecodeError
from typing import Optional, List, Tuple, Set, Dict

from pytest_harvest import get_session_results_dct

from tests.onehop.util import get_unit_test_codes
from reasoner_validator.biolink import check_biolink_model_compliance_of_input_edge
from tests.onehop import util as oh_util
from translator.trapi import set_trapi_version

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def _clean_up_filename(source: str):
    name = source.split('/')[-1][:-1]
    name = name.replace(".py::", "-")
    name = name.replace("[", "-")
    name = name.replace("]", "")
    name = f"{name}.results"
    logger.debug(f"_clean_up_filename: '{source}' to '{name}'")
    return name


def pytest_sessionfinish(session):
    """ Gather all results and save them to a csv.
    Works both on worker and master nodes, and also with xdist disabled"""

    session_results = get_session_results_dct(session)
    for t, v in session_results.items():
        if v['status'] == 'failed':
            # clean up the name for safe file system usage
            rfname = _clean_up_filename(t)
            rb = v['fixtures']['results_bag']
            # rb['location'] looks like "test_triples/KP/Exposures_Provider/CAM-KP_API.json"
            if 'location' in rb:
                lparts = rb['location'].split('/')
                lparts[0] = 'results'
                lparts[-1] = rfname
                try:
                    os.makedirs('/'.join(lparts[:-1]))
                except OSError:
                    pass
                outname = '/'.join(lparts)
            else:
                outname = rfname
            if 'request' in rb:
                with open(outname, 'w') as outf:
                    outf.write(rb['location'])
                    outf.write('\n')
                    json.dump(rb['request'], outf, indent=4)
                    outf.write(f'\nStatus Code: {rb["response"]["status_code"]}\n')
                    json.dump(rb['response']['response_json'], outf, indent=4)
            else:
                # This means that there was no generated request.
                # But we don't need to make a big deal about it.
                with open(outname+"NOTEST", 'w') as outf:
                    outf.write('Error generating results: No request generated?')
                    json.dump(rb['case'], outf, indent=4)


def pytest_addoption(parser):
    """
    :param parser:
    """
    parser.addoption("--teststyle", action="store", default='all', help='Which Test to Run?')
    parser.addoption("--one", action="store_true", help="Only use first edge from each KP file")
    parser.addoption(
        "--triple_source", action="store", default='test_triples/KP',
        help="Directory or file from which to retrieve triples"
    )
    parser.addoption(
        "--ARA_source", action="store", default='test_triples/ARA',
        help="Directory or file from which to retrieve ARA Config"
    )
    # We hard code a 'current' version (1.2 as of March 2022)
    # but we'll eventually use an endpoint's SmartAPI published value
    parser.addoption(
        "--TRAPI_Version", action="store", default=None,
        help='TRAPI API Version to use for the tests (default: latest public release)'
    )
    # We could eventually use a TRAPI/meta_knowledge_graph value,
    # but we'll use the Biolink Model Toolkit default for now?
    parser.addoption(
        "--Biolink_Release", action="store", default=None,
        help='Biolink Model Release to use for the tests (default: latest Biolink Model Toolkit default)'
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
    if os.path.isfile(entry):
        filelist.append(entry)
    else:
        dtrips = os.walk(entry)
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


def get_kp_test_data_sources(metafunc) -> List[str]:
    """
    Returns a list of KPtest data sources.

    First implementation just wraps the existing local test data files.
    """
    triple_source = metafunc.config.getoption('triple_source')

    if not os.path.exists(triple_source):
        print("No such location:", triple_source)
        return []

    filelist: List[str] = _build_filelist(triple_source)

    return filelist


def load_kp_test_data_source(source: str) -> Optional[Dict]:
    """
    Load one specified KP test data source.

    First implementation just wraps the legacy local file loading code.
    """
    if not source.endswith('json'):
        return None
    with open(source, 'r') as inf:
        try:
            kpjson: Dict = json.load(inf)
        except (JSONDecodeError, TypeError):
            logger.error(f"generate_trapi_kp_tests(): input file '{source}': Invalid JSON")

            # Previous use of an exit() statement here seemed a bit drastic bailout here...
            # JSON errors in a single file? Rather, just skip over to the next file?
            return None

    return kpjson


def generate_trapi_kp_tests(metafunc, biolink_release):
    """
    :param metafunc
    :param biolink_release
    """
    edges = []
    idlist = []

    kp_data_sources: List[str] = get_kp_test_data_sources(metafunc)

    for source in kp_data_sources:

        kpjson = load_kp_test_data_source(source)

        dataset_level_test_exclusions: Set = set()
        if "exclude_tests" in kpjson:
            dataset_level_test_exclusions.update(
                [test for test in kpjson["exclude_tests"] if test in get_unit_test_codes()]
            )

        if 'url' in kpjson:
            for edge_i, edge in enumerate(kpjson['edges']):

                # We can already do some basic Biolink Model validation here of the
                # S-P-O contents of the edge being input from the current triples file?
                model_version, errors = \
                    check_biolink_model_compliance_of_input_edge(
                        edge,
                        biolink_release=biolink_release
                    )
                if errors:
                    # defer reporting of errors to higher level of test harness
                    edge['biolink_errors'] = model_version, errors

                # TODO: 'location', 'api_name', 'url', biolink_release should all
                #       eventually be set from Translator SmartAPI Registry metadata
                edge['location'] = source
                edge['api_name'] = source.split('/')[-1]
                edge['url'] = kpjson['url']
                edge['biolink_release'] = biolink_release

                if 'source_type' in kpjson:
                    edge['source_type'] = kpjson['source_type']
                else:
                    # If not specified, we assume that the KP is an "aggregator_knowledge_source"
                    edge['source_type'] = "aggregator"

                if 'infores' in kpjson:
                    edge['infores'] = kpjson['infores']
                else:
                    logger.warning(
                        f"generate_trapi_kp_tests(): input file '{source}' is missing its 'infores' field value?"
                    )
                    edge['infores'] = None

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

                idlist.append(f'{source}_{edge_i}')

                if metafunc.config.getoption('one'):
                    break

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


def get_ara_test_data_sources(metafunc) -> List[str]:
    """
    Returns a list of ARA test data sources.

    First implementation just wraps the existing local test data files.
    """
    ara_source = metafunc.config.getoption('ARA_source')

    # Figure out which ARAs should be able to get which triples from which KPs
    filelist: List[str] = _build_filelist(ara_source)

    return filelist


def load_ara_test_data_source(source: str) -> Tuple[str, Optional[Dict]]:
    """
    Load one specified ARA test data source.

    First implementation just wraps the legacy local file loading code.
    """
    f: str = source.split('/')[-1]
    with open(source, 'r') as inf:
        arajson: Dict = json.load(inf)

    return f, arajson


# Once the smartapi tests are up, we'll want to pass them in here as well
def generate_trapi_ara_tests(metafunc, kp_edges):
    """
    :param metafunc
    :param kp_edges
    """
    kp_dict = defaultdict(list)
    for e in kp_edges:
        # eh, not handling api name very well
        kp_dict[e['api_name'][:-5]].append(e)

    ara_edges = []
    idlist = []

    ara_data_sources: List[str] = get_ara_test_data_sources(metafunc)

    for source in ara_data_sources:

        f, arajson = load_ara_test_data_source(source)

        for kp in arajson['KPs']:
            for edge_i, kp_edge in enumerate(kp_dict['_'.join(kp.split())]):
                edge = kp_edge.copy()
                edge['api_name'] = f
                edge['url'] = arajson['url']

                if 'infores' in arajson:
                    edge['ara_infores'] = arajson['infores']
                else:
                    logger.warning(
                        f"generate_trapi_ara_tests(): input file '{source}' " +
                        "is missing its ARA 'infores' field...ARA provenance will not be properly tested?"
                    )
                    edge['ara_infores'] = None

                edge['kp_source'] = kp

                edge['kp_source_type'] = kp_edge['source_type']

                if 'infores' in kp_edge:
                    edge['kp_infores'] = kp_edge['infores']
                else:
                    logger.warning(
                        f"generate_trapi_ara_tests(): KP source '{kp}' " +
                        "is missing its KP 'infores' field...KP provenance will not be properly tested?"
                    )
                    edge['kp_infores'] = None

                if 'query_opts' in arajson:
                    edge['query_opts'] = arajson['query_opts']
                else:
                    edge['query_opts'] = {}

                idlist.append(f'{f}_{kp}_{edge_i}')
                ara_edges.append(edge)

    metafunc.parametrize('ara_trapi_case', ara_edges, ids=idlist)


def pytest_generate_tests(metafunc):
    """This hook is run at test generation time.  These functions look at the configured triples on disk
    and use them to parameterize inputs to the test functions. Note that this gets called multiple times, once
    for each test_* function, and you can only parameterize an argument to that specific test_* function.
    However, for the ARA tests, we still need to get the KP data, since that is where the triples live."""
    trapi_version = metafunc.config.getoption('TRAPI_Version')
    set_trapi_version(version=trapi_version)
    biolink_release = metafunc.config.getoption('Biolink_Release')
    trapi_kp_edges = generate_trapi_kp_tests(metafunc, biolink_release=biolink_release)
    if metafunc.definition.name == 'test_trapi_aras':
        generate_trapi_ara_tests(metafunc, trapi_kp_edges)
