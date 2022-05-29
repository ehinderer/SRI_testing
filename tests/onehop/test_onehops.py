"""
One Hops Testing Suite
"""
from os import linesep
from typing import List, Dict

import pytest

from tests.onehop.util import in_excluded_tests
from translator.trapi import check_provenance, execute_trapi_lookup
from tests.onehop import util as oh_util

import logging
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

_edge_error_seen_already: List = list()


def _report_and_skip_edge(test: str, edge: Dict):
    location = edge['location']
    subject_category = edge['subject_category']
    the_subject = edge['subject']
    predicate = edge['predicate']
    object_category = edge['object_category']
    the_object = edge['object']
    label = f"({the_subject}:{subject_category})--[{predicate}]->({the_object}:{object_category})"

    if 'biolink_errors' in edge:
        model_version, errors = edge['biolink_errors']
        pytest.skip(
            f"\nKP TRAPI test case S-P-O triple '{label}') " +
            f"from {location} since it is not Biolink Model compliant " +
            f"with model version {model_version}:{linesep}{linesep.join(errors)}"
        )
    else:
        pytest.skip(
            f"Test explicitly excluded for all test triples from {test} '{location}' or " +
            f"just for this particular test triple: '{label}'"
        )


def test_trapi_kps(kp_trapi_case, trapi_creator, results_bag):
    """Generic Test for TRAPI KPs. The kp_trapi_case fixture is created in conftest.py by looking at the test_triples
    These get successively fed to test_TRAPI.  This function is further parameterized by trapi_creator, which knows
    how to take an input edge and create some kind of TRAPI query from it.  For instance, by_subject removes the object,
    while raise_object_by_subject removes the object and replaces the object category with its biolink parent.
    This approach will need modification if there turn out to be particular elements we want to test for different
    creators.
    """
    if not ('biolink_errors' in kp_trapi_case or in_excluded_tests(test=trapi_creator, test_case=kp_trapi_case)):
        execute_trapi_lookup(kp_trapi_case, trapi_creator, results_bag)
    else:
        _report_and_skip_edge("KP", kp_trapi_case)


@pytest.mark.parametrize(
    "trapi_creator",
    [
        oh_util.by_subject,
        oh_util.by_object,
        oh_util.raise_subject_entity,
        oh_util.raise_object_by_subject,
        oh_util.raise_predicate_by_subject
    ]
)
def test_trapi_aras(ara_trapi_case, trapi_creator, results_bag):
    """Generic Test for ARA TRAPI.  It does the same thing as the KP trapi, calling an ARA that should be pulling
    data from the KP.
    Then it performs a check on the result to make sure that the provenance is correct.
    Currently, that provenance check is a short circuit since ARAs are not reporting this in a standard way yet.
    """
    if not ('biolink_errors' in ara_trapi_case or in_excluded_tests(test=trapi_creator, test_case=ara_trapi_case)):
        response_message = execute_trapi_lookup(ara_trapi_case, trapi_creator, results_bag)
        if response_message is not None:
            check_provenance(ara_trapi_case, response_message)
    else:
        _report_and_skip_edge("ARA", ara_trapi_case)
