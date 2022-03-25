from typing import Optional
from copy import deepcopy

from bmt import Toolkit

from .trapi import set_trapi_version

from translator.biolink import get_biolink_model_schema
from translator.sri.testing.util import ontology_kp


_bmt_toolkit = None


def get_toolkit() -> Optional[Toolkit]:
    global _bmt_toolkit
    if not _bmt_toolkit:
        raise RuntimeError("Biolink Model Toolkit is not initialized?!?")
    return _bmt_toolkit


def global_test_configuration(biolink_version, trapi_version):
    # Note here that we let BMT control which version of Biolink we are using,
    # unless the value for which is overridden on the CLI
    global _bmt_toolkit

    # Toolkit takes a couple of seconds to initialize, so don't want it initialized per-test
    if biolink_version:
        biolink_schema = get_biolink_model_schema()
        _bmt_toolkit = Toolkit(biolink_schema)
    else:
        _bmt_toolkit = Toolkit()

    # The TRAPI version is set to a hard coded
    # default if not reset below by pytest CLI
    set_trapi_version(trapi_version)


def create_one_hop_message(edge, look_up_subject=False):
    """Given a complete edge, create a valid TRAPI message for "one hop" querying for the edge.
    if look_up_subject is False (default) then the object id is not included, (lookup object
    by subject) and if look_up_subject is True, then the subject id is not included (look up
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


def by_subject(request):
    """Given a known triple, create a TRAPI message that looks up the object by the subject"""
    message = create_one_hop_message(request, look_up_subject=False)
    return message, 'object', 'b'


def inverse_by_new_subject(request):
    """Given a known triple, create a TRAPI message that inverts the predicate,
       then looks up the new object by the new subject (original object)"""
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


def by_object(request):
    """Given a known triple, create a TRAPI message that looks up the subject by the object"""
    message = create_one_hop_message(request, look_up_subject=True)
    return message, 'subject', 'a'


def raise_subject_entity(request):
    """
    Given a known triple, create a TRAPI message that uses
    the parent of the original entity and looks up the object
    """
    subject_cat = request['subject_category']
    subject = request['subject']
    parent_subject = ontology_kp.get_parent(subject, subject_cat)
    if parent_subject is None:
        print(f"\nSubject identifier '{subject}[{subject_cat}]') " +
              "is either not an ontology term or does not map onto a parent ontology term.")
        return (None,)*3
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
