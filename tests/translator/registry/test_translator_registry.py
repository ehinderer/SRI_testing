"""
Unit tests for Translator SmartAPI Registry
"""
from typing import List
from sys import stderr
import logging

from translator.registry import query_smart_api, SMARTAPI_QUERY_PARAMETERS, iterate_test_data_from_registry

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def test_default_empty_query():
    registry_data = query_smart_api()
    assert len(registry_data) > 0, "Default query failed"


def test_fake_url():
    registry_data = query_smart_api(url="fake url")
    assert registry_data and registry_data.startswith("Invalid URL"), "Didn't get expected request exception?"


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
    registry_data = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    test_data_locations: List[str] = iterate_test_data_from_registry(registry_data)
    assert len(test_data_locations) > 0, "No Test Data found?"

