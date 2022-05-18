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

SMARTAPI_URL = "https://smart-api.info/api/"
SMARTAPI_QUERY_PARAMETERS = "q=__all__&tags=%22trapi%22&" +\
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
    query_string = f"query?{parameters}" if parameters else "query"
    data: Optional[Dict] = None
    try:
        request = requests.get(f"{url}{query_string}")
        if request.status_code == 200:
            data = request.json()
    except RequestException as re:
        print(re)
        data = {"Error": "Translator SmartAPI Registry Access Exception cannot be accessed: "+str(re)}

    return data


def iterate_services_from_registry(registry_data):
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


def get_nested_tag_value(data, path: List[str], pos: int):
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

    if not tag_path:
        logger.debug(f"\tEmpty 'tag_path' argument?")
        return None

    parts = tag_path.split(".")
    return get_nested_tag_value(json_data, parts, 0)


def capture_tag_value(service_metadata: Dict, resource: str, tag: str, value: str):
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

    assert component_type in ["KP", "ARA"]

    service_metadata: Dict[str, Dict[str, Optional[str]]] = dict()

    for index, service in enumerate(registry_data['hits']):
        # Grab global metadata...
        service_title = tag_value(service, "info.title")
        service_version = tag_value(service, "info.version")

        infores = tag_value(service, "info.x-translator.infores")
        component = tag_value(service, "info.x-translator.component")

        if infores and component and component == component_type:

            # ...Grab more Translator/TRAPI metadata...
            biolink_version = tag_value(service, "info.x-translator.biolink-version")
            trapi_version = tag_value(service, "info.x-trapi.version")
            test_data_location = tag_value(service, "info.x-trapi.test_data_location")

            # ... create an infores bucket for it...
            logger.debug(f"{index}: {infores} version {str(service_version)} metadata - {service_title}")
            if infores not in service_metadata:
                service_metadata[infores] = dict()
            else:
                # TODO: duplicate infores may mean a distinction between a 'production' and 'development' service?
                #       Just report the anomaly as a warning for now and ignore the entry?
                logger.warning(
                    f"Resource {infores} is duplicated in Translator SmartAPI Registry?\n" +
                    "This may result for entries which are loosely tagged as 'production' versus 'development'?\n" +
                    "We ignore this situation for now, pending availability of additional metadata?"
                )
                continue

            # ... then store all the metadata...

            capture_tag_value(service_metadata, infores, "service_title", service_title)
            capture_tag_value(service_metadata, infores, "service_version", service_version)

            logger.info(f"\t{infores} is a '{component}' component")
            service_metadata[infores]["component"] = component

            capture_tag_value(service_metadata, infores, "biolink_version", biolink_version)
            capture_tag_value(service_metadata, infores, "trapi_version", trapi_version)
            capture_tag_value(service_metadata, infores, "test_data_location", test_data_location)

    return service_metadata


def extract_kp_test_data_metadata_from_registry(
        registry_data: Dict
) -> Dict[str, Dict[str,  Optional[str]]]:
    return extract_component_test_metadata_from_registry(registry_data, component_type="KP")


def extract_ara_test_data_metadata_from_registry(
        registry_data: Dict
) -> Dict[str, Dict[str,  Optional[str]]]:
    return extract_component_test_metadata_from_registry(registry_data, component_type="ARA")


# Singleton reading of the Registry Data
# (do I need to periodically refresh it in long-running applications?)
_the_registry_data: Optional[Dict] = None


def _get_the_registry_data():
    global _the_registry_data
    if not _the_registry_data:
        _the_registry_data = query_smart_api(parameters=SMARTAPI_QUERY_PARAMETERS)
    return _the_registry_data


def get_translator_kp_test_data_metadata() -> Dict[str, Dict[str, Optional[str]]]:
    registry_data: Dict = _get_the_registry_data()
    return extract_kp_test_data_metadata_from_registry(registry_data)


def get_translator_ara_test_data_metadata() -> Dict[str, Dict[str, Optional[str]]]:
    registry_data: Dict = _get_the_registry_data()
    return extract_ara_test_data_metadata_from_registry(registry_data)
