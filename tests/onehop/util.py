from typing import Optional
from copy import deepcopy

from bmt import Toolkit
from translator.biolink import get_biolink_model_schema
from translator.sri.testing.util import ontology_kp

_bmt_toolkit = None


def get_toolkit() -> Optional[Toolkit]:
    global _bmt_toolkit
    if not _bmt_toolkit:
        raise RuntimeError("Biolink Model Toolkit is not initialized?!?")
    return _bmt_toolkit


_default_trapi_version = None


def get_trapi_version() -> Optional[str]:
    # This TRAPI release variable is allowed to be None if not reset below by pytest CLI
    # since the ReasonerAPI Validator defaults to using the 'latest' TRAPI release
    global _default_trapi_version
    return _default_trapi_version


def global_test_configuration(biolink_version, trapi_version):
    # Note here that we let BMT control which version of Biolink we are using,
    # unless the value for which is overridden on the CLI
    global _bmt_toolkit, _default_trapi_version

    # Toolkit takes a couple of seconds to initialize, so don't want it initialized per-test
    if biolink_version:
        biolink_schema = get_biolink_model_schema()
        _bmt_toolkit = Toolkit(biolink_schema)
    else:
        _bmt_toolkit = Toolkit()

    _default_trapi_version = trapi_version



###
#
# Functions for creating TRAPI messages from a known edge
#
# Each function returns the new message, and also some information used to evaluate whether the
# correct value was retrieved.  The second return value (object or subject) is the name of what is
# being returned and the third value (a or b) is which query node it should be bound to in one of the
# results.  For example, when we look up a triple by subject, we should expect that the object entity
# is bound to query node b.
#


def by_subject(request):
    """Given a known triple, create a TRAPI message that looks up the object by the subject"""
    message = create_one_hop_message(request, look_up_subject=False)
    return message, 'object', 'b'


def by_object(request):
    """Given a known triple, create a TRAPI message that looks up the subject by the object"""
    message = create_one_hop_message(request, look_up_subject=True)
    return message, 'subject', 'a'


def raise_subject_entity(request):
    """Given a know triple create a TRAPI message that uses the parent of the original entity and looks up the object"""
    subject_cat = request['subject_category']
    subject = request['subject']
    parent_subject = ontology_kp.get_parent(subject, subject_cat)
    if parent_subject is None:
        print('No Parent: ', subject)
        return None
    mod_request = deepcopy(request)
    mod_request['subject'] = parent_subject
    message = create_one_hop_message(mod_request, look_up_subject=False)
    return message, 'object', 'b'


def raise_object_by_subject(request):
    """Given a known triple, create a TRAPI message that uses the parent of the original object category and looks up
    the object by the subject"""
    original_object_element = get_toolkit().get_element(request['object_category'])
    transformed_request = request.copy()  # there's no depth to request, so it's ok
    parent = get_toolkit().get_element(original_object_element['is_a'])
    transformed_request['object_category'] = parent['class_uri']
    message = create_one_hop_message(transformed_request, look_up_subject=False)
    return message, 'object', 'b'


def raise_predicate_by_subject(request):
    """Given a known triple, create a TRAPI message that uses the parent of the original predicate and looks up
    the object by the subject"""
    transformed_request = request.copy()  # there's no depth to request, so it's ok
    if request['predicate'] != 'biolink:related_to':
        original_predicate_element = get_toolkit().get_element(request['predicate'])
        parent = get_toolkit().get_element(original_predicate_element['is_a'])
        transformed_request['predicate'] = parent['slot_uri']
    message = create_one_hop_message(transformed_request, look_up_subject=False)
    return message, 'object', 'b'


def create_one_hop_message(edge, look_up_subject=False):
    """Given a complete edge, create a valid TRAPI message for querying for the edge.
    if look_up_subject is False (default) then the object id is not included, (lookup object
    by subject) and if look_up_subject is True, then the subject id is not included (look up
    subject by object)"""
    query_graph = {
        "nodes": {
            'a': {
                "category": edge['subject_category']
            },
            'b': {
                "category": edge['object_category']
            }
        },
        "edges": {
            'ab': {
                "subject": "a",
                "object": "b",
                "predicate": edge['predicate']
            }
        }
    }
    if look_up_subject:
        query_graph['nodes']['b']['ids'] = [edge['object']]
    else:
        query_graph['nodes']['a']['ids'] = [edge['subject']]
    message = {"message": {"query_graph": query_graph, 'knowledge_graph': {"nodes": {}, "edges": {}, }, 'results': []}}
    return message