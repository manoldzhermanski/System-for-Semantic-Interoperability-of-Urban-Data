import requests
import sys
import os
import json
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', 'gtfs_static'))
sys.path.append(project_root)

from typing import List, Dict, Any
from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_data

ORION_LD_URL = "http://localhost:1026/ngsi-ld/v1/entities"
ORION_LD_BATCH_CREATE_URL= "http://localhost:1026/ngsi-ld/v1/entityOperations/create"
HEADERS = {
    "Content-Type": "application/json",
    "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs-static/gtfs-static-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}

# POST Requests

def post_gtfs_static_entity(entity: Dict[str, Any]) -> None:
    try:
        response = requests.post(ORION_LD_BATCH_CREATE_URL, json=entity, headers=HEADERS)
        if response.status_code == 201:
            print(f"Entity {entity['id']} created successfully.")
        elif response.status_code == 409:
            print(f"Entity {entity['id']} already exists.")
        else:
            print(f"Failed to create {entity['id']}: {response.status_code} {response.text}")
    except requests.RequestException as e:
        print(f"Request error while creating entity {entity.get('id')}: {e}")

def load_entities(entities: List[Dict[str, Any]], delay: float = 0):
    for entity in entities:
        post_gtfs_static_entity(entity)
        time.sleep(delay)

def gtfs_static_post_batch_request(batch_ngsi_ld_data: List[Dict[str, Any]]):
    entities_ids = [entity['id'] for entity in batch_ngsi_ld_data]
    entities_ids = "\n".join(entities_ids)
    try:
        response = requests.post(ORION_LD_BATCH_CREATE_URL, json=batch_ngsi_ld_data, headers=HEADERS)
        if response.status_code == 201:
            print(f"Created batch of {len(batch_ngsi_ld_data)} entities:\n{entities_ids}\n")
        else:
            print(f"Failed to create entities {response.status_code}")
    except  requests.RequestException as e:
        print(f"GTFS Static Batch POST Request Error: {e}")
    

def gtfs_static_batch_load_to_context_broker(ngsi_ld_data: List[Dict[str, Any]], batch_size: int = 1000, delay: float = 0.1):
    for i in range(0, len(ngsi_ld_data), batch_size):
        batch = ngsi_ld_data[i: i + batch_size]
        gtfs_static_post_batch_request(batch)
        time.sleep(delay)
        

# GET functions

# DELETE functions


if __name__ == "__main__":
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("agency")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("calendar_dates")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("fare_attributes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("levels")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("pathways")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("routes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("shapes")

    ngsi_ld_data = gtfs_static_get_ngsi_ld_data("stop_times")

    #load_entities(ngsi_ld_data)

    gtfs_static_batch_load_to_context_broker(ngsi_ld_data)


    #get_gtfs_static_entities_by_gtfs_type()
    pass