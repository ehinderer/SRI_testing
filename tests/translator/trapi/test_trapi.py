"""
Unit tests for the generic (shared) components of the TRAPI testing utilities
"""
import logging
from typing import Optional

import pytest

from translator.sri.testing import set_global_environment
from translator.trapi import get_trapi_version, check_provenance

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_set_default_global_environment():
    set_global_environment()
    trapi_version: Optional[str] = get_trapi_version()
    assert trapi_version
    assert trapi_version.startswith("1.2")


def test_set_specific_trapi_versioned_global_environment():
    set_global_environment()
    trapi_version: Optional[str] = get_trapi_version()
    assert trapi_version
    assert trapi_version.startswith("1.2")


TEST_ARA_CASE = {
    "url": "http://test_ara_endpoint",
    "ara_infores": "infores:test_ara",
    "kp_source": "Test KP",
    "kp_source_type": "original",
    "kp_infores": "infores:test_kp"
}


# check_provenance(ara_case, ara_response), triggers AssertError exceptions
@pytest.mark.parametrize(
    "query",
    [
        # (
        #         "mock_ara_case",
        #         "mock_ara_response",
        #         (True|False)
        # ),   # set 3rd argument to 'True' if the check_provenance should pass; 'False' if it should fail
        (
                # No attributes key
                TEST_ARA_CASE,
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                        }
                    },
                },
                "edge missing 'attributes' key"
        ),
        (
                # No attributes key
                TEST_ARA_CASE,
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                            "attributes": {}
                        }
                    },
                },
                "edge has no 'attributes'"
        ),
        (
                TEST_ARA_CASE,
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                            "attributes": {
                                "attribute_1": {
                                    "attribute_type_id": "",
                                    "value": ""
                                },
                                "attribute_2": {
                                    "attribute_type_id": "",
                                    "value": ""
                                },
                                "attribute_3": {
                                    "attribute_type_id": "",
                                    "value": ""
                                },
                            }
                        }
                    },
                },
                "invalid attributes"
        ),

        (
                TEST_ARA_CASE,
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                            "attributes": {
                                "attribute_1": {
                                    "attribute_type_id": "",
                                    "value": ""
                                },
                                "attribute_2": {
                                    "attribute_type_id": "",
                                    "value": ""
                                },
                                "attribute_3": {
                                    "attribute_type_id": "",
                                    "value": ""
                                },
                            }
                        }
                    },
                },
                "invalid attributes"
        ),
    ]
)
def test_check_provenance(query):
    try:
        check_provenance(query[0], query[1])

    except AssertionError as ae:
        assert len(query[2]) != 0, "check_provenance() should pass!"
        assert str(ae) == query[2], "unexpected assertion error?"
        return

    assert len(query[2]) == 0, f"check_provenance() should fail with assertion error: '{query[2]}'"
