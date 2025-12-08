import sys
import requests
import zipfile
import os
import csv
import json
from pathlib import Path
from io import BytesIO
from typing import Any
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import validation_functions.validation_utils as validation_utils

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
    
    # Ensure base_dir exists
    os.makedirs(base_dir, exist_ok=True)

    # Ensure base_dir/data exists
    extract_to = os.path.join(base_dir, "data")
    os.makedirs(extract_to, exist_ok=True)
    
    # Extract the ZIP file
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall(extract_to)
    
    
def gtfs_static_read_file(file_path: str) -> list[dict[str, Any]]:
    """
    Reads a GTFS file and returns its contents as a list of dictionaries.
    Each dictionary corresponds to a row in the GTFS file, with keys from the header row.
    Because the expected delimiter in the GTFS Static files is ',' (comma), we check if this is true
    """
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        first_line = file.readline()
        
        # If the file is empty, return []
        if not first_line.strip():
            return []

        # Require comma delimiter
        if "," not in first_line:
            raise ValueError("Invalid delimiter: GTFS files must use comma ',' as delimiter")

        # Reset pointer after reading first line
        file.seek(0)  
        reader = csv.DictReader(file, delimiter=",")
        
        # Reject headers that are purely numeric → typical sign of missing header
        if reader.fieldnames and any(name.strip().isdigit() for name in reader.fieldnames):
            raise ValueError("Missing or invalid header row: GTFS files must contain a valid CSV header.")
        
        # Reject empty column names
        if not reader.fieldnames or any(name.strip() == "" for name in reader.fieldnames):
            raise ValueError("Missing or invalid header row: GTFS files must contain a valid CSV header.")
        
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
    
    required_fileds = ["agency_id", "agency_name", "agency_url", "agency_timezone"]
    
    for agency in raw_data:
        
        # Check if an agency entity contains the required fields
        for field in required_fileds:
            if not agency.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        agency_id = (agency.get("agency_id") or "").strip()
        agency_name = (agency.get("agency_name") or "").strip()
        agency_url = (agency.get("agency_url") or "").strip()
        agency_timezone = (agency.get("agency_timezone") or "").strip()
        agency_lang = (agency.get("agency_lang") or "").strip() or None
        agency_phone = (agency.get("agency_phone") or "").strip() or None
        agency_fare_url = (agency.get("agency_fare_url") or "").strip() or None 
        agency_email = (agency.get("agency_email") or "").strip() or None        
        raw_cemv_support = (agency.get("cemv_support") or "").strip() or None

        if validation_utils.is_string(agency_id) is False:
            raise ValueError(f"Invalid type for 'agency_id': {type(agency_id)}")
        
        if validation_utils.is_string(agency_name) is False:
            raise ValueError(f"Invalid string format for 'agency_name': {agency_name}")
            
        if validation_utils.is_valid_url(agency_url) is False:
            raise ValueError(f"Invalid URL format for 'agency_url': {agency_url}")
        
        if validation_utils.is_valid_timezone(agency_timezone) is False:
            raise ValueError(f"Invalid timezone format for 'agency_timezone': {agency_timezone}")
        
        if agency_lang is not None and agency_lang != "":
            if validation_utils.is_valid_language_code(agency_lang) is False:
                raise ValueError(f"Invalid language code format for 'agency_lang': {agency_lang}")
        
        if agency_phone is not None and agency_phone != "":
            if validation_utils.is_valid_phone_number(agency_phone) is False:
                raise ValueError(f"Invalid language code format for 'agency_phone': {agency_phone}")
        
        if agency_fare_url is not None and agency_fare_url != "":
            if agency_fare_url and validation_utils.is_valid_url(agency_fare_url) is False:
                raise ValueError(f"Invalid URL format for 'agency_fare_url': {agency_fare_url}")
        
        if agency_email is not None and agency_email != "":
            if validation_utils.is_valid_email(agency_email) is False:
                raise ValueError(f"Invalid email format for 'agency_email': {agency_email}")
        
        if raw_cemv_support is not None and raw_cemv_support != "":
            if not validation_utils.is_valid_cemv_support(raw_cemv_support):
                raise ValueError(f"Invalid value for 'cemv_support': {raw_cemv_support}")
            cemv_support = int(raw_cemv_support)
        else:
            cemv_support = None

        # Populate FIWARE's data model
        ngsi_ld_agency = {
            "id": f"urn:ngsi-ld:GtfsAgency:{agency_id}",
            "type": "GtfsAgency",
            
            "agency_name": {
                "type": "Property", 
                "value": agency_name
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
            
            "agency_fare_url": {
                "type": "Property",
                "value": agency_fare_url
            },
            
            "agency_email": {
                "type": "Property", 
                "value": agency_email
            },
            
            "cemv_support": {
                "type": "Property",
                "value": cemv_support
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
    
    required_fileds = ["service_id", "date", "exception_type"]
    
    for calendar_date in raw_data:
        
        # Check if a calendar date entity contains the required fields
        for field in required_fileds:
            if not calendar_date.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        raw_service_id = (calendar_date.get("service_id") or "").strip()
        raw_date = (calendar_date.get("date") or "").strip()
        raw_exception = (calendar_date.get("exception_type") or "").strip()

        if validation_utils.is_string(raw_service_id) is False:
            raise ValueError(f"Invalid type for 'service_id':{type(raw_service_id)}")
        service_id = f"urn:ngsi-ld:GtfsService:{raw_service_id}"

        if validation_utils.is_valid_date(raw_date) is False:
            raise ValueError(f"Invalid date format for 'date': {raw_date}")
        applies_on = datetime.strptime(raw_date, "%Y%m%d").date().isoformat()

        if validation_utils.is_valid_calendar_date_exception_type(raw_exception) is False:
            raise ValueError(f"Invalid value for 'exception_type':{raw_exception}")
        exception_type = int(raw_exception)

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
    
    required_fileds = ["fare_id", "price", "currency_type", "payment_method", "transfers", "agency_id"]
    
    for fare in raw_data:
        
        # Check if a fare attributes entity contains the required fields
        for field in required_fileds:
            if not fare.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        fare_id = (fare.get("fare_id") or "").strip()
        raw_price = (fare.get("price") or "").strip()
        currency_type = (fare.get("currency_type") or "").strip()
        raw_payment_method = (fare.get("payment_method") or "").strip()
        raw_transfers = (fare.get("transfers") or "").strip()        
        raw_agency = (fare.get("agency_id") or "").strip()
        raw_transfer_duration = (fare.get("transfer_duration") or "").strip() or None
        transfer_duration = None

        if validation_utils.is_string(fare_id) is False:
            raise ValueError(f"Invalid type for 'fare_id': {type(fare_id)}")
        
        if validation_utils.is_float(raw_price) is False:
            raise ValueError(f"Invalid value for 'price': {raw_price}")
        
        price = float(raw_price)
        if price < 0.0:
            raise ValueError(f"Invalid value for 'price': {raw_price}")

        if validation_utils.is_valid_currency_code(currency_type) is False:
            raise ValueError(f"Invalid value for 'currency_type: {currency_type}")
                
        if validation_utils.is_valid_fare_attributes_payment_method(raw_payment_method) is False:
            raise ValueError(f"Invalid value for 'payment_method': {raw_payment_method}")
        payment_method = int(raw_payment_method)

        if validation_utils.is_valid_fare_attributes_transfers(raw_transfers) is False:
            raise ValueError(f"Invalid value for 'transfers': {raw_transfers}")
        transfers = int(raw_transfers)

        if validation_utils.is_string(raw_agency) is False:
            raise ValueError(f"Invalid type for 'agency': {type(raw_agency)}")
        agency = f"urn:ngsi-ld:GtfsAgency:{raw_agency}"
        
        if raw_transfer_duration is not None and raw_transfer_duration != "":
            if validation_utils.is_int(raw_transfer_duration) is False:
                raise ValueError(f"Invalid value for 'transfer_duration': {raw_transfer_duration}")
            transfer_duration = int(raw_transfer_duration)
            if transfer_duration < 0:
                raise ValueError(f"Invalid value for 'transfer_duration': {raw_transfer_duration}")

        
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
    
    required_fields = ["level_id", "level_index"]
    
    for level in raw_data:
        
        for field in required_fields:
            if not level.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        level_id = (level.get("level_id") or "").strip()
        level_name = (level.get("level_name") or "").strip() or None
        raw_level_index = (level.get("level_index") or "").strip()
        
        if validation_utils.is_string(level_id) is False:
            raise ValueError(f"Invalid type for 'level_id': {type(level_id)}")
        
        if level_name is not None and level_name != "":
            if validation_utils.is_string(level_name) is False:
                raise ValueError(f"Invalid type for 'level_name': {type(level_name)}")

        if validation_utils.is_float(raw_level_index) is False:
            raise ValueError(f"Invalid value for 'level_index': must be a floating point number")
        level_index = float(raw_level_index)
        
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

    required_fields = ["pathway_id", "from_stop_id", "to_stop_id", "pathway_mode", "is_bidirectional"]

    for pathway in raw_data:

        for field in required_fields:
            if not pathway.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        pathway_id = (pathway.get("pathway_id") or "").strip()
        raw_from_stop_id = (pathway.get("from_stop_id") or "").strip()
        raw_to_stop_id = (pathway.get("to_stop_id") or "").strip()
        raw_pathway_mode = (pathway.get("pathway_mode") or "").strip()
        raw_is_bidirectional = (pathway.get("is_bidirectional") or "").strip()
        raw_length = (pathway.get("length") or "").strip() or None
        raw_traversal_time = (pathway.get("traversal_time") or "").strip() or None
        raw_stair_count = (pathway.get("stair_count") or "").strip() or None
        raw_max_slope = (pathway.get("max_slope") or "").strip() or None
        raw_min_width = (pathway.get("min_width") or "").strip() or None
        signposted_as = (pathway.get("signposted_as") or "").strip() or None
        reversed_signposted_as = (pathway.get("reversed_signposted_as") or "").strip() or None

        length = None
        traversal_time = None
        stair_count = None
        max_slope = None
        min_width = None
        
        if validation_utils.is_string(pathway_id) is False:
            raise ValueError(f"Invalid type for 'pathway_id': {type(pathway_id)}")
        
        if validation_utils.is_string(raw_from_stop_id) is False:
            raise ValueError(f"Invalid type for 'from_stop_id': {type(raw_from_stop_id)}")
        from_stop_id = f"urn:ngsi-ld:GtfsStop:{raw_from_stop_id}"

        if validation_utils.is_string(raw_to_stop_id) is False:
            raise ValueError(f"Invalid type for 'to_stop_id': {type(raw_to_stop_id)}")
        to_stop_id = f"urn:ngsi-ld:GtfsStop:{raw_to_stop_id}"

        if validation_utils.is_valid_pathways_pathway_mode(raw_pathway_mode) is False:
            raise ValueError(f"Invalid value for 'pathway_mode: {raw_pathway_mode}")
        pathway_mode = int(raw_pathway_mode)

        if validation_utils.is_valid_pathways_is_bidirectional(raw_is_bidirectional) is False:
            raise ValueError(f"Invalid value for 'is_bidirectional: {raw_is_bidirectional}")
        is_bidirectional = int(raw_is_bidirectional)

        if raw_length is not None and raw_length != "":
            if validation_utils.is_float(raw_length) is False:
                raise ValueError(f"Invalid type for 'length': {type(raw_length)}")
            length = float(raw_length)
            if length < 0.0:
                raise ValueError(f"Invalid value for 'length': {length}")
            
        if raw_traversal_time is not None and raw_traversal_time != "":
            if validation_utils.is_float(raw_traversal_time) is False:
                raise ValueError(f"Invalid type for 'traversal_time': {type(raw_traversal_time)}")
            traversal_time = float(raw_traversal_time)
            if traversal_time <= 0.0:
                raise ValueError(f"Invalid value for 'traversal_time': {traversal_time}")
            
        if raw_stair_count is not None and raw_stair_count != "":
            if validation_utils.is_int(raw_stair_count) is False:
                raise ValueError(f"Invalid type for 'stair_count': {type(raw_stair_count)}")
            stair_count = int(raw_stair_count)
            
        if raw_max_slope is not None and raw_max_slope != "":
            if validation_utils.is_float(raw_max_slope) is False:
                raise ValueError(f"Invalid type for 'max_slope': {type(raw_max_slope)}")
            max_slope = float(raw_max_slope)

        if raw_min_width is not None and raw_min_width != "":
            if validation_utils.is_float(raw_min_width) is False:
                raise ValueError(f"Invalid type for 'min_width': {type(raw_min_width)}")
            min_width = float(raw_min_width)
            if min_width <= 0.0:
                raise ValueError(f"Invalid value for 'min_width': {min_width}")
            
        if signposted_as is not None and signposted_as != "":
            if validation_utils.is_string(signposted_as) is False:
                raise ValueError(f"Invalid value for 'signposted_as'")
            
        if reversed_signposted_as is not None and reversed_signposted_as != "":
            if validation_utils.is_string(reversed_signposted_as) is False:
                raise ValueError(f"Invalid value for 'reversed_signposted_as'")

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
    
    required_fields = ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type"]
    
    for route in raw_data:
        
        for field in required_fields:
            if not route.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        route_id = (route.get("route_id") or "").strip()
        agency_id = (route.get("agency_id") or "").strip()
        route_short_name = (route.get("route_short_name") or "").strip()
        route_long_name = (route.get("route_long_name") or "").strip()
        raw_route_type = (route.get("route_type") or "").strip()
        
        route_desc = (route.get("route_desc") or "").strip() or None
        route_url = (route.get("route_url") or "").strip() or None
        route_color = (route.get("route_color") or "").strip() or None
        route_text_color = (route.get("route_text_color") or "").strip() or None
        
        raw_route_sort_order = (route.get("route_sort_order") or "").strip() or None
        raw_continuous_pickup = (route.get("continuous_pickup") or "").strip() or None
        raw_continuous_drop_off = (route.get("continuous_drop_off") or "").strip() or None
        
        route_type = None
        route_sort_order = None
        continuous_pickup = None
        continuous_drop_off = None
        
        if validation_utils.is_string(route_id) is False:
            raise ValueError(f"Invalid type for 'route_id': {type(route_id)}")
        
        if validation_utils.is_string(agency_id) is False:
            raise ValueError(f"Invalid type for 'agency_id': {type(agency_id)}")
        
        if validation_utils.is_string(route_short_name) is False:
            raise ValueError(f"Invalid type for 'route_short_name': {type(route_short_name)}")
        
        if validation_utils.is_string(route_long_name) is False:
            raise ValueError(f"Invalid type for 'route_long_name': {type(route_long_name)}")
        
        if validation_utils.is_valid_route_type(raw_route_type) is False:
            raise ValueError(f"Invalid value for 'route_type': {raw_route_type}")
        route_type = int(raw_route_type)
        
        if route_desc is not None and route_desc != "":
            if validation_utils.is_string(route_desc) is False:
                raise ValueError(f"Invalid type for 'route_desc': {type(route_desc)}")
        
        if route_url is not None and route_url != "":
            if validation_utils.is_valid_url(route_url) is False:
                raise ValueError(f"Invalid URL format 'route_url': {route_url}")
        
        if route_color is not None and route_color != "":
            if validation_utils.is_valid_color(route_color) is False:
                raise ValueError(f"Invalid Color format 'route_color': {route_color}")
        
        if route_text_color is not None and route_text_color != "":
            if validation_utils.is_valid_color(route_text_color) is False:
                raise ValueError(f"Invalid Color format 'route_text_color': {route_text_color}")
        
        if raw_route_sort_order is not None and raw_route_sort_order != "":
            if validation_utils.is_int(raw_route_sort_order) is False:
                raise ValueError(f"Invalid type for 'route_sort_order': {type(raw_route_sort_order)}")
            route_sort_order = int(raw_route_sort_order)
            if route_sort_order < 0:
                raise ValueError(f"Invalid value for 'route_sort_order': {route_sort_order}")
            
        if raw_continuous_pickup is not None and raw_continuous_pickup != "":
            if validation_utils.is_valid_continuous_pickup(raw_continuous_pickup) is False:
                raise ValueError(f"Invalid value for 'continuous_pickup': {raw_continuous_pickup}")
            continuous_pickup = int(raw_continuous_pickup)
            
        if raw_continuous_drop_off is not None and raw_continuous_drop_off != "":
            if validation_utils.is_valid_continuous_pickup(raw_continuous_drop_off) is False:
                raise ValueError(f"Invalid value for 'continuous_drop_off': {raw_continuous_drop_off}")
            continuous_drop_off = int(raw_continuous_drop_off)
        
        # Populate FIWARE's data model
        ngsi_ld_route = {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:{route_id}",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsAgency:{agency_id}"
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

    required_fields = ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    for shape in raw_data:
        
        for field in required_fields:
            if not shape.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
            
        shape_id = (shape.get("shape_id") or "").strip()
        raw_location_longitude = (shape.get("shape_pt_lon") or "").strip()
        raw_location_latitude = (shape.get("shape_pt_lat") or "").strip()
        raw_shape_pt_sequence = (shape.get("shape_pt_sequence") or "").strip()
        raw_shape_dist_traveled = (shape.get("shape_dist_traveled") or "").strip()
        
        location_longitude = None
        location_latitude = None
        shape_pt_sequence = None
        shape_dist_traveled = None
        
        if validation_utils.is_string(shape_id) is False:
            raise ValueError(f"Invalid type for 'shape_id': {type(shape_id)}")
        
        if validation_utils.is_float(raw_location_longitude) is False:
            raise ValueError(f"Invalid type for 'shape_pt_lon': {type(raw_location_longitude)}")
        location_longitude = float(raw_location_longitude)
        
        if validation_utils.is_float(raw_location_latitude) is False:
            raise ValueError(f"Invalid type for 'shape_pt_lat': {type(raw_location_latitude)}")
        location_latitude = float(raw_location_latitude)
        
        if validation_utils.is_int(raw_shape_pt_sequence) is False:
            raise ValueError(f"Invalid type for 'shape_pt_sequence': {type(raw_shape_pt_sequence)}")
        shape_pt_sequence = int(raw_shape_pt_sequence)
        if shape_pt_sequence < 0:
            raise ValueError(f"Invalid value for 'shape_pt_sequence': {shape_pt_sequence}")
        
        if raw_shape_dist_traveled is not None and raw_shape_dist_traveled != "":
            if validation_utils.is_float(raw_shape_dist_traveled) is False:
                raise ValueError(f"Invalid type for shape_dist_traveled: {type(raw_shape_dist_traveled)}")
            shape_dist_traveled = float(raw_shape_dist_traveled)
            if shape_dist_traveled < 0:
                raise ValueError(f"Invalid value for 'shape_dist_traveled': {shape_dist_traveled}")
            
        if shape_id not in shapes_dict:
            shapes_dict[shape_id] = []

        shapes_dict[shape_id].append({"seq": shape_pt_sequence, "coords": [location_longitude, location_latitude], "dist": shape_dist_traveled})

    for shape_id, points in shapes_dict.items():
        points.sort(key=lambda p: p["seq"])
        coords = [p["coords"] for p in points]
        dist_trav = [p["dist"] for p in points if p["dist"] is not None or ""]
        
        if dist_trav == []:
            dist_trav = None
                
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
                    "coordinates": coords
                }
            },
            
            "distanceTravelled": {
                "type": "Property",
                "value": dist_trav
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
    
    always_required_fields = ["trip_id", "stop_sequence"]
    
    for stop_time in raw_data:
        
        for field in always_required_fields:
            if not stop_time.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
            
        has_arrival_departure = (
            bool(stop_time.get("arrival_time")) and
            bool(stop_time.get("departure_time"))
        )

        has_pickup_window = (
            bool(stop_time.get("start_pickup_drop_off_window")) and
            bool(stop_time.get("end_pickup_drop_off_window"))
        )
        
        
        if has_arrival_departure and has_pickup_window:
            raise ValueError(
                "arrival_time/departure_time and "
                "start_pickup_drop_off_window/end_pickup_drop_off_window "
                "cannot be defined at the same time"
            )

        if not has_arrival_departure and not has_pickup_window:
            raise ValueError(
                "Either arrival_time/departure_time or "
                "start_pickup_drop_off_window/end_pickup_drop_off_window "
                "must be defined"
            )
            
        if bool(stop_time.get("arrival_time")) ^ bool(stop_time.get("departure_time")):
            raise ValueError(
                "arrival_time and departure_time must be defined together"
            )

        if bool(stop_time.get("start_pickup_drop_off_window")) ^ bool(stop_time.get("end_pickup_drop_off_window")):
            raise ValueError(
                "start_pickup_drop_off_window and end_pickup_drop_off_window "
                "must be defined together"
            )
            
        has_stop_id = bool(stop_time.get("stop_id"))
        has_location_group_id = bool(stop_time.get("location_group_id"))
        has_location_id = bool(stop_time.get("location_id"))
        
        if has_location_group_id or has_location_id:
            if has_stop_id:
                raise ValueError("stop_id is forbidden when location_group_id or location_id is defined")
        else:
            if not has_stop_id:
                raise ValueError("stop_id is required when location_group_id and location_id are not defined")
            
            
        if has_stop_id or has_location_id:
            if has_location_group_id:
                raise ValueError("location_group_id is forbidden when stop_id or location_id is defined")
        else:
            if not has_location_group_id:
                raise ValueError("location_group_id is required when stop_id and location_id are not defined")
            
            
        if has_stop_id or has_location_group_id:
            if has_location_id:
                raise ValueError("location_id is forbidden when stop_id or location_group_id is defined")
        else:
            if not has_location_id:
                raise ValueError("location_id is required when stop_id and location_group_id are not defined")
        
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        raw_trip_id = (stop_time.get("trip_id") or "").strip()
        
        arrival_time = None
        departure_time = None
        stop_id = None
        location_group_id = None
        location_id = None
        stop_sequence = None
        start_pickup_drop_off_window = None
        end_pickup_drop_off_window = None
        pickup_type = None
        drop_off_type = None
        continuous_pickup = None
        continuous_drop_off = None
        shape_dist_traveled = None
        timepoint = None
        pickup_booking_rule_id = None
        drop_off_booking_rule_id = None
        
        if validation_utils.is_string(raw_trip_id) is False:
            raise ValueError(f"Invalid type for 'trip_id': {type(raw_trip_id)}")
        trip_id = f"urn:ngsi-ld:GtfsTrip:{raw_trip_id}"
        
        if has_arrival_departure:
            arrival_time = (stop_time.get("arrival_time") or "").strip()
            departure_time = (stop_time.get("departure_time") or "").strip()
            
            if validation_utils.is_valid_time(arrival_time) is False:
                raise ValueError(f"Invalid time format for 'arrival_time': {arrival_time}")
            
            if validation_utils.is_valid_time(departure_time) is False:
                raise ValueError(f"Invalid time format for 'departure_time': {departure_time}")
        
        
        if has_stop_id:
            raw_stop_id = (stop_time.get("stop_id") or "").strip()
            if validation_utils.is_string(raw_stop_id) is False:
                raise ValueError(f"Invalid type for 'stop_id': {type(raw_stop_id)}")
            stop_id = f"urn:ngsi-ld:GtfsStop:{raw_stop_id}"
            
        if has_location_group_id:
            raw_location_group_id = (stop_time.get("location_group_id") or "").strip()
            if validation_utils.is_string(raw_location_group_id) is False:
                raise ValueError(f"Invalid type for 'location_group_id': {type(raw_location_group_id)}")
            location_group_id = f"urn:ngsi-ld:GtfsLocationGroup:{raw_location_group_id}"
            
        if has_location_id:
            raw_location_id = (stop_time.get("location_id") or "").strip()
            if validation_utils.is_string(raw_location_id) is False:
                raise ValueError(f"Invalid type for 'location_id': {type(raw_location_id)}")
            location_id = f"urn:ngsi-ld:GtfsLocation:{raw_location_id}"
            
        raw_stop_sequence = (stop_time.get("stop_sequence") or "").strip()
        if validation_utils.is_int(raw_stop_sequence) is False:
            raise ValueError(f"Invalid type for 'stop_sequence': {type(raw_stop_sequence)}")
        stop_sequence = int(raw_stop_sequence)
        if stop_sequence < 0:
            raise ValueError(f"Invalid value for 'stop_sequence': {stop_sequence}")
        
        
        stop_headsign = (stop_time.get("stop_headsign") or "").strip() or None
        if stop_headsign is not None and stop_headsign != "":
            if validation_utils.is_string(stop_headsign) is False:
                raise ValueError(f"Invalid type for 'stop_headsign': {type(stop_headsign)}")
            
        if has_location_group_id or has_location_id:
            start_pickup_drop_off_window = (stop_time.get("start_pickup_drop_off_window") or "").strip()
            end_pickup_drop_off_window = (stop_time.get("end_pickup_drop_off_window") or "").strip()
            if validation_utils.is_valid_time(start_pickup_drop_off_window) is False:
                raise ValueError(f"Invalid time format for 'start_pickup_drop_off_window': {start_pickup_drop_off_window}")
            if validation_utils.is_valid_time(end_pickup_drop_off_window) is False:
                raise ValueError(f"Invalid time format for 'end_pickup_drop_off_window': {end_pickup_drop_off_window}")
            
        raw_pickup_type = (stop_time.get("pickup_type") or "").strip() or None
        if raw_pickup_type is not None and raw_pickup_type != "":
            if validation_utils.is_valid_pickup_type(raw_pickup_type) is False:
                raise ValueError(f"Invalid value for 'pickup_type': {raw_pickup_type}")
            pickup_type = int(raw_pickup_type)
            if has_location_id or has_location_group_id:
                if raw_pickup_type in (0, 3):
                    raise ValueError("pickup_type must not be 0 or 3 when start_pickup_drop_off_window  or end_pickup_drop_off_window is defined")
            
        raw_drop_off_type = (stop_time.get("drop_off_type") or "").strip() or None
        if raw_drop_off_type is not None and raw_drop_off_type != "":
            if validation_utils.is_valid_drop_off_type(raw_drop_off_type) is False:
                raise ValueError(f"Invalid value for 'drop_off_type': {raw_drop_off_type}")
            drop_off_type = int(raw_drop_off_type)
            if has_location_id or has_location_group_id:
                if raw_drop_off_type in (0, 3):
                    raise ValueError("drop_off_type must not be 0 or 3 when start_pickup_drop_off_window  or end_pickup_drop_off_window is defined")

        raw_continous_pickup = (stop_time.get("continuous_pickup") or "").strip() or None
        if raw_continous_pickup is not None and raw_continous_pickup != "":
            if validation_utils.is_valid_continuous_pickup(raw_continous_pickup) is False:
                raise ValueError(f"Invalid value for 'continuous_pickup': {raw_continous_pickup}")
            continuous_pickup = int(raw_continous_pickup)
            if has_location_id or has_location_group_id:
                if continuous_pickup != 1:
                    raise ValueError("continuous_pickup must be 1 when start_pickup_drop_off_window or end_pickup_drop_off_window is defined")
                
        raw_continous_drop_off = (stop_time.get("continuous_drop_off") or "").strip() or None
        if raw_continous_drop_off is not None and raw_continous_drop_off != "":
            if validation_utils.is_valid_continuous_drop_off(raw_continous_drop_off) is False:
                raise ValueError(f"Invalid value for 'continuous_drop_off': {raw_continous_drop_off}")
            continuous_drop_off = int(raw_continous_drop_off)
            if has_location_id or has_location_group_id:
                if continuous_drop_off != 1:
                    raise ValueError("continuous_drop_off must be 1 when start_pickup_drop_off_window or end_pickup_drop_off_window is defined")
                
        raw_shape_dist_traveled = (stop_time.get("shape_dist_traveled") or "").strip() or None
        if raw_shape_dist_traveled is not None and raw_shape_dist_traveled != "":
            if validation_utils.is_float(raw_shape_dist_traveled) is False:
                raise ValueError(f"Invalid type for 'shape_dist_traveled': {type(raw_shape_dist_traveled)}")
            shape_dist_traveled = float(raw_shape_dist_traveled)
            if shape_dist_traveled < 0:
                raise ValueError(f"Invalid value for 'shape_dist_traveled': {shape_dist_traveled}")
     
        raw_timepoint = (stop_time.get("timepoint") or "").strip() or None
        if raw_timepoint is not None and raw_timepoint != "":
            if validation_utils.is_valid_timepoint(raw_timepoint) is False:
                raise ValueError(f"Invalid value for 'timepoint': {raw_timepoint}")
            timepoint = int(raw_timepoint)
            
        raw_pickup_booking_rule_id = (stop_time.get("pickup_booking_rule_id") or "").strip() or None
        if raw_pickup_booking_rule_id is not None and raw_pickup_booking_rule_id != "":
            if validation_utils.is_string(raw_pickup_booking_rule_id) is False:
                raise ValueError(f"Invalid type for 'pickup_booking_rule_id': {type(raw_pickup_booking_rule_id)}")
            pickup_booking_rule_id = f"urn:ngsi-ld:GtfsBookingRule:{raw_pickup_booking_rule_id}"
            
        raw_drop_off_booking_rule_id = (stop_time.get("drop_off_booking_rule_id") or "").strip() or None
        if raw_drop_off_booking_rule_id is not None and raw_drop_off_booking_rule_id != "":
            if validation_utils.is_string(raw_drop_off_booking_rule_id) is False:
                raise ValueError(f"Invalid type for 'drop_off_booking_rule_id': {type(raw_drop_off_booking_rule_id)}")
            drop_off_booking_rule_id = f"urn:ngsi-ld:GtfsBookingRule:{raw_drop_off_booking_rule_id}"
        
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
            
            "location_group_id": {
                "type": "Relationship",
                "object": location_group_id
            },
            
            "location_id": {
                "type": "Relationship",
                "object": location_id
            },

            "stopSequence": {
                "type": "Property", 
                "value": stop_sequence
            },
            
            "stopHeadsign": {
                "type": "Property", 
                "value": stop_headsign
            },
            
            "start_pickup_drop_off_window": {
                "type": "Property",
                "value": start_pickup_drop_off_window
            },
            
            "end_pickup_drop_off_window": {
                "type": "Property",
                "value": end_pickup_drop_off_window
            },
            
            "pickupType": {
                "type": "Property", 
                "value": pickup_type
            },
            
            "dropOffType": {
                "type": "Property", 
                "value": drop_off_type
            },
            
            "continuousPickup": {
                "type": "Property", 
                "value": continuous_pickup
            },
            
            "continuousDropOff": {
                "type": "Property", 
                "value": continuous_drop_off
            },
            
            "shapeDistTraveled": {  
                "type": "Property", 
                "value": shape_dist_traveled
            },
            
            "timepoint": {
                "type": "Property", 
                "value": timepoint
            },
            
            "pickup_booking_rule_id": {
                "type": "Relationship",
                "object": pickup_booking_rule_id
            },
            
            "drop_off_booking_rule_id": {
                "type": "Relationship",
                "object": drop_off_booking_rule_id
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
    
    required_fields = ["stop_id", "stop_name", "stop_lat", "stop_lon", "parent_station"]
    for stop in raw_data:
        
        for field in required_fields:
            if not stop.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
            
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        stop_id = (stop.get("stop_id") or "").strip()
        stop_code = (stop.get("stop_code") or "").strip() or None
        stop_name = (stop.get("stop_name") or "").strip()
        tts_stop_name = (stop.get("tts_stop_name") or "").strip() or None
        stop_desc = (stop.get("stop_desc") or "").strip() or None
        raw_stop_longitude = (stop.get("stop_lon") or "").strip()
        raw_stop_latitude = (stop.get("stop_lat") or "").strip()
        raw_zone_id = (stop.get("zone_id") or "").strip() or None
        stop_url = (stop.get("stop_url") or "").strip() or None
        raw_location_type = (stop.get("location_type") or "").strip() or None
        raw_parent_station = (stop.get("parent_station") or "").strip() or None
        stop_timezone = (stop.get("stop_timezone") or "") or None
        raw_wheelchair_boarding = (stop.get("wheelchair_boarding") or "").strip() or None
        raw_level_id = (stop.get("level_id") or "").strip() or None
        platform_code = (stop.get("platform_code") or "").strip() or None
        raw_stop_access = (stop.get("stop_access") or "").strip() or None
        
        stop_longitude = None
        stop_latitude = None
        zone_id = None
        location_type = None
        parent_station = None
        wheelchair_boarding = None
        level_id = None
        stop_access = None
        
        if validation_utils.is_string(stop_id) is False:
            raise ValueError(f"Invalid type for 'stop_id': {type(stop_id)}")
        
        if stop_code is not None and stop_code != "":
            if validation_utils.is_string(stop_code) is False:
                raise ValueError(f"Invalid type for 'stop_code': {type(stop_code)}")
        
        if validation_utils.is_string(stop_name) is False:
            raise ValueError(f"Invalid type for 'stop_name': {type(stop_name)}")
        
        if stop_code is not None and stop_code != "":
            if validation_utils.is_string(tts_stop_name) is False:
                raise ValueError(f"Invalid type for 'tts_stop_name': {type(tts_stop_name)}")
            
        if stop_desc is not None and stop_desc != "":
            if validation_utils.is_string(stop_desc) is False:
                raise ValueError(f"Invalid type for 'stop_desc': {type(stop_desc)}")
        
        if validation_utils.is_float(raw_stop_longitude) is False:
            raise ValueError(f"Invalid type for 'stop_lon': {type(raw_stop_longitude)}")
        stop_longitude = float(raw_stop_longitude)
        
        if validation_utils.is_float(raw_stop_latitude) is False:
            raise ValueError(f"Invalid type for 'stop_lat': {type(raw_stop_latitude)}")
        stop_latitude = float(raw_stop_latitude)
        
        if raw_zone_id is not None and raw_zone_id != "":
            if validation_utils.is_string(raw_zone_id) is False:
               raise ValueError(f"Invalid type for 'zone_id': {type(raw_zone_id)}") 
            zone_id = f"urn:ngsi-ld:GtfsZone:{raw_zone_id}"
            
        if stop_url is not None and stop_url != "":
            if validation_utils.is_valid_url(stop_url) is False:
                raise ValueError(f"Invalid URL for 'stop_url': {stop_url}")
            
        if raw_location_type is not None and raw_location_type != "":
            if validation_utils.is_valid_location_type(raw_location_type) is False:
                raise ValueError(f"Invalid value for 'location_type': {raw_location_type}")
            location_type = int(raw_location_type)
            
        if location_type == 1:
            if raw_parent_station:
                raise ValueError("parent_station is forbidden when location_type = 1 (station)")
        elif location_type in (2, 3, 4):
            if not raw_parent_station:
                raise ValueError(f"parent_station is required when location_type = {location_type}")
            parent_station = f"urn:ngsi-ld:GtfsStation:{raw_parent_station}"
        elif location_type == 0:
            if raw_parent_station:
                parent_station = f"urn:ngsi-ld:GtfsStation:{raw_parent_station}"
        else:
            raise ValueError(f"Invalid location_type: {location_type}")
        
        if stop_timezone is not None and stop_timezone != "":
            if validation_utils.is_valid_timezone(stop_timezone) is False:
                raise ValueError(f"Invalid timezone for 'stop_timezone'")
            
        if raw_wheelchair_boarding is not None and raw_wheelchair_boarding != "":
            if validation_utils.is_valid_wheelchair_boarding(raw_wheelchair_boarding) is False:
                raise ValueError(f"Invalid value for 'wheelchair_boarding': {raw_wheelchair_boarding}")
            wheelchair_boarding = int(raw_wheelchair_boarding)
        
        if raw_level_id is not None and raw_level_id != "":
            if validation_utils.is_string(raw_level_id) is False:
                raise ValueError(f"Invalid type for 'level_id': {type(raw_level_id)}")
            level_id = f"urn:ngsi-ld:GtfsLevel:{raw_level_id}"
            
        if platform_code is not None and platform_code != "":
            if validation_utils.is_string(platform_code) is False:
                raise ValueError(f"Invalid type for 'platform_code': {type(platform_code)}")
            
        if raw_stop_access:
            if validation_utils.is_valid_stop_access(raw_stop_access) is False:
                raise ValueError(f"Invalid value for 'stop_access': {raw_stop_access}")

            if location_type in (1, 2, 3, 4):
                raise ValueError(f"stop_access is forbidden when location_type={location_type}")

            if not raw_parent_station:
                raise ValueError("stop_access is forbidden when parent_station is empty")

            stop_access = int(raw_stop_access)
        
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
            
            "tts_stop_name":{
                "type": "Property",
                "value": tts_stop_name
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
            
            "zone_id": {
                "type": "Relationship",
                "object": zone_id
            },
            
            "stop_url": {
                "type": "Property",
                "value": stop_url
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
            
            "wheelchair_boarding": {
                "type": "Property",
                "value": wheelchair_boarding
            },
            
            "level": {
                "type": "Relationship",
                "object": level_id
            },
            
            "platform_code": {
                "type": "Property",
                "value": platform_code
            },
            
            "stop_access": {
                "type": "Property",
                "value": stop_access
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
    
    required_fields = ["transfer_type"]
    
    for transfer in raw_data:
        
        for field in required_fields:
            if not transfer.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")

        raw_transfer_type = (transfer.get("transfer_type") or "").strip()
        if validation_utils.is_valid_transfer_type(raw_transfer_type) is False:
            raise ValueError(f"Invalid value for 'transfer_type': {raw_transfer_type}")
        transfer_type = int(raw_transfer_type)
        
        raw_from_stop_id = (transfer.get("from_stop_id") or "").strip() or None
        raw_to_stop_id = (transfer.get("to_stop_id") or "").strip() or None
        raw_from_route_id = (transfer.get("from_route_id") or "").strip() or None
        raw_to_route_id = (transfer.get("to_route_id") or "").strip() or None
        raw_from_trip_id = (transfer.get("from_trip_id") or "").strip() or None
        raw_to_trip_id = (transfer.get("to_trip_id") or "").strip() or None
        raw_min_transfer_time = (transfer.get("min_transfer_time") or "").strip() or None
        
        from_stop_id = None
        to_stop_id = None
        from_route_id = None
        to_route_id = None
        from_trip_id = None
        to_trip_id = None
        min_transfer_time = None
        
        if transfer_type in {1, 2, 3}:
            if not raw_from_stop_id or not raw_to_stop_id:
                raise ValueError(f"from_stop_id and to_stop_id are required when transfer_type = {transfer_type}")
            from_stop_id = f"urn:ngsi-ld:GtfsStop:{raw_from_stop_id}"
            to_stop_id = f"urn:ngsi-ld:GtfsStop:{raw_to_stop_id}"
        else:
            if raw_from_stop_id:
                from_stop_id = f"urn:ngsi-ld:GtfsStop:{raw_from_stop_id}"
            if raw_to_stop_id:
                to_stop_id = f"urn:ngsi-ld:GtfsStop:{raw_to_stop_id}"

        
        if raw_from_route_id is not None and raw_from_route_id != "":
            if validation_utils.is_string(raw_from_route_id) is False:
                raise ValueError(f"Invalid type for 'from_route_id': {type(raw_from_route_id)}")
            from_route_id = f"urn:ngsi-ld:GtfsRoute:{raw_from_route_id}"
               
        if raw_to_route_id is not None and raw_to_route_id != "":
            if validation_utils.is_string(raw_to_route_id) is False:
                raise ValueError(f"Invalid type for 'to_route_id': {type(raw_to_route_id)}")
            to_route_id = f"urn:ngsi-ld:GtfsRoute:{raw_to_route_id}"
            
        if transfer_type in {4, 5}:
            if not raw_from_trip_id or not raw_to_trip_id:
                raise ValueError(f"from_trip_id and to_trip_id are required when transfer_type = {transfer_type}")
            from_trip_id = f"urn:ngsi-ld:GtfsTrip:{raw_from_trip_id}"
            to_trip_id = f"urn:ngsi-ld:GtfsTrip:{raw_to_trip_id}"
        else:
            if raw_from_trip_id:
                from_trip_id = f"urn:ngsi-ld:GtfsTrip:{raw_from_trip_id}"
            if raw_to_trip_id:
                to_trip_id = f"urn:ngsi-ld:GtfsTrip:{raw_to_trip_id}"

        if raw_min_transfer_time is not None and raw_min_transfer_time != "":
            if validation_utils.is_int(raw_min_transfer_time) is False:
                raise ValueError(f"Invalid type for 'min_transfer_time': {type(raw_min_transfer_time)}")
            min_transfer_time = int(raw_min_transfer_time)
            if min_transfer_time < 0:
                raise ValueError(f"Invalid value for 'min_transfer_time': {min_transfer_time}")
            
        id_parts = [
            "Transfer",
        ]
        
        if from_stop_id:
            id_parts.append(f"fromStop:{from_stop_id}")
            
        if to_stop_id:
            id_parts.append(f"toStop:{to_stop_id}")

        if from_trip_id:
            id_parts.append(f"fromTrip:{from_trip_id}")

        if to_trip_id:
            id_parts.append(f"toTrip:{to_trip_id}")

        if from_route_id:
            id_parts.append(f"fromRoute:{from_route_id}")

        if to_route_id:
            id_parts.append(f"toRoute:{to_route_id}")
            
        entity_id = "urn:ngsi-ld:GtfsTransfer:" + ":".join(id_parts)


        # Populate FIWARE's data model
        ngsi_ld_transfer = {
            "id": entity_id,
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
    
    required_fields = ["route_id", "service_id", "trip_id"]
    
    for trip in raw_data:
        
        for field in required_fields:
            if not trip.get(field):
                raise ValueError(f"Missing required GTFS field: {field}")
                
        # Get GTFS Static data fields and transform them into the specific data types (str, int, float etc)
        trip_id = (trip.get("trip_id") or "").strip()
        raw_route_id = (trip.get("route_id") or "").strip()
        raw_service_id = (trip.get("service_id") or "").strip()
        trip_headsign = (trip.get("trip_headsign") or "").strip() or None
        trip_short_name = (trip.get("trip_short_name") or "").strip() or None
        raw_direction_id = (trip.get("direction_id") or "").strip() or None
        raw_block_id = (trip.get("block_id") or "").strip() or None
        raw_shape_id = (trip.get("shape_id") or "").strip() or None
        raw_wheelchair_accessible = (trip.get("wheelchair_accessible") or "").strip() or None
        raw_bikes_allowed = (trip.get("bikes_allowed") or  "").strip() or None
        raw_cars_allowed = (trip.get("cars_allowed") or "").strip() or None
        
        route_id = None
        service_id = None
        direction_id = None
        block_id = None
        shape_id = None
        wheelchair_accessible = None
        bikes_allowed = None
        cars_allowed = None
        
        if validation_utils.is_string(trip_id) is False:
            raise ValueError(f"Invalid type for 'trip_id': {type(trip_id)}")
        
        if validation_utils.is_string(raw_route_id) is False:
            raise ValueError(f"Invalid type for 'route_id': {type(raw_route_id)}")
        route_id = f"urn:ngsi-ld:GtfsRoute:{raw_route_id}"
        
        if validation_utils.is_string(raw_service_id) is False:
            raise ValueError(f"Invalid type for 'service_id': {type(raw_service_id)}")
        service_id = f"urn:ngsi-ld:GtfsService:{raw_service_id}"
        
        if trip_headsign is not None and trip_headsign != "":
            if validation_utils.is_string(trip_headsign) is False:
                raise ValueError(f"Invalid type for 'trip_headsign': {type(trip_headsign)}")
            
        if trip_short_name is not None and trip_short_name != "":
            if validation_utils.is_string(trip_short_name) is False:
                raise ValueError(f"Invalid type for 'trip_short_name': {type(trip_short_name)}")
        
        if raw_direction_id is not None and raw_direction_id != "":
            if validation_utils.is_valid_direction_id(raw_direction_id) is False:
                raise ValueError(f"Invalid value for 'direction_id': {raw_direction_id}")
            
        if raw_block_id is not None and raw_block_id != "":
            if validation_utils.is_string(raw_block_id) is False:
                raise ValueError(f"Invalid type for 'block_id': {type(raw_block_id)}")
            block_id = f"urn:ngsi-ld:GtfsBlock:{raw_block_id}"
            
        if raw_shape_id is not None and raw_shape_id != "":
            if validation_utils.is_string(raw_shape_id) is False:
                raise ValueError(f"Invalid type for 'shape_id': {type(raw_shape_id)}")  
            shape_id = f"urn:ngsi-ld:GtfsShape:{raw_shape_id}"
            
        if raw_wheelchair_accessible is not None and raw_wheelchair_accessible != "":
            if validation_utils.is_valid_wheelchair_accessible(raw_wheelchair_accessible) is False:
                raise ValueError(f"Invalid value for 'wheelchair_accessible': {raw_wheelchair_accessible}")
            wheelchair_accessible = int(raw_wheelchair_accessible)
            
        if raw_bikes_allowed is not None and raw_bikes_allowed != "":
            if validation_utils.is_valid_bikes_allowed(raw_bikes_allowed) is False:
                raise ValueError(f"Invalid value for 'bikes_allowed': {raw_bikes_allowed}")
            bikes_allowed = int(raw_bikes_allowed)
            
        if raw_cars_allowed is not None and raw_cars_allowed != "":
            if validation_utils.is_valid_cars_allowed(raw_cars_allowed) is False:
                raise ValueError(f"Invalid value for 'cars_allowed': {raw_cars_allowed}")
            cars_allowed = int(raw_cars_allowed)
        
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
            },
            
            "carsAllowed": {
                "type": "Property",
                "value": cars_allowed
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