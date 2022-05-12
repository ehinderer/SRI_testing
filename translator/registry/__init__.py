"""
Translator SmartAPI Registry access module.
"""
from typing import Optional
from datetime import datetime

import requests
import yaml
from requests.exceptions import RequestException

SMARTAPI_URL = "https://smart-api.info/api/"
SMARTAPI_QUERY_PARAMETERS = "q=__all__&tags=%22trapi%22&fields=info,_meta,_status,paths,tags,openapi,swagger&size=1000&from=0"


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


def query_smart_api(url: str = SMARTAPI_URL, parameters: Optional[str] = None):
    query_string = f"query?{parameters}" if parameters else "query"
    data = None
    try:
        request = requests.get(f"{url}{query_string}")
        if request.status_code == 200:
            data = request.json()
    except RequestException as re:
        print(re)
        data = str(re)
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
