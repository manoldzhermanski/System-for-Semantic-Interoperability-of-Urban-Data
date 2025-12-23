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

# -----------------------------------------------------
# Get Data
# -----------------------------------------------------

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
    
# -----------------------------------------------------
# Read Data
# -----------------------------------------------------

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
    
# -----------------------------------------------------
# Required field checks
# -----------------------------------------------------

def validate_required_fields(data: dict[str, Any],required_fields: list[str]) -> None:
    """
    Validates that all required GTFS fields are present and not empty.

    Args:
        data (dict[str, Any]): The GTFS record to validate.
        required_fields (list[str]): A list of field names that must be present in the data.

    Raises:
        ValueError: If any of the required fields are missing or empty.
    """

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required GTFS field: {field}")

        value = data.get(field)

        if value is None:
            raise ValueError(f"Missing required GTFS field: {field}")

        if isinstance(value, str) and value == "":
            raise ValueError(f"Missing required GTFS field: {field}")

# -----------------------------------------------------
# Cleanup string
# -----------------------------------------------------

def cleanup_string(value: Any) -> str | None:
    """
    Cleans up a value by converting it to string, stripping whitespace,
    and normalizing empty values to None.

    Args:
        value (Any): Input value, typically a string from CSV data.

    Returns:
        str | None: Cleaned string, or None if the value is empty or null.
    """

    if value in (None, ""):
        return None
    value = str(value).strip()
    return value or None

# -----------------------------------------------------
# Parse functions
# -----------------------------------------------------

def parse_int(value: str | None, field: str) -> int | None:
    """
    Parses a string into a int, handling empty or None values.

    Args:
        value (str | None): The string to parse. Can be empty or None.
        field (str): The name of the field (used in error messages).

    Returns:
        int | None: The parsed int value, or None if input is empty or None.

    Raises:
        ValueError: If the string cannot be parsed as a int.
    """

    value = cleanup_string(value)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{field} must be integer, got '{value}'")

def parse_float(value: str | None, field: str) -> float | None:
    """
    Parses a string into a float, handling empty or None values.

    Args:
        value (str | None): The string to parse. Can be empty or None.
        field (str): The name of the field (used in error messages).

    Returns:
        float | None: The parsed float value, or None if input is empty or None.

    Raises:
        ValueError: If the string cannot be parsed as a float.
    """

    value = cleanup_string(value)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{field} must be float, got '{value}'")
    
def parse_date(value: str | None, field: str) -> str | None:    
    """
    Parses a date into a YYYYMMDD format.

    Args:
        value (str): The date string.
        field (str): The name of the field (used in error messages).

    Returns:
        str | None: The date in YYYYMMDD format, or None if input is empty or None.

    Raises:
        ValueError: If not in the expected YYYYMMDD format.
    """

    clean_value = cleanup_string(value)
    if clean_value in (None, ""):
        return None
    try:
        return datetime.strptime(clean_value, "%Y%m%d").date().strftime("%Y%m%d")
    except ValueError:
        raise ValueError(f"{field} must be a valid date in YYYYMMDD format, got '{clean_value}'")

def parse_time(value: str | None, field: str) -> str | None:
    """
    Parses a time string into HH:MM:SS format

    Args:
        value (str): The time string. Hours may exceed 24.
        field (str): The name of the field (used in error messages).

    Returns:
        string: A string representing the parsed time, or None if input is empty or None.

    Raises:
        ValueError: If the input is empty, not in HH:MM:SS format, or contains invalid numbers
        (minutes or seconds not in 0–59, hours negative).
    """

    clean_value = cleanup_string(value)
    if clean_value in (None, ""):
        return None

    parts = clean_value.split(":")
    if len(parts) != 3:
        raise ValueError(f"{field} must be in HH:MM:SS format, got '{clean_value}'")

    try:
        hours, minutes, seconds = map(int, parts)
        if minutes not in range(60) or seconds not in range(60) or hours < 0:
            raise ValueError
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except ValueError:
        raise ValueError(f"{field} must be a valid time in HH:MM:SS format, got '{value}'")

def parse_gtfs_agency_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS agency record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'agency.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - agency_id: str | None
            - agency_name: str | None
            - agency_url: str | None
            - agency_timezone: str | None
            - agency_lang: str | None
            - agency_phone: str | None
            - agency_fare_url: str | None
            - agency_email: str | None
            - cemv_support: int | None

    Raises:
        ValueError: If 'cemv_support' cannot be parsed as an integer.
    """

    return {
        "agency_id": cleanup_string(entity.get("agency_id")),
        "agency_name": cleanup_string(entity.get("agency_name")),
        "agency_url": cleanup_string(entity.get("agency_url")),
        "agency_timezone": cleanup_string(entity.get("agency_timezone")),
        "agency_lang": cleanup_string(entity.get("agency_lang")),
        "agency_phone": cleanup_string(entity.get("agency_phone")),
        "agency_fare_url": cleanup_string(entity.get("agency_fare_url")),
        "agency_email": cleanup_string(entity.get("agency_email")),
        "cemv_support": parse_int(entity.get("cemv_support"), "cemv_support"),
    }

def parse_gtfs_calendar_dates_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS calendar_dates record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'calendar_dates.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - service_id: str | None
            - date: str (YYYYMMDD format)
            - exception_type: int | None

    Raises:
        ValueError: If 'date' is not in YYYYMMDD format or 'exception_type' cannot be parsed as integer.
    """

    return {
        "service_id": cleanup_string(entity.get("service_id")),
        "date": parse_date(entity.get("date"), "date"),
        "exception_type": parse_int(entity.get("exception_type"), "exception_type")
    }

def parse_gtfs_fare_attributes_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS fare attribute record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'fare_attributes.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - fare_id: str | None
            - price: float | None
            - currency_type: str | None
            - payment_method: int | None
            - transfers: int | None
            - agency_id: str | None
            - transfer_duration: int | None

    Raises:
        ValueError: If any float or integer field cannot be parsed correctly.
    """

    return {
        "fare_id": cleanup_string(entity.get("fare_id")),
        "price": parse_float(entity.get("price"), "price"),
        "currency_type": cleanup_string(entity.get("currency_type")),
        "payment_method": parse_int(entity.get("payment_method"), "payment_method"),
        "transfers": parse_int(entity.get("transfers"), "transfers"),
        "agency_id": cleanup_string(entity.get("agency_id")),
        "transfer_duration": parse_int(entity.get("transfer_duration"), "transfer_duration")
    }

def parse_gtfs_levels_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS level record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'levels.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - level_id: str | None
            - level_index: float | None
            - level_name: str | None

    Raises:
        ValueError: If 'level_index' cannot be parsed as a float.
    """

    return {
        "level_id": cleanup_string(entity.get("level_id")),
        "level_index": parse_float(entity.get("level_index"), "level_index"),
        "level_name": cleanup_string(entity.get("level_name"))
    }

def parse_gtfs_pathways_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS pathway record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'pathways.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - pathway_id: str | None
            - from_stop_id: str | None
            - to_stop_id: str | None
            - pathway_mode: int | None
            - is_bidirectional: int | None
            - length: float | None
            - traversal_time: int | None
            - stair_count: int | None
            - max_slope: float | None
            - min_width: float | None
            - signposted_as: str | None
            - reversed_signposted_as: str | None

    Raises:
        ValueError: If any integer or float field cannot be parsed correctly.
    """

    return {
        "pathway_id": cleanup_string(entity.get("pathway_id")),
        "from_stop_id": cleanup_string(entity.get("from_stop_id")),
        "to_stop_id": cleanup_string(entity.get("to_stop_id")),
        "pathway_mode": parse_int(entity.get("pathway_mode"), "pathway_mode"),
        "is_bidirectional": parse_int(entity.get("is_bidirectional"), "is_bidirectional"),
        "length": parse_float(entity.get("length"), "length"),
        "traversal_time": parse_int(entity.get("traversal_time"), "traversal_time"),
        "stair_count": parse_int(entity.get("stair_count"), "stair_count"),
        "max_slope": parse_float(entity.get("max_slope"), "max_slope"),
        "min_width": parse_float(entity.get("min_width"), "min_width"),
        "signposted_as": cleanup_string(entity.get("signposted_as")),
        "reversed_signposted_as": cleanup_string(entity.get("reversed_signposted_as"))
    }

def parse_gtfs_routes_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS route record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'routes.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - route_id: str | None
            - agency_id: str | None
            - route_short_name: str | None
            - route_long_name: str | None
            - route_desc: str | None
            - route_type: int | None
            - route_url: str | None
            - route_color: str | None
            - route_text_color: str | None
            - route_sort_order: int | None
            - continuous_pickup: int | None
            - continuous_drop_off: int | None
            - network_id: str | None
            - cemv_support: int | None

    Raises:
        ValueError: If any integer field cannot be parsed correctly.
    """

    return {
        "route_id": cleanup_string(entity.get("route_id")),
        "agency_id": cleanup_string(entity.get("agency_id")),
        "route_short_name": cleanup_string(entity.get("route_short_name")),
        "route_long_name": cleanup_string(entity.get("route_long_name")),
        "route_desc": cleanup_string(entity.get("route_desc")),
        "route_type": parse_int(entity.get("route_type"), "route_type"),
        "route_url": cleanup_string(entity.get("route_url")),
        "route_color": cleanup_string(entity.get("route_color")),
        "route_text_color": cleanup_string(entity.get("route_text_color")),
        "route_sort_order": parse_int(entity.get("route_sort_order"), "route_sort_order"),
        "continuous_pickup": parse_int(entity.get("continuous_pickup"), "continuous_pickup"),
        "continuous_drop_off": parse_int(entity.get("continuous_drop_off"), "continuous_drop_off"),
        "network_id": cleanup_string(entity.get("network_id")),
        "cemv_support": parse_int(entity.get("cemv_support"), "cemv_support")
    }

def parse_gtfs_shapes_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS shape record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'shapes.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - shape_id: str | None
            - shape_pt_lat: float | None
            - shape_pt_lon: float | None
            - shape_pt_sequence: int | None
            - shape_dist_traveled: float | None

    Raises:
        ValueError: If any float or integer field cannot be parsed correctly.
    """

    return {
        "shape_id": cleanup_string(entity.get("shape_id")),
        "shape_pt_lat": parse_float(entity.get("shape_pt_lat"), "shape_pt_lat"),
        "shape_pt_lon": parse_float(entity.get("shape_pt_lon"), "shape_pt_lon"),
        "shape_pt_sequence": parse_int(entity.get("shape_pt_sequence"), "shape_pt_sequence"),
        "shape_dist_traveled": parse_float(entity.get("shape_dist_traveled"), "shape_dist_traveled")
    }

def parse_gtfs_stop_times_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS stop_times record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'stop_times.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - trip_id: str | None
            - arrival_time: str | None (GTFS HH:MM:SS, supports over 24h)
            - departure_time: str | None (GTFS HH:MM:SS, supports over 24h)
            - stop_id: str | None
            - location_group_id: str | None
            - location_id: str | None
            - stop_sequence: int | None
            - stop_headsign: str | None
            - start_pickup_drop_off_window: str | None
            - end_pickup_drop_off_window: str | None
            - pickup_type: int | None
            - drop_off_type: int | None
            - continuous_pickup: int | None
            - continuous_drop_off: int | None
            - shape_dist_traveled: float | None
            - timepoint: int | None
            - pickup_booking_rule_id: str | None
            - drop_off_booking_rule_id: str | None

    Raises:
        ValueError: If any integer field ('stop_sequence', 'pickup_type', etc.) or float field 
        ('shape_dist_traveled') cannot be parsed, or if any GTFS time field cannot be parsed.
    """
    
    return {
        "trip_id": cleanup_string(entity.get("trip_id")),
        "arrival_time": parse_time(entity.get("arrival_time"), "arrival_time"),
        "departure_time": parse_time(entity.get("departure_time"), "departure_time"),
        "stop_id": cleanup_string(entity.get("stop_id")),
        "location_group_id": cleanup_string(entity.get("location_group_id")),
        "location_id": cleanup_string(entity.get("location_id")),
        "stop_sequence": parse_int(entity.get("stop_sequence"), "stop_sequence"),
        "stop_headsign": cleanup_string(entity.get("stop_headsign")),
        "start_pickup_drop_off_window": parse_time(entity.get("start_pickup_drop_off_window"), "start_pickup_drop_off_window"),
        "end_pickup_drop_off_window": parse_time(entity.get("end_pickup_drop_off_window"), "end_pickup_drop_off_window"),
        "pickup_type": parse_int(entity.get("pickup_type"), "pickup_type"),
        "drop_off_type": parse_int(entity.get("drop_off_type"), "drop_off_type"),
        "continuous_pickup": parse_int(entity.get("continuous_pickup"), "continuous_pickup"),
        "continuous_drop_off": parse_int(entity.get("continuous_drop_off"), "continuous_drop_off"),
        "shape_dist_traveled": parse_float(entity.get("shape_dist_traveled"), "shape_dist_traveled"),
        "timepoint": parse_int(entity.get("timepoint"), "timepoint"),
        "pickup_booking_rule_id": cleanup_string(entity.get("pickup_booking_rule_id")),
        "drop_off_booking_rule_id": cleanup_string(entity.get("drop_off_booking_rule_id"))
    }

def parse_gtfs_stops_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS stop record into a cleaned and typed dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a single row from 'stops.txt',
            where all values are strings as read from the CSV.

    Returns:
        dict[str, Any]: A dictionary with cleaned and properly typed fields:
            - stop_id: str | None
            - stop_code: str | None
            - stop_name: str | None
            - tts_stop_name: str | None
            - stop_desc: str | None
            - stop_lat: float | None
            - stop_lon: float | None
            - zone_id: str | None
            - stop_url: str | None
            - location_type: int | None
            - parent_station: str | None
            - stop_timezone: str | None
            - wheelchair_boarding: int | None
            - level_id: str | None
            - platform_code: str | None
            - stop_access: int | None

    Raises:
        ValueError: If any integer or float field cannot be parsed correctly.
    """
        
    return {
        "stop_id": cleanup_string(entity.get("stop_id")),
        "stop_code": cleanup_string(entity.get("stop_code")),
        "stop_name": cleanup_string(entity.get("stop_name")),
        "tts_stop_name": cleanup_string(entity.get("tts_stop_name")),
        "stop_desc": cleanup_string(entity.get("stop_desc")),
        "stop_lat": parse_float(entity.get("stop_lat"), "stop_lat"),
        "stop_lon": parse_float(entity.get("stop_lon"), "stop_lon"),
        "zone_id": cleanup_string(entity.get("zone_id")),
        "stop_url": cleanup_string(entity.get("stop_url")),
        "location_type": parse_int(entity.get("location_type"), "location_type"),
        "parent_station": cleanup_string(entity.get("parent_station")),
        "stop_timezone": cleanup_string(entity.get("stop_timezone")),
        "wheelchair_boarding": parse_int(entity.get("wheelchair_boarding"), "wheelchair_boarding"),
        "level_id": cleanup_string(entity.get("level_id")),
        "platform_code": cleanup_string(entity.get("platform_code")),
        "stop_access": parse_int(entity.get("stop_access"), "stop_access")
    }

def parse_gtfs_transfers_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS transfer record into typed and cleaned dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a GTFS 'transfers.txt' row, with string values for all fields.

    Returns:
        dict[str, Any]: A dictionary with cleaned and typed fields:
            - from_stop_id: str | None
            - to_stop_id: str | None
            - from_route_id: str | None
            - to_route_id: str | None
            - from_trip_id: str | None
            - to_trip_id: str | None
            - transfer_type: int | None
            - min_transfer_time: int | None

    Raises:
        ValueError: If 'transfer_type' or 'min_transfer_time' cannot be parsed as integer.
    """
    return {
        "from_stop_id": cleanup_string(entity.get("from_stop_id")),
        "to_stop_id": cleanup_string(entity.get("to_stop_id")),
        "from_route_id": cleanup_string(entity.get("from_route_id")),
        "to_route_id": cleanup_string(entity.get("to_route_id")),
        "from_trip_id": cleanup_string(entity.get("from_trip_id")),
        "to_trip_id": cleanup_string(entity.get("to_trip_id")),
        "transfer_type": parse_int(entity.get("transfer_type"), "transfer_type"),
        "min_transfer_time": parse_int(entity.get("min_transfer_time"), "min_transfer_time")
    }

def parse_gtfs_trips_data(entity: dict[str, str]) -> dict[str, Any]:
    """
    Parses a single GTFS trip record into typed and cleaned dictionary.

    Args:
        entity (dict[str, str]): A dictionary representing a GTFS 'trips.txt' row, with string values for all fields.

    Returns:
        dict[str, Any]: A dictionary with cleaned and typed fields:
            - route_id: str | None
            - service_id: str | None
            - trip_id: str | None
            - trip_headsign: str | None
            - trip_short_name: str | None
            - direction_id: int | None
            - block_id: str | None
            - shape_id: str | None
            - wheelchair_accessible: int | None
            - bikes_allowed: int | None
            - cars_allowed: int | None

    Raises:
        ValueError: If any integer field cannot be parsed correctly.
    """

    return {
        "route_id": cleanup_string(entity.get("route_id")),
        "service_id": cleanup_string(entity.get("service_id")),
        "trip_id": cleanup_string(entity.get("trip_id")),
        "trip_headsign": cleanup_string(entity.get("trip_headsign")),
        "trip_short_name": cleanup_string(entity.get("trip_short_name")),
        "direction_id": parse_int(entity.get("direction_id"), "direction_id"),
        "block_id": cleanup_string(entity.get("block_id")),
        "shape_id": cleanup_string(entity.get("shape_id")),
        "wheelchair_accessible": parse_int(entity.get("wheelchair_accessible"), "wheelchair_accessible"),
        "bikes_allowed": parse_int(entity.get("bikes_allowed"), "bikes_allowed"),
        "cars_allowed": parse_int(entity.get("cars_allowed"), "cars_allowed")
    }

# -----------------------------------------------------
# Validate GTFS-Static data
# -----------------------------------------------------

def validate_gtfs_agency_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS agency entity.

    This function performs:
    - Validation of required fields
    - Normalization of agency_id to NGSI-LD URN
    - Validation of URLs, timezone, language code, phone number, email
    - Validation of 'cemv_support' values

    Args:
        entity (dict[str, Any]): A parsed GTFS agency entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """

    # Required GTFS fields
    required_fileds = ["agency_name", "agency_url", "agency_timezone"]
    validate_required_fields(entity, required_fileds)

    # Validate URL fields
    for url_field in ["agency_url", "agency_fare_url"]:
        url = entity.get(url_field)
        if url and not validation_utils.is_valid_url(url):
            raise ValueError(f"{url_field} must be a valid URL, got '{url}'")

    # Validate timezone
    timezone = entity.get("agency_timezone")
    if not validation_utils.is_valid_timezone(timezone):
        raise ValueError(f"agency_timezone must be a valid timezone, got {timezone}")

    # Validate language code (if provided)
    agency_lang = entity.get("agency_lang")
    if agency_lang and not validation_utils.is_valid_language_code(agency_lang):
        raise ValueError(f"agency_lang must be a valid language code, got {agency_lang}")

    # Validate phone number (if provided)
    agency_phone = entity.get("agency_phone")
    if agency_phone and not validation_utils.is_valid_phone_number(agency_phone):
        raise ValueError(f"agency_phone must be a valid phone number, got {agency_phone}")

    # Validate email (if provided)
    email = entity.get("agency_email")
    if email and not validation_utils.is_valid_email(email):
        raise ValueError(f"agency_email must be a valid email address, got '{email}'")

    # Validate 'cemv_support' value (if provided)
    cemv_support = entity.get("cemv_support")
    if cemv_support is not None and not validation_utils.is_valid_cemv_support(cemv_support):
        raise ValueError(f"cemv_support must be 0, 1 or 2, got {cemv_support}")

def validate_gtfs_calendar_dates_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS calendar dates entity.

    This function performs:
    - Validation of required fields
    - Validation of date (YYYYMMDD format)
    - Validation of 'exception_type' values

    Args:
        entity (dict[str, Any]): A parsed GTFS calendar date entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Required GTFS fields
    required_fields = ["service_id", "date", "exception_type"]
    validate_required_fields(entity, required_fields)

    # Validate date format (YYYYMMDD)
    date = entity.get("date")
    if not validation_utils.is_valid_date(date):
        raise ValueError(f"date must be a valid date in YYYYMMDD, got '{date}'")

    # Validate 'exception_type' value
    exception_type = entity.get("exception_type")
    if not validation_utils.is_valid_exception_type(exception_type):
        raise ValueError(f"exception_type must be 1 or 2, got {exception_type}")

def validate_gtfs_fare_attributes_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS fare attributes entity.

    This function performs:
    - Validation of required fields
    - The price is a valid non-negative currency value with up to 2 decimal places
    - The currency_type is a valid ISO 4217 currency code
    - Validation of 'payment_method', 'transfers' values
    - If provided, 'transfer_duration' is a non-negative integer
    - NOTE: In GTFS Static 'transfers' can be empty and means 'Unlimited transfers are permitted'
      NGSI-LD does not allow empty values, thus -1 is assigned as 'Unlimited transfers are permitted'
    Args:
        entity (dict[str, Any]): A parsed GTFS fare attributes entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Required fields
    required_fields = ["fare_id", "price", "currency_type", "payment_method", "transfers"]
    validate_required_fields(entity, required_fields)

    # Validate price
    price = entity.get("price")
    if not validation_utils.is_valid_currency_price(price):
        raise ValueError(f"'price' is not a valid currency price, got {price}")
    
    # Validate 'currency_type'
    currency_type = entity.get("currency_type")
    if not validation_utils.is_valid_currency_code(currency_type):
        raise ValueError(f"'currency_type' is not a valid currency code")
    
    # Validate 'payment_method'
    payment_method = entity.get("payment_method")
    if not validation_utils.is_valid_payment_method(payment_method):
        raise ValueError(f"'payment_method' must be 0 or 1, got {payment_method}")

    # Validate 'transfers'
    transfers = entity.get("transfers")
    if not validation_utils.is_valid_transfers(transfers):
        raise ValueError(f"'transfers' should be 0, 1 or 2, got {transfers}")
    
    # If present, write 'agency_id' as NGSI URN
    agency_id = entity.get("agency_id")
    if agency_id:
        entity["agency_id"] = f"urn:ngsi-ld:GtfsAgency:{entity["agency_id"]}"

    # Validate 'transfer_duration'
    transfer_duration = entity.get("transfer_duration")
    if transfer_duration and transfer_duration < 0:
        raise ValueError(f"'transfer_duration' must be a non-negative integer, got {transfer_duration}")

def validate_gtfs_levels_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS level entity.

    This function performs:
    - Validation of required fields
    Args:
        entity (dict[str, Any]): A parsed GTFS level entity.

    Raises:
        ValueError: If any required field is missing
    """
    # Required fields
    required_fields = ["level_id", "level_index"]
    validate_required_fields(entity, required_fields)

def validate_gtfs_pathways_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS pathway entity.

    This function performs:
    - Validation of required fields
    - Validation of 'pathway_mode', 'is_bidirectional' values
    - Validate that if 'pathway_mode' is 7, 'is_bidirectional' cannot be 1
    - Validate that 'length' is a non-negative float
    - Validate that 'traversal_time' is a positive integer
    - Validate that 'stair_count' is a non-zero integer
    - Validate that 'min_width' is a positive float
    - Validate that 'max_slope' can only be defined for 'pathway_mode' = 1 or 3

    Args:
        entity (dict[str, Any]): A parsed GTFS pathways entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Required fields
    required_fields = ["pathway_id", "from_stop_id", "to_stop_id", "pathway_mode", "is_bidirectional"]
    validate_required_fields(entity, required_fields)

    # If present, write 'from_stop_id' and 'to_stop_id' as NGSI URN
    entity["from_stop_id"] = f"urn:ngsi-ld:GtfsStop:{entity["from_stop_id"]}"
    entity["to_stop_id"] = f"urn:ngsi-ld:GtfsStop:{entity["to_stop_id"]}"    
  

    # Validate 'pathway_mode'
    pathway_mode = entity.get("pathway_mode")
    if not validation_utils.is_valid_pathway_mode(pathway_mode):
        raise ValueError(f"'pathway_mode' has to be 1, 2, 3, 4, 5, 6 or 7, got {pathway_mode}")
    
    # Validate 'is_bidirectional'
    is_bidirectional = entity.get("is_bidirectional")
    if not validation_utils.is_valid_is_bidirectional(is_bidirectional):
        raise ValueError(f"'is_bidirectional' has to be 0 or 1, got {is_bidirectional}")
    
    # Validate that if 'pathway_mode' is 7, 'is_bidirectional' cannot be 1
    if pathway_mode == 7 and is_bidirectional == 1:
        raise ValueError(f"'is_bidirectional' cannot be 1 when 'pathway_mode' is 7")
    
    # Validate that length is a non-negative float
    length = entity.get("length")
    if length is not None and length < 0:
        raise ValueError(f"'length' must be a non-negative float, got {length}")
    
    # Validate 'traversal_time' value
    traversal_time = entity.get("traversal_time")
    if traversal_time is not None and traversal_time <= 0:
        raise ValueError(f"'traversal_time' must be a positive integer, got {traversal_time}")
    
    # Validate 'stair_count' value
    stair_count = entity.get("stair_count")
    if stair_count is not None and stair_count == 0:
        raise ValueError(f"'stair_count' must be a non-zero integer, got {stair_count}")
    
    # Validate that 'max_slope' can only be defined for 'pathway_mode' = 1 or 3
    max_slope = entity.get("max_slope")
    if max_slope is not None and pathway_mode not in {1, 3}:
        raise ValueError(f"'max_slope' can only be defined when 'pathway_mode' is 1 or 3")
    
    # Validate 'min_width' value
    min_width = entity.get("min_width")
    if min_width is not None and min_width <= 0:
        raise ValueError(f"'min_width' must be a positive float, got {min_width}")

def validate_gtfs_routes_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS route entity.

    This function performs:
    - Validation of required fields
    - Validation that either 'route_short_name' or 'route_long_name' is defined
    - Validate that 'route_short_name' is not more than 12 characters long
    - Validate of 'route_type', 'continuous_pickup', 'continuous_drop_off' and 'cemv_support' values
    - Validate that 'route_url' is a valid URL
    - Validate that 'route_color' and 'route_text_color' are valid color codes
    - Validate that 'route_sort_order' is a non-negative integer

    Args:
        entity (dict[str, Any]): A parsed GTFS route entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """

    # Required fields
    required_fields = ["route_id", "route_type"]
    validate_required_fields(entity, required_fields)

    # If present, write 'agency_id' as NGSI URN
    agency_id = entity.get("agency_id")
    if not agency_id:
        entity["agency_id"] = f"urn:ngsi-ld:GtfsAgency:{agency_id}"

    # Validate that either 'route_short_name' or 'route_long_name' are defined
    has_route_short_name = bool(entity.get("route_short_name"))
    has_route_long_name = bool(entity.get("route_long_name"))

    if not has_route_short_name and not has_route_long_name:
        raise ValueError("Either 'route_short_name' or 'route_long_name' has to be defined")
    
    # Validate 'route_short_name' length
    if has_route_short_name:
        route_short_name = entity.get("route_short_name")
        if route_short_name is not None and len(route_short_name) > 12:
            raise ValueError("'route_short_name' has to be no longer than 12 characters")
        
    # Validate 'route_type' values
    route_type = entity.get("route_type")
    if not validation_utils.is_valid_route_type(route_type):
        raise ValueError(f"'route_type' has to be 0, 1, 2, 3, 4, 5, 6, 7, 11 or 12, got {route_type}")
    
    # Validate that 'route_url' is a valid URL
    route_url = entity.get("route_url")
    if route_url is not None and not validation_utils.is_valid_url(route_url):
        raise ValueError(f"Invalid URL for 'route_url': {route_url}")
    
    # Validate that 'route_color' is a valid color code
    route_color = entity.get("route_color")
    if route_color is not None and not validation_utils.is_valid_color(route_color):
        raise ValueError(f"Invalid color code for 'route_color': {route_color}")
    
    # Validate that 'route_text_color' is a valid color code
    route_text_color = entity.get("route_text_color")
    if route_text_color is not None and not validation_utils.is_valid_color(route_text_color):
        raise ValueError(f"Invalid color code for 'route_text_color': {route_text_color}")

    # Validate that 'route_sort_order' is a non-negative integer
    route_sort_order = entity.get("route_sort_order")
    if route_sort_order is not None and route_sort_order < 0:
        raise ValueError("'route_sort_order' must be a non-negative integer")

    # Validate 'continuous_pickup' values
    continuous_pickup = entity.get("continuous_pickup")
    if continuous_pickup is not None and not validation_utils.is_valid_continuous_pickup(continuous_pickup):
        raise ValueError(f"'continuous_pickup' has to be 0, 1, 2 or 3, got {continuous_pickup}")
    
    # Validate 'continuous_drop_off' values
    continuous_drop_off = entity.get("continuous_drop_off")
    if continuous_drop_off is not None and not validation_utils.is_valid_continuous_drop_off(continuous_drop_off):
        raise ValueError(f"'continuous_drop_off' has to be 0, 1, 2 or 3, got {continuous_drop_off}")
    
    # If present, write 'network_id' as NGSI URN
    network_id = entity.get("network_id")
    if network_id is not None:
        entity["network_id"] = f"urn:ngsi-ld:Network:{entity["network_id"]}"

    # Validate 'cemv_support' values
    cemv_support = entity.get("cemv_support")
    if cemv_support is not None and not validation_utils.is_valid_cemv_support(cemv_support):
        raise ValueError(f"'cemv_support' has to be 0, 1 or 2, got {cemv_support}")

def validate_gtfs_shapes_entity(entity: dict[str, Any]) -> None:

    required_fields = ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    validate_required_fields(entity, required_fields)

    shape_id = entity.get("shape_id")
    if shape_id is None:
        raise ValueError(f"'shape_id' cannot be None")
    entity["shape_id"] = f"urn:ngsi-ld:GtfsShape:{entity['shape_id']}"

    shape_pt_sequence = entity.get("shape_pt_sequence")
    if shape_pt_sequence is not None and shape_pt_sequence < 0:
        raise ValueError(f"'shape_pt_sequence' must be a non-negative integer, got {shape_pt_sequence}")

    shape_dist_traveled = entity.get("shape_dist_traveled")
    if shape_dist_traveled is not None and shape_dist_traveled < 0:
        raise ValueError(f"'shape_dist_traveled' must be a non-negative float, got {shape_dist_traveled}") 

def validate_gtfs_stop_times_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS stop entity.

    This function performs:
    - Validation of required fields
    - Validate 'timepoint', 'pickup_type', 'drop_off_type', 'continuous_pickup', 'continuous_drop_off'
    - Validate that if 'timepoint' is 1, 'arrival_time' and 'departure_time' are defined
    - Validate that either 'arrival_time' and 'departure_time' OR 'start_pickup_drop_off_window' and 'end_pickup_drop_off_window'
      are defined but not at the same time
    - Validate that exactly one location identifier is defined - stop_id, location_group_id or location_id
    - Write the defined location identified into NGSI URN
    - Validate that location_group_id or location_id is defined, 'start_pickup_drop_off_window' and 'end_pickup_drop_off_window'
      are also defined
    - Validate that 'stop_sequence' is a non-negative integer
    - Validate that location_group_id or location_id is defined, 'continuous_pickup' and 'continuous_drop_off' are 1 
    - Validate that location_group_id or location_id is defined,'pickup_type' cannot be 0 or 3
    - Validate that location_group_id or location_id is defined,'drop_off_type' cannot be 0
    - Validate that 'shape_dist_traveled' is a non-negative float
    - If present, write pickup_booking_rule_id and drop_off_booking_rule_id as NGSI URN

    Args:
        entity (dict[str, Any]): A parsed GTFS stop time entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Check that the required fields are defined
    required_fields = ["trip_id", "stop_sequence"]
    validate_required_fields(entity, required_fields)

    # Validate 'timepoint' values
    timepoint = entity.get("timepoint")
    if timepoint is not None and not validation_utils.is_valid_timepoint(timepoint):
        raise ValueError(f"'timepoint' should be 0 or 1, got {timepoint}")
    
    has_arrival_departure = (bool(entity.get("arrival_time")) and bool(entity.get("departure_time")))
    has_pickup_window = (bool(entity.get("start_pickup_drop_off_window")) and bool(entity.get("end_pickup_drop_off_window")))
    
    # Check that if 'timepoint' is 1 than 'arrival_time and 'departure_time' are defined
    if timepoint == 1 and not has_arrival_departure:
        raise ValueError("arrival_time and departure_time are required when timepoint = 1")
    
    # Validate that both time groups are not defined at the same time
    if has_arrival_departure and has_pickup_window:
        raise ValueError(
            "arrival_time/departure_time and "
            "start_pickup_drop_off_window/end_pickup_drop_off_window "
            "cannot be defined at the same time"
        )

    # Validate that either one of the time groups are defined
    if not has_arrival_departure and not has_pickup_window:
        raise ValueError(
            "Either arrival_time/departure_time or "
            "start_pickup_drop_off_window/end_pickup_drop_off_window "
            "must be defined"
        )
      
    # Check that exactly one location identifier is defined
    has_stop_id = bool(entity.get("stop_id"))
    has_location_group_id = bool(entity.get("location_group_id"))
    has_location_id = bool(entity.get("location_id"))

    if sum([has_stop_id, has_location_group_id, has_location_id]) != 1:
        raise ValueError("Exactly one of stop_id, location_group_id or location_id must be defined")

    # Write NGSI-LD URNs based on which location identifier is defined
    if has_stop_id:
        entity["stop_id"] = f"urn:ngsi-ld:GtfsStop:{entity['stop_id']}"

    if has_location_group_id:
        entity["location_group_id"] = (f"urn:ngsi-ld:LocationGroup:{entity['location_group_id']}")

    if has_location_id:
        entity["location_id"] = f"urn:ngsi-ld:Location:{entity['location_id']}"
        
    # Validate that if 'location_id' or 'location_group_id' are defined, 
    # start_pickup_drop_off_window and end_pickup_drop_off_window must also be defined
    if has_location_id or has_location_group_id:
        if not has_pickup_window:
            raise ValueError(
            "start_pickup_drop_off_window and end_pickup_drop_off_window "
            "are required when using location_id or location_group_id"
            )
    
    # Validate that 'stop_sequence' is a non-negative integer
    stop_sequence = entity.get("stop_sequence")
    if stop_sequence is not None and stop_sequence < 0:
        raise ValueError(f"'stop_sequence' must be a non-negative integer, got {stop_sequence}")
    
    # Validate 'pickup_type' values
    pickup_type = entity.get("pickup_type")
    if pickup_type is not None and not validation_utils.is_valid_pickup_type(pickup_type):
        raise ValueError(f"'pickup_type' must be 0, 1, 2 or 3, got {pickup_type}")
    
    # Validate that if 'location_id' or 'location_group_id' are defined, 'pickup_type' cannot be 0 or 3
    if has_location_group_id or has_location_id:
        if pickup_type in {0, 3}:
            raise ValueError(f"'pickup_type' cannot be 0 or 3 when using location_group_id or location_id")
    
    # Validate 'drop_off_type' values 
    drop_off_type = entity.get("drop_off_type")
    if drop_off_type is not None and not validation_utils.is_valid_drop_off_type(drop_off_type):
        raise ValueError(f"'drop_off_type' must be 0, 1, 2 or 3, got {drop_off_type}")
    
    # Validate that if 'location_id' or 'location_group_id' are defined, 'drop_off_type' cannot be 0
    if has_location_group_id or has_location_id:
        if drop_off_type == 0:
            raise ValueError(f"'drop_off_type' cannot be 0 when using location_group_id or location_id")
    
    # Validate 'continuous_pickup' values    
    continuous_pickup = entity.get("continuous_pickup")
    if continuous_pickup is not None and not validation_utils.is_valid_continuous_pickup(continuous_pickup):
        raise ValueError(f"'continuous_pickup' must be 0, 1, 2 or 3, got {continuous_pickup}")
    
    # Validate that if 'location_id' or 'location_group_id' are defined, 'continuous_pickup' can only be 1
    if has_location_group_id or has_location_id:
        if continuous_pickup != 1:
            raise ValueError(f"'continuous_pickup' cannot be 0, 2 or 3 when using location_group_id or location_id")
    
    # Validate 'continuous_drop_off' values
    continuous_drop_off = entity.get("continuous_drop_off")
    if continuous_drop_off is not None and not validation_utils.is_valid_continuous_drop_off(continuous_drop_off):
        raise ValueError(f"'continuous_drop_off' must be 0, 1, 2 or 3, got {continuous_drop_off}")
    
    # Validate that if 'location_id' or 'location_group_id' are defined, 'continuous_drop_off' can only be 1
    if has_location_group_id or has_location_id:
        if continuous_drop_off != 1:
            raise ValueError(f"'continuous_drop_off' cannot be 0, 2 or 3 when using location_group_id or location_id")
    
    # Validate that 'shape_dist_traveled' is a non-negative float
    shape_dist_traveled = entity.get("shape_dist_traveled")
    if shape_dist_traveled is not None and shape_dist_traveled < 0:
        raise ValueError(f"'shape_dist_traveled' should be a non-negative float, got {shape_dist_traveled}")

    # If present, write 'pickup_booking_rule_id' as a NGSI URN
    pickup_booking_rule_id = entity.get("pickup_booking_rule_id")
    if pickup_booking_rule_id is not None:
        entity["pickup_booking_rule_id"] = f"urn:ngsi-ld:GtfsBookingRule:{pickup_booking_rule_id}"

    # If present, write 'drop_off_booking_rule_id' as a NGSI URN
    drop_off_booking_rule_id = entity.get("drop_off_booking_rule_id")
    if drop_off_booking_rule_id is not None:
        entity["drop_off_booking_rule_id"] = f"urn:ngsi-ld:GtfsBookingRule:{drop_off_booking_rule_id}"

def validate_gtfs_stops_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS stop entity.

    This function performs:
    - Validation of required fields
    - Turns 'stop_id', 'zone_id', 'level_id' into NGSI URN
    - Validate of 'location_type', 'wheelchair_boarding' and 'stop_access' values
    - Checks that 'stop_name', 'stop_lat' and 'stop_lon' are present when 'location_type' is 0, 1 or 2
    - Checks that 'parent_station' is present when 'location_type' is 2, 3 or 4 and forbidden when 'location_type' is 1
    - Checks that 'stop_url' is a valid URL
    - Checks that 'stop_timezone' is a valid Timezone
    - Checks that 'stop_access' is forbidden when 'location_type' is 1, 2, 3 or 4

    Args:
        entity (dict[str, Any]): A parsed GTFS stop entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    required_fields = ["stop_id"]
    validate_required_fields(entity, required_fields)

    entity["stop_id"] = f"urn:ngsi-ld:GtfsStop:{entity["stop_id"]}"
    
    # Validate 'location_type' values
    location_type = entity.get("location_type")
    if not validation_utils.is_valid_location_type(location_type):
        raise ValueError(f"'location_type' must be 0, 1, 2, 3 or 4, got {location_type}")
    
    # Check that 'stop_name', 'stop_lat' and 'stop_lon' are present when 'location_type' is 0, 1 or 2
    if location_type in {0, 1, 2}:
        stop_name = entity.get("stop_name")
        if stop_name is None:
            raise ValueError("'stop_name' is required when 'location_type' is 0, 1 or 2")
        
        stop_lat = entity.get("stop_lat")
        if stop_lat is None:
            raise ValueError(f"'stop_lat' is required when 'location_type' is 0, 1 or 2")
        
        stop_lon = entity.get("stop_lon")
        if stop_lon is None:
            raise ValueError(f"'stop_lon' is required when 'location_type' is 0, 1 or 2")
        
    # Check that 'parent_station' is required when 'location_type' is 2, 3 or 4 and forbidden when 'location_type' is 1
    parent_station = entity.get("parent_station")
    if location_type in {2, 3, 4}:
        if not parent_station:
            raise ValueError(f"'parent_station' is required when 'location_type' is 2, 3 or 4")
        entity["parent_station"] = f"urn:ngsi-ld:GtfsStop:{entity["parent_station"]}"
    elif location_type == 1:
        if parent_station:
            raise ValueError(f"'parent_station' is forbidden when 'location_type' is 1")
    
    # If present, write zone_id as NGSI URN 
    zone_id = entity.get("zone_id")
    if zone_id is not None:
        zone_id = f"urn:ngsi-ld:GtfsZone:{zone_id}"

    # Validate that 'stop_url' is a valid URL
    stop_url = entity.get("stop_url")
    if stop_url is not None and not validation_utils.is_valid_url(stop_url):
        raise ValueError(f"Invalid URL for 'stop_url': {stop_url}")
    
    # Validate that 'stop_timezone' is a valid timezone
    stop_timezone = entity.get("stop_timezone")
    if stop_timezone is not None and not validation_utils.is_valid_timezone(stop_timezone):
        raise ValueError(f"Invalid timezone for 'stop_timezone': {stop_timezone}")
    
    # Validate 'wheelchair_boarding' values
    wheelchair_boarding = entity.get("wheelchair_boarding")
    if wheelchair_boarding is not None and not validation_utils.is_valid_wheelchair_boarding(wheelchair_boarding):
        raise ValueError(f"'wheelchair_boarding' must be 0, 1 or 2, got {wheelchair_boarding}")
    
    # Validate that 'level_id' is a valid URL
    level_id = entity.get("level_id")
    if level_id is not None:
        entity["level_id"] = f"urn:ngsi-ld:GtfsLevel:{level_id}"

    # Validate 'stop_access' values
    stop_access = entity.get("stop_access")
    if stop_access is not None and not validation_utils.is_valid_stop_access(stop_access):
        raise ValueError(f"'stop_access' must be 0 or 1, got {stop_access}")
    
    # Check that 'stop_access' is forbidden when 'location_type' is 1, 2, 3 or 4
    if location_type in {2, 3, 4}:
        if stop_access:
            raise ValueError(f"'stop_access' is forbidden for location_type 2, 3 and 4")
    if location_type == 1:
        if stop_access:
            raise ValueError(f"'stop_access' is forbidden when 'parent_station' is empty, which happens only when 'location_type' is 1")

def validate_gtfs_transfers_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS transfers entity.

    This function performs:
    - Validation of required fields
    - Validate of 'transfer_type' values
    - Validate that 'from_stop_id' and 'to_stop_id' are present when 'transfer_type' is 1, 2 or 3
    - Validate that 'from_trip_id' and 'to_trip_id' are present when 'transfer_type' is 4 or 5
    - If present, turns 'from_route_id' and 'to_route_id' into NGSI URN
    - Validate that 'min_transfer_time' is a non-negative integer
    Args:
        entity (dict[str, Any]): A parsed GTFS transfers entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    required_fields = ["transfer_type"]
    validate_required_fields(entity, required_fields)

    # Validate 'transfer_type' values
    transfer_type = entity.get("transfer_type")
    if not validation_utils.is_valid_transfer_type(transfer_type):
        raise ValueError(f"'transfer_type' must be 0, 1, 2, 3, 4 or 5, got {transfer_type}")
    
    # Validate that 'from_stop_id' and 'to_stop_id' are present when 'transfer_type' is 1, 2 or 3
    if transfer_type in {1, 2, 3}:
        from_stop_id = entity.get("from_stop_id")
        if from_stop_id is None:
            raise ValueError("'from_stop_id' is required when transfer_type is 1, 2 or 3")
        
        to_stop_id = entity.get("to_stop_id")
        if to_stop_id is None:
            raise ValueError("'to_stop_id' is required when transfer_type is 1, 2 or 3")

    # Validate that 'from_trip_id' and 'to_trip_id' are present when 'transfer_type' is 4 or 5
    if transfer_type in {4, 5}:

        from_trip_id = entity.get("from_trip_id")
        if from_trip_id is None:
            raise ValueError("'from_trip_id' is required when transfer_type is 4 or 5")
        
        to_trip_id = entity.get("to_trip_id")
        if to_trip_id is None:
            raise ValueError("'to_trip_id' is required when transfer_type is 4 or 5")

    # If present, write 'from_route_id' as NGSI URN
    from_route_id = entity.get("from_route_id")
    if from_route_id is not None:
        entity["from_route_id"] = f"urn:ngsi-ld:GtfsRoute:{from_route_id}"

    # If present, write 'to_route_id' as NGSI URN
    to_route_id = entity.get("to_route_id")
    if to_route_id is not None:
        entity["to_route_id"] = f"urn:ngsi-ld:GtfsRoute:{to_route_id}"
    
    # Check that 'min_transfer_time' is a non-negative integer
    min_transfer_time = entity.get("min_transfer_time")
    if min_transfer_time is not None and min_transfer_time < 0:
        raise ValueError(f"'min_transfer_time' must be a non-negative integer, got {min_transfer_time}")

def validate_gtfs_trips_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS trip entity.

    This function performs:
    - Validation of required fields
    - If present, turns 'route_id' and 'service_id' into NGSI URN
    - Validate of 'wheelchair_accessible', 'bikes_allowed' and 'cars_allowed' values

    Args:
        entity (dict[str, Any]): A parsed GTFS trip entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Required fields
    required_fields = ["route_id", "service_id", "trip_id"]
    validate_required_fields(entity, required_fields)

    # Write 'route_id' as NGSI URN
    entity["route_id"] = f"urn:ngsi-ld:GtfsRoute:{entity["route_id"]}"

    # Write 'service_id' as NGSI URN
    entity["service_id"] = f"urn:ngsi-ld:GtfsService:{entity["service_id"]}"

    # Validate 'direction_id' value
    direction_id = entity.get("direction_id")
    if direction_id is not None and not validation_utils.is_valid_direction_id(direction_id):
        raise ValueError(f"'direction_id' must be 0 or 1, got {direction_id}")

    # If present, write 'block_id' as NGSI URN 
    block_id = entity.get("block_id")
    if block_id is not None:
        block_id = f"urn:ngsi-ld:GtfsBlock:{block_id}"

    # If present, write 'shape_id' as NGSI URN 
    shape_id = entity.get("shape_id")
    if shape_id is not None:
        shape_id = f"urn:ngsi-ld:GtfsShape:{shape_id}"

    # Validate 'wheelchair_accessible' value
    wheelchair_accessible = entity.get("wheelchair_accessible")
    if wheelchair_accessible is not None and not validation_utils.is_valid_wheelchair_accessible(wheelchair_accessible):
        raise ValueError(f"'wheelchair_accessible' must be 0, 1 or 2, got {wheelchair_accessible}")

    # Validate 'bikes_allowed' value
    bikes_allowed = entity.get("bikes_allowed")
    if bikes_allowed is not None and not validation_utils.is_valid_bikes_allowed(bikes_allowed):
        raise ValueError(f"'bikes_allowed' must be 0, 1 or 2, got {bikes_allowed}")
    
    # Validate 'cars_allowed' value
    cars_allowed = entity.get("cars_allowed")
    if cars_allowed is not None and not validation_utils.is_valid_cars_allowed(cars_allowed):
        raise ValueError(f"'cars_allowed' must be 0, 1 or 2, got {cars_allowed}")

# -----------------------------------------------------
# Convert GTFS-Static data to NGSI-LD
# -----------------------------------------------------

def convert_gtfs_agency_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": f"urn:ngsi-ld:GtfsAgency:{entity.get("agency_id")}",
        "type": "GtfsAgency",
            
        "agency_name":{
            "type": "Property",
            "value": entity.get("agency_name")
        },

        "agency_url": {
            "type": "Property", 
            "value": entity.get("agency_url")
        },
            
        "agency_timezone": {
            "type": "Property", 
            "value": entity.get("agency_timezone")
        },
            
        "agency_lang": {
            "type": "Property", 
            "value": entity.get("agency_lang")
        },
        
        "agency_phone": {
            "type": "Property", 
            "value": entity.get("agency_phone")
        },
            
        "agency_fare_url": {
            "type": "Property",
            "value": entity.get("agency_fare_url")
        },
        
        "agency_email": {
            "type": "Property", 
            "value": entity.get("agency_email")
        },
            
        "cemv_support": {
            "type": "Property",
            "value": entity.get("cemv_support")
        }
    }

def convert_gtfs_calendar_dates_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:Sofia:{entity.get("service_id")}:{entity.get("date")}",
            "type": "GtfsCalendarDateRule",
            
            "hasService": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsService:{entity.get("service_id")}"
            },
            
            "appliesOn": {
                "type": "Property",
                "value": entity.get("date")
            },
            
            "exceptionType": {
                "type": "Property",
                "value": entity.get("exception_type")
            }
        }

def convert_gtfs_fare_attributes_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsFareAttributes:{entity.get("fare_id")}",
            "type": "GtfsFareAttributes",
            
            "price": {
                "type": "Property", 
                "value": entity.get("price")
            },
            
            "currency_type": {
                "type": "Property", 
                "value": entity.get("currency_type")
            },
            
            "payment_method": {
                "type": "Property", 
                "value": entity.get("payment_method")
            },
            
            "transfers": {
                "type": "Property", 
                "value": entity.get("transfers")
            },
            
            "agency": {
                "type": "Relationship",
                "object": entity.get("agency_id")
            },
            
            "transfer_duration": {
                "type" : "Property",
                "value": entity.get("transfer_duration")
            }
        }

def convert_gtfs_levels_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsLevel:{entity.get("level_id")}",
            "type": "GtfsLevel",
            "name": {
                "type": "Property",
                "value": entity.get("level_name")
            },
            
            "level_index": {
                "type": "Property",
                "value": entity.get("level_index")
            }
        }

def convert_gtfs_pathways_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsPathway:{entity.get("pathway_id")}",
            "type": "GtfsPathway",
            
            "hasOrigin": {
                "type": "Relationship",
                "object": entity.get("from_stop_id")
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": entity.get("to_stop_id")
            },
            
            "pathway_mode": {
                "type": "Property",
                "value": entity.get("pathway_mode")
            },
            
            "isBidirectional": {
                "type": "Property",
                "value": entity.get("is_bidirectional")
            },
            
            "length": {
                "type": "Property",
                "value": entity.get("length")
            },
            
            "traversal_time": {
                "type": "Property",
                "value": entity.get("traversal_time")
            },
            
            "stair_count": {
                "type": "Property",
                "value": entity.get("stair_count")
            },
            
            "max_slope": {
                "type": "Property",
                "value": entity.get("max_slope")
            },
            
            "min_width": {
                "type": "Property",
                "value": entity.get("min_width")
            },
            
            "signposted_as": {
                "type": "Property",
                "value": entity.get("signposted_as")
            },
            
            "reversed_signposted_as": {
                "type": "Property",
                "value": entity.get("reversed_signposted_as")
            }
        }

def convert_gtfs_routes_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:{entity.get("route_id")}",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": entity.get("agency_id")
            },
            
            "shortName": {
                "type": "Property", 
                "value": entity.get("route_short_name")
            },
            
            "name": {
                "type": "Property", 
                "value": entity.get("route_long_name")
            },
            
            "description": {
                "type": "Property", 
                "value": entity.get("route_desc")
            },
            
            "routeType": {
                "type": "Property", 
                "value": entity.get("route_type")
            },
            
            "route_url": {
                "type": "Property", 
                "value": entity.get("route_url")
            },
            
            "routeColor": {
                "type": "Property", 
                "value": entity.get("route_color")
            },
            
            "routeTextColor": {
                "type": "Property", 
                "value": entity.get("route_text_color")
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": entity.get("route_sort_order")
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": entity.get("continuous_pickup")
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": entity.get("continuous_drop_off")
            }
        }

def convert_gtfs_stop_times_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsStopTime:{entity.get("trip_id")}:{entity.get("stop_sequence")}",
            "type": "GtfsStopTime",
            
            "hasTrip": {
                "type": "Relationship",
                "object": entity.get("trip_id")
            },
            
            "arrivalTime": {
                "type": "Property", 
                "value": entity.get("arrival_time")
            },
            
            "departureTime": {
                "type": "Property", 
                "value": entity.get("departure_time")
            },
            
            "hasStop": {
                "type": "Relationship",
                "object": entity.get("stop_id")
            },
            
            "location_group_id": {
                "type": "Relationship",
                "object": entity.get("location_group_id")
            },
            
            "location_id": {
                "type": "Relationship",
                "object": entity.get("location_id")
            },

            "stopSequence": {
                "type": "Property", 
                "value": entity.get("stop_sequence")
            },
            
            "stopHeadsign": {
                "type": "Property", 
                "value": entity.get("stop_headsign")
            },
            
            "start_pickup_drop_off_window": {
                "type": "Property",
                "value": entity.get("start_pickup_drop_off_window")
            },
            
            "end_pickup_drop_off_window": {
                "type": "Property",
                "value": entity.get("end_pickup_drop_off_window")
            },
            
            "pickupType": {
                "type": "Property", 
                "value":entity.get("pickup_type")
            },
            
            "dropOffType": {
                "type": "Property", 
                "value": entity.get("drop_off_type")
            },
            
            "continuousPickup": {
                "type": "Property", 
                "value": entity.get("continuous_pickup")
            },
            
            "continuousDropOff": {
                "type": "Property", 
                "value": entity.get("continuous_drop_off")
            },
            
            "shapeDistTraveled": {  
                "type": "Property", 
                "value": entity.get("shape_dist_traveled")
            },
            
            "timepoint": {
                "type": "Property", 
                "value": entity.get("timepoint")
            },
            
            "pickup_booking_rule_id": {
                "type": "Relationship",
                "object": entity.get("pickup_booking_rule_id")
            },
            
            "drop_off_booking_rule_id": {
                "type": "Relationship",
                "object": entity.get("drop_off_booking_rule_id")
            }
        }

def convert_gtfs_stops_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": entity.get("stop_id"),
            "type": "GtfsStop",
            
            "code": {
                "type": "Property", 
                "value": entity.get("stop_code")
            },
            
            "name": {
                "type": "Property", 
                "value": entity.get("stop_name")
            },
            
            "tts_stop_name":{
                "type": "Property",
                "value": entity.get("tts_stop_name")
            },
            
            "description": {
                "type": "Property", 
                "value": entity.get("stop_desc")
            },
            
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        entity.get("stop_lon"),
                        entity.get("stop_lat")
                    ]
                }
            },
            
            "zone_id": {
                "type": "Relationship",
                "object": entity.get("zone_id")
            },
            
            "stop_url": {
                "type": "Property",
                "value": entity.get("stop_url")
            },
            
            "locationType": {
                "type": "Property", 
                "value": entity.get("location_type")
            },
            
            "hasParentStation": {  
                "type": "Relationship",
                "object": entity.get("parent_station")
            },
            
            "timezone": {
                "type": "Property", 
                "value": entity.get("stop_timezone")
            },
            
            "wheelchair_boarding": {
                "type": "Property",
                "value": entity.get("wheelchair_boarding")
            },
            
            "level": {
                "type": "Relationship",
                "object": entity.get("level_id")
            },
            
            "platform_code": {
                "type": "Property",
                "value": entity.get("platform_code")
            },
            
            "stop_access": {
                "type": "Property",
                "value": entity.get("stop_access")
            }
        }

def convert_gtfs_transfers_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    id_parts = [
        "Transfer",
    ]
        
    if entity.get("from_stop_id") is not None:
        id_parts.append(f"fromStop:{entity.get("from_stop_id")}")
        entity['from_stop_id'] = f"urn:ngsi-ld:GtfsStop:{entity['from_stop_id']}"
            
    if entity.get("to_stop_id") is not None:
        id_parts.append(f"toStop:{entity.get("to_stop_id")}")
        entity['to_stop_id'] = f"urn:ngsi-ld:GtfsStop:{entity['to_stop_id']}"
        
    if entity.get("from_trip_id") is not None:
        id_parts.append(f"fromTrip:{entity.get("from_trip_id")}")
        entity["from_trip_id"] = f"urn:ngsi-ld:GtfsTrip:{entity["from_trip_id"]}"

    if entity.get("to_trip_id") is not None:
        id_parts.append(f"toTrip:{entity.get("to_trip_id")}")
        entity["to_trip_id"] = f"urn:ngsi-ld:GtfsTrip:{entity["to_trip_id"]}"
            
    entity_id = "urn:ngsi-ld:GtfsTransferRule:" + ":".join(id_parts)
    
    return {
            "id": entity_id,
            "type": "GtfsTransferRule",
            "hasOrigin": {
                "type": "Relationship",
                "object": entity.get("from_stop_id")
            },
            
            "hasDestination": {
                "type": "Relationship",
                "object": entity.get("to_stop_id")
            },
            
            "from_route_id": {
                "type": "Relationship",
                "object": entity.get("from_route_id")
            },
            
            "to_route_id": {
                "type": "Relationship",
                "object": entity.get("to_route_id")
            },
            
            "from_trip_id": {
                "type": "Relationship",
                "object": entity.get("from_trip_id")
            },
            
            "to_trip_id": {
                "type": "Relationship",
                "object": entity.get("to_trip_id")
            },
            
            "transferType": {
                "type": "Property",
                "value": entity.get("transfer_type")
            },
            
            "minimumTransferTime": {
                "type": "Property",
                "value": entity.get("min_transfer_time")
            }
        }

def convert_gtfs_trips_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    return {
            "id": f"urn:ngsi-ld:GtfsTrip:{entity.get("trip_id")}",
            "type": "GtfsTrip",
            
            "route": {
                "type": "Relationship",
                "object": entity.get("route_id")
            },
            
            "service": {
                "type": "Relationship",
                "object": entity.get("service_id")
            },
            
            "headSign": {
                "type": "Property",
                "value": entity.get("trip_headsign")
            },

            "shortName": {
                "type": "Property",
                "value": entity.get("trip_short_name")
            },
            
            "direction": {
                "type": "Property",
                "value": entity.get("direction_id")
            },

            "block": {
                "type": "Relationship",
                "object": entity.get("block_id")
            },
            
            "hasShape": {
                "type": "Relationship",
                "object": entity.get("shape_id")
            },
            
            "wheelChairAccessible": {
                "type": "Property",
                "value": entity.get("wheelchair_accessible")
            },
            
            "bikesAllowed": {
                "type": "Property",
                "value": entity.get("bikes_allowed")
            },
            
            "carsAllowed": {
                "type": "Property",
                "value": entity.get("cars_allowed")
            }
        }
# -----------------------------------------------------
# Remove None values
# -----------------------------------------------------

def remove_none_values(entity: dict[str, Any]) -> dict[str, Any]:
        
        entity = {
            k: v for k, v in entity.items()
            if not (isinstance(v, dict) and None in v.values())
        }

        return entity
    

def gtfs_static_agency_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    
    ngsi_ld_data = []
    for agency in raw_data:

        parsed_entity = parse_gtfs_agency_data(agency)
        validate_gtfs_agency_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_agency_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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
        
        parsed_entity = parse_gtfs_calendar_dates_data(calendar_date)
        validate_gtfs_calendar_dates_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_calendar_dates_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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

        parsed_entity = parse_gtfs_fare_attributes_data(fare)
        validate_gtfs_fare_attributes_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_fare_attributes_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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

        parsed_entity = parse_gtfs_levels_data(level)
        validate_gtfs_levels_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_levels_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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
        parsed_entity = parse_gtfs_pathways_data(pathway)
        validate_gtfs_pathways_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_pathways_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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
        parsed_entity = parse_gtfs_routes_data(route)
        validate_gtfs_routes_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_routes_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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
        
        # Check if a shape entity contains the required fields
        validate_required_fields(shape, required_fields)
            
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
    
    for stop_time in raw_data:
        parsed_entity = parse_gtfs_stop_times_data(stop_time)
        validate_gtfs_stop_times_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_stop_times_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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
        parsed_entity = parse_gtfs_stops_data(stop)
        validate_gtfs_stops_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_stops_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
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
        parsed_entity = parse_gtfs_transfers_data(transfer)
        validate_gtfs_transfers_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_transfers_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)
        
    return ngsi_ld_data


def gtfs_static_trips_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static trips data to NGSI-LD format.
    Args:
        raw_data (list[dict[str, Any]]): List of dictionaries containing trip data from GTFS static files.
    Returns:
        list[dict[str, Any]]: List of dictionaries in NGSI-LD format representing GTFS trips.
    """
  
    for trip in raw_data:
        parsed_entity = parse_gtfs_trips_data(trip)
        validate_gtfs_trips_entity(parsed_entity)
        ngsi_ld_entity = convert_gtfs_trips_to_ngsi_ld(parsed_entity)
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        ngsi_ld_data.append(ngsi_ld_entity)

        
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
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "shapes.txt"))
    #ngsi_ld_data = gtfs_static_shapes_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "stop_times.txt"))
    #ngsi_ld_data = gtfs_static_stop_times_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "stops.txt"))
    #ngsi_ld_data = gtfs_static_stops_to_ngsi_ld(feed_dict)
    
    feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "transfers.txt"))
    ngsi_ld_data = gtfs_static_transfers_to_ngsi_ld(feed_dict)
    
    #feed_dict = gtfs_static_read_file(os.path.join("gtfs_static", "data", "trips.txt"))
    #ngsi_ld_data = gtfs_static_trips_to_ngsi_ld(feed_dict)
    
    print(json.dumps(ngsi_ld_data, indent=2, ensure_ascii=False))
    #print(json.dumps(feed_dict, indent=2, ensure_ascii=False))
    pass