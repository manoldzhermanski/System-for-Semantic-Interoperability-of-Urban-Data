import io
import zipfile
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
    Converts a GTFS-Realtime Vehicle Position Feed (from MessageToDict) to a list of NGSI-LD entities.
    """
    ngsi_ld_entities = []

    # Extract entities from the feed_dict
    entities = feed_dict.get("entity", [])

    # Iterate through each entity and convert to NGSI-LD format
    for entity in entities:
        # Create the base NGSI-LD entity structure
        ngsi_ld_entity = {
            "id": f"urn:ngsi-ld:GtfsVehiclePosition:{entity.get('id', 'Unknown')}",
            "type": "GtfsVehiclePosition"
        }

        # Extract vehicle, trip, and position information
        vehicle = entity.get("vehicle", {})
        trip = vehicle.get("trip", {})
        position = vehicle.get("position", {})

        # If scheduleRelationship propery is present, add it to the entity
        if "scheduleRelationship" in trip:
            ngsi_ld_entity["schedule_relationship"] = {
                "type": "Property",
                "value": trip.get("scheduleRelationship")
            }
        
        # If tripId is present, add it to the entity as a relationship
        if "routeId" in trip:
            ngsi_ld_entity["route"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsRoute:{trip.get("routeId")}"
            }

        # if longitude and latitude are present in position, add them to the entity as a GeoProperty of type Point
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
            
        # If speed property is present in position, add it to the entity
        if "speed" in position:
            ngsi_ld_entity["speed"] = {
                "type": "Property",
                "value": position["speed"]
            }

        # if currentStatus property is present in vehicle, add it to the entity
        if "currentStatus" in vehicle:
            ngsi_ld_entity["current_status"] = {
                "type": "Property",
                "value": vehicle["currentStatus"]
            }
        
        # If timestamp property is present in vehicle, convert it to ISO8601 and add it to the entity
        if "timestamp" in vehicle:
            iso_time = unix_to_iso8601(int(vehicle["timestamp"]))
            ngsi_ld_entity["timestamp"] = {
                "type": "Property",
                "value": iso_time
            }

        # If congestionLevel property is present in vehicle, add it to the entity
        if "congestionLevel" in vehicle:
            ngsi_ld_entity["congestion_level"] = {
                "type": "Property",
                "value": vehicle["congestionLevel"]
            }

        # If stopId is present, add it to the entity as a relationship
        if "stopId" in vehicle:
            ngsi_ld_entity["stop"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsStop:{vehicle["stopId"]}"
            }

        # If vehicleId is present, add it to the entity as a relationship
        if "vehicle" in vehicle and "id" in vehicle["vehicle"]:
            ngsi_ld_entity["vehicle"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:Vehicle:{vehicle["vehicle"]["id"]}"
            }

        # If occupancyStatus property is present, add it to the entity
        if "occupancyStatus" in vehicle:
            ngsi_ld_entity["occupancy_status"] = {
                "type": "Property",
                "value": vehicle["occupancyStatus"]
            }

        # Add @context as the last key
        ngsi_ld_entity["@context"] = [
            "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]

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
        # Create the base NGSI-LD entity structure
        ngsi_entity = {
            "id": f"urn:ngsi-ld:GtfsTripUpdate:{entity.get('id', 'Unknown')}",
            "type": "GtfsTripUpdate"            
        }
        # Extract trip and stop time updates
        trip_update = entity.get("tripUpdate", {})
        trip = trip_update.get("trip", {})
        stop_time_updates = trip_update.get("stopTimeUpdate", [])

        # If isDeleted property is present, add it to the entity
        if "isDeleted" in entity:
            ngsi_entity["is_deleted"] = {
                "type": "Property",
                "value": entity.get("isDeleted", "Unknown")
            }
        # If startTime property is present, add it to the entity
        if "startTime" in trip:
            ngsi_entity["start_time"] = {
                "type": "Property",
                "value": trip.get("startTime", "Unknown")
            }
        
        # If startDate property is present, add it to the entity
        if "startDate" in trip:
            ngsi_entity["start_date"] = {
                "type": "Property",
                "value": trip.get("startDate", "Unknown")
            }
        
        # If scheduleRelationship property is present, add it to the entity
        if "scheduleRelationship" in trip:
            ngsi_entity["schedule_relationship"] = {
                "type": "Property",
                "value": trip.get("scheduleRelationship", "Unknown")
            }
        
        # If routeId is present, add it to the entity as a relationship
        if "routeId" in trip:
            ngsi_entity["route"] = {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsRoute:{trip.get('routeId', 'Unknown')}"
            }
        
        # If stopId is present, convert it's values into a list and add it to the entity as a relationship
        if "stopTimeUpdate" in trip_update:
            # Get the stop time updates and convert them to a list of entities
            stop_time_updates = trip_update.get("stopTimeUpdate", [])
            stop_time_updates_list = []

            # Iterate through each stop time update and convert to NGSI-LD format
            for stop_time_update in stop_time_updates:

                # Create a dictionary for the stop time entity
                stop_time_entity = {}

                # If arrival property is present in stop_time_update, convert it to ISO8601 and add it to the entity
                if "arrival" in stop_time_update:
                    iso_time = unix_to_iso8601(int(stop_time_update["arrival"]["time"]))
                    stop_time_entity["arrival_time"] = {
                        "type": "Property",
                        "value": iso_time
                    }

                # If departure property is present in stop_time_update, convert it to ISO8601 and add it to the entity
                if "departure" in stop_time_update:
                    iso_time = unix_to_iso8601(int(stop_time_update["departure"]["time"]))
                    stop_time_entity["departure_time"] = {
                        "type": "Property",
                        "value": iso_time
                    }

                # If stopId is present in stop_time_update, add it to the entity as a relationship
                if "stopId" in stop_time_update:
                    stop_time_entity["stop"] = {
                        "type": "Relationship",
                        "object": f"urn:ngsi-ld:GtfsStop:{stop_time_update['stopId']}"
                    }

                # If scheduleRelationship property is present in stop_time_update, add it to the entity
                if "scheduleRelationship" in stop_time_update:
                    stop_time_entity["schedule_relationship"] = {
                        "type": "Property",
                        "value": stop_time_update["scheduleRelationship"]
                    }
                # Append the stop time entity to the list
                stop_time_updates_list.append(stop_time_entity)
            
            # Add the stop time updates list to the NGSI-LD entity
            ngsi_entity["stop_time_update"] = {
                "type": "Property",
                "value": stop_time_updates_list
            }

        # Add @context as the last key
        ngsi_entity["@context"] = [
            "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]

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
        ngsi_entity = {
            "id": f"urn:ngsi-ld:GtfsAlert:{entity.get('id', 'Unknown')}",
            "type": "GtfsAlert"
        }
        # Extract alert, url, header_text and description text information
        alert = entity.get("alert", {})
        urls = alert.get("url", [])
        header_text = alert.get("headerText", {})
        description_text = alert.get("descriptionText", {})
        
        # If activePeriod property is present, convert it to ISO8601 and add it to the entity
        if "activePeriod" in alert:
            active_periods = []
            for period in alert["activePeriod"]:
                active_period = {}
                if "start" in period:
                    active_period["start"] = unix_to_iso8601(int(period["start"]))
                if "end" in period:
                    active_period["end"] = unix_to_iso8601(int(period["end"]))
                if active_period:  # Only add if at least one is present
                    active_periods.append(active_period)
            
            ngsi_entity["active_period"] = {
                "type": "Property",
                "value": active_periods
            }

        # If informedEntity is present, convert it to a list of entities and add it as a value
        # Each informedEntity can have a routeId, which is converted to a relationship
        if "informedEntity" in alert:
            informed_entities = []
            for informed_entity in alert["informedEntity"]:
                if "routeId" in informed_entity:
                    informed_entities.append({
                        "route": f"urn:ngsi-ld:GtfsRoute:{informed_entity['routeId']}"
                    })
            
            ngsi_entity["informed_entity"] = {
                "type": "Property",
                "value": informed_entities
            }
        
        # If cause property is present, add it to the entity
        if "cause" in alert:
            ngsi_entity["cause"] = {
                "type": "Property",
                "value": alert["cause"]
            }
        # If effect property is present, add it to the entity
        if "effect" in alert:
            ngsi_entity["effect"] = {
                "type": "Property",
                "value": alert["effect"]
            }

        # If url is present, convert it to a list of translations and add it to the entity
        if "translation" in urls:
            translations = []
            for translation in urls["translation"]:
                if "text" in translation and "language" in translation:
                    translations.append({
                        "text": translation["text"],
                        "language": translation["language"]
                    })
            ngsi_entity["url"] = {
                "type": "Property",
                "value": translations
            }
        
        # If header_text is present, convert it to a list of translations and add it to the entity
        if "translation" in header_text:
            translations = []
            for translation in header_text["translation"]:
                if "text" in translation and "language" in translation:
                    translations.append({
                        "text": translation["text"],
                        "language": translation["language"]
                    })
            ngsi_entity["header_text"] = {
                "type": "Property",
                "value": translations
            }
        
        # If description_text is present, convert it to a list of translations and add it to the entity
        if "translation" in description_text:
            translations = []
            for translation in description_text["translation"]:
                if "text" in translation and "language" in translation:
                    translations.append({
                        "text": translation["text"],
                        "language": translation["language"]
                    })
            ngsi_entity["description_text"] = {
                "type": "Property",
                "value": translations
            }

        # Add @context as the last key
        ngsi_entity["@context"] = [
            "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
            "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
        ]
        
        # Append the NGSI-LD entity to the list
        ngsi_ld_entities.append(ngsi_entity)

    # Return the list of NGSI-LD entities
    return ngsi_ld_entities


if __name__ == "__main__":
    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_VEHICLE_POSITION_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_VEHICLE_POSITION_URL)
    feed_dict = gtfs_realtime_feed_to_dict(feed_data)
    ngsi_ld_fed = gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict)
    #print(json.dumps(ngsi_ld_fed, indent=2, ensure_ascii=False))
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
    ngsi_ld_alerts = gtfs_realtime_alerts_to_ngsi_ld(feed_dict)
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    #print(json.dumps(ngsi_ld_alerts, indent=2, ensure_ascii=False))