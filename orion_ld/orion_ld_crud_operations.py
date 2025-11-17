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
ORION_LD_BATCH_CREATE_URL = "http://localhost:1026/ngsi-ld/v1/entityOperations/create"
ORION_LD_BATCH_DELETE_URL = "http://localhost:1026/ngsi-ld/v1/entityOperations/delete"
ORION_LD_BATCH_UPDATE_URL = "http://localhost:1026/ngsi-ld/v1/entityOperations/upsert?options=update"
HEADERS = {
    "Content-Type": "application/json",
    "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs_static/gtfs_static_context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
}

def orion_ld_define_header(keyword: str) -> dict[str, str]:
    """
    Define headers for Orion-LD requests based on the provided keyword.
    Args:
        keyword (str): Keyword to determine the type of headers to return.
    Returns:
        dict[str, str]: Headers dictionary for the specified keyword.
    """
    if keyword == "gtfs_static":
        return {
            "Content-Type": "application/json",
            "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs_static/gtfs_static_context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
        }
    elif keyword == "pois":
        return {
            "Content-Type": "application/json",
            "Link": '<https://raw.githubusercontent.com/smart-data-models/dataModel.PointOfInterest/master/context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
        }
    else:
        return {
            "Content-Type": "application/json",
            "Link": '<https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
        }

# POST Requests

def orion_ld_post_batch_request(batch_ngsi_ld_data: List[Dict[str, Any]]) -> None:
    """
    Send a POST request to ORION-LD's endpoint for batch create of entities.
    Args:
        batch_ngsi_ld_data (List[Dict[str, Any]]): List of entities in NGSI-LD format to be created in a batch.
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
        print(f" Batch POST Request Error: {e}")
    

def orion_ld_batch_load_to_context_broker(ngsi_ld_data: List[Dict[str, Any]], batch_size: int = 1000, delay: float = 0.1) -> None:
    """    Load entities in NGSI-LD format to the context broker in batches.
    Args:
        ngsi_ld_data (List[Dict[str, Any]]): List of entities in NGSI-LD format to be loaded.
        batch_size (int): Number of entities to be sent in each batch. Default is 1000.
        delay (float): Delay in seconds between each batch request. Default is 0.1 seconds.
    Returns:
        None: The function does not return anything, but prints the result of each batch request.
    """
    # Create batches of the NGSI-LD data and send them to the context broker
    for i in range(0, len(ngsi_ld_data), batch_size):
        
        batch = ngsi_ld_data[i: i + batch_size]
        orion_ld_post_batch_request(batch)
        
        # delay the POST Request, so to not break the Orion-LD architecture
        time.sleep(delay)
        
# GET functions

def orion_ld_get_entity_by_id(entity_id: str) -> List[Dict[str, Any]]:
    """
    Send GET request for a specific entity based on its ID
    Args:
        entity_id (str): Entity ID

    Returns:
        List[Dict[str, Any]]: Entity Data in JSON format
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
        for entity in data:
            for v in entity.values():
                if isinstance(v, dict) and "value" in v and isinstance(v["value"], str):
                    v["value"] = codecs.decode(v["value"], 'unicode_escape')

        # Return the data after the transformation
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error when sending GET request: {e}")

        # If an exception is raised, return []
        return []


def orion_ld_get_entities_by_type(entity_type: str) -> List[Dict[str, Any]]:
    """
    Send GET Request for all entities of a specific entity type.
    Orion-LD allows to GET 1000 entities at a time - configured though the limit parameter
    Orion-LD  allows to choose from what index to start getting entities - configured through the offset parameter
    IMPORTANT: Orion-LD allows to GET up to 34 000 entities total. Use this function more as a helper function.
    Args:
        entity_type (str): Entity Type.
    Returns:
        List[Dict[str, Any]]: List of entities of the specified type
    """
    # List to store all entities
    all_entities = []

    # Current index from which to start getting entitites
    offset = 0
    limit = 1000

    # While there are entities of the desired type, get 1000 at a time
    while True:
        params = {
            "type": entity_type,
            "limit": limit,
            "offset": offset
            }
        try:
            # Send a GET request to extract entities of type 'entity_type'
            response = requests.get(f'{ORION_LD_URL}', headers=HEADERS, params=params)
            # Raise exception, if unsuccessful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # If data is empty, that means all entities are fetched thus break loop
            if not data:
                break

            # For every dictionary in the data list, check its values for a "value" key that is a string.
            # If so, decode it using unicode_escape to handle any escaped characters (like cyrilic).
            for entity in data:
                for v in entity.values():
                    if isinstance(v, dict) and "value" in v and isinstance(v["value"], str):
                        v["value"] = codecs.decode(v["value"], 'unicode_escape')

            # Append entities
            all_entities.extend(data)

            # Update index for getting entities
            offset += limit
        except requests.exceptions.RequestException as e:
            print(f"Error when sending GET request: {e}")
        
    # Return all entities
    return all_entities


def orion_ld_get_entities_by_query_expression(entity_type: str, query_expression: str) -> List[Dict[str, Any]]:
    """
    Send a GET request for specific Entity type and filter it with a query expression.
    Automatically converts any non-ASCII characters in the query to Unicode escape format.
    Orion-LD allows to GET 1000 entities at a time - configured though the limit parameter
    Orion-LD  allows to choose from what index to start getting entities - configured through the offset parameter
    Args:
        entity_type (str): Entity Type.
        query_expression (str): Expression to filter out the entities.

    Returns:
        List[Dict[str, Any]]: List of filtered entities.
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
            "type": entity_type,
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
            for entity in data:
                for v in entity.values():
                    if isinstance(v, dict) and "value" in v and isinstance(v["value"], str):
                        v["value"] = codecs.decode(v["value"], 'unicode_escape')

            # Append enitites
            all_entities.append(data)

            # Update index for getting entities
            offset += 1000

        except requests.exceptions.RequestException as e:
            print(f"Error when sending GET request: {e}")
    
    # Return all entities
    return all_entities


def orion_ld_get_attribute_values_from_etities(entity_ids: List[str], attribute_list: List[str]) -> List[Dict[str, Any]]:
    """
    Send a GET request to fetch specific entitis and filter their attributes
    Args:
        entity_ids List[str]:  List of specific entities to be fetched.
        attribute_list: List[str]: Attributes that to be filtered from the fetched entities.

    Returns:
        List[Dict[str, Any]]: List of filtered entities.
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


def orion_ld_get_count_of_entities_by_type(entity_type: str) -> int:
    """
    Returns the number of NGSI-LD entities of a given entity type from Orion-LD.

    Args:
        entity_type (str): Short type name as defined in your JSON-LD context
    Returns:
        int: Number of entities of the specified type.
    """
    # Limit is 0, just so it doesn't return an entity
    # We set the count option, to get the number of enitites of the desired type
    params = {
        "type": entity_type,
        "limit": 0,
        "options": "count"
    }

    try:
        # Send a GET request to get the number of elements of type 'entity_type'
        response = requests.get(ORION_LD_URL, headers=HEADERS, params=params)
        
        # Raise exception, if unsuccessful
        response.raise_for_status()
        
        # Get the value of the key 'NGSILD-Results-Count' and parse it as int.
        # If the key is not found, return 0
        count = int(response.headers.get("NGSILD-Results-Count", 0))
        return count
    
    except requests.RequestException as e:
        print(f"Error getting entity count: {e}")
        return 0
    
# UPDATE functions

def orion_ld_batch_replace_entity_data(batch_ngsi_ld_data: List[Dict[str, Any]]) -> None:
    """
    Send a POST request to ORION-LD's endpoint for batch replace of entities.
    Args:
        batch_ngsi_ld_data (List[Dict[str, Any]]): List of entities in NGSI-LD format to be updated.
    Returns:
        None: The function does not return anything, but prints the result of the POST request.
    """
    # Get ids of the entities from the batch
    entities_ids = [entity['id'] for entity in batch_ngsi_ld_data]

    # Concatenate them with '\n'
    entities_ids = "\n".join(entities_ids)
    try:
        # Send a POST request to ORION-LD's endpoint for batch create where we the data is already in NGSI-LD format
        response = requests.post(ORION_LD_BATCH_UPDATE_URL, json=batch_ngsi_ld_data, headers=HEADERS)

        # If successful, report which enteties were created
        if response.status_code == 201:
            print(f"Replaced entity data for the following {len(batch_ngsi_ld_data)} entities:\n{entities_ids}\n")
        # If failed, explain why
        else:
            print(f"Failed to replace entity data {response.status_code} {response.text}")
    except  requests.exceptions.RequestException as e:
        print(f"POST Request Error: {e}")
# DELETE functions

def orion_ld_delete_entity(entity_id: str) -> None:
    """
    Delete an entity by its id
    Args:
        entity_id (str): ID of an NGSI-LD enity
    """
    
    try:
        # Send a DELETE request to Orion-LD to delete the entity with the specified ID
        response = requests.delete(f"{ORION_LD_URL}/{entity_id}", headers=HEADERS)
        
        # Raise exception, if unsuccessful
        response.raise_for_status()
        
        print(f"Deleted entity with id: {entity_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error when sending DELETE request for entity {entity_id}: {e}")

def orion_ld_batch_delete_entities_by_type(entity_type: str) -> None:
    
    # Get number of entities
    entity_count = orion_ld_get_count_of_entities_by_type(entity_type)
    print(f'Total entities: {entity_count}')
    
    while entity_count != 0:
        # Will return max 34 000 entities in 1 function call
        # Experimentally found
        entities = orion_ld_get_entities_by_type(entity_type)
        
        # Get a list of the entities ID
        entity_ids = [entity['id'] for entity in entities]
        
        # Split entity_ids into batches of max 1000
        batch_size = 1000
        batches = [entity_ids[i:i + batch_size] for i in range(0, len(entity_ids), batch_size)]
        
        for batch in batches:
            try:
                # Send a Batch Delete request to Orion-LD with the IDs in the current batch
                response = requests.post(ORION_LD_BATCH_DELETE_URL, json=batch, headers=HEADERS)
                
                # Raise exception, if unsuccessful
                response.raise_for_status()
                print(f"Deleted batch of {len(batch)} entities of type {entity_type}")
                
            except requests.exceptions.RequestException as e:
                print(f"Batch DELETE Request Error: {e}")
        
        # Update count        
        entity_count = orion_ld_get_count_of_entities_by_type(entity_type)
        print(f'Remaining entities: {entity_count}')


if __name__ == "__main__":
    HEADERS = orion_ld_define_header("gtfs_static")
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("agency")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("calendar_dates")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("fare_attributes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("levels")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("pathways")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("routes")

    ngsi_ld_data = gtfs_static_get_ngsi_ld_data("shapes")

    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("stop_times")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("stops")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("transfers")
    
    #ngsi_ld_data = gtfs_static_get_ngsi_ld_data("trips")

    orion_ld_batch_load_to_context_broker(ngsi_ld_data)
    
    #get_request_response = orion_ld_get_entities_by_query_expression("GtfsStop", 'name=="МЕТРОСТАНЦИЯ ОПЪЛЧЕНСКА"')
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #get_request_response = orion_ld_get_entity_by_id("urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:TB25")
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #get_request_response = orion_ld_get_attribute_values_from_etities(["urn:ngsi-ld:GtfsStop:TB6408", "urn:ngsi-ld:GtfsStop:A1157"], ["location", "code"])
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #get_request_response = orion_ld_get_entities_by_type("GtfsCalendarDateRule")
    #print(len(get_request_response))
    #print(json.dumps(get_request_response, indent=2, ensure_ascii=False))

    #orion_ld_delete_entity("urn:ngsi-ld:GtfsAgency:A")

    #orion_ld_batch_delete_entities_by_type("GtfsShape")
    
    #print(orion_ld_get_count_of_entities_by_type("GtfsShape"))

    pass