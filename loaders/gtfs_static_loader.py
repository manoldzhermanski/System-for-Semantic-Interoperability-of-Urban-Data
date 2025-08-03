import requests
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', 'gtfs_static'))
sys.path.append(project_root)

from typing import List, Dict, Any
from gtfs_static_utils import gtfs_static_read_file, gtfs_static_agency_to_ngsi_ld

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

# Примерна употреба
if __name__ == "__main__":
    feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "agency.txt"))
    ngsi_ld_data = gtfs_static_agency_to_ngsi_ld(feed_dict)
    load_entities(ngsi_ld_data)
