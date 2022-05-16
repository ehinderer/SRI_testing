"""
Unit tests for Translator SmartAPI Registry
"""
from typing import Tuple, Dict
from sys import stderr
import logging
import pytest

from translator.registry import (
    query_smart_api,
    SMARTAPI_QUERY_PARAMETERS,
    extract_kp_test_data_locations_from_registry, tag_value, extract_ara_test_data_locations_from_registry,
    get_translator_kp_test_data_locations, get_translator_ara_test_data_locations
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
            print(
                f"\tMissing 'hits' tag in hit entry? Ignoring entry...",
                flush=True, file=stderr
            )
            continue
        info = service["info"]
        if "title" not in info:
            print(
                f"\tMissing 'title' tag in 'hit.info'? Ignoring entry...",
                flush=True, file=stderr
            )
            continue
        title = info["title"]
        print(
            f"\n{index} - '{title}':",
            flush=True, file=stderr
        )
        if "x-translator" not in info:
            print(
                f"\tMissing 'x-translator' tag in 'hit.info'? Ignoring entry...",
                flush=True, file=stderr
            )
            continue
        x_translator = info["x-translator"]
        if "component" not in x_translator:
            print(
                f"\tMissing 'component' tag in 'hit.info.x-translator'? Ignoring entry...",
                flush=True, file=stderr
            )
            continue
        component = x_translator["component"]
        if "x-trapi" not in info:
            print(
                f"\tMissing 'x-trapi' tag in 'hit.info'? Ignoring entry...",
                flush=True, file=stderr
            )
            continue
        x_trapi = info["x-trapi"]

        if component == "KP":
            if "test_data_location" not in x_trapi:
                print(
                    f"\tMissing 'test_data_location' tag in 'hit.info.x-trapi'? Ignoring entry...",
                    flush=True, file=stderr
                )
                continue
            else:
                test_data_location = x_trapi["test_data_location"]
                print(
                    f"\t'hit.info.x-trapi.test_data_location': '{test_data_location}'",
                    flush=True, file=stderr
                )
        else:
            print(
                f"\tIs an ARA?",
                flush=True, file=stderr
            )


def test_test_data_location_retrievals():
    registry_data: Dict = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    test_data_locations: Dict[str, str] = extract_kp_test_data_locations_from_registry(registry_data)
    assert len(test_data_locations) > 0, "No Test Data found?"


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


def template_test_extract_component_test_data_locations_from_registry(
        query: Tuple[Dict, str, str],
        component_type: str,
        method
):
    assert component_type in ["KP", "ARA"]
    test_data_locations: Dict[str, str] = method(query[0])
    if not query[1]:
        assert len(test_data_locations) == 0, f"Expecting empty {component_type} 'test_data_locations'"
    else:
        assert test_data_locations, f"Expecting non-empty {component_type} 'test_data_locations'"
        assert query[1] in test_data_locations, \
            f"Expected infores '{query[1]}' missing in {component_type} '{test_data_locations}' dictionary?"
        assert test_data_locations[query[1]] == query[2], \
            f"Expected  {component_type} test_data_location '{query[2]}'  to be returned for infores '{query[1]}'"

        print(f"{component_type} Test Data Locations: ", test_data_locations, flush=True, file=stderr)


# extract_kp_test_data_locations_from_registry(registry_data) -> Dict[str, str]
@pytest.mark.parametrize(
    "query",
    [
        (  # Query 0 - Valid 'hits' entry with non-empty 'info.x-trapi.test_data_location'
                {
                    "hits": [
                        {
                            "info": {
                                "x-translator": {
                                    "component": "KP",
                                    "infores": "infores:kp"
                                },
                                "x-trapi": {
                                    "test_data_location": "http://kp-web-test-data-directory"
                                }
                            }
                        }
                    ]
                },
                "infores:kp",
                "http://kp-web-test-data-directory"
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
                                "component": "ARA",
                                "infores": "infores:ara"
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
                                "component": "KP"
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
                                "component": "KP",
                                "infores": "infores:kp"
                            }
                        }
                    }
                ]
            },
            "infores:kp",
            None
        ),
        (   # Query 7 - "hits" KP component entry with missing 'info.x-trapi.test_data_location' tag value
            {
                "hits": [
                    {
                        "info": {
                            "title": "KP component entry with missing 'info.x-trapi.test_data_location",
                            "x-translator": {
                                "component": "KP",
                                "infores": "infores:kp"
                            },
                            "x-trapi": {

                            }
                        }
                    }
                ]
            },
            "infores:kp",
            None
        )
    ]
)
def test_extract_kp_test_data_locations_from_registry(query: Tuple[Dict, str, str]):
    template_test_extract_component_test_data_locations_from_registry(
        query, "KP",
        extract_kp_test_data_locations_from_registry
    )


# extract_kp_test_data_locations_from_registry(registry_data) -> Dict[str, str]
@pytest.mark.parametrize(
    "query",
    [
        (  # Query 0 - Valid 'hits' entry with non-empty 'info.x-trapi.test_data_location'
                {
                    "hits": [
                        {
                            "info": {
                                "x-translator": {
                                    "component": "ARA",
                                    "infores": "infores:kp"
                                },
                                "x-trapi": {
                                    "test_data_location": "http://ara-web-test-data-directory"
                                }
                            }
                        }
                    ]
                },
                "infores:kp",
                "http://ara-web-test-data-directory"
        )
    ]
)
def test_extract_ara_test_data_locations_from_registry(query: Tuple[Dict, str, str]):
    template_test_extract_component_test_data_locations_from_registry(
        query, "ARA",
        extract_ara_test_data_locations_from_registry
    )


def test_get_translator_kp_test_data_locations():
    test_data_locations = get_translator_kp_test_data_locations()
    assert any([value for value in test_data_locations.values()]), \
        "No 'KP' test_data_locations found in Translator SmartAPI Registry?"


def test_get_translator_ara_test_data_locations():
    test_data_locations = get_translator_ara_test_data_locations()
    assert any([value for value in test_data_locations.values()]),\
        "No 'ARA' test_data_locations found in Translator SmartAPI Registry?"
