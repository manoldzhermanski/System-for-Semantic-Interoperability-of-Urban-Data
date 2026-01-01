import os
import re
import sys
import json
import requests
from google.transit.gtfs_realtime_pb2 import FeedMessage # type: ignore
from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict
from typing import Any
from datetime import datetime, timezone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

def unix_to_iso8601(timestamp: int) -> str:
    """
    Convert UNIX timestamp (seconds) to ISO 8601 UTC string.
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def iso8601_to_unix(timestamp: str) -> int:
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp

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
            a primitive value (e.g. str, int, None).

    Returns:
        Any: A new data structure with all dictionary keys converted to
        snake_case. Primitive values are returned unchanged.
    """

    if isinstance(data, dict):
        return {
            to_snake_case(key): normalize_keys_to_snake_case(value)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [normalize_keys_to_snake_case(item) for item in data]

    return data

def to_ngsi_ld_urn(value: Any, entity_type: str) -> Any:
    if value is None:
        return None
    return f"urn:ngsi-ld:{entity_type}:{value}"

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
    
    if vehicle is None:
        return {}
    
    return {
        "id": to_ngsi_ld_urn(vehicle.get("id"), "GtfsVehicle"),
        "label": vehicle.get("label"),
        "license_plate": vehicle.get("license_plate"),
        "wheelchair_accessible": vehicle.get("wheelchair_accessible")
    }

def gtfs_realtime_clean_empty_values(value: Any) -> Any:
    """
    Recursively removes:
    - None
    - empty dicts {}
    - empty lists []

    If after pruning a structure becomes empty,
    it is removed as well.
    """

    # None → remove
    if value is None:
        return None

    # List → prune items
    if isinstance(value, list):
        result = []
        for item in value:
            pruned = gtfs_realtime_clean_empty_values(item)
            if pruned is not None:
                result.append(pruned)
        return result if result else None

    # Dict → prune keys
    if isinstance(value, dict):
        result = {}
        for key, val in value.items():
            pruned = gtfs_realtime_clean_empty_values(val)
            if pruned is not None:
                result[key] = pruned
        return result if result else None

    # Primitive → keep
    return value

# -----------------------------------------------------
# GTFS Realtime to NGSI-LD Parsing Functions
# -----------------------------------------------------

def parse_gtfs_realtime_vehicle_position(entity: dict[str, Any]) -> dict[str, Any]:
    vehicle_info = entity.get("vehicle")
    vehicle_info_trip = vehicle_info.get("trip") if vehicle_info else None
    vehicle_info_vehicle = vehicle_info.get("vehicle") if vehicle_info else None
    multi_carriage_details = vehicle_info.get("multi_carriage_details", []) if vehicle_info else []
    
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
    trip_update_info = entity.get("trip_update")
    trip_udate_info_trip = trip_update_info.get("trip") if trip_update_info else None
    trip_update_info_vehicle = trip_update_info.get("vehicle") if trip_update_info else None
    stop_time_update = trip_update_info.get("stop_time_update", []) if trip_update_info else []
    trip_update_info_trip_properties = trip_update_info.get("trip_properties") if trip_update_info else None
    
    
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
    
    alert_info = entity.get("alert")
    alert_active_period = [
        {
            "start": unix_to_iso8601(int(period.get("start"))),
            "end": unix_to_iso8601(int(period.get("end")))
        }
        for period in (alert_info.get("active_period") if alert_info else [])
    ]
    
    alert_info_infromed_entity = alert_info.get("informed_entity") if alert_info else []
    
    alert_informed_entity = [
        {
            "agency_id": to_ngsi_ld_urn(infromed_entity.get("agency_id"), "GtfsAgency"),
            "route_id": to_ngsi_ld_urn(infromed_entity.get("route_id"), "GtfsRoute"),
            "route_type": infromed_entity.get("route_type"),
            "direction_id": infromed_entity.get("direction_id"),
            "trip": gtfs_realtime_normalize_trip_descriptor_message(infromed_entity.get("trip")),
            "stop_id": to_ngsi_ld_urn(infromed_entity.get("stop_id"), "GtfsStop")
        }
        for infromed_entity in alert_info_infromed_entity
    ]
    
    alert_cause = alert_info.get("cause") if alert_info else None
    alert_effect = alert_info.get("effect") if alert_info else None
    alert_severity_level = alert_info.get("severity_level") if alert_info else None
        
    translated_fields = ["cause_detail", "effect_detail", "url", "header_text", "description_text",
                         "tts_header_text", "tts_description_text", "image_alternative_text"]

    translations = {
        field: gtfs_realtime_normalize_translated_string_message(alert_info, field)
        for field in translated_fields
    }

    
    alert_image = alert_info.get("image") if alert_info else None
    alert_image_localized_image = alert_image.get("localized_image") if alert_image else []
    localized_images = [
        {
            "url": image.get("url"),
            "media_type": image.get("media_type"),
            "language": image.get("language")
        }
        for image in alert_image_localized_image
    ]
    
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
    message into an NGSI-LD compatible entity.

    The function:
    - Generates a stable NGSI-LD URN for the vehicle position entity
    - Embeds normalized GTFS TripDescriptor and VehicleDescriptor data
    - Converts positional and status fields into NGSI-LD Properties
    - Preserves multi-carriage occupancy information if present

    Args:
        entity (dict[str, Any]):
            A normalized GTFS-Realtime VehiclePosition message.
            Expected structure includes a "vehicle" field containing
            trip, vehicle, position, and occupancy-related data.

    Returns:
        dict[str, Any]:
            An NGSI-LD entity dictionary with the following structure:
            {
                "id": str,
                "trip": { "type": "Property", "value": dict },
                "vehicle": { "type": "Property", "value": dict },
                "position": { "type": "Property", "value": dict },
                "current_stop_sequence": { "type": "Property", "value": int | None },
                "stop_id": { "type": "Property", "value": str | None },
                "current_status": { "type": "Property", "value": str | None },
                "timestamp": { "type": "Property", "value": str | None },
                "congestion_level": { "type": "Property", "value": str | None },
                "occupancy_status": { "type": "Property", "value": str | None },
                "occupancy_percentage": { "type": "Property", "value": int | None },
                "multi_carriage_details": { "type": "Property", "value": list[dict] }
            }

    Notes:
        - This function does NOT create new entities per update.
          It follows a state-based NGSI-LD model.
        - Missing fields are mapped to None.
        - Timestamp values are converted from Unix time to ISO 8601.
    """
    vehicle_info = entity.get("vehicle")
    vehicle_info_trip = vehicle_info.get("trip") if vehicle_info else None
    vehicle_info_vehicle = vehicle_info.get("vehicle") if vehicle_info else None
    multi_carriage_details = vehicle_info.get("multi_carriage_details", []) if vehicle_info else []
    
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
    
    return {
        "id": to_ngsi_ld_urn(entity.get("id"), "GtfsRealtimeVehiclePosition"),
        "type": "GtfsRealtimeVehiclePosition",
        "trip": {
            "type": "Property",
            "value": gtfs_realtime_normalize_trip_descriptor_message(vehicle_info_trip)
        },
        "vehicle": {
            "type": "Property",
            "value": gtfs_realtime_normalize_vehicle_descriptor_message(vehicle_info_vehicle)
            },
        "position": {
            "type": "Property",
            "value": {
                "latitude": vehicle_info.get("position").get("latitude") if vehicle_info else None,
                "longitude": vehicle_info.get("position").get("longitude") if vehicle_info else None,
                "bearing": vehicle_info.get("position").get("bearing") if vehicle_info else None,
                "odometer": vehicle_info.get("position").get("odometer") if vehicle_info else None,
                "speed": vehicle_info.get("position").get("speed") if vehicle_info else None,
                }
            },
        "current_stop_sequence": {
            "type": "Property",
            "value": vehicle_info.get("current_stop_sequence") if vehicle_info else None,
            },
        "stop_id": {
            "type": "Relationship",
            "object": to_ngsi_ld_urn(vehicle_info.get("stop_id"), "GtfsStop") if vehicle_info else None
            },
        "current_status": {
            "type": "Property",
            "value": vehicle_info.get("current_status") if vehicle_info else None
            },
        "timestamp": {
            "type": "Property",
            "value": unix_to_iso8601(int(vehicle_info.get("timestamp"))) if vehicle_info else None,
            },
        "congestion_level": {
            "type": "Property",
            "value": vehicle_info.get("congestion_level") if vehicle_info else None,
            },
        "occupancy_status": {
            "type": "Property",
            "value": vehicle_info.get("occupancy_status") if vehicle_info else None,
            },
        "occupancy_percentage": {
            "type": "Property",
            "value": vehicle_info.get("occupancy_percentage") if vehicle_info else None,
            },
        "multi_carriage_details": {
            "type": "Property",
            "value": carriage_details
            },
    }

def convert_gtfs_realtime_trip_updates_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    trip_update_info = entity.get("trip_update")
    trip_udate_info_trip = trip_update_info.get("trip") if trip_update_info else None
    trip_update_info_vehicle = trip_update_info.get("vehicle") if trip_update_info else None
    stop_time_update = trip_update_info.get("stop_time_update", []) if trip_update_info else []
    trip_update_info_trip_properties = trip_update_info.get("trip_properties") if trip_update_info else None
    
    
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
    
    return {
        "id": to_ngsi_ld_urn(entity.get("id"), "GtfsRealtimeTripUpdate"),
        "type": "GtfsRealtimeTripUpdate",
        "trip": {
            "type": "Property",
            "value": gtfs_realtime_normalize_trip_descriptor_message(trip_udate_info_trip)
        },
        "vehicle": {
            "type": "Property",
            "value": gtfs_realtime_normalize_vehicle_descriptor_message(trip_update_info_vehicle)
        },
        "stop_time_update": {
            "type": "Property",
            "value": stop_time_updates
        },
        "timestamp": {
            "type": "Property",
            "value": unix_to_iso8601(int(trip_update_info.get("timestamp"))) if trip_update_info else None
        },
        "delay": {
            "type": "Property",
            "value": trip_update_info.get("delay") if trip_update_info else None
        },
        "trip_properties": {
            "type": "Property",
            "value": {
                "trip_id": to_ngsi_ld_urn(trip_update_info_trip_properties.get("trip_id"), "GtfsTrip") if trip_update_info_trip_properties else None,
                "start_date": trip_update_info_trip_properties.get("start_date") if trip_update_info_trip_properties else None,
                "start_time": trip_update_info_trip_properties.get("start_time") if trip_update_info_trip_properties else None,
                "trip_headsign": trip_update_info_trip_properties.get("trip_headsign") if trip_update_info_trip_properties else None,
                "trip_short_name": trip_update_info_trip_properties.get("trip_short_name") if trip_update_info_trip_properties else None,
                "shape_id": to_ngsi_ld_urn(trip_update_info_trip_properties.get("shape_id"), "GtfsShape") if trip_update_info_trip_properties else None
            }
        }
    }

def convert_gtfs_realtime_alerts_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    
    alert_info = entity.get("alert")
    alert_active_period = [
        {
            "start": unix_to_iso8601(int(period.get("start"))),
            "end": unix_to_iso8601(int(period.get("end")))
        }
        for period in (alert_info.get("active_period") if alert_info else [])
    ]
    
    alert_info_infromed_entity = alert_info.get("informed_entity") if alert_info else []
    
    alert_informed_entity = [
        {
            "agency_id": to_ngsi_ld_urn(infromed_entity.get("agency_id"), "GtfsAgency"),
            "route_id": to_ngsi_ld_urn(infromed_entity.get("route_id"), "GtfsRoute"),
            "route_type": infromed_entity.get("route_type"),
            "direction_id": infromed_entity.get("direction_id"),
            "trip": gtfs_realtime_normalize_trip_descriptor_message(infromed_entity.get("trip")),
            "stop_id": to_ngsi_ld_urn(infromed_entity.get("stop_id"), "GtfsStop")
        }
        for infromed_entity in alert_info_infromed_entity
    ]
    
    alert_cause = alert_info.get("cause") if alert_info else None
    alert_effect = alert_info.get("effect") if alert_info else None
    alert_severity_level = alert_info.get("severity_level") if alert_info else None
        
    translated_fields = ["cause_detail", "effect_detail", "url", "header_text", "description_text",
                         "tts_header_text", "tts_description_text", "image_alternative_text"]

    translations = {
        field: gtfs_realtime_normalize_translated_string_message(alert_info, field)
        for field in translated_fields
    }

    
    alert_image = alert_info.get("image") if alert_info else None
    alert_image_localized_image = alert_image.get("localized_image") if alert_image else []
    localized_images = [
        {
            "url": image.get("url"),
            "media_type": image.get("media_type"),
            "language": image.get("language")
        }
        for image in alert_image_localized_image
    ]
    
    return {
        "id": to_ngsi_ld_urn(entity.get("id"), "GtfsRealtimeAlert"),
        "type": "GtfsRealtimeAlert",
        "active_period": {
            "type": "Property",
            "value": alert_active_period
            },
        "informed_entity": {
            "type": "Property",
            "value": alert_informed_entity
            },
        "cause": {
            "type": "Property",
            "value": alert_cause
            },
        "cause_detail": {
            "type": "Property",
            "value": {
                "translation": translations["cause_detail"]
                }
            },
        "effect": {
            "type": "Property",
            "value": alert_effect
            },
        "effect_detail": {
            "type": "Property",
            "value": {
                "translation": translations["effect_detail"]
                }
            },
        "url":{
            "type": "Property",
            "value": {
                "translation": translations["url"]
                }
            },
        "header_text": {
            "type": "Property",
            "value": {
                "translation": translations["header_text"]
                }
            },
        "description_text": {
            "type": "Property",
            "value": {
                "translation": translations["description_text"]
                }
            },
        "tts_header_text": {
            "type": "Property",
            "value": {
                "translation": translations["tts_header_text"]
                }
            },
        "tts_description_text":{
            "type": "Property",
            "value": {
                "translation": translations["tts_description_text"]
                }
            },
        "severity_level": {
            "type": "Property",
            "value": alert_severity_level
            },
        "image": {
            "type": "Property",
            "value": {
                "localized_image": localized_images
                }
            },
        "image_alternative_text":{
            "type": "Property",
            "value": {
                "translation": translations["image_alternative_text"]
                }
            }
    }  
# -----------------------------------------------------
# Main Conversion Functions
# -----------------------------------------------------

def gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime Vehicle Position Feed (from MessageToDict) to a list of NGSI-LD entities.
    Args:
        feed_dict (dict[str, Any]): Dictionary of feed data
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS Realtime Alert data.
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        vehicle_position_id = entity.get("id")
        vehicle_position_trip_id = f"urn:ngsi-ld:GtfsTrip:{entity.get('vehicle').get('trip').get('tripId')}" if entity.get('vehicle').get('trip').get('tripId') else None
        vehicle_position_trip_schedule_relationship = entity.get('vehicle').get('trip').get('scheduleRelationship') or None
        vehicle_position_trip_route_id = f"urn:ngsi-ld:GtfsRoute:{entity.get('vehicle').get('trip').get('routeId')}" if entity.get('vehicle').get('trip').get('routeId') else None
        longitude = float(entity.get('vehicle').get('position').get('longitude')) or 0.0
        latitude = float(entity.get('vehicle').get('position').get('latitude')) or 0.0
        vehicle_position_speed = float(entity.get('vehicle').get('position').get('speed')) or -1.0
        vehicle_position_current_status = entity.get('vehicle').get('currentStatus') or None
        vehicle_position_timestamp = unix_to_iso8601(int(entity.get('vehicle').get('timestamp'))) or None
        vehicle_position_congestion_level = entity.get('vehicle').get('congestionLevel') or None
        vehicle_position_stop_id = f"urn:ngsi-ld:GtfsStop:{entity.get('vehicle').get('stopId')}" if entity.get('vehicle').get('stopId') else None
        vehicle_position_vehicle_id = f"urn:ngsi-ld:Vehicle:{entity.get('vehicle').get('vehicle').get('id')}" if entity.get('vehicle').get('vehicle').get('id') else None
        vehicle_position_occupancy_status = entity.get('vehicle').get('occupancyStatus') or None
        
        # Create custom data model and populate it
        ngsi_ld_entity = {
            "id": f"urn:ngsi-ld:GtfsRealtimeVehiclePosition:{vehicle_position_id}",
            "type": "GtfsRealtimeVehiclePosition",
            "trip_id": {
                "type": "Relationship",
                "object": vehicle_position_trip_id
            },
            "schedule_relationship": {
                "type": "Property",
                "value": vehicle_position_trip_schedule_relationship
            },
            "route_id": {
                "type": "Relationship",
                "object": vehicle_position_trip_route_id
            },
            "position": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                    }  
            },
            "speed": {
                "type": "Property",
                "value": vehicle_position_speed
                },                
            "current_status": {
                "type": "Property",
                "value": vehicle_position_current_status
            },
            
            "timestamp": {
                "type": "Property",
                "value": vehicle_position_timestamp
            },
            
            "congestion_level": {
                "type": "Property",
                "value": vehicle_position_congestion_level
            },
            
            "stop_id": {
                "type": "Relationship",
                "object": vehicle_position_stop_id
            },
            
            "vehicle_id": {
                "type": "Relationship",
                "object": vehicle_position_vehicle_id
            },
            
            "occupancy_status": {
                "type": "Property",
                "value": vehicle_position_occupancy_status
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_entity = {
            k: v for k, v in ngsi_ld_entity.items()
            if not (isinstance(v, dict) and (None or -1.0) in v.values())
        }
        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

def gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime Trip Update feed (from MessageToDict) to a list of NGSI-LD entities.
    Args:
        feed_dict (dict[str, Any]): Dictionary of feed data
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS Realtime Alert data.
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        trip_update_id = entity.get('id')
        trip_update_is_deleted = entity.get('isDeleted') or False
        trip_udate_trip_id = f"urn:ngsi-ld:GtfsTrip:{entity.get('tripUpdate').get('trip').get('tripId')}" if entity.get('tripUpdate').get('trip').get('tripId') else ""
        trip_update_schedule_relationship = entity.get('tripUpdate').get('trip').get('scheduleRelationship') or ""
        trip_update_route_id = f"urn:ngsi-ld:GtfsRoute:{entity.get('tripUpdate').get('trip').get('routeId')}" if entity.get('tripUpdate').get('trip').get('routeId') else ""
        

        # Get the stop time updates and convert them to a list of entities
        stop_time_updates = entity.get("tripUpdate").get("stopTimeUpdate")
        stop_time_updates_list = []

        # Iterate through each stop time update and convert to NGSI-LD format
        for stop_time_update in stop_time_updates:
            
            arrival_time = unix_to_iso8601(int(stop_time_update.get('arrival').get('time'))) if stop_time_update.get('arrival').get('time') else ""
            arrival_uncertainty = stop_time_update.get('arrival').get('uncertainty') or 0
            departure_time = unix_to_iso8601(int(stop_time_update.get('departure').get('time'))) if stop_time_update.get('departure').get('time') else ""
            departure_uncertainty = stop_time_update.get('departure').get('uncertainty') or 0
            stop_time_update_stop_id = f"urn:ngsi-ld:GtfsStop:{stop_time_update.get('stopId')}" if stop_time_update.get('stopId') else ""
            stop_time_schedule_relationship = stop_time_update.get('scheduleRelationship')
            
            # Create a dictionary for the stop time entity
            stop_time_entity = {
                "arrival": {
                    "type": "Property",
                    "value": {
                        "time": arrival_time,
                        "uncertainty": arrival_uncertainty
                    }
                },
                
                "departure": {
                    "type": "Property",
                    "value": {
                        "time": departure_time,
                        "uncertainty": departure_uncertainty
                    }
                },
                
                "stop_id": {
                    "type": "Relationship",
                    "object": stop_time_update_stop_id
                },
                
                "schedule_relationship": {
                    "type": "Property",
                    "value": stop_time_schedule_relationship
                }
            }
            
            # Append the stop time entity to the list
            stop_time_updates_list.append(stop_time_entity)
                
        # Create custom data model and populate it
        ngsi_ld_entity = {
            "id": f"urn:ngsi-ld:GtfsTripUpdate:{trip_update_id}",
            "type": "GtfsRealtimeTripUpdate",
            "is_deleted": {
                "type": "Property",
                "value": trip_update_is_deleted
            },
            "trip_id": {
                "type": "Relationship",
                "object": trip_udate_trip_id
            },
            "schedule_relationship": {
                "type": "Property",
                "value": trip_update_schedule_relationship
            },
            "route_id": {
                "type": "Relationship",
                "object": trip_update_route_id
            },
            "stop_time_update": {
                "type": "Property",
                "value": stop_time_updates_list
            }          
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_entity = {
            k: v for k, v in ngsi_ld_entity.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

def gtfs_realtime_alerts_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime alerts feed (from MessageToDict) to a list of NGSI-LD entities.
    Args:
        feed_dict (dict[str, Any]): Dictionary of feed data
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS Realtime Alert data.
    
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        
        # Set alert id
        alert_id = entity.get('id')
        
        # Get alert active periods
        alert_active_periods = entity.get('alert').get('activePeriod')
        
        active_periods_list = []
        
        # Traverse through all start and end active periods
        for active_period in alert_active_periods:
            
            # Turn into ISO 8601 date format    
            start_of_period = unix_to_iso8601(int(active_period.get('start'))) if active_period.get('start') else ""
            end_of_period = unix_to_iso8601(int(active_period.get('end'))) if active_period.get('end') else ""
                
            period = {
                "active_period_start": {
                    "type": "Property",
                    "value": start_of_period
                },
                "active_period_end": {
                    "type": "Property",
                    "value": end_of_period
                }
            }

            # Append active periods
            active_periods_list.append(period)
        
        # Get informed entities
        informed_entities = entity.get('alert').get('informedEntity')
        informed_entities_list = []
        
        # Iterate through all routes in the informedEntity
        for informed_entity in informed_entities:
            
            route_id = f"urn:ngsi-ld:GtfsRoute:{informed_entity.get('routeId')}" if informed_entity.get('routeId') else ""
            
            entity_obj = {
                "route_id": {
                    "type": "Relationship",
                    "object": route_id
                }
            }
            # Append the routes from informedEntity
            informed_entities_list.append(entity_obj)
        
        # Get cause and effect of the alert
        alert_cause = entity.get('alert').get('cause')
        alert_effect = entity.get('alert').get('effect')
        
        # Get Url text translation    
        alert_url_translations = entity.get('alert').get('url').get('translation')
        alert_url_translation_list = []
        
        # Iterate through url translations
        for alert_url_translation in alert_url_translations:
            
            alert_url_translations_text = alert_url_translation.get('text') or ""
            alert_url_translations_language = alert_url_translation.get('language') or ""
            
            translation = {
                "alert_url_text": {
                    "type": "Property",
                    "value": alert_url_translations_text
                },
                
                "alert_url_language": {
                    "type": "Property",
                    "value": alert_url_translations_language
                }
            }
            # Append trnaslation
            alert_url_translation_list.append(translation)
            
        # Get Header text translation    
        alert_header_translations = entity.get('alert').get('headerText').get('translation')
        alert_header_translation_list = []
        
        # Iterate through the header translations
        for alert_header_translation in alert_header_translations:
            
            alert_header_translations_text = alert_header_translation.get('text') or ""
            alert_header_translations_language = alert_header_translation.get('language') or ""
            
            translation = {
                "alert_header_text": {
                    "type": "Property",
                    "value": alert_header_translations_text
                },
                
                "alert_header_language": {
                    "type": "Property",
                    "value": alert_header_translations_language
                }
            }
            
            # Append translation
            alert_header_translation_list.append(translation)
        
        # Get Description text translation    
        alert_description_translations = entity.get('alert').get('descriptionText').get('translation')
        alert_description_translation_list = []
        
        # Iterate though the alert description translations
        for alert_description_translation in alert_description_translations:
            
            alert_description_translations_text = alert_description_translation.get('text') or ""
            alert_description_translations_language = alert_description_translation.get('language') or ""
            
            translation = {
                "alert_description_text": {
                    "type": "Property",
                    "value": alert_description_translations_text
                },
                
                "alert_description_language": {
                    "type": "Property",
                    "value": alert_description_translations_language
                }
            }

            # Append translation
            alert_description_translation_list.append(translation)
        
        # Create custom data model
        ngsi_ld_entity = {
            "id": f"urn:ngsi-ld:GtfsAlert:{alert_id}",
            "type": "GtfsRealtimeAlert",
            "active_period": {
                "type": "Property",
                "value": active_periods_list
            },   
            "informed_entity": {
                "type": "Property",
                "value": informed_entities_list
            },   
            "alert_cause": {
                "type": "Property",
                "value": alert_cause
            },             
            "alert_effect": {
                "type": "Property",
                "value": alert_effect
            },     
            "url_translation": {
                "type": "Property",
                "value": alert_url_translation_list
            },               
            "alert_header_translation": {
                "type": "Property",
                "value": alert_header_translation_list
            },
            "alert_description_translation": {
                "type": "Property",
                "value": alert_description_translation_list
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_entity = {
            k: v for k, v in ngsi_ld_entity.items()
            if not (isinstance(v, dict) and None in v.values())
        }

        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities


if __name__ == "__main__":
    #api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_VEHICLE_POSITIONS_URL)
    #feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_VEHICLE_POSITIONS_URL)
    #feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    #normal_feed_dict = normalize_keys_to_snake_case(feed_dict)
    #vehicle_position = normal_feed_dict.get("entity")
    #normal_position = parse_gtfs_realtime_vehicle_position(vehicle_position[0])
    #cleaned_position = gtfs_realtime_clean_empty_values(normal_position)
    #print(json.dumps(cleaned_position, indent=2, ensure_ascii=False))
    
    #for position in vehicle_position:
    #    normal_position = parse_gtfs_realtime_vehicle_position(position)
    #    print(json.dumps(normal_position, indent=2, ensure_ascii=False))
    
    #normalized_feed_dict = gtfs_realtime_normalize_vehicle_position(normal_feed_dict)
    #ngsi_ld_fеed = gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_fеed, indent=2, ensure_ascii=False))
    #print(json.dumps(normal_feed_dict, indent=2, ensure_ascii=False))

    api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_TRIP_UPDATES_URL)
    feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_TRIP_UPDATES_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    normal_feed_dict = normalize_keys_to_snake_case(feed_dict)
    trip_update = normal_feed_dict.get("entity")
    normal_position = parse_gtfs_realtime_trip_updates(trip_update[0])
    cleaned_normal_position = gtfs_realtime_clean_empty_values(normal_position)
    print(json.dumps(cleaned_normal_position, indent=2, ensure_ascii=False))
    
    #for update in trip_update:
    #    normal_position = parse_gtfs_realtime_trip_updates(update)
    #    #cleaned_normal_position = gtfs_realtime_clean_empty_values(normal_position)
    #    print(json.dumps(normal_position, indent=2, ensure_ascii=False))
    
    #ngsi_ld_trip_updates = gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_trip_updates, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))

    api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_ALERTS_URL)
    feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_ALERTS_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    normal_feed_dict = normalize_keys_to_snake_case(feed_dict)
    alerts = normal_feed_dict.get("entity")
    normal_position = parse_gtfs_realtime_alerts(alerts[0])
    cleaned_normal_position =gtfs_realtime_clean_empty_values(normal_position)
    print(json.dumps(cleaned_normal_position, indent=2, ensure_ascii=False))
    
    #for alert in alerts:
    #    normal_position = parse_gtfs_realtime_alerts(alert)
        #cleaned_normal_position =gtfs_realtime_clean_empty_values(normal_position)
    #    print(json.dumps(normal_position, indent=2, ensure_ascii=False))

    #ngsi_ld_alerts = gtfs_realtime_alerts_to_ngsi_ld(feed_dict)
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    #print(json.dumps(ngsi_ld_alerts, indent=2, ensure_ascii=False))
    pass