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
ORION_LD_BATCH_DELETE_URL = "http://localhost:1026/ngsi-ld/v1/entityOperations/delete"
HEADERS = {
    "Content-Type": "application/json",
    "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs-static/gtfs-static-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}

# POST Requests

def gtfs_static_post_batch_request(batch_ngsi_ld_data: List[Dict[str, Any]]) -> None:
    """
    Send a POST request to ORION-LD's endpoint for batch create of GTFS Static entities.
    Args:
        batch_ngsi_ld_data (List[Dict[str, Any]]): List of GTFS Static entities in NGSI-LD format to be created in a batch.
    Returns:
        None: The function does not return anything, but prints the result of the POST request.
    """
    # Get ids of the entities from the batch
    entities_ids = [entity['id'] for entity in batch_ngsi_ld_data]

    # Concatenate them with '\n'
    entities_ids = "\n".join(entities_ids)
    try:
        # Send a POST request to ORION-LD's endpoint for batch create where we the data is already in NGSI-LD format
        response = requests.post(ORION_LD_BATCH_CREATE_URL, json=batch_ngsi_ld_data, headers=HEADERS)

        # If successful, report which enteties were created
        if response.status_code == 201:
            print(f"Created batch of {len(batch_ngsi_ld_data)} entities:\n{entities_ids}\n")
        # If failed, explain why
        else:
            print(f"Failed to create entities {response.status_code} {response.text}")
    except  requests.exceptions.RequestException as e:
        print(f"GTFS Static Batch POST Request Error: {e}")
    

def gtfs_static_batch_load_to_context_broker(ngsi_ld_data: List[Dict[str, Any]], batch_size: int = 1000, delay: float = 0.1) -> None:
    """    Load GTFS Static data in NGSI-LD format to the context broker in batches.
    Args:
        ngsi_ld_data (List[Dict[str, Any]]): List of GTFS Static entities in NGSI-LD format to be loaded.
        batch_size (int): Number of entities to be sent in each batch. Default is 1000.
        delay (float): Delay in seconds between each batch request. Default is 0.1 seconds.
    Returns:
        None: The function does not return anything, but prints the result of each batch request.
    """
    for i in range(0, len(ngsi_ld_data), batch_size):
        batch = ngsi_ld_data[i: i + batch_size]
        gtfs_static_post_batch_request(batch)
        time.sleep(delay)
        
# GET functions

def gtfs_static_get_entity_by_id(entity_id: str) -> List[Dict[str, Any]]:
    """
    Send GET request for a specific GTFS Static Entity based on its ID
    Args:
        entity_id (str): GTFS Static Entity ID

    Returns:
        List[Dict[str, Any]]: GTFS Static Entity Data in JSON format
    """
    
    try:
        # Send GET request to Orion-LD by modifying the API request to point to the specific entity ID
        response = requests.get(f'{ORION_LD_URL}/{entity_id}', headers=HEADERS)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # For every dictionary value in the data, check if it has a "value" key and if its value is a string.
        # If so, decode it using unicode_escape to handle any escaped characters (like cyrilic).
        for value in (v for v in data.values() if isinstance(v, dict) and "value" in v and isinstance(v["value"], str)):
            value["value"] = codecs.decode(value["value"], 'unicode_escape')

        # Return the data after the transformation
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error when sending GET request: {e}")

        # If an exception is raised, return []
        return []

def gtfs_static_get_entities_by_type(gtfs_static_type: str) -> List[Dict[str, Any]]:
    """
    Send GET Request for all entities of a specific GTFS Static Type
    Orion-LD allows to GET 1000 entities at a time - configured though the limit parameter
    Orion-LD  allows to choose from what index to start getting entities - configured through the offset parameter
    Args:
        gtfs_static_type (str): GTFS Static Type
        Allowed values: GtfsAgency, GtfsCalendarDateRule, GtfsFareAttributes, GtfsLevel, GtfsPathway
                        GtfsRoute, GtfsShape, GtfsStopTime, GtfsStop, GtfsTransferRule, GtfsTrip
    Returns:
        List[Dict[str, Any]]: List of all GTFS Static Entities of the specified type
    """
    # List to store all entities
    all_entities = []

    # Current index from which to start getting entitites
    offset = 0

    # While there are entities of the desired type, get 1000 at a time
    while True:
        params = {
            "limit": 1000,
            "offset": offset
            }
        try:
            # Send a GET request to extract entities of type 'gtfs_static_type'
            response = requests.get(f'{ORION_LD_URL}/?type={gtfs_static_type}', headers=HEADERS, params=params)
            # Raise exception, if unsuccessful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # If data is empty, that means all entities are fetched thus break loop
            if not data:
                break

            # For every dictionary value in the data, check if it has a "value" key and if its value is a string.
            # If so, decode it using unicode_escape to handle any escaped characters (like cyrilic).
            for value in (v for v in data.values() if isinstance(v, dict) and "value" in v and isinstance(v["value"], str)):
                value["value"] = codecs.decode(value["value"], 'unicode_escape')

            # Append enitites
            all_entities.append(data)

            # Update index for getting entities
            offset += 1000        
        except requests.exceptions.RequestException as e:
            print(f"Error when sending GET request: {e}")
        
    # Return all entities
    return all_entities


def gtfs_static_get_entities_by_query_expression(gtfs_type: str, query_expression: str) -> List[Dict[str, Any]]:
    """
    Send a GET request for specific GTFS Static Entity type and filter it with a query expression.
    Automatically converts any non-ASCII characters in the query to Unicode escape format.
    Orion-LD allows to GET 1000 entities at a time - configured though the limit parameter
    Orion-LD  allows to choose from what index to start getting entities - configured through the offset parameter
    Args:
        gtfs_type (str): GTFS Static Entity Type.
        query_expression (str): Expression to filter out the GTFS Static Entities.

    Returns:
        List[Dict[str, Any]]: List of filtered GTFS Static entities.
    """
    # Decode the URL-encoded strings, living is as the original variant
    decoded_query_expression = unquote(query_expression)
    # Turn all non-ASCII symbols into escape sequences which are then turned into a string.
    # This is needed to allow to send query expressions that contain cyrilic.
    # Orion-LD stores the cyrilic values as escape sequences
    escaped_query_expression = decoded_query_expression.encode('unicode_escape').decode('ascii')
    
    # List to store all entities
    all_entities = []

    # Current index from which to start getting entitites
    offset = 0

    # While there are entities that satisfy the query request, get 1000 at a time
    while True:

        params = {
            "type": gtfs_type,
            "q": escaped_query_expression,
            "offset": offset,
            "limit": 1000
        }

        try:
            # Send a GET request with the query expression and starting index
            response = requests.get(ORION_LD_URL, headers=HEADERS, params=params)

            # Raise exception, if unsuccessful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()
            
            # If data is empty, that means all entities are fetched thus break loop
            if not data:
                break

            # For every dictionary value in the data, check if it has a "value" key and if its value is a string.
            # If so, decode it using unicode_escape to handle any escaped characters (like cyrilic).
            for value in (v for v in data.values() if isinstance(v, dict) and "value" in v and isinstance(v["value"], str)):
                value["value"] = codecs.decode(value["value"], 'unicode_escape')

            # Append enitites
            all_entities.append(data)

            # Update index for getting entities
            offset += 1000

        except requests.exceptions.RequestException as e:
            print(f"Error when sending GET request: {e}")
    
    # Return all entities
    return all_entities

def gtfs_static_get_attribute_values_from_etities(entity_ids: List[str], attribute_list: List[str]) -> List[Dict[str, Any]]:
    """
    Send a GET request to fetch specific GTFS Static Entitis and filter their attributes
    Args:
        entity_ids List[str]:  List of specific GTFS Static Entities to be fetched.
        attribute_list: List[str]: Attributes that to be filtered from the fetched GTFS Static Entities.

    Returns:
        List[Dict[str, Any]]: List of filtered GTFS Static entities.
    """
    # Concatenate the enitities' ids and attribute list which we want to extract
    entities = ",".join(entity_ids)
    attributes = ",".join(attribute_list)

    try:
        # Send GET request to get the attributes for the enitites
        response = requests.get(f'{ORION_LD_URL}/?id={entities}&attrs={attributes}', headers=HEADERS)

        # Raise exception, if unsuccessful
        response.raise_for_status()

        # Parse the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error when sending GET request: {e}")

        # If exception is raised, return []
        return []

def gtfs_static_count_entities(entity_type: str) -> int:
    """
    Returns the number of NGSI-LD entities of a given GTFS Static type from Orion-LD.

    Args:
        entity_type (str): Short type name as defined in your JSON-LD context
        Allowed values: GtfsAgency, GtfsCalendarDateRule, GtfsFareAttributes, GtfsLevel, GtfsPathway
                        GtfsRoute, GtfsShape, GtfsStopTime, GtfsStop, GtfsTransferRule, GtfsTrip

    Returns:
        int: Number of entities of the specified type.
    """
    params = {
        "type": entity_type,
        "limit": 0,
        "options": "count"
    }

    try:
        response = requests.get(ORION_LD_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        count = int(response.headers.get("NGSILD-Results-Count", 0))
        return count
    except requests.RequestException as e:
        print(f"Error getting entity count: {e}")
        return 0
    
# DELETE functions

def gtfs_static_delete_entity(entity_id: str) -> None:
        try:
            response = requests.delete(f"{ORION_LD_URL}/{entity_id}", headers=HEADERS)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error when sending DELETE request: {e}")

def gtfs_static_batch_delete_entities_by_type(gtfs_static_type: str) -> None:
    entities = gtfs_static_get_entities_by_type(gtfs_static_type)
    enitities_ids = [f"{entity['id']}" for entity in entities]

    try:
        response = requests.post(ORION_LD_BATCH_DELETE_URL, json=enitities_ids, headers=HEADERS)
        response.raise_for_status()
        print(f"Deleted batch of {len(enitities_ids)} entities of type {gtfs_static_type}")
    except requests.exceptions.RequestException as e:
        print(f"GTFS Static Batch DELETE Request Error: {e}")
    pass

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

    #get_request_response = gtfs_static_get_entity_by_id("urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:TB25")
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #get_request_response = gtfs_static_get_attribute_values_from_etities(["urn:ngsi-ld:GtfsStop:TB6408", "urn:ngsi-ld:GtfsStop:A1157"], ["location", "code"])
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #get_request_response = gtfs_static_get_entities_by_type("GtfsCalendarDateRule")
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #gtfs_static_delete_entity("urn:ngsi-ld:GtfsAgency:A")

    #gtfs_static_batch_delete_entities_by_type("GtfsCalendarDateRule")

    #print(gtfs_static_count_entities("GtfsRoute"))
    pass