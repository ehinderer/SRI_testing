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
                    "kp_api_name": "Test_KP_1",
                    "idx": "2",
                },
                "test_name",
                "test_onehops.py::test_trapi_kps[Test_KP_1#2-test_name] FAILED"
        ),
        (
                {
                    "kp_api_name": "Test_KP_1",
                    "idx": "2",
                },
                None,
                "test_onehops.py::test_trapi_kps[Test_KP_1#2-input] FAILED"
        ),
        (
                {
                    "ara_api_name": "Test_ARA",
                    "kp_api_name": "Test_KP_1",
                    "idx": "2",
                },
                "test_name",
                "test_onehops.py::test_trapi_aras[Test_ARA|Test_KP_1#2-test_name] FAILED"
        ),
        (
                {
                    "ara_api_name": "Test_ARA",
                    "kp_api_name": "Test_KP_1",
                    "idx": "2",
                },
                None,
                "test_onehops.py::test_trapi_aras[Test_ARA|Test_KP_1#2-input] FAILED"
        )
    ]
)
def test_generate_test_error_msg_prefix(query):
    prefix = generate_test_error_msg_prefix(case=query[0], test_name=query[1])
    assert prefix == query[2]
