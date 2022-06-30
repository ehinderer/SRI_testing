"""
Unit tests for the generic (shared) components of the TRAPI testing utilities
"""
import logging
from typing import Optional, Dict, Tuple

import pytest

from translator.trapi import set_trapi_version, get_trapi_version, check_provenance, generate_test_error_msg_prefix, \
    TestReport

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


TEST_ARA_CASE_TEMPLATE = {
    "idx" : 0,
    "url": "http://test_ara_endpoint",
    "ara_api_name": "test_ARA",
    "ara_source": "infores:test_ara",
    "kp_api_name": "Test_KP_1",
    "kp_source": "infores:panther",
    "kp_source_type": "original"
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
                "knowledge graph has no edges?"
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
                                        "value": "infores:panther"
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
                                        "value": "infores:panther"
                                    }
                                ]

                            }
                        }
                    }
                },
                "has neither 'primary' nor 'original' knowledge source?"
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
                                        "value": "infores:panther"
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
        errors = list()
        test_report = TestReport(errors)
        check_provenance(query[0], query[1], test_report)
    except AssertionError as ae:
        assert query[2], "check_provenance() should pass!"
        assert str(ae).endswith(query[2]), "unexpected assertion error?"
        return

    assert not query[2], f"check_provenance() should fail with assertion error: '{query[2]}'"
