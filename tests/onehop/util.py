from copy import deepcopy
from functools import wraps
from os import makedirs
from re import sub
from typing import Set, Dict, Optional, List

from reasoner_validator.biolink import get_biolink_model_toolkit
from translator.sri.testing.util import ontology_kp


def clean_up_unit_test_filename(source: str):
    """
    Reformat (test run key) source identifier into a well-behaved test file name.
    :param source:
    :return:
    """
    name = source.split('/')[-1][:-1]
    name = name.strip("[]")
    name = name.replace(".py::", "-")
    name = sub(r"[:\[\]|#/]+", "-", name)
    return name


def unit_test_report_filepath(location: Optional[str], unit_test_key: str, test_run_id: str, status: str) -> str:
    """

    :param location: str. original file path
    :param unit_test_key: str, specific unit test key
    :param test_run_id: str, caller-defined test session_id
    :param status: test outcome (i.e. PASSED, FAILED, SKIPPED
    :return:
    """

    # clean up the name for safe file system usage
    rfname = clean_up_unit_test_filename(unit_test_key)

    # We tag the filename with its status
    rfname = f"{rfname}_{status.upper()}"

    # rb['location'] looks like "test_triples/KP/Exposures_Provider/CAM-KP_API.json"
    lparts: List[str]
    if location:

        # TODO: the following location path split doesn't work so well
        #       when given a complex location, like an internet URI
        #       Try to just limit to the tail of the lparts list of path directories?
        lparts = location.split('/')[-4:]

        lparts[0] = test_run_id
        lparts[-1] = rfname
        try:
            makedirs('/'.join(lparts[:-1]))
        except OSError:
            pass
    else:
        lparts = [test_run_id, rfname]

    outname = '/'.join(lparts)
    return outname


def create_one_hop_message(edge, look_up_subject=False):
    """Given a complete edge, create a valid TRAPI message for "one hop" querying for the edge.
    If the look_up_subject is False (default) then the object id is not included, (lookup object
    by subject) and if the look_up_subject is True, then the subject id is not included (look up
    subject by object)"""
    # TODO: This key method is actually very TRAPI version sensitive since
    #       the core message structure evolved between various TRAPI versions,
    #       e.g. category string => categories list; predicate string => predicates list
    #
    query_graph = {
        "nodes": {
            'a': {
                "categories": [edge['subject_category']]
            },
            'b': {
                "categories": [edge['object_category']]
            }
        },
        "edges": {
            'ab': {
                "subject": "a",
                "object": "b",
                "predicates": [edge['predicate']]
            }
        }
    }
    if look_up_subject:
        query_graph['nodes']['b']['ids'] = [edge['object']]
    else:
        query_graph['nodes']['a']['ids'] = [edge['subject']]
    message = {"message": {"query_graph": query_graph, 'knowledge_graph': {"nodes": {}, "edges": {}, }, 'results': []}}
    return message


#####################################################################################################
#
# Functions for creating TRAPI messages from a known edge
#
# Each function returns the new message, and also some information used to evaluate whether the
# correct value was retrieved.  The second return value (object or subject) is the name of what is
# being returned and the third value (a or b) is which query node it should be bound to in one of the
# results.  For example, when we look up a triple by subject, we should expect that the object entity
# is bound to query node b.
#
#####################################################################################################
_unit_tests: Dict = dict()


def get_unit_test_codes() -> Set[str]:
    global _unit_tests
    return set(_unit_tests.keys())


def get_unit_test_name(code: str) -> str:
    global _unit_tests
    return _unit_tests[code]


def in_excluded_tests(test, test_case) -> bool:
    global _unit_tests
    try:
        test_name = test.__name__
    except AttributeError:
        raise RuntimeError(f"in_excluded_tests(): invalid 'test' parameter: '{str(test)}'")
    try:
        if "exclude_tests" in test_case:
            # returns 'true' if the test_name corresponds to a test in the list of excluded test (codes)
            return any([test_name == get_unit_test_name(code) for code in test_case["exclude_tests"]])
    except TypeError as te:
        raise RuntimeError(f"in_excluded_tests(): invalid 'test_case' parameter: '{str(test_case)}': {str(te)}")
    except KeyError as ke:
        raise RuntimeError(
            f"in_excluded_tests(): invalid test_case['excluded_test'] code? " +
            f"'{str(test_case['excluded_tests'])}': {str(ke)}"
        )

    return False


class TestCode:
    """
    Assigns a shorthand test code to a unit test method.
    """
    def __init__(self, code, unit_test_name):
        global _unit_tests
        self.code = code
        self.method = unit_test_name
        _unit_tests[code] = unit_test_name

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            return result
        return wrapper


@TestCode("BS", "by_subject")
def by_subject(request):
    """Given a known triple, create a TRAPI message that looks up the object by the subject"""
    message = create_one_hop_message(request, look_up_subject=False)
    return message, 'object', 'b'


@TestCode("IBNS", "inverse_by_new_subject")
def inverse_by_new_subject(request):
    """Given a known triple, create a TRAPI message that inverts the predicate,
       then looks up the new object by the new subject (original object)"""
    tk = get_biolink_model_toolkit(biolink_version=request['biolink_version'])
    original_predicate_element = tk.get_element(request['predicate'])
    if original_predicate_element['symmetric']:
        transformed_predicate = request['predicate']
    else:
        transformed_predicate_name = original_predicate_element['inverse']
        if transformed_predicate_name is None:
            transformed_predicate = None
        else:
            tp = tk.get_element(transformed_predicate_name)
            transformed_predicate = tp.slot_uri

    # Not everything has an inverse (it should, and it will, but it doesn't right now)
    if transformed_predicate is None:
        return None, None, None

    # probably don't need to worry here but just-in-case
    # only work off a copy of the original request...
    transformed_request = request.copy()
    transformed_request.update({
        "subject_category": request['object_category'],
        "object_category": request['subject_category'],
        "predicate": transformed_predicate,
        "subject": request['object'],
        "object": request['subject']
    })
    message = create_one_hop_message(transformed_request, look_up_subject=False)
    # We inverted the predicate, and will be querying by the new subject, so the output will be in node b
    # but, the entity we are looking for (now the object) was originally the subject because of the inversion.
    return message, 'subject', 'b'


@TestCode("BO", "by_object")
def by_object(request):
    """Given a known triple, create a TRAPI message that looks up the subject by the object"""
    message = create_one_hop_message(request, look_up_subject=True)
    return message, 'subject', 'a'


@TestCode("RSE", "raise_subject_entity")
def raise_subject_entity(request):
    """
    Given a known triple, create a TRAPI message that uses
    a parent instance of the original entity and looks up the object.
    This only works if a given instance (category) has an identifier (prefix) namespace
     bound to some kind of hierarchical class of instances (i.e. ontological structure)
    """
    subject_cat = request['subject_category']
    subject = request['subject']
    parent_subject = ontology_kp.get_parent(subject, subject_cat, biolink_version=request['biolink_version'])
    if parent_subject is None:
        # We directly trigger an AssertError here for clarity of unit test failure?
        assert False, f"\nSubject identifier '{subject}[{subject_cat}]' " + \
              "is either not an ontology term or does not map onto a parent ontology term."

    mod_request = deepcopy(request)
    mod_request['subject'] = parent_subject
    message = create_one_hop_message(mod_request, look_up_subject=False)
    return message, 'object', 'b'


@TestCode("ROBS", "raise_object_by_subject")
def raise_object_by_subject(request):
    """
    Given a known triple, create a TRAPI message that uses the parent
    of the original object category and looks up the object by the subject
    """
    tk = get_biolink_model_toolkit(biolink_version=request['biolink_version'])
    original_object_element = tk.get_element(request['object_category'])
    transformed_request = request.copy()  # there's no depth to request, so it's ok
    parent = tk.get_element(original_object_element['is_a'])
    transformed_request['object_category'] = parent['class_uri']
    message = create_one_hop_message(transformed_request, look_up_subject=False)
    return message, 'object', 'b'


@TestCode("RPBS", "raise_predicate_by_subject")
def raise_predicate_by_subject(request):
    """
    Given a known triple, create a TRAPI message that uses the parent
    of the original predicate and looks up the object by the subject
    """
    tk = get_biolink_model_toolkit(biolink_version=request['biolink_version'])
    transformed_request = request.copy()  # there's no depth to request, so it's ok
    if request['predicate'] != 'biolink:related_to':
        original_predicate_element = tk.get_element(request['predicate'])
        parent = tk.get_element(original_predicate_element['is_a'])
        transformed_request['predicate'] = parent['slot_uri']
    message = create_one_hop_message(transformed_request, look_up_subject=False)
    return message, 'object', 'b'
