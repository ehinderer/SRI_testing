"""
Unit tests for the generic (shared) components of the TRAPI testing utilities
"""
import logging

import pytest

from translator.trapi import generate_test_error_msg_prefix

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "query",
    [
        (
                {
                    "kp_source": "infores:test-kp-1",
                    "idx": "2",
                },
                "test_name",
                "test_onehops.py::test_trapi_kps[test-kp-1#2-test_name] FAILED"
        ),
        (
                {
                    "kp_source": "infores:test-kp-1",
                    "idx": "2",
                },
                None,
                "test_onehops.py::test_trapi_kps[test-kp-1#2-input] FAILED"
        ),
        (
                {
                    "ara_source": "infores:test-ara",
                    "kp_source": "infores:test-kp-1",
                    "idx": "2",
                },
                "test_name",
                "test_onehops.py::test_trapi_aras[test-ara|test-kp-1#2-test_name] FAILED"
        ),
        (
                {
                    "ara_source": "infores:test-ara",
                    "kp_source": "infores:test-kp-1",
                    "idx": "2",
                },
                None,
                "test_onehops.py::test_trapi_aras[test-ara|test-kp-1#2-input] FAILED"
        )
    ]
)
def test_generate_test_error_msg_prefix(query):
    prefix = generate_test_error_msg_prefix(case=query[0], test_name=query[1])
    assert prefix == query[2]
