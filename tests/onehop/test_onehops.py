"""
One Hops Testing Suite

Existing KP Unit Tests (defined in onehop.util module):

- by_subject
- inverse_by_new_subject
- by_object
- raise_subject_entity
- raise_object_by_subject
- raise_predicate_by_subject

"""
from typing import List, Dict

import pytest

from tests.onehop.util import in_excluded_tests
from translator.trapi import execute_trapi_lookup, TestReport
from tests.onehop import util as oh_util

import logging
logger = logging.getLogger(__name__)

_edge_error_seen_already: List = list()


def _report_and_skip_edge(scope: str, test, test_case: Dict, test_report: TestReport):
    """

    :param scope: str, 'KP" or 'ARA'
    :param test: the particular unit test being skipped
    :param test_case: input edge data unit test case
    :param test_report: TestReport wrapper for reporting test status
    :raises: pytest.skip with an informative message
    """

    # resource_id = test_case[f"{scope.lower()}_api_name"]

    try:
        test_name = test.__name__
    except AttributeError:
        raise RuntimeError(f"_report_and_skip_edge(): invalid 'test' parameter: '{str(test)}'")

    # edge_i = test_case["idx"]

    subject_category = test_case['subject_category']
    subject_id = test_case['subject']
    predicate = test_case['predicate']
    object_category = test_case['object_category']
    object_id = test_case['object']
    label = f"({subject_id}${subject_category})--[{predicate}]->({object_id}${object_category})"

    if 'biolink_errors' in test_case:
        model_version, errors = test_case['biolink_errors']
        test_report.skip(
            f"test case S-P-O triple '{label}', since it is not "
            f"Biolink Model compliant: {' and '.join(errors)}"
        )
    else:
        test_report.skip(
            f"test case S-P-O triple '{label}' or all test case S-P-O triples from resource test location."
        )


def test_trapi_kps(kp_trapi_case, trapi_creator, results_bag):
    """Generic Test for TRAPI KPs. The kp_trapi_case fixture is created in conftest.py by looking at the test_triples
    These get successively fed to test_TRAPI.  This function is further parameterized by trapi_creator, which knows
    how to take an input edge and create some kind of TRAPI query from it.  For instance, by_subject removes the object,
    while raise_object_by_subject removes the object and replaces the object category with its biolink parent.
    This approach will need modification if there turn out to be particular elements we want to test for different
    creators.
    """
    results_bag.location = kp_trapi_case['kp_test_data_location']
    results_bag.case = kp_trapi_case
    results_bag.errors = list()

    test_report = TestReport(
        test_case=kp_trapi_case,
        test_name=trapi_creator.__name__,
        errors=results_bag.errors
    )

    if not ('biolink_errors' in kp_trapi_case or in_excluded_tests(test=trapi_creator, test_case=kp_trapi_case)):
        execute_trapi_lookup(case=kp_trapi_case, creator=trapi_creator, rbag=results_bag, test_report=test_report)
        test_report.assert_test_outcome()
    else:
        _report_and_skip_edge("KP", test=trapi_creator, test_case=kp_trapi_case, test_report=test_report)


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
    """Generic Test for ARA TRAPI.  It does the same thing as the KP TRAPI, calling an ARA that should be pulling
    data from the KP.
    Then it performs a check on the result to make sure that the provenance is correct.
    """
    results_bag.location = ara_trapi_case['ara_test_data_location']
    results_bag.case = ara_trapi_case
    results_bag.errors = list()

    test_report = TestReport(
        test_case=ara_trapi_case,
        test_name=trapi_creator.__name__,
        errors=results_bag.errors
    )

    if not ('biolink_errors' in ara_trapi_case or in_excluded_tests(test=trapi_creator, test_case=ara_trapi_case)):
        execute_trapi_lookup(
            case=ara_trapi_case,
            creator=trapi_creator,
            rbag=results_bag,
            test_report=test_report,
            validate_provenance=True
        )
        test_report.assert_test_outcome()
    else:
        _report_and_skip_edge("ARA", test=trapi_creator, test_case=ara_trapi_case, test_report=test_report)
