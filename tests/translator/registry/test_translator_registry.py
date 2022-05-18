"""
Unit tests for Translator SmartAPI Registry
"""
from typing import Optional, Tuple, Dict
import logging
import pytest

from translator.registry import (
    query_smart_api,
    SMARTAPI_QUERY_PARAMETERS,
    extract_kp_test_data_metadata_from_registry, tag_value, extract_ara_test_data_metadata_from_registry,
    get_translator_kp_test_data_metadata, get_translator_ara_test_data_metadata
)

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_default_empty_query():
    registry_data = query_smart_api()
    assert len(registry_data) > 0, "Default query failed"


_QUERY_SMART_API_EXCEPTION_PREFIX = "Translator SmartAPI Registry Access Exception cannot be accessed:"


def test_fake_url():
    registry_data: Dict = query_smart_api(url="fake url")
    assert registry_data and "Error" in registry_data, "Missing error message?"
    assert registry_data["Error"].startswith(_QUERY_SMART_API_EXCEPTION_PREFIX), "Unexpected error message?"


def test_trapi_entry_retrievals():
    registry_data = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    assert "total" in registry_data, f"\tMissing 'total' tag in results?"
    assert registry_data["total"] > 0, f"\tZero 'total' in results?"
    assert "hits" in registry_data, f"\tMissing 'hits' tag in results?"
    for index, service in enumerate(registry_data['hits']):
        if "info" not in service:
            logger.debug(f"\tMissing 'hits' tag in hit entry? Ignoring entry...")
            continue
        info = service["info"]
        if "title" not in info:
            logger.debug(f"\tMissing 'title' tag in 'hit.info'? Ignoring entry...")
            continue
        title = info["title"]
        logger.debug(f"\n{index} - '{title}':")
        if "x-translator" not in info:
            logger.debug(f"\tMissing 'x-translator' tag in 'hit.info'? Ignoring entry...")
            continue
        x_translator = info["x-translator"]
        if "component" not in x_translator:
            logger.debug(f"\tMissing 'component' tag in 'hit.info.x-translator'? Ignoring entry...")
            continue
        component = x_translator["component"]
        if "x-trapi" not in info:
            logger.debug(f"\tMissing 'x-trapi' tag in 'hit.info'? Ignoring entry...")
            continue
        x_trapi = info["x-trapi"]

        if component == "KP":
            if "test_data_location" not in x_trapi:
                logger.debug(f"\tMissing 'test_data_location' tag in 'hit.info.x-trapi'? Ignoring entry...")
                continue
            else:
                test_data_location = x_trapi["test_data_location"]
                logger.debug(f"\t'hit.info.x-trapi.test_data_location': '{test_data_location}'")
        else:
            logger.debug(f"\tIs an ARA?")


def test_test_data_location_retrievals():
    registry_data: Dict = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    service_metadata: Dict[str, Dict[str,  Optional[str]]] = extract_kp_test_data_metadata_from_registry(registry_data)
    assert len(service_metadata) > 0, "No Test Data found?"


def test_empty_json_data():
    value = tag_value({}, "testing.one.two.three")
    assert not value


_TEST_JSON_DATA = {
        "testing": {
            "one": {
                "two": {
                    "three": "The End!"
                },

                "another_one": "for_fun"
            }
        }
    }


def test_valid_tag_path():
    value = tag_value(_TEST_JSON_DATA, "testing.one.two.three")
    assert value == "The End!"


def test_empty_tag_path():
    value = tag_value(_TEST_JSON_DATA, "")
    assert not value


def test_missing_intermediate_tag_path():
    value = tag_value(_TEST_JSON_DATA, "testing.one.four.five")
    assert not value


def test_missing_end_tag_path():
    value = tag_value(_TEST_JSON_DATA, "testing.one.two.three.four")
    assert not value


def assert_tag(metadata: Dict, infores: str, tag: str):
    assert tag in metadata[infores], f"Missing tag {tag} in service metadata"


def shared_test_extract_component_test_data_metadata_from_registry(
        query: Tuple[Dict, str, str],
        component_type: str,
        method
):
    assert component_type in ["KP", "ARA"]
    service_metadata: Dict[str, Dict[str,  Optional[str]]] = method(query[0])
    if not query[1]:
        assert len(service_metadata) == 0, f"Expecting empty {component_type} service metadata"
    else:
        assert service_metadata, f"Expecting a non-empty {component_type} service metadata result?"

        logger.debug(f"{component_type} Service Metadata: {service_metadata}")

        assert query[1] in service_metadata, \
            f"Missing infores '{query[1]}' expected in {component_type} '{service_metadata}' dictionary?"

        assert_tag(service_metadata, query[1], "service_title")
        assert_tag(service_metadata, query[1], "service_version")
        assert_tag(service_metadata, query[1], "component")
        assert_tag(service_metadata, query[1], "biolink_version")
        assert_tag(service_metadata, query[1], "trapi_version")
        assert_tag(service_metadata, query[1], "test_data_location")

        assert service_metadata[query[1]]["test_data_location"] == query[2], \
            f"Missing  {component_type} test_data_location '{query[2]}'  to be returned for infores '{query[1]}'"


# extract_kp_test_data_metadata_from_registry(registry_data) -> Dict[str, str]
@pytest.mark.parametrize(
    "query",
    [
        (  # Query 0 - Valid 'hits' entry with non-empty 'info.x-trapi.test_data_location'
                {
                    "hits": [
                        {
                            "info": {
                                "title": "Some KP",
                                "version": "0.0.1",
                                "x-translator": {
                                    "component": "KP",
                                    "infores": "infores:some-kp"
                                },
                                "x-trapi": {
                                    "test_data_location": "http://some-kp-web-test-data-directory"
                                }
                            }
                        }
                    ]
                },
                "infores:some-kp",
                "http://some-kp-web-test-data-directory"
        ),
        (   # Query 1 - Empty "hits" List
            {
                "hits": []
            },
            None,
            None
        ),
        (   # Query 2 - Empty "hits" entry
            {
                "hits": [{}]
            },
            None,
            None
        ),
        (   # Query 3 - "hits" entry with missing 'component' (and 'infores')
            {
                "hits": [
                    {
                        "info": {
                        }
                    }
                ]
            },
            None,
            None
        ),
        (   # Query 4 - "hits" ARA component entry
            {
                "hits": [
                    {
                        "info": {
                            "x-translator": {
                                "infores": "infores:some-ara",
                                "component": "ARA"
                            }
                        }
                    }
                ]
            },
            None,
            None
        ),
        (   # Query 5 - "hits" KP component entry with missing 'infores'
            {
                "hits": [
                    {
                        "info": {
                            "x-translator": {
                                "infores": "infores:some-kp"
                            }
                        }
                    }
                ]
            },
            None,
            None
        ),
        (   # Query 6 - "hits" KP component entry with missing 'info.x-trapi'
            {
                "hits": [
                    {
                        "info": {
                            "x-translator": {
                                "infores": "infores:some-kp",
                                "component": "KP"
                            }
                        }
                    }
                ]
            },
            "infores:some-kp",
            None
        ),
        (   # Query 7 - "hits" KP component entry with missing 'info.x-trapi.test_data_location' tag value
            {
                "hits": [
                    {
                        "info": {
                            "title": "KP component entry with missing 'info.x-trapi.test_data_location",
                            "x-translator": {
                                "infores": "infores:some-kp",
                                "component": "KP"
                            },
                            "x-trapi": {

                            }
                        }
                    }
                ]
            },
            "infores:some-kp",
            None
        )
    ]
)
def test_extract_kp_test_data_metadata_from_registry(query: Tuple[Dict, str, str]):
    shared_test_extract_component_test_data_metadata_from_registry(
        query, "KP",
        extract_kp_test_data_metadata_from_registry
    )


# extract_kp_test_data_metadata_from_registry(registry_data) -> Dict[str, str]
@pytest.mark.parametrize(
    "query",
    [
        (  # Query 0 - Valid 'hits' ARA entry with non-empty 'info.x-trapi.test_data_location'
                {
                    "hits": [
                        {
                            "info": {
                                "title": "Some ARA",
                                "version": "0.0.1",
                                "x-translator": {
                                    "infores": "infores:some-ara",
                                    "component": "ARA",
                                    "team": "some-translator-team",
                                    "biolink-version": "2.2.16"
                                },
                                "x-trapi": {
                                    "version": "1.2.0",
                                    "test_data_location": "http://some-ara-web-test-data-directory"
                                }
                            }
                        }
                    ]
                },
                "infores:some-ara",
                "http://some-ara-web-test-data-directory"
        )
    ]
)
def test_extract_ara_test_data_metadata_from_registry(query: Tuple[Dict, str, str]):
    shared_test_extract_component_test_data_metadata_from_registry(
        query, "ARA",
        extract_ara_test_data_metadata_from_registry
    )


def test_get_translator_kp_test_data_metadata():
    service_metadata = get_translator_kp_test_data_metadata()
    assert any([value for value in service_metadata.values()]), \
        "No 'KP' service metadata found in Translator SmartAPI Registry?"


def test_get_translator_ara_test_data_metadata():
    service_metadata = get_translator_ara_test_data_metadata()
    assert any([value for value in service_metadata.values()]),\
        "No 'ARA' service metadata found in Translator SmartAPI Registry?"
