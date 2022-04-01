"""
One Hops Testing Suite
"""
import logging

import pytest

from translator.trapi import check_provenance, execute_trapi_lookup
from tests.onehop import util as oh_util

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_trapi_kps(kp_trapi_case, trapi_creator, results_bag):
    """Generic Test for TRAPI KPs. The kp_trapi_case fixture is created in conftest.py by looking at the test_triples
    These get successively fed to test_TRAPI.  This function is further parameterized by trapi_creator, which knows
    how to take an input edge and create some kind of TRAPI query from it.  For instance, by_subject removes the object,
    while raise_object_by_subject removes the object and replaces the object category with its biolink parent.
    This approach will need modification if there turn out to be particular elements we want to test for different
    creators.
    """
    execute_trapi_lookup(kp_trapi_case, trapi_creator, results_bag)


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
    response_message = execute_trapi_lookup(ara_trapi_case, trapi_creator, results_bag)
    if response_message is not None:
        check_provenance(ara_trapi_case, response_message)
