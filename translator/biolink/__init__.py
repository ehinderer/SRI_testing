from typing import Optional, Dict, List, Tuple
from functools import lru_cache

import re
import logging

from bmt import Toolkit

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

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
def check_biolink_model_compliance_of_knowledge_graph(kg):
    """
    Validate a TRAPI-schema compliant message knowledge graph
    against the currently active BMT Biolink Model release.

    :param kg: knowledge graph to be validated

    :returns: 2-tuple of Biolink Model version (str) and List[str] (possibly empty) of error messages
    """
    bmtk: Toolkit = get_toolkit()
    model_version = bmtk.get_model_version()

    # data fields to be validated...
    # subject_category_curie = edge['subject_category']
    # object_category_curie = edge['object_category']
    # predicate_curie = edge['predicate']
    # subject_curie = edge['subject']
    # object_curie = edge['object']

    # Perform various validations
    errors: List[str] = list()

    # TODO: attempt the validation here...

    return model_version, errors
