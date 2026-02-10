import logging
import requests
import sys
import os
import json
import time
import codecs
from pathlib import Path
from urllib.parse import unquote

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from typing import  Any
import config

logger = logging.getLogger("Orion-LD")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


# -----------------------------------------------------
# HEADER Definition Function
# -----------------------------------------------------  

def orion_ld_define_header(keyword: str) -> dict[str, str]:
    """
    Define headers for Orion-LD requests based on the provided keyword.
    Args:
        keyword (str): 
        Keyword to determine the type of headers to return.
    Returns:
        dict[str, str]: 
            Headers dictionary for the specified keyword.
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
    elif keyword == "gtfs_realtime":
        return {
            "Content-Type": "application/json",
            "Link": '<https://manoldzhermanski.github.io/System-for-Semantic-Interoperability-of-Urban-Data/gtfs_realtime/gtfs_realtime_context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
        }
    else:
        return {
            "Content-Type": "application/json",
            "Link": '<https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
        }

# -----------------------------------------------------
# POST Requests
# -----------------------------------------------------  

def orion_ld_post_batch_request(batch_ngsi_ld_data: list[dict[str, Any]], header: dict[str, str]) -> None:
    """
    Sends a batch POST request to the Orion-LD broker to create multiple NGSI-LD entities.

    Args:
        batch_ngsi_ld_data (list[dict[str, Any]]):
            List of NGSI-LD entities
            
        headers (dict[str, str]):
            HTTP headers to be included in the request (Content-Type and Link)

    Returns:
        None
        
    Raises:
        requests.exceptions.HTTPError:
            If the batch request fails (status code != 201).

        requests.exceptions.RequestException:
            For network-related errors.
    """
    

    entity_ids = [e["id"] for e in batch_ngsi_ld_data]

    response = requests.post(
        config.OrionLDEndpoint.BATCH_CREATE_ENDPOINT.value,
        json=batch_ngsi_ld_data,
        headers=header,
    )

    if response.status_code == 201:
        logger.info("Successfully created batch of %d entities", len(batch_ngsi_ld_data))
        return

    if response.status_code == 207:
        payload = response.json()

        successes = payload.get("success", [])
        errors = payload.get("errors", [])

        if successes:
            logger.info("Successfully created %d entities", len(successes))

        real_errors = []

        for err in errors:
            title = err.get("error", {}).get("title", "").lower()
            entity_id = err.get("entityId")

            if "already exists" in title:
                logger.warning("Entity already exists, skipping: %s", entity_id)
            else:
                real_errors.append(err)

        if real_errors:
            raise requests.exceptions.HTTPError(f"Batch partially failed with real errors: {real_errors}")
        return

    raise requests.exceptions.HTTPError(
        f"Batch failed (status={response.status_code}): {response.text}")
    
def orion_ld_batch_load_to_context_broker(ngsi_ld_data: list[dict[str, Any]], header: dict, batch_size: int = 1000, delay: float = 0.1) -> None:
    """
    Load NGSI-LD entities to Orion-LD context broker in batches.

    Args:
        ngsi_ld_data (list[dict[str, Any]]):
            List of NGSI-LD entities
            
        headers (dict[str, str]):
            HTTP headers for the request (Content-Type and Link)
            
        batch_size (int, optional):
            Number of entities per batch. Defaults to 1000 - max default number.
            
        delay (float, optional):
            Delay in seconds between sending each batch. Defaults to 0.1s - empirically found as sufficient.

    Returns:
        None

    Side Effects:
        - Sends multiple POST requests to the Orion-LD broker.
        - Logs batch creation status through `orion_ld_post_batch_request`.
        - Adds a delay between batches to prevent overloading the broker.
    """
    # Iterate over ngsi_ld_data in chunks of batch_size
    for i in range(0, len(ngsi_ld_data), batch_size):
        batch = ngsi_ld_data[i: i + batch_size]
        
        logger.debug("Sending batch %d to Orion-LD (%d entities)", i // batch_size + 1, len(batch))
        
        # Delegate actual batch POST to helper function
        orion_ld_post_batch_request(batch, header)
        
        # Delay between batches to prevent overwhelming the broker
        time.sleep(delay)
        
# -----------------------------------------------------
# GET Requests
# -----------------------------------------------------  

def orion_ld_get_entity_by_id(entity_id: str, header: dict[str, str]) -> dict[str, Any]:
    """
    Get a single NGSI-LD entity from Orion-LD by its entity ID.

    The function sends an HTTP GET request to the Orion-LD Context Broker
    and returns the entity as a JSON dictionary. Additionally, it post-processes
    NGSI-LD attributes to decode any escaped Unicode characters (e.g. Cyrillic)

    Args:
        entity_id (str):
            ID written as NGSI-LD URN

        header (Dict[str, str]):
            HTTP headers used for the request (Content-Type and Link)

    Returns:
        Dict[str, Any]:
            A dictionary representing the NGSI-LD entity.
            If the request fails, an empty dictionary is returned.

    Raises:
        RequestException when there is an error with the GET Request
    """
    try:
        # Send GET request to Orion-LD for a specific entity
        response = requests.get(f"{config.OrionLDEndpoint.ENTITIES_ENDPOINT.value}/{entity_id}", headers=header)
        
        # Raise an exception for HTTP error responses
        response.raise_for_status()
        
        # Ensure correct response encoding
        response.encoding = "utf-8"

        # Parse JSON response
        data = response.json()

        # Iterate through all attributes of the entity
        for attr in data.values():
            if isinstance(attr, dict):
                # Decode escaped Unicode in Property values
                if "value" in attr and isinstance(attr["value"], str):
                    attr["value"] = codecs.decode(attr["value"], "unicode_escape")

                # Decode escaped Unicode in Relationship values
                if "object" in attr and isinstance(attr["object"], str):
                    attr["object"] = codecs.decode(attr["object"], "unicode_escape")

        return data

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when sending GET Request: {e}")

def orion_ld_get_entities_by_type(entity_type: str, header: dict[str, str]) -> list[dict[str, Any]]:
    """
    Retrieve all entities of a specific NGSI-LD type from Orion-LD, handling pagination.

    Orion-LD allows fetching a limited number of entities per request (default limit=1000)
    and supports pagination via the `offset` parameter. This function retrieves all entities
    of the specified type up to Orion-LD's maximum limit (34,000).

    Args:
        entity_type (str): 
            The NGSI-LD entity type to retrieve.
        
        header (dict[str, str]): 
            HTTP headers to include in the request (Content-Type and Link)

    Returns:
        list[dict[str, Any]]: A list of NGSI-LD entities of the specified type.

    Raises:
        requests.exceptions.RequestException: If there is a network or HTTP error during the requests.
    """
    # List to store all entities
    all_entities = []

    # Starting index for pagination
    offset = 0
    
    # Number of entities per request
    limit = 1000
    
    # Prevent infinite loops by setting a maximum number of iterations
    max_iterations = 1000000000
    iteration = 0

    # While there are entities of the desired type, get 1000 at a time
    while True:
        
        params = {
            "type": entity_type,
            "limit": limit,
            "offset": offset,
            }
        
        #iteration += 1
        #if iteration > max_iterations:
        #    raise RuntimeError("Too many iterations in get_entities_by_type")
        
        try:
            # Send a GET request to extract entities of type 'entity_type'
            response = requests.get(config.OrionLDEndpoint.ENTITIES_ENDPOINT.value, headers=header, params=params)
            
            # Raise an exception for HTTP error responses
            response.raise_for_status()
            
            # Ensure correct response encoding
            response.encoding = "utf-8"

            # Parse the JSON response
            data = response.json()

            # Break if no more entities
            if not data:
                break

            # Extend entity list
            all_entities.extend(data)

            # Move offset for next page
            offset += limit
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Error when sending GET request: {e}")
        
    # Return all entities
    return all_entities

def orion_ld_get_entities_by_query_expression(entity_type: str, header:dict, query_expression: str) -> list[dict[str, Any]]:
    """
    Retrieve all entities of a specific NGSI-LD type that match a given query expression.

    Orion-LD allows fetching a limited number of entities per request (default limit=1000)
    and supports pagination via the `offset` parameter. This function retrieves all entities
    of the specified type up to Orion-LD's maximum limit (34,000). The function automatically
    converts non-ASCII characters in the query expression to Unicode escape sequences for
    handling queries in Cyrillic.
    
    Args:
        entity_type (str): 
            The NGSI-LD entity type to retrieve
        
        header (dict[str, str]): 
            HTTP headers to include in the request (Content-Type and Link)
        
        query_expression (str): 
            Query expression to filter entities

    Returns:
        list[dict[str, Any]]: List of entities matching the query.

    Raises:
        requests.exceptions.RequestException: If there is a network or HTTP error during the request.
        RuntimeError: If the pagination loop exceeds the maximum allowed iterations (safety measure).
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
    
    # Number of entities per request
    limit = 1000
    
    # Prevent infinite loops by setting a maximum number of iterations
    max_iterations = 50
    iteration = 0

    # While there are entities that satisfy the query request, get 1000 at a time
    while True:

        params = {
            "type": entity_type,
            "q": escaped_query_expression,
            "offset": offset,
            "limit": limit
        }

        iteration += 1
        if iteration > max_iterations:
            raise RuntimeError("Too many iterations in get_entities_by_type")

        try:
            # Send a GET request with the query expression and starting index
            response = requests.get(config.OrionLDEndpoint.ENTITIES_ENDPOINT.value, headers=header, params=params)

            # Raise an exception for HTTP error responses
            response.raise_for_status()
            
            # Ensure correct response encoding
            response.encoding = "utf-8"

            # Parse the JSON response
            data = response.json()
            
            # Break if no more entities
            if not data:
                break

            # Extend entity list
            all_entities.extend(data)

            # Move offset for next page
            offset += 1000

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"Error when sending GET request: {e}")
    
    # Return all entities
    return all_entities

def orion_ld_get_attribute_values_from_etities(entity_ids: list[str], attribute_list: list[str], header: dict) -> list[dict[str, Any]]:
    """
    Retrieve specific attributes for a given list of NGSI-LD entities from Orion-LD.

    This function fetches only selected attributes for explicitly specified entity IDs
    using the `id` and `attrs` query parameters supported by Orion-LD.

    Args:
        entity_ids (list[str]):
            List of NGSI-LD entity IDs to be fetched
        attribute_list (list[str]):
            List of attribute names to retrieve from each entity
        header (dict[str, str]):
            HTTP headers to include in the request (Content-Type and Link)

    Returns:
        list[dict[str, Any]]:
            List of NGSI-LD entities containing only the requested attributes.

    Raises:
        requests.exceptions.RequestException:
            If the HTTP request fails or Orion-LD returns an error status.
    """
    # Join entity IDs and attribute names into comma-separated strings
    entities = ",".join(entity_ids)
    attributes = ",".join(attribute_list)

    try:
        # Send GET request to Orion-LD with explicit entity IDs and attribute filtering
        response = requests.get(f'{config.OrionLDEndpoint.ENTITIES_ENDPOINT.value}/?id={entities}&attrs={attributes}', headers=header)

        # Raise an exception for HTTP error responses
        response.raise_for_status()
        
        # Ensure correct response encoding
        response.encoding = "utf-8"
        
        # Parse the JSON response
        data = response.json()

        # Return the filtered entities
        return data
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when sending GET request: {e}")

def orion_ld_get_count_of_entities_by_type(entity_type: str, header: dict[str, str]) -> int:
    """
    Retrieve the total number of NGSI-LD entities of a given type from Orion-LD.

    This function uses the NGSI-LD `options=count` query parameter together with
    `limit=0` in order to retrieve only the total entity count without fetching
    any actual entity payload.

    The count is returned by Orion-LD in the `NGSILD-Results-Count` response header.

    Args:
        entity_type (str):
            type of NGSI-LD entities to count.
        header (dict[str, str]):
            HTTP headers to include in the request (Content-Type and Link)

    Returns:
        int:
            Number of entities of the specified type.
            Returns 0 if the count header is missing or if a request error occurs.

    Notes:
        - Orion-LD returns the entity count via the `NGSILD-Results-Count` HTTP header.
        - `limit=0` prevents returning any entity data, making the request lightweight.

    """
    # Request parameters:
    # - limit=0 ensures no entities are returned in the response body
    # - options=count instructs Orion-LD to return the total count in the headers
    params = {
        "type": entity_type,
        "limit": 0,
        "options": "count"
    }

    try:
        # Send GET request to Orion-LD to get the count of entities of the specified type
        response = requests.get(config.OrionLDEndpoint.ENTITIES_ENDPOINT.value, headers=header, params=params)
        
        # Raise exception for HTTP error responses
        response.raise_for_status()
        
        # Ensure correct response encoding
        response.encoding = "utf-8"
        
        # Extract entity count from response headers
        # If the header is missing, default to 0
        count = int(response.headers.get("NGSILD-Results-Count", 0))
        return count
    
    except requests.exceptions.RequestException as e:
        logger.error("Error getting entity count: %s", e)
        return 0

# -----------------------------------------------------
# UPDATE Requests
# -----------------------------------------------------  

def orion_ld_batch_replace_entity_data(batch_ngsi_ld_data: list[dict[str, Any]], header: dict[str, str]) -> None:
    """
    Perform a batch replace operation for NGSI-LD entities in Orion-LD.

    This function sends a POST request to the Orion-LD batch update endpoint
    to fully replace the data of multiple entities.

    Orion-LD returns:
        - HTTP 201 if all entities are successfully replaced
        - HTTP 207 (Multi-Status) if the batch is partially successful

    Args:
        batch_ngsi_ld_data (list[dict[str, Any]]):
            List of NGSI-LD entities to be replaced. Each entity must include
            a valid `id` and `type`.
        header (dict[str, str]):
            HTTP headers to include in the request (Content-Type and Link)

    Returns:
        None

    Raises:
        requests.exceptions.HTTPError:
            If the batch replace operation fails with an unexpected HTTP status code.
        requests.exceptions.RequestException:
            If a network or request-related error occurs.
    """
    # Extract entity IDs for logging and debugging purposes
    entities_ids = [entity['id'] for entity in batch_ngsi_ld_data]
    entities_ids = "\n".join(entities_ids)
    
    try:
        # Send POST request to Orion-LD batch update endpoint
        response = requests.post(config.OrionLDEndpoint.BATCH_UPDATE_ENDPOINT.value, json=batch_ngsi_ld_data, headers=header)

        # Orion-LD considers 201 (Created) and 207 (Multi-Status) as valid responses
        if response.status_code not in (201, 204, 207):
            raise requests.exceptions.HTTPError(f"Batch replace failed (status={response.status_code}): {response.text}")
        
        # Log successful batch replace
        logger.info("Replaced entity data successfully for entities %s", response.status_code)

    except  requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"POST Request Error: {e}")
        
# -----------------------------------------------------
# DELETE Requests
# -----------------------------------------------------  

def orion_ld_delete_entity(entity_id: str, header: dict[str, str]) -> None:
    """
    Delete an NGSI-LD entity from Orion-LD by its entity ID.

    This function sends a DELETE request to the Orion-LD entities endpoint
    and removes the specified entity if it exists.

    Args:
        entity_id (str):
            Full NGSI-LD entity ID
        header (dict[str, str]):
            HTTP headers to include in the request (Content-Type and Link)

    Returns:
        None

    Raises:
        requests.exceptions.HTTPError:
            If Orion-LD returns an HTTP error status.
        requests.exceptions.RequestException:
            If a network or request-related error occurs.
    """
    
    try:
        # Send DELETE request to Orion-LD for the specified entity
        response = requests.delete(f"{config.OrionLDEndpoint.ENTITIES_ENDPOINT.value}/{entity_id}", headers=header)
        
        # Raise exception for HTTP error responses
        response.raise_for_status()
        
        # Log successful deletion
        logger.info(f"Deleted entity with id: {entity_id}")
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when sending DELETE request for entity {entity_id}: {e}")

def orion_ld_batch_delete_entities_by_type(entity_type: str, header: dict[str, str]) -> None:
    """
    Delete all NGSI-LD entities of a given type from Orion-LD in batches.

    The function:
    - Retrieves entities by type
    - Splits their IDs into batches of max 1000 (Orion-LD limitation)
    - Sends batch delete requests until no entities of the given type remain

    Args:
        entity_type (str):
            NGSI-LD entity type to be deleted.
        header (dict[str, str]):
            HTTP headers for the Orion-LD requests (Content-Type and Link)

    Returns:
        None

    Raises:
        requests.exceptions.RequestException:
            If a batch delete request fails.
    """
    # Initial entity count
    entity_count = orion_ld_get_count_of_entities_by_type(entity_type, header)
    logger.info(f'Total entities: {entity_count}')
    
    # Continue deleting until no entities remain
    while entity_count > 0:
        
        # Orion-LD returns up to ~34k entities per call
        entities = orion_ld_get_entities_by_type(entity_type, header)
        
        # Extract entity IDs
        entity_ids = [entity['id'] for entity in entities]
        
        # Split IDs into batches of max 1000
        batch_size = 1000
        batches = [entity_ids[i:i + batch_size] for i in range(0, len(entity_ids), batch_size)]
        
        for batch in batches:
            try:
                # Send a Batch Delete request to Orion-LD with the IDs in the current batch
                response = requests.post(config.OrionLDEndpoint.BATCH_DELETE_ENDPOINT.value, json=batch, headers=header)
                
                # Raise exception for HTTP error responses
                response.raise_for_status()
                
                logger.info(f"Deleted batch of {len(batch)} entities of type {entity_type}")
                
            except requests.exceptions.RequestException as e:
                raise requests.exceptions.RequestException(f"Batch DELETE Request Error: {e}")
        
        # Update remaining entity count      
        entity_count = orion_ld_get_count_of_entities_by_type(entity_type, header)
        logger.debug(f'Remaining entities: {entity_count}')

if __name__ == "__main__":
    header = orion_ld_define_header("gtfs_static")
    #orion_ld_batch_delete_entities_by_type("GtfsCalendarDateRule", header)
    print(orion_ld_get_count_of_entities_by_type("GtfsCalendarDateRule", header))
    pass
