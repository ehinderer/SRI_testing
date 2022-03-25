"""
Configure onehop tests
"""
import os
import json
from collections import defaultdict
from json import JSONDecodeError

from pytest_harvest import get_session_results_dct
from tests.onehop import util as oh_util
from tests.onehop.util import get_trapi_version


def pytest_sessionfinish(session):
    """ Gather all results and save them to a csv.
    Works both on worker and master nodes, and also with xdist disabled"""

    session_results = get_session_results_dct(session)
    for t, v in session_results.items():
        if v['status'] == 'failed':
            rfname = f"{t.split('/')[-1][:-1]}.results"
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
    parser.addoption(
        "--TRAPI_version", action="store", default=None,  # we'll use the reasoner_validation default?
        help='TRAPI API release to use for the tests (default: latest public release)'
    )
    parser.addoption(
        "--Biolink_version", action="store", default=None,  # we'll use the Biolink Model Toolkit default?
        help='Biolink Model release to use for the tests (default: latest Biolink Model Toolkit default)'
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


def generate_trapi_kp_tests(metafunc):
    """
    :param metafunc
    """
    triple_source = metafunc.config.getoption('triple_source')
    edges = []
    idlist = []
    if not os.path.exists(triple_source):
        print("No such location:", triple_source)
        return edges
    
    filelist = _build_filelist(triple_source)
    for kpfile in filelist:
        with open(kpfile, 'r') as inf:
            if not kpfile.endswith('json'):
                continue
            try:
                kpjson = json.load(inf)
            except (JSONDecodeError, TypeError):
                print('Invalid JSON')
                print(kpfile)
                exit()
                
        if kpjson['TRAPI'] and 'url' in kpjson:
            for edge_i, edge in enumerate(kpjson['edges']):
                edge['location'] = kpfile
                edge['api_name'] = kpfile.split('/')[-1]
                edge['url'] = kpjson['url']
                edge['trapi_version'] = kpjson['TRAPI'] \
                    if kpjson['TRAPI'] and not isinstance(kpjson['TRAPI'], bool) else get_trapi_version()
                if 'query_opts' in kpjson:
                    edge['query_opts'] = kpjson['query_opts']
                else:
                    edge['query_opts'] = {}
                edges.append(edge)
                idlist.append(f'{kpfile}_{edge_i}')
                if metafunc.config.getoption('one'):
                    break

    if "kp_trapi_case" in metafunc.fixturenames:
        metafunc.parametrize('kp_trapi_case', edges, ids=idlist)
        teststyle = metafunc.config.getoption('teststyle')
        if teststyle == 'all':
            metafunc.parametrize(
                "trapi_creator",
                [
                    oh_util.by_subject,
                    oh_util.inverse_by_new_subject,
                    oh_util.by_object,
                    oh_util.raise_subject_entity,
                    oh_util.raise_object_by_subject,
                    oh_util.raise_predicate_by_subject
                ]
            )
        else:
            metafunc.parametrize("trapi_creator", [getattr(oh_util, teststyle)])

    return edges


# Once the smartapi tests are up, we'll want to pass them in here as well
def generate_trapi_ara_tests(metafunc, kp_edges):
    """
    :param metafunc
    :param kp_edges
    """
    if "ara_trapi_case" not in metafunc.fixturenames:
        return
    kp_dict = defaultdict(list)
    for e in kp_edges:
        # eh, not handling api name very well
        kp_dict[e['api_name'][:-5]].append(e)
    ara_edges = []
    idlist = []
    ara_source = metafunc.config.getoption('ARA_source')

    # Figure out which ARAs should be able to get which triples from which KPs
    filelist = _build_filelist(ara_source)
    for arafile in filelist:
        f = arafile.split('/')[-1]
        with open(arafile, 'r') as inf:
            arajson = json.load(inf)
        for kp in arajson['KPs']:
            for edge_i, kp_edge in enumerate(kp_dict['_'.join(kp.split())]):
                edge = kp_edge.copy()
                edge['api_name'] = f
                edge['url'] = arajson['url']
                edge['trapi_version'] = arajson['TRAPI'] \
                    if arajson['TRAPI'] and not isinstance(arajson['TRAPI'], bool) else get_trapi_version()
                edge['kp_source'] = kp
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
    biolink_version = metafunc.config.getoption('Biolink_version')
    trapi_version = metafunc.config.getoption('TRAPI_version')
    oh_util.global_test_configuration(biolink_version=biolink_version, trapi_version=trapi_version)
    trapi_kp_edges = generate_trapi_kp_tests(metafunc)
    generate_trapi_ara_tests(metafunc, trapi_kp_edges)
