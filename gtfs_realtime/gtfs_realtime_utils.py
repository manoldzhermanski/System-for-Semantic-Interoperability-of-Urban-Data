import os
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
# Normalization Functions
# -----------------------------------------------------
def gtfs_realtime_normalize_trip_descriptor_message(trip: dict) -> dict[str, Any]:
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

    # Extract nested modified_trip dictionary if present
    modified_trip = trip.get("modified_trip")

    return {
        "trip_id": trip.get("trip_id"),
        "route_id": trip.get("route_id"),
        "direction_id": trip.get("direction_id"),
        "start_time": trip.get("start_time"),
        "start_date": trip.get("start_date"),
        "schedule_relationship": trip.get("schedule_relationship"),

        # Normalize modified_trip; return None values if a field is missing
        "modified_trip": {
            "modifications_id": modified_trip.get("modifications_id") if modified_trip else None,
            "affected_trip_id": modified_trip.get("affected_trip_id") if modified_trip else None,
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

def gtfs_realtime_normalize_vehicle_position(entity: dict[str, Any]) -> dict[str, Any]:
    return {}

def gtfs_realtime_normalize_trip_updates(entity: dict[str, Any]) -> dict[str, Any]:
    return {}

def gtfs_realtime_normalize_alerts(entity: dict[str, Any]) -> dict[str, Any]:
    
    alert_info = entity.get("alert")
    alert_active_period = [
        {
            "start": period.get("start"),
            "end": period.get("end")
        }
        for period in (alert_info.get("activePeriod") if alert_info else [])
    ]
    
    alert_info_infromed_entity = alert_info.get("informedEntity") if alert_info else []
    
    alert_informed_entity = [
        {
            "agency_id": infromed_entity.get("agency_id"),
            "route_id": infromed_entity.get("route_id"),
            "route_type": infromed_entity.get("route_type"),
            "direction_id": infromed_entity.get("direction_id"),
            "trip": gtfs_realtime_normalize_trip_descriptor_message(infromed_entity.get("trip")),
            "stop_id": infromed_entity.get("stop_id")
        }
        for infromed_entity in alert_info_infromed_entity
    ]
    
    alert_cause = alert_info.get("cause") if alert_info else None
    alert_effect = alert_info.get("effect") if alert_info else None
    alert_severity_level = alert_info.get("severity_level") if alert_info else None
    
    cause_detail_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "cause_detail")    
    effect_detail_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "effect_detail")
    url_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "url")
    header_text_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "header_text")
    description_text_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "description_text")
    tts_header_text_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "tts_header_text")
    tts_description_text_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "tts_description_text")
    image_alternative_text_translation = gtfs_realtime_normalize_translated_string_message(alert_info, "image_alternative_text")
    
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
        "id": entity.get("id"),
        "active_period": alert_active_period,
        "informed_entity": alert_informed_entity,
        "cause": alert_cause,
        "cause_detail": {
            "translation": cause_detail_translation
            },
        "effect": alert_effect,
        "effect_detail": {
            "translation": effect_detail_translation
            },
        "url": {
            "translation": url_translation
            },
        "header_text": {
            "translation": header_text_translation
            },
        "description_text": {
            "translation": description_text_translation
            },
        "tts_header_text": {
            "translation": tts_header_text_translation
            },
        "tts_description_text": {
            "translation": tts_description_text_translation
            },
        "severity_level": alert_severity_level,
        "image": {
            "localized_image": localized_images
            },
        "image_alternative_text": {
            "translation": image_alternative_text_translation
            },
    }

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
    #ngsi_ld_fеed = gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_fеed, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))

    #api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_TRIP_UPDATES_URL)
    #feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_TRIP_UPDATES_URL)
    #feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    #ngsi_ld_trip_updates = gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_trip_updates, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))

    api_response = gtfs_realtime_get_feed(config.GtfsSource.GTFS_REALTIME_ALERTS_URL)
    feed_data = gtfs_realtime_parse_feed(api_response, config.GtfsSource.GTFS_REALTIME_ALERTS_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    #ngsi_ld_alerts = gtfs_realtime_alerts_to_ngsi_ld(feed_dict)
    print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    #print(json.dumps(ngsi_ld_alerts, indent=2, ensure_ascii=False))
    pass