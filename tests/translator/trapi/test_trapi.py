"""
Unit tests for the generic (shared) components of the TRAPI testing utilities
"""
import logging
from typing import Optional, Dict, Tuple

import pytest

from translator.trapi import set_trapi_version, get_trapi_version, check_provenance

logger = logging.getLogger(__name__)


def test_set_default_global_environment():
    set_trapi_version()
    trapi_version: Optional[str] = get_trapi_version()
    assert trapi_version
    assert trapi_version.startswith("1.2")


def test_set_specific_global_environment():
    set_trapi_version("1.1")
    trapi_version: Optional[str] = get_trapi_version()
    assert trapi_version
    assert trapi_version.startswith("1.1")


TEST_ARA_CASE_TEMPLATE = {
    "url": "http://test_ara_endpoint",
    "ara_infores": "test_ara",  # value should be specified without the 'infores' prefix, in the ARA case template
    "kp_source": "Test KP",
    "kp_source_type": "original",
    "kp_infores": "test_kp"  # value should be specified without the 'infores' prefix, in the ARA case template
}


def get_ara_test_case(changes: Optional[Dict[str, str]] = None):
    test_case = TEST_ARA_CASE_TEMPLATE.copy()
    if changes:
        test_case.update(changes)
    return test_case


# check_provenance(ara_case, ara_response), triggers AssertError exceptions
@pytest.mark.parametrize(
    "query",
    [
        # (
        #         "mock_ara_case",
        #         "mock_ara_response",  # mock data has dumb edges: don't worry about the S-P-O, just the attributes
        #         "AssertError_message"
        # ),   # set 3rd argument to AssertError message if test edge should 'fail'; otherwise, empty string (for pass)
        (
            # Query 0. No attributes key
            get_ara_test_case(),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                    }
                },
            },
            "Knowledge graph has no edges?"
        ),
        (
            # Query 1. No attributes key
            get_ara_test_case(),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {}
                    }
                },
            },
            "has no 'attributes' key?"
        ),

        (
            # Query 2. No attributes key
            get_ara_test_case(),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {
                            "attributes": {}
                        }
                    }
                },
            },
            "has no attributes?"
        ),
        (
            # Query 3. missing ARA knowledge source provenance
            get_ara_test_case(),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {
                            "attributes": [
                                {
                                    "attribute_type_id": "",  # could be set to anything ... blank is equivalent
                                    "value": ""  # don't care...
                                },
                            ]
                        }
                    }
                }
            },
            "missing ARA knowledge source provenance?"
        ),
        (
                # Query 4. value is an empty list?
                get_ara_test_case(),
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                            "edge_1": {
                                "attributes": [
                                    {
                                        "attribute_type_id": "biolink:aggregator_knowledge_source",
                                        "value": []
                                    },
                                ]
                            }
                        }
                    }
                },
                "value is an empty list?"
        ),
        (
                # Query 5. value has an unrecognized data type for a provenance attribute?
                get_ara_test_case(),
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                            "edge_1": {
                                "attributes": [
                                    {
                                        "attribute_type_id": "biolink:aggregator_knowledge_source",
                                        "value": 1234
                                    },
                                ]
                            }
                        }
                    }
                },
                "value has an unrecognized data type for a provenance attribute?"
        ),
        (
            # Query 6. KP provenance value is not a well-formed InfoRes CURIE? Should fail?
            get_ara_test_case(),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {
                            "attributes": [
                                {
                                    "attribute_type_id": "biolink:aggregator_knowledge_source",
                                    "value": "infores:test_ara"
                                },
                                {
                                    "attribute_type_id": "biolink:original_knowledge_source",
                                    "value": "not_an_infores"
                                }
                            ]
                        }
                    }
                }
            },
            "is not a well-formed InfoRes CURIE?"
        ),
        (
                # Query 7. KP provenance value is not a well-formed InfoRes CURIE? Should fail?
                get_ara_test_case(),
                {  # ara_response
                    "knowledge_graph": {
                        "edges": {
                            "edge_1": {
                                "attributes": [
                                    {
                                        "attribute_type_id": "biolink:aggregator_knowledge_source",
                                        "value": "infores:test_ara"
                                    }
                                ]
                            }
                        }
                    }
                },
                "is missing as expected knowledge source provenance?"
        ),
        (
            # Query 8. kp type is 'original'. Should pass?
            get_ara_test_case(),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {
                            "attributes": [
                                {
                                    "attribute_type_id": "biolink:aggregator_knowledge_source",
                                    "value": "infores:test_ara"
                                },
                                {
                                    "attribute_type_id": "biolink:original_knowledge_source",
                                    "value": "infores:test_kp"
                                }
                            ]
                        }
                    }
                }
            },
            ""
        ),
        (
            # Query 9. Should pass?
            get_ara_test_case({"kp_source_type": "aggregator"}),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {
                            "attributes": [
                                {
                                    "attribute_type_id": "biolink:aggregator_knowledge_source",
                                    "value": "infores:test_ara"
                                },
                                {
                                    "attribute_type_id": "biolink:aggregator_knowledge_source",
                                    "value": "infores:test_kp"
                                }
                            ]

                        }
                    }
                }
            },
            "has neither 'primary' nor 'original' Knowledge Provider knowledge source provenance?"
        ),
        (
            # Query 10. Is complete and should pass?
            get_ara_test_case({"kp_source_type": "aggregator"}),
            {  # ara_response
                "knowledge_graph": {
                    "edges": {
                        "edge_1": {
                            "attributes": [
                                {
                                    "attribute_type_id": "biolink:aggregator_knowledge_source",
                                    "value": "infores:test_ara"
                                },
                                {
                                    "attribute_type_id": "biolink:aggregator_knowledge_source",
                                    "value": "infores:test_kp"
                                },
                                {
                                    "attribute_type_id": "biolink:primary_knowledge_source",
                                    "value": "infores:my_primary_ks"
                                }
                            ]
                        }
                    }
                }
            },
            ""
        )
    ]
)
def test_check_provenance(query: Tuple):
    try:
        check_provenance(query[0], query[1])
    except AssertionError as ae:
        assert query[2], "check_provenance() should pass!"
        assert str(ae).endswith(query[2]), "unexpected assertion error?"
        return

    assert not query[2], f"check_provenance() should fail with assertion error: '{query[2]}'"
