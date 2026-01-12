import re
import sys
import requests
from typing import Any
from pathlib import Path
from datetime import datetime, timezone
from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict
from google.transit.gtfs_realtime_pb2 import FeedMessage # type: ignore

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import remove_none_values
import config

def unix_to_iso8601(timestamp: int | str | None) -> str | None:
    """
    Convert UNIX timestamp (seconds) to ISO 8601 UTC string.
    
    Args:
        timestamp (int | str | None): UNIX timestamp in seconds.
        
    Returns:
        str | None: ISO 8601 formatted string in UTC, or None if input is invalid.
    """
    if timestamp is None:
        return None
    
    if not isinstance(timestamp, (str, int)):
        return None
    
    if isinstance(timestamp, bool):
        return None

    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        return None

    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# NOTE: SHOULD SEE IF IT IS USED AND WHAT FOR
def iso8601_to_unix(timestamp: str) -> int | None:
    try:
        return int(
            datetime
            .fromisoformat(timestamp.replace("Z", "+00:00"))
            .astimezone(timezone.utc)
            .timestamp()
        )
    except Exception:
        return None

# -----------------------------------------------------
# GTFS Realtime Data Manipulations
# -----------------------------------------------------

def gtfs_realtime_get_feed(api_endpoint: config.GtfsSource) -> bytes:
    """
    Fetches a GTFS-Realtime feed from the specified API endpoint.

    The function sends an HTTP GET request to the URL stored in the provided
    GtfsSource enum and returns the raw GTFS-Realtime feed content
    (Protocol Buffers binary format).

    Args:
        api_endpoint (config.GtfsSource): Enum value containing the GTFS-Realtime API endpoint URL.

    Returns:
        bytes: Raw GTFS-Realtime feed data in Protocol Buffers (.pb) format.

    Raises:
        ValueError:
            If the API endpoint does not have a URL configured.
        requests.exceptions.RequestException:
            If the request fails or the server returns an error response.
    """
    try:
        
        # Extract the URL from the enum configuration
        url = api_endpoint.value
        
        # If url is None or empty string, raise ValueError
        if url is None or url.strip() == "":
            raise ValueError(f"API endpoint {api_endpoint.name} has no URL configured")
        
        # Perform HTTP GET request to fetch the GTFS-Realtime feed
        response = requests.get(url)
        
        # Raise an exception for HTTP error responses
        response.raise_for_status()
        
        # Return raw protobuf binary content
        return response.content
    except requests.exceptions.RequestException:
        
        # Raise exception error whein handling the API endpoint
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint.name}")
        
def gtfs_realtime_parse_feed(feed_data: bytes, api_endpoint: config.GtfsSource | None = None) -> FeedMessage:
    """
    Parses the GTFS-Realtime feed data into a FeedMessage object.
    Provide an optional api_endpoint for debugging purposes.
    Args:
        feed_data (bytes): the .pb data received from the API endpoint
        api_endpoint (config.GtfsSource): optional parameter to know which API endpoint was tried to be accessed
    Returns:
        FeedMessage: GTFS Realtime Feed data
    """
    
    # Create an empty GTFS-Realtime FeedMessage protobuf object
    feed = FeedMessage()
    
    try:
        
        # Try and parse the binary protobuf payload into a FeedMessage
        feed.ParseFromString(feed_data)
        
    except DecodeError:
        
        # Raise DecodeError if parsing fails
        raise DecodeError(f'Error parsing GTFS-Realtime feed data {"from " + api_endpoint.name if api_endpoint else ""}')
    
    # Return the successfully parsed GTFS-Realtime feed
    return feed

def gtfs_realtime_feed_to_dict(feed_data: FeedMessage) -> dict[str, Any]:
    """
    Converts a GTFS-Realtime FeedMessage protobuf object into a Python dictionary.

    Args:
        feed_data (FeedMessage): Parsed GTFS-Realtime feed protobuf message.

    Returns:
        dict[str, Any]: Dictionary representation of the GTFS-Realtime feed.
    """
    
    feed_dict = MessageToDict(feed_data)
    return feed_dict

# -----------------------------------------------------
# Key Mapping Functions
# -----------------------------------------------------

def to_snake_case(name: str) -> str:
    """
    Convert a string from CamelCase or PascalCase to snake_case.

    Args:
        name (str): Input string in CamelCase or PascalCase format.

    Returns:
        str: The converted string in snake_case.
    """
    # Insert underscore before capital letters that start a new word
    # Example: "activePeriod" -> "active_Period"
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    
    # Insert underscore between a lowercase letter or digit and a capital letter
    # Example: "TripID" -> "Trip_ID"
    # Convert the final result to lowercase
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

def normalize_keys_to_snake_case(data: Any) -> Any:
    """
    Recursively normalize dictionary keys to snake_case.

    Args:
        data (Any): Input data structure. Can be a dictionary, a list, or
            any other value

    Returns:
        Any: A new data structure with all dictionary keys converted to
        snake_case. Non-collection values are returned unchanged.
    """

    # Normalize dictionary keys and recurse into values
    if isinstance(data, dict):
        return {
            to_snake_case(key): normalize_keys_to_snake_case(value)
            for key, value in data.items()
        }

    # Normalize every list element recursively
    if isinstance(data, list):
        return [normalize_keys_to_snake_case(item) for item in data]

    # Return non-dict and non-list values unchanged
    return data

def to_ngsi_ld_urn(value: str | None, entity_type: str) -> str | None:
    """
    Build an NGSI-LD URN identifier.

    Args:
        value (str | None): Entity identifier value. If None, no URN is
            generated and None is returned.
        entity_type (str): NGSI-LD entity type name.

    Returns:
        str | None: A valid NGSI-LD URN in the form
            'urn:ngsi-ld:<entity_type>:<value>', or None if value is None.

    Raises:
        ValueError: If entity_type is not a string.
    """
    stripped_entity_type = entity_type.strip()
            
    if isinstance(entity_type, str) and stripped_entity_type == "":
        raise ValueError("Entity name must be a non-empty string")
    
    if value is None:
        return None
    
    stripped_value = value.strip()
    if stripped_value == "":
        raise ValueError("Entity value must be a non-empty string")
    
    return f"urn:ngsi-ld:{stripped_entity_type}:{stripped_value}"

# -----------------------------------------------------
# Normalization Functions
# -----------------------------------------------------

def gtfs_realtime_normalize_trip_descriptor_message(trip: dict | None) -> dict[str, Any]:
    """
    Normalize a GTFS-realtime TripDescriptor message.

    This function takes a TripDescriptor message and 
    returns a normalized dictionary structure. Missing fields are 
    handled by being set to None.

    Args:
        trip (dict): TripDescriptor message

    Returns:
        dict[str, Any]: Normalized TripDescriptor with the following structure:
            {
                "trip_id": str | None,
                "route_id": str | None,
                "direction_id": int | None,
                "start_time": str | None,
                "start_date": str | None,
                "schedule_relationship": str | None,
                "modified_trip": {
                    "modifications_id": str | None,
                    "affected_trip_id": str | None,
                    "start_time": str | None,
                    "start_date": str | None
                }
            }
    """

    # Handle None input by using empty dictionary
    if trip is None:
        trip = {}
    
    # Extract nested modified_trip dictionary if present
    modified_trip = trip.get("modified_trip")

    return {
        "trip_id": to_ngsi_ld_urn(trip.get("trip_id"), "GtfsTrip"),
        "route_id": to_ngsi_ld_urn(trip.get("route_id"), "GtfsRoute"),
        "direction_id": trip.get("direction_id"),
        "start_time": trip.get("start_time"),
        "start_date": trip.get("start_date"),
        "schedule_relationship": trip.get("schedule_relationship"),

        # Normalize modified_trip; return None values if a field is missing
        "modified_trip": {
            "modifications_id": modified_trip.get("modifications_id") if modified_trip else None,
            "affected_trip_id": to_ngsi_ld_urn(modified_trip.get("affected_trip_id"), "GtfsTrip") if modified_trip else None,
            "start_time": modified_trip.get("start_time") if modified_trip else None,
            "start_date": modified_trip.get("start_date") if modified_trip else None,
        },
    }
    
def gtfs_realtime_normalize_translated_string_message(entity: dict[str, Any] | None, field: str) -> list[dict[str, Any]]:
    """
    Normalize a GTFS-realtime TranslatedString message.

    This function extracts from a TranslatedString message the content of
    its 'translation' field and returns it as aa list of dictionaires
    with "text" and "language" keys.

    Missing fields or translations are safely handled and result in an empty list.

    Args:
        entity (dict[str, Any] | None): Source dictionary that may contain
            a TranslatedString message.
        field (str): Name of the TranslatedString message field
            (e.g. "cause_detail", "description_text").

    Returns:
        list[dict[str, Any]]: A list of normalized translations with the structure:
            [
                {
                    "text": str | None,
                    "language": str | None
                }
            ]
    """

    # Extract the TranslatedString object from the entity
    entity_field = entity.get(field) if entity else None

    # Get the list of translation entries, defaulting to an empty list
    message = entity_field.get("translation") if entity_field else []

    # Normalize each translation entry into a stable structure
    return [
        {
            "text": translation.get("text"),
            "language": translation.get("language"),
        }
        for translation in message
    ]

def gtfs_realtime_normalize_vehicle_descriptor_message(vehicle: dict[str, Any] | None) -> dict[str, Any]:
    """
    Normalize a GTFS Realtime VehicleDescriptor message

    The function extracts a subset of supported fields and converts the
    vehicle identifier to an NGSI-LD URN.

    Args:
        vehicle (dict[str, Any] | None): GTFS Realtime vehicle descriptor.
            If None, an empty dictionary is returned.

    Returns:
        dict[str, Any]: Normalized vehicle representation with the following keys:
            - id: NGSI-LD URN built from the vehicle id
            - label: Vehicle label
            - license_plate: Vehicle license plate
            - wheelchair_accessible: Wheelchair accessibility enum
    """
    # If no vehicle descriptor is provided, return an empty structure
    if vehicle is None:
        vehicle = {}
    
    # Normalize and extract supported fields
    return {
        "id": to_ngsi_ld_urn(vehicle.get("id"), "GtfsVehicle"),
        "label": vehicle.get("label"),
        "license_plate": vehicle.get("license_plate"),
        "wheelchair_accessible": vehicle.get("wheelchair_accessible")
    }

def gtfs_realtime_clean_empty_values(value: Any) -> Any:
    """
    Recursively remove empty values from a data structure.
    This process gets the structure ready for NGSI-LD mapping

    The function removes:
    - None values
    - empty dictionaries {}
    - empty lists []

    If, after cleaning, a list or dictionary becomes empty,
    it is removed as well (represented as None).

    Args:
        value (Any): Input value which may be a dictionary, list, or any
            other type.

    Returns:
        Any: The cleaned data structure with empty values removed,
            or None if the resulting structure is empty.
    """

    # Base case: remove None values
    if value is None:
        return None

    # Recursively clean list items and drop empty results
    if isinstance(value, list):
        result = []
        for item in value:
            pruned = gtfs_realtime_clean_empty_values(item)
            if pruned is not None:
                result.append(pruned)
        return result if result else None

    # Recursively clean dictionary values and drop empty entries
    if isinstance(value, dict):
        result = {}
        for key, val in value.items():
            pruned = gtfs_realtime_clean_empty_values(val)
            if pruned is not None:
                result[key] = pruned
        return result if result else None

    # Base case: return other types of values as unchanged
    return value

# -----------------------------------------------------
# GTFS Realtime to NGSI-LD Parsing Functions
# -----------------------------------------------------

def parse_gtfs_realtime_vehicle_position(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a GTFS Realtime VehiclePosition feed entity into a consistent Python dictionary
    suitable for further processing and transformation into NGSI-LD.

    This function handles optional and missing fields according to the GTFS Realtime specification.
    Nested structures present in other feed entities such as trip descriptors, vehicle descriptors
    are normalized with helper functions.

    Args:
        entity (dict[str, Any]): A dictionary representing a GTFS Realtime VehiclePosition feed entity.

    Returns:
        dict[str, Any]: A normalized dictionary containing:
            - id: str | None
            - trip: dict | None
            - vehicle: dict | None
            - position: dict | None
            - current_stop_sequence: int| None
            - stop_id: str | None
            - current_status: str | None
            - timestamp: ISO 8601 UTC str | None
            - congestion_level: str | None
            - occupancy_status: str | None
            - occupancy_percentage: int or None
            - multi_carriage_details: list[dict] | None
    """
    # Extract all feed fields which have collection-type data (lists, dictionaries)
    vehicle_info = entity.get("vehicle")
    vehicle_info_trip = vehicle_info.get("trip") if vehicle_info else None
    vehicle_info_vehicle = vehicle_info.get("vehicle") if vehicle_info else None
    multi_carriage_details = vehicle_info.get("multi_carriage_details", []) if vehicle_info else []
    
     # Normalize multi-carriage details
    carriage_details = [
        {
            "id": to_ngsi_ld_urn(carriage.get("id"), "GtfsRealtimeCarriage"),
            "label": carriage.get("label"),
            "occupancy_status": carriage.get("occupancy_status"),
            "occupancy_percentage": carriage.get("occupancy_percentage"),
            "carriage_sequence": carriage.get("carriage_sequence")
        }
        for carriage in multi_carriage_details
    ]
    
    # Return the full normalized VehiclePosition dictionary
    return {
        "id": to_ngsi_ld_urn(entity.get("id"), "GtfsRealtimeVehiclePosition"),
        "trip": gtfs_realtime_normalize_trip_descriptor_message(vehicle_info_trip),
        "vehicle": gtfs_realtime_normalize_vehicle_descriptor_message(vehicle_info_vehicle),
        "position": {
            "latitude": vehicle_info.get("position").get("latitude") if vehicle_info else None,
            "longitude": vehicle_info.get("position").get("longitude") if vehicle_info else None,
            "bearing": vehicle_info.get("position").get("bearing") if vehicle_info else None,
            "odometer": vehicle_info.get("position").get("odometer") if vehicle_info else None,
            "speed": vehicle_info.get("position").get("speed") if vehicle_info else None,
        },
        "current_stop_sequence": vehicle_info.get("current_stop_sequence") if vehicle_info else None,
        "stop_id": to_ngsi_ld_urn(vehicle_info.get("stop_id"), "GtfsStop") if vehicle_info else None,
        "current_status": vehicle_info.get("current_status") if vehicle_info else None,
        "timestamp": unix_to_iso8601(int(vehicle_info.get("timestamp"))) if vehicle_info else None,
        "congestion_level": vehicle_info.get("congestion_level") if vehicle_info else None,
        "occupancy_status": vehicle_info.get("occupancy_status") if vehicle_info else None,
        "occupancy_percentage":vehicle_info.get("occupancy_percentage") if vehicle_info else None,
        "multi_carriage_details": carriage_details
    }

def parse_gtfs_realtime_trip_updates(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a GTFS Realtime TripUpdate feed entity into a consistent Python dictionary
    suitable for further processing and transformation into NGSI-LD.

    This function handles optional and missing fields according to the GTFS Realtime specification.
    Nested structures present in other feed entities such as trip descriptors, vehicle descriptors
    are normalized with helper functions.

    Args:
        entity (dict[str, Any]): A dictionary representing a GTFS Realtime TripUpdate feed entity.

    Returns:
        dict[str, Any]: A normalized dictionary containing:
            - id: str | None
            - trip: dict | None
            - vehicle: dict | None
            - stop_time_update: dict | None
            - timestamp: str | None
            - delay: int | None
            - trip_properties: dict | None
    """
    # Extract all feed fields which have collection-type data (lists, dictionaries)
    trip_update_info = entity.get("trip_update")
    trip_udate_info_trip = trip_update_info.get("trip") if trip_update_info else None
    trip_update_info_vehicle = trip_update_info.get("vehicle") if trip_update_info else None
    stop_time_update = trip_update_info.get("stop_time_update", []) if trip_update_info else []
    trip_update_info_trip_properties = trip_update_info.get("trip_properties") if trip_update_info else None
    
    # Normalize 'stop_time_update'
    stop_time_updates = [
        {
            "stop_sequence": update.get("stop_sequence") if stop_time_update else None,
            "stop_id": to_ngsi_ld_urn(update.get("stop_id"), "GtfsStop") if stop_time_update else None,
            "arrival": {
                "delay": update.get("arrival").get("delay") if stop_time_update else None,
                "time": unix_to_iso8601(int(update.get("arrival").get("time"))) if stop_time_update else None,
                "scheduled_time": update.get("arrival").get("scheduled_time") if stop_time_update else None,
                "uncertainty": update.get("arrival").get("uncertainty") if stop_time_update else None,
                },
            "departure": {
                "delay": update.get("departure").get("delay") if stop_time_update else None,
                "time": unix_to_iso8601(int(update.get("departure").get("time"))) if stop_time_update else None,
                "scheduled_time": update.get("departure").get("scheduled_time") if stop_time_update else None,
                "uncertainty": update.get("departure").get("uncertainty") if stop_time_update else None,
                },
            "departure_occupancy_status": update.get("departure_occupancy_status") if stop_time_update else None,
            "schedule_relationship": update.get("schedule_relationship") if stop_time_update else None,
            "stop_time_properties": {
                "assigned_stop_id": to_ngsi_ld_urn((update.get("stop_time_properties") or {}).get("assigned_stop_id"), "GtfsStop"),
                "stop_headsign": (update.get("stop_time_properties") or {}).get("stop_headsign"),
                "drop_off_type": (update.get("stop_time_properties") or {}).get("drop_off_type"),
                "pickup_type": (update.get("stop_time_properties") or {}).get("pickup_type")
            }
        }
        for update in stop_time_update
    ]
    
    # Return the full normalized TripUpdate dictionary
    return {
        "id": to_ngsi_ld_urn(entity.get("id"), "GtfsRealtimeTripUpdate"),
        "trip":  gtfs_realtime_normalize_trip_descriptor_message(trip_udate_info_trip),
        "vehicle": gtfs_realtime_normalize_vehicle_descriptor_message(trip_update_info_vehicle),
        "stop_time_update":  stop_time_updates,
        "timestamp": unix_to_iso8601(int(trip_update_info.get("timestamp"))) if trip_update_info else None,
        "delay": trip_update_info.get("delay") if trip_update_info else None,
        "trip_properties": {
            "trip_id": to_ngsi_ld_urn(trip_update_info_trip_properties.get("trip_id"), "GtfsTrip") if trip_update_info_trip_properties else None,
            "start_date": trip_update_info_trip_properties.get("start_date") if trip_update_info_trip_properties else None,
            "start_time": trip_update_info_trip_properties.get("start_time") if trip_update_info_trip_properties else None,
            "trip_headsign": trip_update_info_trip_properties.get("trip_headsign") if trip_update_info_trip_properties else None,
            "trip_short_name": trip_update_info_trip_properties.get("trip_short_name") if trip_update_info_trip_properties else None,
            "shape_id": to_ngsi_ld_urn(trip_update_info_trip_properties.get("shape_id"), "GtfsShape") if trip_update_info_trip_properties else None
            }
        }

def parse_gtfs_realtime_alerts(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize a GTFS Realtime Alert feed entity into a consistent Python dictionary
    suitable for further processing and transformation into NGSI-LD.

    This function handles optional and missing fields according to the GTFS Realtime specification.
    Nested structures present in other feed entities such as TranslatedString are normalized with helper functions.

    Args:
        entity (dict[str, Any]): A dictionary representing a GTFS Realtime Alert feed entity.

    Returns:
        dict[str, Any]: A normalized dictionary containing:
            - id: str | None
            - active_period: list[dict] | []
            - informed_entity: list[dict] | []
            - cause: str | None
            - cause_detail: list[dict] | []
            - effect: str | None
            - effect_detail: list[dict] | []
            - url: list[dict] | []
            - header_text: list[dict] | []
            - description_text: list[dict] | []
            - tts_header_text: list[dict] | []
            - tts_description_text: list[dict] | []
            - image: list[dict] | []
            - image_alternative_text: list[dict] | []         
    """
    # Extract all feed fields which have collection-type data (lists, dictionaries)
    alert_info = entity.get("alert")
    active_period = alert_info.get("active_period") if alert_info else []
    alert_info_informed_entity = alert_info.get("informed_entity") if alert_info else []
    
    # Normalize 'active_period'
    alert_active_period = [
        {
            "start": unix_to_iso8601(int(period.get("start"))),
            "end": unix_to_iso8601(int(period.get("end")))
        }
        for period in active_period
    ]
    
    # Normalize 'informed_entity'
    alert_informed_entity = [
        {
            "agency_id": to_ngsi_ld_urn(infromed_entity.get("agency_id"), "GtfsAgency"),
            "route_id": to_ngsi_ld_urn(infromed_entity.get("route_id"), "GtfsRoute"),
            "route_type": infromed_entity.get("route_type"),
            "direction_id": infromed_entity.get("direction_id"),
            "trip": gtfs_realtime_normalize_trip_descriptor_message(infromed_entity.get("trip")),
            "stop_id": to_ngsi_ld_urn(infromed_entity.get("stop_id"), "GtfsStop")
        }
        for infromed_entity in alert_info_informed_entity
    ]
    
    # Get 'cause', 'effect', 'severity_level' and 'image'
    alert_cause = alert_info.get("cause") if alert_info else None
    alert_effect = alert_info.get("effect") if alert_info else None
    alert_severity_level = alert_info.get("severity_level") if alert_info else None
    alert_image = alert_info.get("image") if alert_info else None
    
    # Normalize TranslatedString fields    
    translated_fields = ["cause_detail", "effect_detail", "url", "header_text", "description_text",
                         "tts_header_text", "tts_description_text", "image_alternative_text"]

    translations = {
        field: gtfs_realtime_normalize_translated_string_message(alert_info, field)
        for field in translated_fields
    }

    # Normalize 'localized_image'
    alert_image_localized_image = alert_image.get("localized_image") if alert_image else []
    localized_images = [
        {
            "url": image.get("url"),
            "media_type": image.get("media_type"),
            "language": image.get("language")
        }
        for image in alert_image_localized_image
    ]
    
    # Return the full normalized Alert dictionary
    return {
        "id": to_ngsi_ld_urn(entity.get("id"), "GtfsRealtimeAlert"),
        "active_period": alert_active_period,
        "informed_entity": alert_informed_entity,
        "cause": alert_cause,
        "cause_detail": {
            "translation": translations["cause_detail"]
            },
        "effect": alert_effect,
        "effect_detail": {
            "translation": translations["effect_detail"]
            },
        "url":{
            "translation": translations["url"]
            },
        "header_text": {
            "translation": translations["header_text"]
            },
        "description_text": {
            "translation": translations["description_text"] 
            },
        "tts_header_text": {
            "translation": translations["tts_header_text"]
            },
        "tts_description_text":{
            "translation": translations["tts_description_text"]
            },
        "severity_level":  alert_severity_level,
        "image": {
            "localized_image": localized_images
            },
        "image_alternative_text":{
            "translation": translations["image_alternative_text"]
            }
    }  

# -----------------------------------------------------
# GTFS Realtime to NGSI-LD Conversion Functions
# -----------------------------------------------------

def covert_gtfs_realtime_vehicle_position_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a GTFS-Realtime VehiclePosition entity to a NGSI-LD entity.

    This function maps a normalized GTFS-Realtime VehiclePosition
    feed entity into an NGSI-LD compatible entity.

    Args:
        entity (dict[str, Any]):
            A normalized GTFS-Realtime VehiclePosition feed entity.

    Returns:
        dict[str, Any]:
            An NGSI-LD entity dictionary with the following structure:
            {
                "id": str | None,
                "trip": { "type": "Property", "value": dict | None },
                "vehicle": { "type": "Property", "value": dict | None },
                "position": { "type": "Property", "value": dict | None },
                "current_stop_sequence": { "type": "Property", "value": int | None },
                "stop_id": { "type": "Relationship", "object": str | None },
                "current_status": { "type": "Property", "value": str | None },
                "timestamp": { "type": "Property", "value": str | None },
                "congestion_level": { "type": "Property", "value": str | None },
                "occupancy_status": { "type": "Property", "value": str | None },
                "occupancy_percentage": { "type": "Property", "value": int | None },
                "multi_carriage_details": { "type": "Property", "value": list[dict] | [] }
            }
    """
        
    return {
        "id": entity.get("id"),
        "type": "GtfsRealtimeVehiclePosition",
        "trip": {
            "type": "Property",
            "value": entity.get("trip")
        },
        "vehicle": {
            "type": "Property",
            "value": entity.get("vehicle")
            },
        "position": {
            "type": "Property",
            "value": entity.get("position")
            },
        "current_stop_sequence": {
            "type": "Property",
            "value": entity.get("current_stop_sequence")
            },
        "stop_id": {
            "type": "Relationship",
            "object": entity.get("stop_id")
            },
        "current_status": {
            "type": "Property",
            "value": entity.get("current_status")
            },
        "timestamp": {
            "type": "Property",
            "value": entity.get("timestamp")
            },
        "congestion_level": {
            "type": "Property",
            "value": entity.get("congestion_level")
            },
        "occupancy_status": {
            "type": "Property",
            "value": entity.get("occupancy_status")
            },
        "occupancy_percentage": {
            "type": "Property",
            "value": entity.get("occupancy_percentage")
            },
        "multi_carriage_details": {
            "type": "Property",
            "value": entity.get("multi_carriage_details")
            },
    }

def convert_gtfs_realtime_trip_updates_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a GTFS-Realtime TripUpdate entity to a NGSI-LD entity.

    This function maps a normalized GTFS-Realtime TripUpdate
    feed entity into an NGSI-LD compatible entity.

    Args:
        entity (dict[str, Any]):
            A normalized GTFS-Realtime TripUpdate feed entity.

    Returns:
        dict[str, Any]:
            An NGSI-LD entity dictionary with the following structure:
            {
                "id": str | None,
                "trip": { "type": "Property", "value": dict | None },
                "vehicle": { "type": "Property", "value": dict | None },
                "stop_time_update": { "type": "Property", "value": dict | None },
                "timestamp": { "type": "Property", "value": str | None },
                "delay": { "type": "Property", "value": int | None },
                "trip_properties": { "type": "Property", "value": dict | None },
            }
    """    
    return {
        "id": entity.get("id"),
        "type": "GtfsRealtimeTripUpdate",
        "trip": {
            "type": "Property",
            "value": entity.get("trip")
        },
        "vehicle": {
            "type": "Property",
            "value": entity.get("vehicle")
        },
        "stop_time_update": {
            "type": "Property",
            "value": entity.get("stop_time_update")
        },
        "timestamp": {
            "type": "Property",
            "value": entity.get("timestamp")
        },
        "delay": {
            "type": "Property",
            "value": entity.get("delay")
        },
        "trip_properties": {
            "type": "Property",
            "value": entity.get("trip_properties")
        }
    }

def convert_gtfs_realtime_alerts_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Convert a GTFS-Realtime Alert entity to a NGSI-LD entity.

    This function maps a normalized GTFS-Realtime Alert
    feed entity into an NGSI-LD compatible entity.

    Args:
        entity (dict[str, Any]):
            A normalized GTFS-Realtime Alert feed entity.

    Returns:
        dict[str, Any]:
            An NGSI-LD entity dictionary with the following structure:
            {
                "id": str | None,
                "active_period": { "type": "Property", "value": list[dict] | [] },
                "informed_entity": { "type": "Property", "value": list[dict] | [] },
                "cause": { "type": "Property", "value": str | None },
                "cause_detail": { "type": "Property", "value": list[dict] | [] },
                "effect": { "type": "Property", "value": str | None },
                "effect_detail": { "type": "Property", "value": list[dict] | [] },
                "url": { "type": "Property", "value": list[dict] | [] },
                "header_text": { "type": "Property", "value": list[dict] | [] },
                "description_text": { "type": "Property", "value": list[dict] | [] },
                "tts_header_text": { "type": "Property", "value": list[dict] | [] },
                "tts_description_text": { "type": "Property", "value": list[dict] | [] },
                "image": { "type": "Property", "value": list[dict] | [] },
                "image_alternative_text": { "type": "Property", "value": list[dict] | [] },
            }
    """ 
    return {
        "id": entity.get("id"),
        "type": "GtfsRealtimeAlert",
        "active_period": {
            "type": "Property",
            "value": entity.get("active_period")
            },
        "informed_entity": {
            "type": "Property",
            "value": entity.get("informed_entity")
            },
        "cause": {
            "type": "Property",
            "value": entity.get("cause")
            },
        "cause_detail": {
            "type": "Property",
            "value": entity.get("cause_detail")
            },
        "effect": {
            "type": "Property",
            "value": entity.get("effect")
            },
        "effect_detail": {
            "type": "Property",
            "value": entity.get("effect_detail")
            },
        "url":{
            "type": "Property",
            "value": entity.get("url")
            },
        "header_text": {
            "type": "Property",
            "value": entity.get("header_text")
            },
        "description_text": {
            "type": "Property",
            "value": entity.get("description_text")
            },
        "tts_header_text": {
            "type": "Property",
            "value": entity.get("tts_header_text")
            },
        "tts_description_text":{
            "type": "Property",
            "value": entity.get("tts_description_text")
            },
        "severity_level": {
            "type": "Property",
            "value": entity.get("severity_level")
            },
        "image": {
            "type": "Property",
            "value": entity.get("image")
            },
        "image_alternative_text":{
            "type": "Property",
            "value": entity.get("image_alternative_text")
            }
    }  

# -----------------------------------------------------
# Main Conversion Functions
# -----------------------------------------------------

def gtfs_realtime_vehicle_position_to_ngsi_ld() -> list[dict[str, Any]]:
    """
    Convert a GTFS-Realtime VehiclePosition feed into NGSI-LD entities.

    This function:
    - fetches the GTFS-Realtime feed from a configured source
    - parses and normalizes the feed structure
    - converts each VehiclePosition entity into a normalized internal model
    - cleans empty or unused fields
    - transforms the result into NGSI-LD format

    Returns:
        list[dict[str, Any]]: A list of NGSI-LD entities representing
        GTFS-Realtime VehiclePosition data.
    """
    ngsi_ld_entities = []
    
    # Fetch raw GTFS-Realtime feed from the configured source
    api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_VEHICLE_POSITIONS_URL)
    
    # Parse the feed into a GTFS-Realtime FeedMessage
    feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_VEHICLE_POSITIONS_URL)
    
    # Convert the FeedMessage into a Python dictionary
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    
    # Normalize all keys to snake_case for consistent downstream processing
    normal_feed_dict = normalize_keys_to_snake_case(feed_dict)
    
    # Extract GTFS entities from the normalized dict
    entities = normal_feed_dict.get("entity")

    # Process each VehiclePosition entity independently
    for entity in entities:
        
        # Normalize the GTFS VehiclePosition entity into an internal model
        normalized_entity = parse_gtfs_realtime_vehicle_position(entity)
        
        # Remove empty or unused fields from the normalized structure
        cleaned_entity = gtfs_realtime_clean_empty_values(normalized_entity)
        
        # Convert the cleaned model into NGSI-LD format
        ngsi_ld_entity = covert_gtfs_realtime_vehicle_position_to_ngsi_ld(cleaned_entity)
        
        # Final cleanup to remove None values before publishing
        cleaned_ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(cleaned_ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

def gtfs_realtime_trip_updates_to_ngsi_ld() -> list[dict[str, Any]]:
    """
    Convert a GTFS-Realtime TripUpdate feed into NGSI-LD entities.

    This function:
    - fetches the GTFS-Realtime feed from a configured source
    - parses and normalizes the feed structure
    - converts each TripUpdate entity into a normalized internal model
    - cleans empty or unused fields
    - transforms the result into NGSI-LD format

    Returns:
        list[dict[str, Any]]: A list of NGSI-LD entities representing
        GTFS-Realtime TripUpdate data.
    """
    ngsi_ld_entities = []
    
    # Fetch raw GTFS-Realtime feed from the configured source
    api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_TRIP_UPDATES_URL)
    
    # Parse the feed into a GTFS-Realtime FeedMessage
    feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_TRIP_UPDATES_URL)
    
    # Convert the FeedMessage into a Python dictionary
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    
    # Normalize all keys to snake_case for consistent downstream processing
    normal_feed_dict = normalize_keys_to_snake_case(feed_dict)

    # Extract GTFS entities from the normalized dict
    entities = normal_feed_dict.get("entity", [])

    # Process each TripUpdate entity independently
    for entity in entities:
        
        # Normalize the GTFS TripUpdate entity into an internal model
        normalized_entity = parse_gtfs_realtime_trip_updates(entity)
        
        # Remove empty or unused fields from the normalized structure
        cleaned_entity = gtfs_realtime_clean_empty_values(normalized_entity)
        
        # Convert the cleaned model into NGSI-LD format
        ngsi_ld_entity = convert_gtfs_realtime_trip_updates_to_ngsi_ld(cleaned_entity)
        
        # Final cleanup to remove None values before publishing
        cleaned_ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(cleaned_ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

def gtfs_realtime_alerts_to_ngsi_ld() -> list[dict[str, Any]]:
    """
    Convert a GTFS-Realtime Alert feed into NGSI-LD entities.

    This function:
    - fetches the GTFS-Realtime feed from a configured source
    - parses and normalizes the feed structure
    - converts each Alert entity into a normalized internal model
    - cleans empty or unused fields
    - transforms the result into NGSI-LD format

    Returns:
        list[dict[str, Any]]: A list of NGSI-LD entities representing
        GTFS-Realtime Alert data.
    """
    ngsi_ld_entities = []

    # Fetch raw GTFS-Realtime feed from the configured source
    api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_ALERTS_URL)
    
    # Parse the feed into a GTFS-Realtime FeedMessage
    feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_ALERTS_URL)
    
    # Convert the FeedMessage into a Python dictionary
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    
    # Normalize all keys to snake_case for consistent downstream processing
    normal_feed_dict = normalize_keys_to_snake_case(feed_dict)

    # Extract GTFS entities from the normalized dict
    entities = normal_feed_dict.get("entity")

    # Process each Alert entity independently
    for entity in entities:
        
        # Normalize the GTFS Alert entity into an internal model
        normalized_entity = parse_gtfs_realtime_alerts(entity)

        # Remove empty or unused fields from the normalized structure
        cleaned_entity =gtfs_realtime_clean_empty_values(normalized_entity)
        
        # Convert the cleaned model into NGSI-LD format
        ngsi_ld_entity = convert_gtfs_realtime_alerts_to_ngsi_ld(cleaned_entity)
        
        # Final cleanup to remove None values before publishing
        cleaned_ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(cleaned_ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

# -----------------------------------------------------
# High-level function to get NGSI-LD data
# ----------------------------------------------------- 

def gtfs_realtime_get_ngsi_ld_data(type: str) -> list[dict[str, Any]]:
    """
    Route GTFS-Realtime feed processing based on entity type and return NGSI-LD data.

    Supported GTFS-Realtime types:
        - "VehiclePosition"
        - "TripUpdate"
        - "Alert"

    Args:
        type (str): GTFS-Realtime entity type to process.

    Returns:
        list[dict[str, Any]]: A list of NGSI-LD entities corresponding to the
        requested GTFS-Realtime feed type.

    Raises:
        ValueError: If the provided type is unknown or unsupported.
    """
    
    # Route VehiclePosition feed to its NGSI-LD transformation pipeline
    if type == "VehiclePosition":
        return gtfs_realtime_vehicle_position_to_ngsi_ld()
    
    # Route TripUpdate feed to its NGSI-LD transformation pipeline
    elif type == "TripUpdate":
        return gtfs_realtime_trip_updates_to_ngsi_ld()
    
    # Route Alert feed to its NGSI-LD transformation pipeline
    elif type == "Alert":
        return gtfs_realtime_alerts_to_ngsi_ld()
    
    # Reject unsupported or unknown GTFS-Realtime types
    else:
        raise ValueError("Unknown / Unsupported GTFS Realtime type")