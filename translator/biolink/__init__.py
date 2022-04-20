import sys
from typing import Optional, Dict, List, Tuple
from functools import lru_cache
from pprint import PrettyPrinter
import re
import logging

from bmt import Toolkit

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

pp = PrettyPrinter(indent=4)

"""
Biolink Model related support code for the tests
"""

# Biolink Release number should be a well-formed Semantic Version
semver_pattern = re.compile(r"^\d+\.\d+\.\d+$")


def get_biolink_model_schema(biolink_release: Optional[str] = None) -> Optional[str]:
    """
    Get Biolink Model Schema
    """
    if biolink_release:
        if not semver_pattern.fullmatch(biolink_release):
            raise TypeError(
                "The 'biolink_release' argument '"
                + biolink_release
                + "' is not a properly formatted 'major.minor.patch' semantic version?"
            )
        schema = f"https://raw.githubusercontent.com/biolink/biolink-model/{biolink_release}/biolink-model.yaml"
        return schema
    else:
        return None


_bmt_toolkit: Optional[Toolkit] = None


# At any given time, only a modest number of Biolink Model versions
# are expected to be active targets for SRI Test validations?
@lru_cache(maxsize=10)
def set_biolink_model_toolkit(biolink_version=None):
    # Note here that we let BMT control which version of Biolink we are using,
    # unless the value for which is overridden on the CLI
    global _bmt_toolkit

    # Toolkit takes a couple of seconds to initialize, so don't want it initialized per-test; however,
    # TODO: if we eventually need per-test settings, maybe we should cache various versions locally
    #       (see https://github.com/biolink/kgx/blob/master/kgx/utils/kgx_utils.py#L304).
    if biolink_version:
        biolink_schema = get_biolink_model_schema(biolink_release=biolink_version)
        _bmt_toolkit = Toolkit(biolink_schema)
    else:
        _bmt_toolkit = Toolkit()


def get_toolkit() -> Optional[Toolkit]:
    global _bmt_toolkit
    if not _bmt_toolkit:
        raise RuntimeError("Biolink Model Toolkit is not initialized?!?")
    return _bmt_toolkit


def check_biolink_model_compliance_of_input_edge(edge: Dict[str, str]) -> Tuple[str, Optional[List[str]]]:
    """
    Validate the input edge contents against the current BMT Biolink Model release.

    :param edge: basic contents of a templated input edge - S-P-O including concept Biolink Model categories

    :returns: 2-tuple of Biolink Model version (str) and List[str] (possibly empty) of error messages
    """
    bmtk: Toolkit = get_toolkit()
    model_version = bmtk.get_model_version()
    #
    # Sample method 'edge' input:
    #
    # {
    #     'subject_category': 'biolink:AnatomicalEntity',
    #     'object_category': 'biolink:AnatomicalEntity',
    #     'predicate': 'biolink:subclass_of',
    #     'subject': 'UBERON:0005453',
    #     'object': 'UBERON:0035769'
    # }

    # data fields to be validated...
    subject_category_curie = edge['subject_category']
    object_category_curie = edge['object_category']
    predicate_curie = edge['predicate']
    subject_curie = edge['subject']
    object_curie = edge['object']

    # Perform various validations
    errors: List[str] = list()

    if bmtk.is_category(subject_category_curie):
        subject_category_name = bmtk.get_element(subject_category_curie).name
    else:
        err_msg = f"Unknown subject category: '{subject_category_curie}'"
        errors.append(err_msg)
        subject_category_name = None

    if bmtk.is_category(object_category_curie):
        object_category_name = bmtk.get_element(object_category_curie).name
    else:
        err_msg = f"Unknown object category: '{object_category_curie}'"
        errors.append(err_msg)
        object_category_name = None

    if not bmtk.is_predicate(predicate_curie):
        err_msg = f"Unknown predicate: '{predicate_curie}'"
        errors.append(err_msg)

    if subject_category_name:
        possible_subject_categories = bmtk.get_element_by_prefix(subject_curie)
        if subject_category_name not in possible_subject_categories:
            err_msg = f"Subject '{subject_curie}' prefix unmapped to '{subject_category_curie}'"
            errors.append(err_msg)

    if object_category_name:
        possible_object_categories = bmtk.get_element_by_prefix(object_curie)
        if object_category_name not in possible_object_categories:
            err_msg = f"Object '{object_curie}' prefix unmapped to '{object_category_curie}'"
            errors.append(err_msg)

    return model_version, errors


# TODO: review and fix issue that a Biolink Model compliance test
#       could run too slowly, if the knowledge graph is very large?
_MAX_TEST_NODES = 1
_MAX_TEST_EDGES = 1


def check_biolink_model_compliance_of_knowledge_graph(graph: Dict) -> Tuple[str, Optional[List[str]]]:
    """
    Validate a TRAPI-schema compliant message knowledge graph
    against the currently active BMT Biolink Model release.

    :param graph: knowledge graph to be validated

    :returns: 2-tuple of Biolink Model version (str) and List[str] (possibly empty) of error messages
    """
    bmtk: Toolkit = get_toolkit()
    model_version = bmtk.get_model_version()

    errors: List[str] = list()

    # Access knowledge graph data fields to be validated... fail early if missing...
    nodes: Optional[Dict] = Optional[Dict]
    if 'nodes' in graph and graph['nodes']:
        nodes = graph['nodes']
    else:
        errors.append("No nodes found in the knowledge graph?")
        nodes = None

    edges: Optional[Dict] = Optional[Dict]
    if 'edges' in graph and graph['edges']:
        edges = graph['edges']
    else:
        errors.append("No edges found in the knowledge graph?")
        edges = None

    # I only do a sampling of node and edge content. This ensures that
    # the tests are performant but may miss errors deeper inside the graph?
    nodes_seen = 0
    if nodes:
        for node_id, details in nodes.items():
            print(f"{node_id}: {str(details)}", flush=True)
            if 'categories' in details:
                if not isinstance(details["categories"], List):
                    errors.append(f"The value of node '{node_id}' categories should be a List?")
                else:
                    categories = details["categories"]
                    node_prefix_mapped: bool = False
                    for category in categories:
                        if bmtk.is_category(category):
                            category_name = bmtk.get_element(category).name
                        elif bmtk.is_mixin(category):
                            # finding mixins in the categories is OK, but we otherwise ignore them in validation
                            print(
                                f"\nInfo: Reported category '{category}' resolves to a Biolink Model 'mixin'?",
                                file=sys.stderr, flush=True
                            )
                            continue
                        else:
                            element = bmtk.get_element(category)
                            if element:
                                # got something here... hopefully just an abstract class
                                # but not a regular category nor mixin, so we ignore it!
                                # TODO: how do we better detect abstract classes from the model?
                                #       How strict should our validation be here?
                                print(
                                    f"\nInfo: Reported category '{category}' " +
                                    "resolves to the (possibly abstract) " +
                                    f"Biolink Model element '{element.name}'?",
                                    file=sys.stderr, flush=True
                                )
                                continue

                            # Something truly unrecognized?
                            err_msg = f"'{category}' for node '{node_id}' is not a recognized Biolink Model category?"
                            errors.append(err_msg)
                            category_name = None

                        if category_name:
                            possible_subject_categories = bmtk.get_element_by_prefix(node_id)
                            if category_name in possible_subject_categories:
                                node_prefix_mapped = True
                    if not node_prefix_mapped:
                        err_msg = f"For all node categories [{','.join(categories)}] of " +\
                                  f"'{node_id}', the CURIE prefix namespace remains unmapped?"
                        errors.append(err_msg)
            else:
                errors.append(f"Node '{node_id}' is missing its 'categories'?")

            # TODO: Do we need to (or can we) validate other node fields here? Perhaps not?

            nodes_seen += 1
            if nodes_seen >= _MAX_TEST_NODES:
                break

    edges_seen = 0
    if edges:
        for edge in edges.values():

            print(f"{str(edge)}", flush=True)

            # edge data fields to be validated...
            subject_id = edge['subject'] if 'subject' in edge else None
            predicate = edge['predicate'] if 'predicate' in edge else None
            object_id = edge['object'] if 'object' in edge else None
            attributes = edge['attributes'] if 'attributes' in edge else None

            edge_id = f"{str(subject_id)}--{str(predicate)}->{str(object_id)}"

            if not subject_id:
                errors.append(f"Edge '{edge_id}' has a missing or empty subject slot?")
            elif subject_id not in nodes.keys():
                errors.append(f"Edge subject id '{subject_id}' is missing from the nodes catalog?")

            if not predicate:
                errors.append(f"Edge '{edge_id}' has a missing or empty predicate slot?")
            elif not bmtk.is_predicate(predicate):
                errors.append(f"'{predicate}' is an unknown Biolink Model predicate")

            if not object_id:
                errors.append(f"Edge '{edge_id}' has a missing or empty predicate slot?")
            elif object_id not in nodes.keys():
                errors.append(f"Edge object id '{object_id}' is missing from the nodes catalog?")

            # TODO: not quite sure whether and how to fully validate the 'attributes' of an edge
            # For now, we simply assume that *all* edges must have *some* attributes
            # (at least, provenance related, but we don't explicitly test for them)
            if not attributes:
                errors.append(f"Edge '{edge_id}' has a missing or empty attributes?")

            edges_seen += 1
            if edges_seen >= _MAX_TEST_EDGES:
                break

    return model_version, errors
