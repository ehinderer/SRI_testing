"""
Translator SmartAPI Registry access module.
"""
from typing import Optional, List, Dict
from datetime import datetime

import requests
import yaml

from requests.exceptions import RequestException

import logging
logger = logging.getLogger(__name__)


# As of May 18th, 2022, the Translator SmartAPI Registry doesn't yet
# have any test_data_locations for KPs and ARAs, so we'll start by
# simulating this for now, with mock registry metadata
# (and test data in the SRI Testing project repository)
_MOCK_REGISTRY: bool = True
_MOCK_TRANSLATOR_SMARTAPI_REGISTRY_METADATA = {
    "total": 3,
    "hits": [
        {
            "info": {
                "title": "Unit Test Knowledge Provider 1",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:panther",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_1.json"
                }
            }
        },
        {
            "info": {
                "title": "Unit Test Knowledge Provider 2",
                "version": "0.0.1",
                "x-translator": {
                    "component": "KP",
                    "infores": "infores:ontological-hierarchy",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/KP/Unit_Test_KP/Test_KP_2.json"
                }
            }
        },
        {
            "info": {
                "title": "Unit Test Automatic Relay Agent",
                "version": "0.0.1",
                "x-translator": {
                    "infores": "infores:aragorn",
                    "component": "ARA",
                    "team": "Ranking Agent",
                    "biolink-version": "2.2.16"
                },
                "x-trapi": {
                    "version": "1.2.0",
                    "test_data_location": "https://raw.githubusercontent.com/TranslatorSRI/SRI_testing/main/" +
                                          "tests/onehop/test_triples/ARA/Unit_Test_ARA/Test_ARA.json"
                }
            }
        }
    ]

}

SMARTAPI_URL = "https://smart-api.info/api/"
SMARTAPI_QUERY_PARAMETERS = "q=__all__&tags=%22trapi%22&" + \
                            "fields=info,_meta,_status,paths,tags,openapi,swagger&size=1000&from=0"


def set_timestamp():
    dtnow = datetime.now()
    # getting the timestamp
    ts = datetime.timestamp(dtnow)
    # convert to datetime
    dt = str(datetime.fromtimestamp(ts))
    return dt.split(".")[0]


def get_spec(spec_url):
    spec = None
    try:
        meta_data = requests.get(spec_url)
        if ".json" in spec_url:
            spec = meta_data.json()
        elif ".yml" in spec_url or ".yaml" in spec_url:
            spec = yaml.safe_load(meta_data.content)
    except Exception as e:
        print(e)
    return spec


def get_status(url, meta_path):
    status = None
    try:
        request = requests.get(url + meta_path)
        status = request.status_code
    except Exception as e:
        print(e)
    return status


def query_smart_api(url: str = SMARTAPI_URL, parameters: Optional[str] = None) -> Optional[Dict]:
    """
    Retrieve Translator SmartAPI Metadata for a specified query parameter filter.

    :param url: str, base URL for Translator SmartAPI Registry
    :param parameters: Optional[str], string of query parameters for Translator SmartAPI Registry
    :return: dict, catalog of Translator SmartAPI Metadata indexed by "test_data_location" source.
    """
    # ... if not faking it, access the real thing...
    query_string = f"query?{parameters}" if parameters else "query"
    data: Optional[Dict] = None
    try:
        if _MOCK_REGISTRY:
            # TODO: Using Mock data for now given that the "real" repository
            #       currently lacks KP and ARA 'test_data_location' tags.
            # double deak: fake special "fake URL" unit test result
            if url == "fake URL":
                raise RequestException(f"fake URL!")

            data = _MOCK_TRANSLATOR_SMARTAPI_REGISTRY_METADATA

        else:

            request = requests.get(f"{url}{query_string}")
            if request.status_code == 200:
                data = request.json()

    except RequestException as re:
        print(re)
        data = {"Error": "Translator SmartAPI Registry Access Exception: "+str(re)}

    return data


def iterate_services_from_registry(registry_data):
    """

    :param registry_data: Translator SmartAPI Registry catalog (i.e. as returned by query_smart_api())
    :return:
    """
    service_status_data = []
    for index, service in enumerate(registry_data['hits']):
        print(index, service['info']['title'], set_timestamp())
        try:
            service_spec = get_spec(service['_meta']['url'])
            for server in service_spec['servers']:
                source_data_packet = {
                    "title": service['info']['title'],
                    "time_retrieved": set_timestamp(),
                    "component": service['info']['x-translator']['component'],
                    "meta_data_url": service['_meta']['url'],
                    "server_url": server['url'],
                    "server_x_maturity": None,
                    "server_status": None,
                }
                if 'x-maturity' in server.keys():
                    source_data_packet['server_x_maturity'] = server['x-maturity']
                service_paths = [x for x in service['paths'] if 'meta' in x]
                meta_kg_path = service_paths[0]
                source_data_packet['server_status'] = get_status(server['url'], meta_kg_path)
                print(server['url'], meta_kg_path, source_data_packet['server_status'])
                service_status_data.append(source_data_packet)
        except Exception as e:
            print(e)
    return service_status_data


def get_nested_tag_value(data: Dict, path: List[str], pos: int) -> Optional[str]:
    """
    Navigate dot delimited tag 'path' into a multi-level dictionary, to return its associated value.

    :param data: Dict, multi-level data dictionary
    :param path: str, dotted JSON tag path
    :param pos: int, zero-based current position in tag path
    :return: string value of the multi-level tag, if available; 'None' otherwise if no tag value found in the path
    """
    tag = path[pos]
    part_tag_path = ".".join(path[:pos+1])
    if tag not in data:
        logger.debug(f"\tMissing tag path '{part_tag_path}'?")
        return None

    pos += 1
    if pos == len(path):
        return data[tag]
    else:
        return get_nested_tag_value(data[tag], path, pos)


def tag_value(json_data, tag_path):
    """

    :param json_data:
    :param tag_path:
    :return:
    """
    if not tag_path:
        logger.debug(f"\tEmpty 'tag_path' argument?")
        return None

    parts = tag_path.split(".")
    return get_nested_tag_value(json_data, parts, 0)


def capture_tag_value(service_metadata: Dict, resource: str, tag: str, value: str):
    """

    :param service_metadata:
    :param resource:
    :param tag:
    :param value:
    :return:
    """
    if value:
        logger.info(f"\t{resource} '{tag}': {value}")
        service_metadata[resource][tag] = value
    else:
        logger.warning(f"\t{resource} is missing its service '{tag}'")
        service_metadata[resource][tag] = None


def extract_component_test_metadata_from_registry(
        registry_data: Dict,
        component_type: str
) -> Dict[str, Dict[str,  Optional[str]]]:
    """
    Extract metadata from a registry data dictionary, for all components of a specified type.

    :param registry_data:
        Dict, Translator SmartAPI Registry dataset
        from which specific component_type metadata will be extracted.
    :param component_type: str, value 'KP' or 'ARA'
    :return: Dict[str, Dict[str,  Optional[str]]] of metadata, indexed by 'test_data_location'
    """

    # Sanity check...
    assert component_type in ["KP", "ARA"]

    service_metadata: Dict[str, Dict[str, Optional[str]]] = dict()

    for index, service in enumerate(registry_data['hits']):

        # We are only interested in services belonging to a given category of components
        component = tag_value(service, "info.x-translator.component")
        if not (component and component == component_type):
            continue

        service_title = tag_value(service, "info.title")

        # ... and only interested in resources with a non-empty test_data_location specified
        test_data_location = tag_value(service, "info.x-trapi.test_data_location")
        if not test_data_location:
            logger.info(f"Service {index}: '{service_title}' lacks a 'test_data_location' to be indexed?")
            continue

        if test_data_location not in service_metadata:
            service_metadata[test_data_location] = dict()
        else:
            # TODO: duplicate test_data_locations are problematic for our unique indexing of the service
            logger.warning(
                f"Ignoring service {index}: '{service_title}' " +
                f"with a duplicate test_data_location '{test_data_location}'?"
            )
            continue

        # Grab additional service metadata, then store it all

        service_version = tag_value(service, "info.version")

        infores = tag_value(service, "info.x-translator.infores")
        # Internally, within SRI Testing, we only track the object_id of the infores CURIE
        infores = infores.replace("infores:", "") if infores else None

        biolink_version = tag_value(service, "info.x-translator.biolink-version")
        trapi_version = tag_value(service, "info.x-trapi.version")

        capture_tag_value(service_metadata, test_data_location, "service_title", service_title)
        capture_tag_value(service_metadata, test_data_location, "service_version", service_version)
        capture_tag_value(service_metadata, test_data_location, "infores", infores)
        capture_tag_value(service_metadata, test_data_location, "biolink_version", biolink_version)
        capture_tag_value(service_metadata, test_data_location, "trapi_version", trapi_version)

    return service_metadata


# Singleton reading of the Registry Data
# (do I need to periodically refresh it in long-running applications?)
_the_registry_data: Optional[Dict] = None


def get_the_registry_data():
    global _the_registry_data
    if not _the_registry_data:
        _the_registry_data = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    return _the_registry_data


def get_remote_test_data_file(url: str) -> Optional[Dict]:
    """

    :param url: URL of SRI test data file template for a given resource
    :return: dictionary of test data parameters
    """
    data: Optional[Dict] = None
    try:
        request = requests.get(f"{url}")
        if request.status_code == 200:
            data = request.json()
    except RequestException as re:
        print(re)
        data = {"Error": f"Translator component test data file '{url}' cannot be accessed: "+str(re)}

    return data
