import sys
import requests
import zipfile
import os
import csv
import json
import uuid
from io import BytesIO
from typing import Any
from datetime import datetime


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


def gtfs_static_download_and_extract_zip(api_endpoint: str, base_dir: str = "gtfs-static") -> list[str]:
    """
    Downloads a GTFS-Static ZIP file from the given API URL and extracts its contents to the specified directory.
    """
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint}: {e}") from e

    # Make directory if it does not exist
    extract_to = os.path.join(base_dir, "data")
    os.makedirs(extract_to, exist_ok=True)
    
    # Extract the ZIP file
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall(extract_to)
    
    
def gtfs_static_read_file(file_path: str) -> list[dict[str, Any]]:
    """
    Reads a GTFS file and returns its contents as a list of dictionaries.
    Each dictionary corresponds to a row in the GTFS file, with keys from the header row.
    """
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        return list(reader)
    
    
def gtfs_static_agency_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static agency data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for agency in raw_data:
        
        agency_id = agency.get("agency_id") or str(uuid.uuid4())
        agency_name = agency.get("agency_name") or ""
        source = agency.get("source") or ""
        agency_url = agency.get("agency_url") or ""
        agency_timezone = agency.get("agency_timezone") or ""
        agency_lang = agency.get("agency_lang") or ""
        agency_phone = agency.get("agency_phone") or ""
        agency_email = agency.get("agency_email") or ""
        
        ngsi_ld_agency = {
            "id": f"urn:ngsi-ld:GtfsAgency:{agency_id}",
            "type": "GtfsAgency",
            
            "agency_name": {
                "type": "Property", 
                "value": agency_name
            },
            
            "source": {
                "type": "Property",
                "value": source
            },
            
            "agency_url": {
                "type": "Property", 
                "value": agency_url
            },
            
            "agency_timezone": {
                "type": "Property", 
                "value": agency_timezone
            },
            
            "agency_lang": {
                "type": "Property", 
                "value": agency_lang
            },
            
            "agency_phone": {
                "type": "Property", 
                "value": agency_phone
            },
            
            "agency_email": {
                "type": "Property", 
                "value": agency_email
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_agency)
    return ngsi_ld_data
    
    
def gtfs_static_calendar_dates_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static Calendar Date Rule attributes data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for calendar_date in raw_data:
        
        calendar_date_rule_id = str(uuid.uuid4())
        service_id = f"urn:ngsi-ld:GtfsService:{calendar_date.get("service_id")}" if calendar_date.get("service_id") else ""
        applies_on = datetime.strptime(calendar_date["date"], "%Y%m%d").date().isoformat() if calendar_date.get("date") else ""
        exception_type = calendar_date.get("agency_email") or "1"
        
        ngsi_ld_calendar_date = {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:{calendar_date_rule_id}",
            "type": "GtfsCalendarDateRule",
            
            "hasService": {
                "type": "Relationship",
                "object": service_id
            },
            
            "appliesOn": {
                "type": "Property",
                "value": applies_on
            },
            
            "exceptionType": {
                "type": "Property",
                "value": exception_type
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_calendar_date)
    return ngsi_ld_data
    
    
def gtfs_static_fare_attributes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static fare attributes data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for fare in raw_data:
        
        fare_id = fare.get("fare_id") or str(uuid.uuid4())
        price = float(fare.get("price")) or 0.0
        currency_type = fare.get("currency_type") or ""
        payment_method = int(fare.get("payment_method")) if fare.get("payment_method") else 1
        transfers = int(fare.get("transfers")) or 0
        agency = f"urn:ngsi-ld:GtfsAgency:{fare.get("agency_id")}" if fare.get("agency_id") else ""
        transfer_duration = int(fare.get("transfer_duration")) if fare.get("transfer_duration") else 0
        ngsi_ld_fare = {
            "id": f"urn:ngsi-ld:GtfsFareAttributes:{fare_id}",
            "type": "GtfsFareAttributes",
            
            "price": {
                "type": "Property", 
                "value": price
            },
            
            "currency_type": {
                "type": "Property", 
                "value": currency_type
            },
            
            "payment_method": {
                "type": "Property", 
                "value": payment_method
            },
            
            "transfers": {
                "type": "Property", 
                "value": transfers
            },
            
            "agency": {
                "type": "Relationship",
                "object": agency
            },
            
            "transfer_duration": {
                "type" : "Property",
                "value": transfer_duration
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_fare)
    return ngsi_ld_data


def gtfs_static_levels_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static level data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for level in raw_data:
        
        level_id = level.get("level_id") or str(uuid.uuid4())
        level_name = level.get("level_name") or ""
        level_index = int(level.get("level_index")) or ""
        
        ngsi_ld_level = {
            "id": f"urn:ngsi-ld:GtfsLevel:{level_id}",
            "type": "GtfsLevel",
            "name": {
                "type": "Property",
                "value": level_name
            },
            
            "level_index": {
                "type": "Property",
                "value": level_index
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_level)
    return ngsi_ld_data
    
    
def gtfs_static_pathways_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static pathways data to NGSI-LD format.
    """
    
    ngsi_ld_data = []
    for pathway in raw_data:
        
        pathway_id = pathway.get("pathway_id") or str(uuid.uuid4())
        from_stop_id = f"urn:ngsi-ld:GtfsStop:{pathway.get("from_stop_id")}" if pathway.get("from_stop_id") else ""
        to_stop_id = f"urn:ngsi-ld:GtfsStop:{pathway.get("to_stop_id")}" if pathway.get("to_stop_id") else ""
        pathway_mode = int(pathway.get("pathway_mode")) if pathway.get("pathway_mode") else 0
        is_bidirectional = int(pathway.get("is_bidirectional")) if pathway.get("is_bidirectional") else 0
        length = float(pathway.get("length")) if pathway.get("length") else 0.0
        traversal_time = float(pathway.get("traversal_time")) if pathway.get("traversal_time") else 0.0
        stair_count = int(pathway.get("stair_count")) if pathway.get("stair_count") else 0
        max_slope = float(pathway.get("max_slope")) if pathway.get("max_slope") else 0.0
        min_width = float(pathway.get("min_width")) if pathway.get("min_width") else 0.0
        signposted_as = pathway.get("signposted_as") or ""
        reversed_signposted_as = pathway.get("reversed_signposted_as") or ""
        
        ngsi_ld_pathway = {
            "id": f"urn:ngsi-ld:GtfsPathway:{pathway_id}",
            "type": "GtfsPathway",
            
            "hasOrigin": {
                "type": "Relationship",
                "object": from_stop_id
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": to_stop_id
            },
            
            "pathway_mode": {
                "type": "Property",
                "value": pathway_mode
            },
            
            "isBidirectional": {
                "type": "Property",
                "value": is_bidirectional
            },
            
            "length": {
                "type": "Property",
                "value": length
            },
            
            "traversal_time": {
                "type": "Property",
                "value": traversal_time
            },
            
            "stair_count": {
                "type": "Property",
                "value": stair_count
            },
            
            "max_slope": {
                "type": "Property",
                "value": max_slope
            },
            
            "min_width": {
                "type": "Property",
                "value": min_width
            },
            
            "signposted_as": {
                "type": "Property",
                "value": signposted_as
            },
            
            "reversed_signposted_as": {
                "type": "Property",
                "value": reversed_signposted_as
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_pathway)
    return ngsi_ld_data
    
    
def gtfs_static_routes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static routes data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for route in raw_data:
        
        route_id = route.get("route_id") or str(uuid.uuid4())
        route_short_name = route.get("route_short_name") or ""
        route_long_name = route.get("route_long_name") or ""
        route_desc = route.get("route_desc") or ""
        route_type = route.get("route_type") or "0"
        route_url = route.get("route_url") or ""
        route_color = route.get("route_color") or ""
        route_text_color = route.get("route_text_color") or ""
        route_sort_order = int(route.get("route_sort_order")) if route.get("route_sort_order") else 0
        continuous_pickup = int(route.get("continuous_pickup")) if route.get("continuous_pickup") else 0
        continuous_drop_off = int(route.get("continuous_drop_off")) if route.get("continuous_drop_off") else 0
        
        ngsi_ld_route = {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:{route_id}",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:{route.get("agency_id", "None")}"
            },
            
            "shortName": {
                "type": "Property", 
                "value": route_short_name
            },
            
            "name": {
                "type": "Property", 
                "value": route_long_name
            },
            
            "description": {
                "type": "Property", 
                "value": route_desc
            },
            
            "routeType": {
                "type": "Property", 
                "value": route_type
            },
            
            "route_url": {
                "type": "Property", 
                "value": route_url
            },
            
            "routeColor": {
                "type": "Property", 
                "value": route_color
            },
            
            "routeTextColor": {
                "type": "Property", 
                "value": route_text_color
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": route_sort_order
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": continuous_pickup
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": continuous_drop_off
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_route)
    return ngsi_ld_data


def gtfs_static_shapes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static shapes data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for shape in raw_data:
        
        shape_id = shape.get("shape_id") or str(uuid.uuid4())
        location_logitude = float(shape.get("shape_pt_lon")) if shape.get("shape_pt_lon") else 0.0
        location_latitude = float(shape.get("shape_pt_lat")) if shape.get("shape_pt_lat") else 0.0
        shape_pt_sequence = int(shape.get("shape_pt_sequence")) if shape.get("shape_pt_sequence") else 0
        shape_dist_traveled = float(shape.get("shape_dist_traveled")) if shape.get("shape_dist_traveled") else 0.0
        
        ngsi_ld_shape = {
            "id": f"urn:ngsi-ld:GtfsShape:{shape_id}",
            "type": "GtfsShape",
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        location_logitude,
                        location_latitude
                    ]
                }
            },
            
            "shape_pt_sequence": {
                "type": "Property", 
                "value": shape_pt_sequence
            },
            
            "distanceTravelled": {
                "type": "Property", 
                "value": shape_dist_traveled
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_shape)
    return ngsi_ld_data


def gtfs_static_stop_times_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static stop times data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for stop_time in raw_data:
        
        stop_time_id = str(uuid.uuid4())
        trip_id = f"urn:ngsi-ld:GtfsTrip:{stop_time.get("trip_id")}" if stop_time.get("trip_id") else ""
        arrival_time = stop_time.get("arrival_time") or ""
        departure_time = stop_time.get("departure_time") or ""
        stop_id = f"urn:ngsi-ld:GtfsStop:{stop_time.get("stop_id")}" if stop_time.get("stop_id") else ""
        stop_sequence = int(stop_time.get("stop_sequence")) if stop_time.get("stop_sequence") else 1
        stop_headsign = stop_time.get("stop_headsign") or ""
        pickup_type = stop_time.get("pickup_type") or "0"
        drop_off_type = stop_time.get("drop_off_type") or "0"
        shape_dist_traveled = float(stop_time.get("shape_dist_traveled")) if stop_time.get("shape_dist_traveled") else 0.0
        continuous_pickup = int(stop_time.get("continuous_pickup")) if stop_time.get("continuous_pickup") else 0
        continuous_drop_off = int(stop_time.get("continuous_drop_off")) if stop_time.get("continuous_drop_off") else 0
        timepoint = stop_time.get("timepoint") or "1"
        
        ngsi_ld_stop_time = {
            "id": f"urn:ngsi-ld:GtfsStopTime:{stop_time['trip_id']}",
            "type": "GtfsStopTime",
            
            "hasTrip": {
                "type": "Relationship",
                "object": trip_id
            },
            
            "arrivalTime": {
                "type": "Property", 
                "value": arrival_time
            },
            
            "departureTime": {
                "type": "Property", 
                "value": departure_time
            },
            
            "hasStop": {
                "type": "Relationship",
                "object": stop_id
            },

            "stopSequence": {
                "type": "Property", 
                "value": stop_sequence
            },
            
            "stopHeadsign": {
                "type": "Property", 
                "value": stop_headsign
            },
            
            "pickupType": {
                "type": "Property", 
                "value": pickup_type
            },
            
            "dropOffType": {
                "type": "Property", 
                "value": drop_off_type
            },
            
            "shapeDistTraveled": {  
                "type": "Property", 
                "value": shape_dist_traveled
            },
            
            "continuousPickup": {
                "type": "Property", 
                "value": continuous_pickup
            },
            
            "continuousDropOff": {
                "type": "Property", 
                "value": continuous_drop_off
            },
            
            "timepoint": {
                "type": "Property", 
                "value": timepoint
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_stop_time)
    return ngsi_ld_data


def gtfs_static_stops_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static stops data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for stop in raw_data:
        
        stop_id = stop.get("stop_id") or str(uuid.uuid4())
        stop_code = stop.get("stop_code") or ""
        stop_name = stop.get("stop_name") or ""
        stop_desc = stop.get("stop_desc") or ""
        stop_logitude = float(stop.get("stop_lon")) if stop.get("stop_lon") else 0.0
        stop_latitude = float(stop.get("stop_lat")) if stop.get("stop_lat") else 0.0
        location_type = int(stop.get("location_type")) if stop.get("location_type") else 0
        parent_station = f"urn:ngsi-ld:GtfsStop:{stop.get("parent_station")}" if stop.get("parent_station") else ""
        stop_timezone = stop.get("stop_timezone") or ""
        level = f"urn:ngsi-ld:GtfsLevel:{stop.get("level_id")}" if stop.get("level_id") else ""
        
        ngsi_ld_stop = {
            "id": f"urn:ngsi-ld:GtfsStop:{stop_id}",
            "type": "GtfsStop",
            
            "code": {
                "type": "Property", 
                "value": stop_code
            },
            
            "name": {
                "type": "Property", 
                "value": stop_name
            },
            
            "description": {
                "type": "Property", 
                "value": stop_desc
            },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        stop_logitude,
                        stop_latitude
                    ]
                }
            },
            
            "locationType": {
                "type": "Property", 
                "value": location_type
            },
            
            "hasParentStation": {  
                "type": "Relationship",
                "object": parent_station
            },
            
            "timezone": {
                "type": "Property", 
                "value": stop_timezone
            },
            
            "level": {
                "type": "Relationship",
                "object": level
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_stop)
    return ngsi_ld_data


def gtfs_static_transfers_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static transfers data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for transfer in raw_data:
        generated_id = str(uuid.uuid4())
        from_stop_id = f"urn:ngsi-ld:GtfsStop:{transfer.get("from_stop_id")}" if transfer.get("from_stop_id") else ""
        to_stop_id = f"urn:ngsi-ld:GtfsStop:{transfer.get("to_stop_id")}" if transfer.get("to_stop_id") else ""
        from_route_id = f"urn:ngsi-ld:GtfsRoute:{transfer.get("from_route_id")}" if transfer.get("from_route_id") else ""
        to_route_id = f"urn:ngsi-ld:GtfsRoute:{transfer.get("to_route_id")}" if transfer.get("to_route_id") else ""
        from_trip_id = f"urn:ngsi-ld:GtfsTrip:{transfer.get("from_trip_id")}" if transfer.get("from_trip_id") else ""        
        to_trip_id = f"urn:ngsi-ld:GtfsTrip:{transfer.get("to_trip_id")}" if transfer.get("to_trip_id") else ""
        transfer_type = transfer.get("transfer_type") or "0"
        min_transfer_time = int(transfer.get("min_transfer_time")) if transfer.get("min_transfer_time") else 1
        
        ngsi_ld_transfer = {
            "id": f"urn:ngsi-ld:GtfsTransferRule:{generated_id}",
            "type": "GtfsTransferRule",
            "hasOrigin": {
                "type": "Relationship",
                "object": from_stop_id
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": to_stop_id
            },
            
            "from_route_id": {
                "type": "Relationship",
                "object": from_route_id
            },
            
            "to_route_id": {
                "type": "Relationship",
                "object": to_route_id
            },
            
            "from_trip_id": {
                "type": "Relationship",
                "object": from_trip_id
            },
            
            "to_trip_id": {
                "type": "Relationship",
                "object": to_trip_id
            },
            
            "transferType": {
                "type": "Property",
                "value": transfer_type
            },
            
            "minimumTransferTime": {
                "type": "Property",
                "value": min_transfer_time
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_transfer)
    return ngsi_ld_data


def gtfs_static_trips_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static trips data to NGSI-LD format.
    """
    ngsi_ld_data = []
    for trip in raw_data:
        
        trip_id = trip.get("trip_id") or str(uuid.uuid4())
        route_id = f"urn:ngsi-ld:GtfsRoute:{trip.get("route_id")}" if trip.get("route_id") else ""
        service_id = f"urn:ngsi-ld:GtfsService:{trip.get("service_id")}" if trip.get("service_id") else ""
        trip_headsign = trip.get("trip_headsign") or ""
        trip_short_name = trip.get("trip_short_name") or ""
        direction_id = int(trip.get("direction_id")) if trip.get("direction_id") else 0
        block_id = f"urn:ngsi-ld:GtfsBlock:{trip.get("block_id")}" if trip.get("block_id") else ""
        shape_id = f"urn:ngsi-ld:GtfsShape:{trip.get("shape_id")}" if trip.get("shape_id") else ""
        wheelchair_accessible = int(trip.get("wheelchair_accessible")) if trip.get("wheelchair_accessible") else 0
        bikes_allowed = int(trip.get("bikes_allowed")) if trip.get("bikes_allowed") else 0
        
        ngsi_ld_trip = {
            "id": f"urn:ngsi-ld:GtfsTrip:{trip_id}",
            "type": "GtfsTrip",
            
            "route": {
                "type": "Relationship",
                "object": route_id
            },
            
            "service": {
                "type": "Relationship",
                "object": service_id
            },
            
            "headSign": {
                "type": "Property",
                "value": trip_headsign
            },
            
            "shortName": {
                "type": "Property",
                "value": trip_short_name
            },
            
            "direction": {
                "type": "Property",
                "value": direction_id
            },
            
            "block": {
                "type": "Relationship",
                "object": block_id
            },
            
            "hasShape": {
                "type": "Relationship",
                "object": shape_id
            },
            
            "wheelChairAccessible": {
                "type": "Property",
                "value": wheelchair_accessible
            },
            
            "bikesAllowed": {
                "type": "Property",
                "value": bikes_allowed
            },
            
            "@context": 
                [
                "https://smart-data-models.github.io/dataModel.UrbanMobility/context.jsonld",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
                ]
        }
        ngsi_ld_data.append(ngsi_ld_trip)
    return ngsi_ld_data
    
    
if __name__ == "__main__":
    #gtfs_static_download_and_extract_zip(config.GTFS_STATIC_ZIP_URL)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "agency.txt"))
    #ngsi_ld_data = gtfs_static_agency_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "calendar_dates.txt"))
    #ngsi_ld_data = gtfs_static_calendar_dates_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "fare_attributes.txt"))
    #ngsi_ld_data = gtfs_static_fare_attributes_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "levels.txt"))
    #ngsi_ld_data = gtfs_static_levels_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "pathways.txt"))
    #ngsi_ld_data = gtfs_static_pathways_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "routes.txt"))
    #ngsi_ld_data = gtfs_static_routes_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "shapes.txt"))
    #ngsi_ld_data = gtfs_static_shapes_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "stop_times.txt"))
    #ngsi_ld_data = gtfs_static_stop_times_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "stops.txt"))
    #ngsi_ld_data = gtfs_static_stops_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "transfers.txt"))
    #ngsi_ld_data = gtfs_static_transfers_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs-static", "data", "trips.txt"))
    #ngsi_ld_data = gtfs_static_trips_to_ngsi_ld(feed_dict)
    
    print(json.dumps(ngsi_ld_data, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))