import requests
import config
from gtfs_realtime_pb2 import FeedMessage
from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict
from typing import Any
import json
from datetime import datetime, timezone

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
    Converts a GTFS-Realtime vehicle position feed (from MessageToDict) to a list of NGSI-LD entities.
    Each entity in feed_dict['entity'] is converted to NGSI-LD format.
    """
    ngsi_ld_entities = []
    entities = feed_dict.get("entity", [])
    for entity in entities:
        ngsi_ld_entity = {
            "id": f"urn:ngsi-ld:GtfsVehiclePosition:{entity.get('id', 'Unknown')}",
            "type": "GtfsVehiclePosition"
        }

        vehicle = entity.get("vehicle", {})
        trip = vehicle.get("trip", {})
        position = vehicle.get("position", {})

        if "scheduleRelationship" in trip:
            ngsi_ld_entity["schedule_relationship"] = {
                "type": "Property",
                "value": trip.get("scheduleRelationship")
            }
        if "routeId" in trip:
            ngsi_ld_entity["route"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsRoute:{trip.get("routeId")}"
            }
        if "longitude" in position and "latitude" in position:
            ngsi_ld_entity["location"] = {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        position["longitude"],
                        position["latitude"]
                    ]
                }
            }
        if "speed" in position:
            ngsi_ld_entity["speed"] = {
                "type": "Property",
                "value": position["speed"]
            }
        if "currentStatus" in vehicle:
            ngsi_ld_entity["current_status"] = {
                "type": "Property",
                "value": vehicle["currentStatus"]
            }
        if "timestamp" in vehicle:
            iso_time = unix_to_iso8601(int(vehicle["timestamp"]))
            ngsi_ld_entity["timestamp"] = {
                "type": "Property",
                "value": iso_time
            }
        if "congestionLevel" in vehicle:
            ngsi_ld_entity["congestion_level"] = {
                "type": "Property",
                "value": vehicle["congestionLevel"]
            }
        if "stopId" in vehicle:
            ngsi_ld_entity["stop"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsStop:{vehicle["stopId"]}"
            }
        if "vehicle" in vehicle and "id" in vehicle["vehicle"]:
            ngsi_ld_entity["vehicle"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Vehicle:{vehicle["vehicle"]["id"]}"
            }
        if "occupancyStatus" in vehicle:
            ngsi_ld_entity["occupancy_status"] = {
                "type": "Property",
                "value": vehicle["occupancyStatus"]
            }

        # Add any other top-level keys as Properties
        for key, value in entity.items():
            if key in ("id", "vehicle"):
                continue
            ngsi_ld_entity[key] = {
                "type": "Property",
                "value": value
            }

        # Remove keys with None values
        ngsi_ld_entity = {k: v for k, v in ngsi_ld_entity.items() if v is not None}

        # Add @context as the last key
        ngsi_ld_entity["@context"] = [
            "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]

        ngsi_ld_entities.append(ngsi_ld_entity)

    return ngsi_ld_entities

def gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Converts a GTFS-Realtime trip updates feed (from MessageToDict) to a list of NGSI-LD entities.
    Each entity in feed_dict['entity'] is converted to NGSI-LD format.
    """
    ngsi_ld_entities = []
    entities = feed_dict.get("entity", [])
    for entity in entities:
        ngsi_entity = {
            "id": f"urn:ngsi-ld:GtfsTripUpdate:{entity.get('id', 'Unknown')}",
            "type": "GtfsTripUpdate"            
        }

        trip_update = entity.get("tripUpdate", {})
        trip = trip_update.get("trip", {})
        stop_time_updates = trip_update.get("stopTimeUpdate", [])

        if "isDeleted" in entity:
            ngsi_entity["is_deleted"] = {
                "type": "Property",
                "value": entity.get("isDeleted", "Unknown")
            }

        if "startTime" in trip:
            ngsi_entity["start_time"] = {
                "type": "Property",
                "value": trip.get("startTime", "Unknown")
            }

        if "startDate" in trip:
            ngsi_entity["start_date"] = {
                "type": "Property",
                "value": trip.get("startDate", "Unknown")
            }
        
        if "scheduleRelationship" in trip:
            ngsi_entity["schedule_relationship"] = {
                "type": "Property",
                "value": trip.get("scheduleRelationship", "Unknown")
            }
        
        if "routeId" in trip:
            ngsi_entity["route"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsRoute:{trip.get('routeId', 'Unknown')}"
            }
        
        if "stopTimeUpdate" in trip_update:
            stop_time_updates = trip_update.get("stopTimeUpdate", [])
            stop_time_updates_list = []
            for stop_time_update in stop_time_updates:
                stop_time_entity = {}
                if "arrival" in stop_time_update:
                    iso_time = unix_to_iso8601(int(stop_time_update["arrival"]["time"]))
                    stop_time_entity["arrival_time"] = {
                        "type": "Property",
                        "value": iso_time
                    }

                if "departure" in stop_time_update:
                    iso_time = unix_to_iso8601(int(stop_time_update["departure"]["time"]))
                    stop_time_entity["departure_time"] = {
                        "type": "Property",
                        "value": iso_time
                    }

                if "stopId" in stop_time_update:
                    stop_time_entity["stop"] = {
                        "type": "Relationship",
                        "object": f"urn:ngsi-ld:GtfsStop:{stop_time_update['stopId']}"
                    }

                if "scheduleRelationship" in stop_time_update:
                    stop_time_entity["schedule_relationship"] = {
                        "type": "Property",
                        "value": stop_time_update["scheduleRelationship"]
                    }

                stop_time_updates_list.append(stop_time_entity)
            
            ngsi_entity["stop_time_update"] = {
                "type": "Property",
                "value": stop_time_updates_list
            }
        # Add observedAt attribute before @context
        ngsi_entity["observedAt"] = {
            "type": "Property",
            "value": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        # Add @context as the last key
        ngsi_entity["@context"] = [
            "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
        ngsi_ld_entities.append(ngsi_entity)
        return ngsi_ld_entities
    

if __name__ == "__main__":
    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_VEHICLE_POSITION_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_VEHICLE_POSITION_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    ngsi_ld_fed = gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict)
    print(json.dumps(ngsi_ld_fed, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    #print(ngsi_ld_feed)

    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_TRIP_UPDATES_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_TRIP_UPDATES_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    ngsi_ld_trip_updates = gtfs_realtime_trip_updates_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_trip_updates, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))

    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_ALERTS_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_ALERTS_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))