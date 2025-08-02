import os
import sys
import json
import requests
from gtfs_realtime_pb2 import FeedMessage
from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict
from typing import Any
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config


def unix_to_iso8601(ts: int) -> str:
    """
    Convert UNIX timestamp (seconds) to ISO8601 UTC string.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def get_gtfs_realtime_feed(api_endpoint: str) -> bytes:
    """
    Based on the API endpoint, sends a GET request to fetch the GTFS-Realtime feed.
    """
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint}: {e}")
        
def parse_gtfs_realtime_feed(feed_data: bytes, api_endpoint: str = None) -> FeedMessage:
    """
    Parses the GTFS-Realtime feed data into a FeedMessage object.
    Provide an optional api_endpoint for debugging purposes.
    """
    feed = FeedMessage()
    try:
        feed.ParseFromString(feed_data)
    except DecodeError as e:
        endpoint_info = f" from {api_endpoint}" if api_endpoint else ""
        raise ValueError(f"Error parsing GTFS-Realtime feed data from {endpoint_info}: {e}")
    return feed

def gtfs_realtime_feed_to_dict(feed_data: FeedMessage) -> MessageToDict:
    """
    Converts a FeedMessage object to a dictionary using MessageToDict.
    """
    feed_dict = MessageToDict(feed_data)
    return feed_dict

def gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime Vehicle Position Feed (from MessageToDict) to a list of NGSI-LD entities.
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        
        vehicle_position_id = entity.get("id")  or str(uuid.uuid4())
        vehicle_position_trip_id = f"urn:ngsi-ld:GtfsTrip:{entity.get('vehicle').get('trip').get('tripId')}" if entity.get('vehicle').get('trip').get('tripId') else ""
        vehicle_position_trip_schedule_relationship = entity.get('vehicle').get('trip').get('scheduleRelationship') or ""
        vehicle_position_trip_route_id = f"urn:ngsi-ld:GtfsRoute:{entity.get('vehicle').get('trip').get('routeId')}" if entity.get('vehicle').get('trip').get('routeId') else ""
        longitude = float(entity.get('vehicle').get('position').get('longitude')) or 0.0
        latitude = float(entity.get('vehicle').get('position').get('latitude')) or 0.0
        vehicle_position_speed = float(entity.get('vehicle').get('position').get('speed')) or 0.0
        vehicle_position_current_status = entity.get('vehicle').get('currentStatus') or ""
        vehicle_position_timestamp = unix_to_iso8601(int(entity.get('vehicle').get('timestamp'))) or ""
        vehicle_position_congestion_level = entity.get('vehicle').get('congestionLevel')
        vehicle_position_stop_id = f"urn:ngsi-ld:GtfsStop:{entity.get('vehicle').get('stopId')}" if entity.get('vehicle').get('stopId') else ""
        vehicle_position_vehicle_id = f"urn:ngsi-ld:Vehicle:{entity.get('vehicle').get('vehicle').get('id')}" if entity.get('vehicle').get('vehicle').get('id') else ""
        vehicle_position_occupancy_status = entity.get('vehicle').get('occupancyStatus') or ""
        
        # Create the base NGSI-LD entity structure
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
                "type": "Property",
                "value": vehicle_position_trip_route_id
            },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        longitude,
                        latitude
                    ]
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
            
            "vehicle": {
                "type": "Relationship",
                "object": vehicle_position_vehicle_id
            },
            
            "occupancy_status": {
                "type": "Property",
                "value": vehicle_position_occupancy_status
            },
            
            "@context":
                [
                    "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
            
        }
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_ld_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

def gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime Trip Update feed (from MessageToDict) to a list of NGSI-LD entities.
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        
        trip_update_id = entity.get('id') or str(uuid.uuid4())
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
                
        # Create the base NGSI-LD entity structure
        ngsi_entity = {
            "id": f"urn:ngsi-ld:GtfsTripUpdate:{trip_update_id}",
            "type": "GtfsRealtimeTripUpdate",
            
            "is_deleted": {
                "type": "Property",
                "value": trip_update_is_deleted
            },
            
            "trip_update": {
                "type": "Property",
                "value": {
                    "trip": {
                        "type": "Property",
                        "value": {
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
                        }
                    },
                    
                    "stop_time_update": {
                        "type": "Property",
                        "value": stop_time_updates_list
                    }
                }
            },
                      
            "@context": [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]            
        }
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities

def gtfs_realtime_alerts_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime alerts feed (from MessageToDict) to a list of NGSI-LD entities.
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        # Create the base NGSI-LD entity structure 
        
        alert_cause = entity.get('alert').get('cause')
        alert_effect = entity.get('alert').get('effect')
        alert_url_translations = entity.get('alert').get('url').get('translation')
        alert_header_translations = entity.get('alert').get('headerText').get('translation')
        alert_description_translations = entity.get('alert').get('descriptionText').get('translation')
        alert_active_periods = entity.get('alert').get('activePeriod')
        
        active_periods_list = []
        for active_period in alert_active_periods:
                
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

            active_periods_list.append(period)
        
        informed_entities = entity.get('alert').get('informedEntity')
        informed_entities_list = []
        
        for informed_entity in informed_entities:
            
            route_id = f"urn:ngsi-ld:GtfsRoute:{informed_entity.get('routeId')}" if informed_entity.get('routeId') else ""
            
            entity_obj = {
                "route_id": {
                    "type": "Relationship",
                    "object": route_id
                }
            }

            informed_entities_list.append(entity_obj)
        
        alert_url_translation_list = []
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
            
            alert_url_translation_list.append(translation)
            
        
        alert_header_translation_list = []
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
            
            alert_header_translation_list.append(translation)
            
        
        alert_description_translation_list = []
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
            
            alert_description_translation_list.append(translation)
        
        ngsi_entity = {
            "id": f"urn:ngsi-ld:GtfsAlert:{entity.get('id', 'Unknown')}",
            "type": "GtfsRealtimeAlert",
            "alert": {
                "type": "Property",
                "value": {
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
                    
                    "url": {
                        "type": "Property",
                        "value": {
                            "translation": {
                                "type": "Property",
                                "value": alert_url_translation_list
                            }
                        }
                    },
                    
                    "alert_header": {
                        "type": "Property",
                        "value": {
                            "translation": {
                                "type": "Property",
                                "value": alert_header_translation_list
                            }
                        }
                    },
                    
                    "alert_description": {
                        "type": "Property",
                        "value": {
                            "translation": {
                                "type": "Property",
                                "value": alert_description_translation_list
                            }
                        }
                    },
                    
                    "@context": [
                        "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                        "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                    ]
                },
            }
        }

        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities


if __name__ == "__main__":
    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_VEHICLE_POSITIONS_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_VEHICLE_POSITIONS_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    ngsi_ld_fеed = gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_fеed, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))


    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_TRIP_UPDATES_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_TRIP_UPDATES_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    ngsi_ld_trip_updates = gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_trip_updates, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))

    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_ALERTS_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_ALERTS_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    ngsi_ld_alerts = gtfs_realtime_alerts_to_ngsi_ld(feed_dict)
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    print(json.dumps(ngsi_ld_alerts, indent=2, ensure_ascii=False))