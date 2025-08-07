import requests
import sys
import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', 'gtfs_static'))
sys.path.append(project_root)

from typing import List, Dict, Any
from gtfs_static_utils import gtfs_static_get_ngsi_ld_data

ORION_LD_URL = "http://localhost:1026/ngsi-ld/v1/entities"
HEADERS = {
    "Content-Type": "application/json",
    "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs-static/gtfs-static-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}

def post_gtfs_static_entity(entity: Dict[str, Any]) -> None:
    try:
        response = requests.post(ORION_LD_URL, json=entity, headers=HEADERS)
        if response.status_code == 201:
            print(f"Entity {entity['id']} created successfully.")
        elif response.status_code == 409:
            print(f"Entity {entity['id']} already exists.")
        else:
            print(f"Failed to create {entity['id']}: {response.status_code} {response.text}")
    except requests.RequestException as e:
        print(f"Request error while creating entity {entity.get('id')}: {e}")

def load_entities(entities: List[Dict[str, Any]]):
    for entity in entities:
        post_gtfs_static_entity(entity)

# GET functions

def get_gtfs_static_entities_by_gtfs_type() -> None:

    params = {
    "type": "GtfsCalendarDateRule",
    "options": "count"
    }

    try:
        response = requests.get(ORION_LD_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP грешка: {http_err} - Отговор: {response.text}")

    except requests.exceptions.ConnectionError:
        print("Грешка: Няма връзка с Orion-LD брокера.")

    except requests.exceptions.Timeout:
        print("Грешка: Времето за отговор изтече.")

    except requests.exceptions.RequestException as err:
        print(f"Непредвидена грешка при заявката: {err}")

# DELETE functions


if __name__ == "__main__":
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("agency")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("calendar_dates")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("fare_attributes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("levels")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("pathways")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("routes")

    ngsi_ld_data = gtfs_static_get_ngsi_ld_data("shapes")

    load_entities(ngsi_ld_data)



    #get_gtfs_static_entities_by_gtfs_type()
    pass