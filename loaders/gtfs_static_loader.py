import requests
import sys
import os
import json
import time
import codecs
from urllib.parse import unquote




script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import List, Dict, Any
from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_data

ORION_LD_URL = "http://localhost:1026/ngsi-ld/v1/entities"
ORION_LD_BATCH_CREATE_URL= "http://localhost:1026/ngsi-ld/v1/entityOperations/create"
HEADERS = {
    "Content-Type": "application/json",
    "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs-static/gtfs-static-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}

# POST Requests

def gtfs_static_post_batch_request(batch_ngsi_ld_data: List[Dict[str, Any]]):
    entities_ids = [entity['id'] for entity in batch_ngsi_ld_data]
    entities_ids = "\n".join(entities_ids)
    try:
        response = requests.post(ORION_LD_BATCH_CREATE_URL, json=batch_ngsi_ld_data, headers=HEADERS)
        if response.status_code == 201:
            print(f"Created batch of {len(batch_ngsi_ld_data)} entities:\n{entities_ids}\n")
        else:
            print(f"Failed to create entities {response.status_code} {response.text}")
    except  requests.RequestException as e:
        print(f"GTFS Static Batch POST Request Error: {e}")
    

def gtfs_static_batch_load_to_context_broker(ngsi_ld_data: List[Dict[str, Any]], batch_size: int = 1000, delay: float = 0.1):
    for i in range(0, len(ngsi_ld_data), batch_size):
        batch = ngsi_ld_data[i: i + batch_size]
        gtfs_static_post_batch_request(batch)
        time.sleep(delay)
        
# GET functions

def gtfs_static_get_entity(entity_id: str) -> List[Dict[str, Any]]:
    """
    Send GET request for a specific GTFS Static Entity based on its ID
    Args:
        entity_id (str): GTFS Static Entity ID

    Returns:
        List[Dict[str, Any]]: GTFS Static Entity Data in JSON format
    """
    # Send GET request to Orion-LD by modifying the API request to point to the specific entity ID
    try:
        response = requests.get(f'{ORION_LD_URL}/{entity_id}', headers=HEADERS)
        print(response.url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and "value" in value and isinstance(value["value"], str):
                    value["value"] = codecs.decode(value["value"], 'unicode_escape')
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error when sending GET request: {e}")
        return []


def gtfs_static_get_entities_by_query_expression(gtfs_type: str, query_expression: str) -> List[Dict[str, Any]]:
    """
    Send a GET request for specific GTFS Static Entity type and filter it with a query expression.
    Automatically converts any non-ASCII characters in the query to Unicode escape format.

    Args:
        gtfs_type (str): GTFS Static Entity Type.
        query_expression (str): Expression to filter out the GTFS Static Entities.

    Returns:
        List[Dict[str, Any]]: List of filtered GTFS Static entities.
    """
    decoded_query_expression = unquote(query_expression)
    escaped_query_expression = decoded_query_expression.encode('unicode_escape').decode('ascii')

    params = {
        "type": gtfs_type,
        "q": escaped_query_expression
    }

    try:
        response = requests.get(ORION_LD_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error when sending GET request: {e}")
        return []

def gtfs_static_get_entities_with_attributes(entity_ids: List[str], attribute_list: List[str]) -> List[Dict[str, Any]]:
    """
    Send a GET request to fetch specific GTFS Static Entitis and filter their attributes
    Args:
        entity_ids List[str]:  List of specific GTFS Static Entities to be fetched.
        attribute_list: List[str]: Attributes that to be filtered from the fetched GTFS Static Entities.

    Returns:
        List[Dict[str, Any]]: List of filtered GTFS Static entities.
    """
    entities = ",".join(entity_ids)
    attributes = ",".join(attribute_list)

    try:
        response = requests.get(f'{ORION_LD_URL}/?id={entities}&attrs={attributes}', headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error when sending GET request: {e}")
        return []
    pass
# DELETE functions


if __name__ == "__main__":
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("agency")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("calendar_dates")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("fare_attributes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("levels")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("pathways")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("routes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("shapes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("stop_times")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("stops")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("transfers")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("trips")

    #gtfs_static_batch_load_to_context_broker(ngsi_ld_data)
    
    #get_request_response = gtfs_static_get_entities_by_query_expression("GtfsStop", 'name=="МЕТРОСТАНЦИЯ ОПЪЛЧЕНСКА"')
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #get_request_response = gtfs_static_get_entity("urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:TB25")
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    get_request_response = gtfs_static_get_entities_with_attributes(["urn:ngsi-ld:GtfsStop:TB6408", "urn:ngsi-ld:GtfsStop:A1157"], ["location", "code"])
    print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    pass