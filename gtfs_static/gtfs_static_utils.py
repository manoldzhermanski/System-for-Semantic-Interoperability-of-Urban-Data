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
from shapely.geometry import LineString

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config
    
def gtfs_static_download_and_extract_zip(api_endpoint: config.GtfsSource, base_dir: str = "gtfs_static") -> None:
    """
    Downloads a GTFS-Static ZIP file from the given API URL and extracts its contents to the specified directory.
    """
    try:
        url = api_endpoint.value or ""
        if url == "":
            raise ValueError(f"API endpoint for {api_endpoint.name} is not set.")
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint.name}: {e}") from e

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
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for agency in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        agency_id = agency.get("agency_id")
        agency_name = agency.get("agency_name") or None
        source = agency.get("source") or None
        agency_url = agency.get("agency_url") or None
        agency_timezone = agency.get("agency_timezone") or None
        agency_lang = agency.get("agency_lang") or None
        agency_phone = agency.get("agency_phone") or None 
        agency_email = agency.get("agency_email") or None
        
        # Populate FIWARE's data model
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_agency = {
            k: v for k, v in ngsi_ld_agency.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_agency)
        
    # Return the list of NGSI-LD GtfsAgency
    return ngsi_ld_data
    
    
def gtfs_static_calendar_dates_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static Calendar Date Rule attributes data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for calendar_date in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        service_id = f"urn:ngsi-ld:GtfsService:{calendar_date.get("service_id")}" if calendar_date.get("service_id") else None
        applies_on = datetime.strptime(calendar_date["date"], "%Y%m%d").date().isoformat() if calendar_date.get("date") else None
        exception_type = calendar_date.get("exception_type") or None
        
        # Populate FIWARE's data model
        ngsi_ld_calendar_date = {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:Sofia:{calendar_date.get("service_id")}:{applies_on}",
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_calendar_date = {
            k: v for k, v in ngsi_ld_calendar_date.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_calendar_date)
        
    # Return the list of NGSI-LD GtfsCalendarDateRule
    return ngsi_ld_data
    
    
def gtfs_static_fare_attributes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static fare attributes data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for fare in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        fare_id = fare.get("fare_id")
        price = float(fare["price"]) if fare.get("price") not in (None, "") else None
        currency_type = fare.get("currency_type") or None
        payment_method = int(fare["payment_method"]) if fare.get("payment_method") not in (None, "") else None
        transfers = int(fare["transfers"]) if fare.get("transfers") not in (None, "") else None
        agency = f"urn:ngsi-ld:GtfsAgency:{fare.get("agency_id")}" if fare.get("agency_id") else None
        transfer_duration = int(fare["transfer_duration"]) if fare.get("transfer_duration") not in (None, "") else None
        
        # Create custom NGSI-LD data model and populate it
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_fare = {
            k: v for k, v in ngsi_ld_fare.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_fare)
        
    # Return the list of NGSI-LD GtfsFareAttributes
    return ngsi_ld_data


def gtfs_static_levels_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static level data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for level in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        level_id = level.get("level_id")
        level_name = level.get("level_name") or None
        level_index = int(level["level_index"]) if level.get("level_index") not in (None, "") else None
        
        # Create custom NGSI-LD data model and populate it
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_level = {
            k: v for k, v in ngsi_ld_level.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_level)
        
    # Return the list of NGSI-LD GtfsLevel
    return ngsi_ld_data
    
    
def gtfs_static_pathways_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static pathways data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    
    ngsi_ld_data = []
    for pathway in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        pathway_id = pathway.get("pathway_id")
        from_stop_id = f"urn:ngsi-ld:GtfsStop:{pathway.get("from_stop_id")}" if pathway.get("from_stop_id") else None
        to_stop_id = f"urn:ngsi-ld:GtfsStop:{pathway.get("to_stop_id")}" if pathway.get("to_stop_id") else None
        pathway_mode = int(pathway["pathway_mode"]) if pathway.get("pathway_mode") not in (None, "") else None
        is_bidirectional = int(pathway["is_bidirectional"]) if pathway.get("is_bidirectional") not in (None, "") else None
        length = float(pathway["length"]) if pathway.get("length") not in (None, "") else None
        traversal_time = float(pathway["traversal_time"]) if pathway.get("traversal_time") not in (None, "") else None
        stair_count = int(pathway["stair_count"]) if pathway.get("stair_count") not in (None, "") else None
        max_slope = float(pathway["max_slope"]) if pathway.get("max_slope") not in (None, "") else None
        min_width = float(pathway["min_width"]) if pathway.get("min_width") not in (None, "") else None
        signposted_as = pathway.get("signposted_as") or None
        reversed_signposted_as = pathway.get("reversed_signposted_as") or None
        
        # Create custom NGSI-LD data model and populate it
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_pathway = {
            k: v for k, v in ngsi_ld_pathway.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_pathway)
        
    # Return the list of NGSI-LD GtfsPathway
    return ngsi_ld_data
    
    
def gtfs_static_routes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static routes data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for route in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        route_id = route.get("route_id")
        route_short_name = route.get("route_short_name") or None
        route_long_name = route.get("route_long_name") or None
        route_desc = route.get("route_desc") or None
        route_type = route.get("route_type") or None
        route_url = route.get("route_url") or None
        route_color = route.get("route_color") or None
        route_text_color = route.get("route_text_color") or None
        route_sort_order = int(route["route_sort_order"]) if route.get("route_sort_order") not in (None, "") else None
        continuous_pickup = int(route["continuous_pickup"]) if route.get("continuous_pickup") not in (None, "") else None
        continuous_drop_off = int(route["continuous_drop_off"]) if route.get("continuous_drop_off") not in (None, "") else None
        
        # Populate FIWARE's data model
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_route = {
            k: v for k, v in ngsi_ld_route.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_route)
        
    # Return the list of NGSI-LD GtfsRoute
    return ngsi_ld_data


def gtfs_static_shapes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static shapes data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    shapes_dict = {}

    for shape in raw_data:
        shape_id = shape.get("shape_id")
        if not shape_id:
            continue

        # parse coordinates and optional sequence
        location_longitude = float(shape["shape_pt_lon"]) if shape.get("shape_pt_lon") not in (None, "") else None
        location_latitude = float(shape["shape_pt_lat"]) if shape.get("shape_pt_lat") not in (None, "") else None
        shape_pt_sequence = int(shape["shape_pt_sequence"]) if shape.get("shape_pt_sequence") not in (None, "") else None
        shape_dist_traveled = float(shape["shape_dist_traveled"]) if shape.get("shape_dist_traveled") not in (None, "") else None
        
        if shape_id not in shapes_dict:
            shapes_dict[shape_id] = []

        shapes_dict[shape_id].append({"seq": shape_pt_sequence, "coords": [location_longitude, location_latitude], "dist": shape_dist_traveled})

    for shape_id, points in shapes_dict.items():
        points.sort(key=lambda p: p["seq"])
        coords = [p["coords"] for p in points]
        
        line = LineString(coords)
        simplified = line.simplify(0.00055, preserve_topology=True)
        simplified_coords = list(simplified.coords)
        
        # Populate FIWARE's data model         
        ngsi_ld_shape = {
            "id": f"urn:ngsi-ld:GtfsShape:{shape_id}",
            "type": "GtfsShape",
            
            "name": {
                "type": "Property",
                "value": shape_id
                },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": simplified_coords
                }
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_shape = {
            k: v for k, v in ngsi_ld_shape.items()
            if not (isinstance(v, dict) and None in v.values())
        }

        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_shape)

    # Return the list of NGSI-LD GtfsShape
    return ngsi_ld_data


def gtfs_static_stop_times_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static stop times data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for stop_time in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        trip_id = f"urn:ngsi-ld:GtfsTrip:{stop_time.get("trip_id")}" if stop_time.get("trip_id") else None
        arrival_time = stop_time.get("arrival_time") or None
        departure_time = stop_time.get("departure_time") or None
        stop_id = f"urn:ngsi-ld:GtfsStop:{stop_time.get("stop_id")}" if stop_time.get("stop_id") else None
        stop_sequence = int(stop_time["stop_sequence"]) if stop_time.get("stop_sequence") not in (None, "") else None
        stop_headsign = stop_time.get("stop_headsign") or None
        pickup_type = stop_time.get("pickup_type") or None
        drop_off_type = stop_time.get("drop_off_type") or None
        shape_dist_traveled = float(stop_time["shape_dist_traveled"]) if stop_time.get("shape_dist_traveled") not in (None, "") else None
        continuous_pickup = int(stop_time["continuous_pickup"]) if stop_time.get("continuous_pickup") not in (None, "") else None
        continuous_drop_off = int(stop_time["continuous_drop_off"]) if stop_time.get("continuous_drop_off") not in (None, "") else None
        timepoint = stop_time.get("timepoint") or None
        
        # Populate FIWARE's data model
        ngsi_ld_stop_time = {
            "id": f"urn:ngsi-ld:GtfsStopTime:{stop_time['trip_id']}:{stop_time['stop_sequence']}",
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_stop_time = {
            k: v for k, v in ngsi_ld_stop_time.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_stop_time)
        
    # Return the list of NGSI-LD GtfsStopTime
    return ngsi_ld_data


def gtfs_static_stops_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static stops data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trip
    """
    ngsi_ld_data = []
    for stop in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        stop_id = stop.get("stop_id")
        stop_code = stop.get("stop_code") or None
        stop_name = stop.get("stop_name") or None
        stop_desc = stop.get("stop_desc") or None
        stop_longitude = float(stop["stop_lon"]) if stop.get("stop_lon") not in (None, "") else None
        stop_latitude = float(stop["stop_lat"]) if stop.get("stop_lat") not in (None, "") else None
        location_type = int(stop["location_type"]) if stop.get("location_type") not in (None, "") else None
        parent_station = f"urn:ngsi-ld:GtfsStop:{stop.get("parent_station")}" if stop.get("parent_station") else None
        stop_timezone = stop.get("stop_timezone") or None
        level = f"urn:ngsi-ld:GtfsLevel:{stop.get("level_id")}" if stop.get("level_id") else None
        
        # Populate FIWARE's data model
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
                        stop_longitude,
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_stop = {
            k: v for k, v in ngsi_ld_stop.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_stop)
    
    # Return the list of NGSI-LD GtfsStop
    return ngsi_ld_data


def gtfs_static_transfers_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static transfers data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trips
    """
    ngsi_ld_data = []
    for transfer in raw_data:
        from_stop_id = f"urn:ngsi-ld:GtfsStop:{transfer.get('from_stop_id')}" if transfer.get("from_stop_id") else None
        to_stop_id = f"urn:ngsi-ld:GtfsStop:{transfer.get('to_stop_id')}" if transfer.get("to_stop_id") else None
        from_route_id = f"urn:ngsi-ld:GtfsRoute:{transfer.get('from_route_id')}" if transfer.get("from_route_id") else None
        to_route_id = f"urn:ngsi-ld:GtfsRoute:{transfer.get('to_route_id')}" if transfer.get("to_route_id") else None
        from_trip_id = f"urn:ngsi-ld:GtfsTrip:{transfer.get('from_trip_id')}" if transfer.get("from_trip_id") else None     
        to_trip_id = f"urn:ngsi-ld:GtfsTrip:{transfer.get('to_trip_id')}" if transfer.get("to_trip_id") else None
        transfer_type = transfer.get("transfer_type") or None
        min_transfer_time = int(transfer["min_transfer_time"]) if transfer.get("min_transfer_time") not in (None, "") else None

        ngsi_ld_transfer = {
            "id": f"urn:ngsi-ld:GtfsTransferRule:{transfer.get('from_stop_id', 'None')}-{transfer.get('to_stop_id', 'None')}",
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
            }
        }

        # Only filter dict values, not strings (id/type)
        ngsi_ld_transfer = {
            k: v for k, v in ngsi_ld_transfer.items()
            if not (isinstance(v, dict) and None in v.values())
        }

        ngsi_ld_data.append(ngsi_ld_transfer)

    return ngsi_ld_data


def gtfs_static_trips_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static trips data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trips.
    """
    ngsi_ld_data = []
    for trip in raw_data:
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        trip_id = trip.get("trip_id")
        route_id = f"urn:ngsi-ld:GtfsRoute:{trip.get("route_id")}" if trip.get("route_id") else None
        service_id = f"urn:ngsi-ld:GtfsService:{trip.get("service_id")}" if trip.get("service_id") else None
        trip_headsign = trip.get("trip_headsign") or None
        trip_short_name = trip.get("trip_short_name") or None
        direction_id = int(trip["direction_id"]) if trip.get("direction_id") not in (None, "") else None
        block_id = f"urn:ngsi-ld:GtfsBlock:{trip.get("block_id")}" if trip.get("block_id") else None
        shape_id = f"urn:ngsi-ld:GtfsShape:{trip.get("shape_id")}" if trip.get("shape_id") else None
        wheelchair_accessible = int(trip["wheelchair_accessible"]) if trip.get("wheelchair_accessible") not in (None, "") else None
        bikes_allowed = int(trip["bikes_allowed"]) if trip.get("bikes_allowed") not in (None, "") else None
        
        # Populate FIWARE's data model
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
            }
        }
        
        # Remove all elements which have an empty value or object, so that the entity can be posted to Orion-LD
        ngsi_ld_trip = {
            k: v for k, v in ngsi_ld_trip.items()
            if not (isinstance(v, dict) and None in v.values())
        }
        
        # Append every NGSI-LD entity after transformation
        ngsi_ld_data.append(ngsi_ld_trip)
        
    # Return the list of NGSI-LD GtfsTrip
    return ngsi_ld_data
    
    
def gtfs_static_get_ngsi_ld_data(file_type: str) -> list[dict[str, Any]]:
    """
    Based on the given file_type, the function reads the correct file type
    and calls the appropriate function for NGSI-LD tranformation
    Args:
        file_type: string which specifies which .txt file to be read
    Allowed values: 
        agency, calendar_dates, fare_attributes, levels, pathways, routes,
        shapes, stop_times, stops, transfers, trips
    Returns:
        list[dict[str, Any]]: Function call from different functions which handle GTFS Static to NGSI-LD transformation
    """
    
    mapping = {
        "agency": ("agency.txt", gtfs_static_agency_to_ngsi_ld),
        "calendar_dates": ("calendar_dates.txt", gtfs_static_calendar_dates_to_ngsi_ld),
        "fare_attributes": ("fare_attributes.txt", gtfs_static_fare_attributes_to_ngsi_ld),
        "levels": ("levels.txt", gtfs_static_levels_to_ngsi_ld),
        "pathways": ("pathways.txt", gtfs_static_pathways_to_ngsi_ld),
        "routes": ("routes.txt", gtfs_static_routes_to_ngsi_ld),
        "shapes": ("shapes.txt", gtfs_static_shapes_to_ngsi_ld),
        "stop_times": ("stop_times.txt", gtfs_static_stop_times_to_ngsi_ld),
        "stops": ("stops.txt", gtfs_static_stops_to_ngsi_ld),
        "transfers": ("transfers.txt", gtfs_static_transfers_to_ngsi_ld),
        "trips": ("trips.txt", gtfs_static_trips_to_ngsi_ld)
    }

    if file_type not in mapping:
        raise ValueError(f"Unsupported GTFS static file type: {file_type}")

    filename, transformer = mapping[file_type]
    filepath = os.path.join("gtfs_static", "data", filename)

    raw_data = gtfs_static_read_file(filepath)
    return transformer(raw_data)
    
if __name__ == "__main__":
    #gtfs_static_download_and_extract_zip(config.GtfsSource.GTFS_STATIC_ZIP_URL)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "agency.txt"))
    #ngsi_ld_data = gtfs_static_agency_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "calendar_dates.txt"))
    #ngsi_ld_data = gtfs_static_calendar_dates_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "fare_attributes.txt"))
    #ngsi_ld_data = gtfs_static_fare_attributes_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "levels.txt"))
    #ngsi_ld_data = gtfs_static_levels_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "pathways.txt"))
    #ngsi_ld_data = gtfs_static_pathways_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "routes.txt"))
    #ngsi_ld_data = gtfs_static_routes_to_ngsi_ld(feed_dict)
    
    feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "shapes.txt"))
    ngsi_ld_data = gtfs_static_shapes_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "stop_times.txt"))
    #ngsi_ld_data = gtfs_static_stop_times_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "stops.txt"))
    #ngsi_ld_data = gtfs_static_stops_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "transfers.txt"))
    #ngsi_ld_data = gtfs_static_transfers_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "trips.txt"))
    #ngsi_ld_data = gtfs_static_trips_to_ngsi_ld(feed_dict)
    
    print(json.dumps(ngsi_ld_data, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    pass