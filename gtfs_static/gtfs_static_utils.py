import os
import csv
import sys
import json
import zipfile
import requests
from typing import Any
from io import BytesIO
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import config
import validation_functions.validation_utils as validation_utils

# -----------------------------------------------------
# Get Data
# -----------------------------------------------------

def gtfs_static_download_and_extract_zip(api_endpoint: config.GtfsSource, base_dir: str = "gtfs_static") -> None:
    """
    Downloads a GTFS Static ZIP archive from the given API endpoint and extracts
    its contents into a local directory structure.

    The function always creates a "data" subdirectory in "base_dir" where
    the GTFS Static files are extracted.

    Args:
        api_endpoint (config.GtfsSource): Enum value containing the GTFS Static ZIP API endpoint.
        base_dir (str, optional): Base directory where the GTFS data will be stored. Default is "gtfs_static".

    Raises:
        ValueError: If the API endpoint is not configured or contains an empty URL.
        requests.exceptions.RequestException: If the ZIP file cannot be downloaded.
        zipfile.BadZipFile: If the downloaded content is not a valid ZIP archive.
    """
    
    try:
        # Extract URL from the enum
        url = api_endpoint.value or ""
        if url == "":
            raise ValueError(f"API endpoint for {api_endpoint.name} is not set.")
        
        # Download GTFS Static ZIP file
        response = requests.get(url)
        response.raise_for_status()
        
    except requests.exceptions.RequestException:
        # Display error message if the download was unsuccessful
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint.name}")
    
    # Ensure base_dir exists
    os.makedirs(base_dir, exist_ok=True)

    # Ensure base_dir/data exists
    extract_to = os.path.join(base_dir, "data")
    os.makedirs(extract_to, exist_ok=True)
    
    # Extract the ZIP file
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall(extract_to)

def gtfs_static_download_zip(api_endpoint: config.GtfsSource, base_dir: str = "gtfs_static") -> bytes:
    """
    Downloads a GTFS Static ZIP archive from the given API endpoint, saves it locally, 
    and returns its content as bytes.

    Args:
        api_endpoint (config.GtfsSource): Enum value containing the GTFS Static ZIP API endpoint.
        base_dir (str, optional): Base directory where the GTFS ZIP will be saved. Default is "gtfs_static".

    Returns:
        bytes: The content of the downloaded ZIP file.

    Raises:
        ValueError: If the API endpoint is not configured or contains an empty URL.
        requests.exceptions.RequestException: If the ZIP file cannot be downloaded.
    """
    url = api_endpoint.value or ""
    if url == "":
        raise ValueError(f"API endpoint for {api_endpoint.name} is not set.")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint.name}")

    # Ensure base_dir exists
    os.makedirs(base_dir, exist_ok=True)

    # Save ZIP to disk
    zip_path = os.path.join(base_dir, "sofia_gtfs.zip")
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Return ZIP content as bytes
    return response.content

def gtfs_static_extract_zip(zip_bytes: bytes, base_dir: str = "gtfs_static") -> None:
    """
    Extracts a GTFS Static ZIP archive (given as bytes) into a local directory structure.
    Always creates a "data" subdirectory in "base_dir" where files are extracted.

    Args:
        zip_bytes (bytes): ZIP file content
        base_dir (str, optional): Base directory where the GTFS data will be stored. Default is "gtfs_static".
    """
    extract_to = os.path.join(base_dir, "data")
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(BytesIO(zip_bytes)) as zip_file:
        zip_file.extractall(extract_to)
    
# -----------------------------------------------------
# Read Data
# -----------------------------------------------------

def gtfs_static_read_file(file_path: str) -> list[dict[str, Any]]:
    """
    Reads a GTFS Static CSV file and returns its contents as a list of dictionaries.

    The keys come from the header row and the values from the remaining rows

    The function enforces basic GTFS Static file integrity checks:
        - The file must not be empty
        - The delimiter must be a comma (',') as required by the GTFS specification
        - A valid, non-empty header row must be present
        - Header column names must not be purely numeric

    Args:
        file_path (str):
            Absolute or relative path to the GTFS ".txt" file.

    Returns:
        list[dict[str, Any]]:
            A list of dictionaries representing the parsed GTFS records.
            Returns an empty list if the file is empty.

    Raises:
        FileNotFoundError:
            If the specified file path does not exist.
        ValueError:
            If the file does not conform to expected GTFS CSV format
            (invalid delimiter, missing or invalid header).
    """
    # Try and read the specified .txt GTFS Static file
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
        
        # Reject headers that are purely numeric (typical sign of missing header)
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
    - Validation of 'exception_type' values

    Args:
        entity (dict[str, Any]): A parsed GTFS calendar date entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Required GTFS fields
    required_fields = ["service_id", "date", "exception_type"]
    validate_required_fields(entity, required_fields)

    # Validate 'exception_type' value
    exception_type = entity.get("exception_type")
    if not validation_utils.is_valid_exception_type(exception_type):
        raise ValueError(f"exception_type must be 1 or 2, got {exception_type}")

def validate_gtfs_fare_attributes_entity(entity: dict[str, Any], city: str) -> None:
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
        entity["agency_id"] = f"urn:ngsi-ld:GtfsAgency:{city}:{entity["agency_id"]}"

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
    if agency_id:
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
    """
    Validates a parsed GTFS shape entity.

    This function performs:
    - Validation of required fields
    - Validate that 'shape_pt_sequence' is a non-negative integer
    - Validate that 'shape_dist_traveled' is a non-negatice float
    Args:
        entity (dict[str, Any]): A parsed GTFS shape entity.

    Raises:
        ValueError: If any required field is missing or any field value is invalid.
    """
    # Validate required fields
    required_fields = ["shape_id", "shape_pt_lat", "shape_pt_lon", "shape_pt_sequence"]
    validate_required_fields(entity, required_fields)

    # Valifate that 'shape_pt_sequence' is a non-negative integer
    shape_pt_sequence = entity.get("shape_pt_sequence")
    if shape_pt_sequence is not None and shape_pt_sequence < 0:
        raise ValueError(f"'shape_pt_sequence' must be a non-negative integer, got {shape_pt_sequence}")

    # Valifate that 'shape_dist_traveled' is a non-negative float
    shape_dist_traveled = entity.get("shape_dist_traveled")
    if shape_dist_traveled is not None and shape_dist_traveled < 0:
        raise ValueError(f"'shape_dist_traveled' must be a non-negative float, got {shape_dist_traveled}") 

def validate_gtfs_stop_times_entity(entity: dict[str, Any]) -> None:
    """
    Validates a parsed GTFS stop time entity.

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
    if location_type is not None and not validation_utils.is_valid_location_type(location_type):
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
    elif location_type == 1:
        if parent_station:
            raise ValueError(f"'parent_station' is forbidden when 'location_type' is 1")
        
    if parent_station:
        entity["parent_station"] = f"urn:ngsi-ld:GtfsStop:{parent_station}"
    
    # If present, write zone_id as NGSI URN 
    zone_id = entity.get("zone_id")
    if zone_id is not None:
        entity["zone_id"] = f"urn:ngsi-ld:GtfsZone:{zone_id}"

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
        entity["block_id"] = f"urn:ngsi-ld:GtfsBlock:{entity["block_id"]}"

    # If present, write 'shape_id' as NGSI URN 
    shape_id = entity.get("shape_id")
    if shape_id is not None:
        entity["shape_id"] = f"urn:ngsi-ld:GtfsShape:{entity["shape_id"]}"

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

def convert_gtfs_agency_to_ngsi_ld(entity: dict[str, Any], city: str) -> dict[str, Any]:
    """
    Maps a parsed GTFS agency entity to an NGSI-LD GtfsAgency entity.

    This function performs:
    - Writing 'agency_id' as NGSI URN
    - Mapping of GTFS agency fields to NGSI-LD Properties

    Args:
        entity (dict[str, Any]): A parsed GTFS agency entity.
        city (str): The city name.

    Returns:
        dict: An NGSI-LD entity of type GtfsAgency.
    """
    return {
        "id": f"urn:ngsi-ld:GtfsAgency:{city}:{entity.get('agency_id')}",
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

def convert_gtfs_calendar_dates_to_ngsi_ld(entity: dict[str, Any], city: str) -> dict[str, Any]:
    """
    Maps a parsed GTFS calendar date entity to an NGSI-LD GtfsCalendarDateRule entity.

    This function performs:
    - Writing 'service_id' and 'date' as NGSI URN
    - Mapping of GTFS calendar date fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS calendar date entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsCalendarDateRule.
    """
    return {
            "id": f"urn:ngsi-ld:GtfsCalendarDateRule:{city}:{entity.get('service_id')}:{entity.get('date')}",
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

def convert_gtfs_fare_attributes_to_ngsi_ld(entity: dict[str, Any], city: str) -> dict[str, Any]:
    """
    Maps a parsed GTFS fare attributes entity to an NGSI-LD GtfsFareAttributes entity.

    This function performs:
    - Writing 'fare_id' and 'agency_id' as NGSI URN
    - Mapping of GTFS fare attributes fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS fare attributes entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsFareAttributes.
    """
    return {
            "id": f"urn:ngsi-ld:GtfsFareAttributes:{city}:{entity.get("fare_id")}",
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

def convert_gtfs_levels_to_ngsi_ld(entity: dict[str, Any], city: str) -> dict[str, Any]:
    """
    Maps a parsed GTFS level entity to an NGSI-LD GtfsLevel entity.

    This function performs:
    - Writing 'level_id' as NGSI URN
    - Mapping of GTFS level fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS level entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsLevel.
    """
    return {
            "id": f"urn:ngsi-ld:GtfsLevel:{city}:{entity.get("level_id")}",
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
    """
    Maps a parsed GTFS pathway entity to an NGSI-LD GtfsPathway entity.

    This function performs:
    - Writing 'pathway_id', 'from_stop_id', 'to_stop_id' as NGSI URN
    - Mapping of GTFS pathway fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS pathway entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsPathway.
    """
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
    """
    Maps a parsed GTFS route entity to an NGSI-LD GtfsRoute entity.

    This function performs:
    - Writing 'route_id', 'agency_id' as NGSI URN
    - Mapping of GTFS route fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS route entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsRoute.
    """
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
            },
            
            "network_id": {
                "type": "Relationship",
                "object": entity.get("network_id")
            },
            
            "cemv_support": {
                "type": "Property", 
                "value": entity.get("cemv_support")
            }
        }

def convert_gtfs_shapes_to_ngsi_ld(shape_id: str, points: list[dict]) -> dict[str, Any]:
    """
    Converts a GTFS shape into an NGSI-LD GtfsShape entity.

    This function performs:
    - Sorting of shape points by their sequence number
    - Extraction of coordinates to build a GeoProperty LineString
    - Collection of traveled distances if available

    Args:
        shape_id (str): The GTFS shape identifier.
        points (list[dict]): A list of shape points, each containing:
            - 'seq': Sequence order of the point
            - 'coords': Coordinate pair [longitude, latitude]
            - 'dist': Distance traveled from the start of the shape (optional)

    Returns:
        dict[str, Any]: An NGSI-LD entity of type GtfsShape.
    """
    points.sort(key=lambda p: p["seq"])

    coords = [p["coords"] for p in points]

    dist_traveled = [p["dist"] for p in points if p["dist"] is not None]
    if not dist_traveled:
        dist_traveled = None
        
    return {
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
                "value": dist_traveled
            }
        }

def convert_gtfs_stop_times_to_ngsi_ld(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Maps a parsed GTFS stop time entity to an NGSI-LD GtfsStopTime entity.

    This function performs:
    - Writing 'trip_id', 'stop_id', 'location_group_id', 'location_id',
      'pickup_booking_rule_id' and 'drop_off_booking_rule_id' as NGSI URN
    - Mapping of GTFS stop time fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS stop time entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsStopTime.
    """
    return {
            "id": f"urn:ngsi-ld:GtfsStopTime:{entity.get("trip_id")}:{entity.get("stop_sequence")}",
            "type": "GtfsStopTime",
            
            "hasTrip": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsTrip:{entity.get("trip_id")}"
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
    """
    Maps a parsed GTFS stop entity to an NGSI-LD GtfsStop entity.

    This function performs:
    - Writing 'stop_id', 'zone_id', 'parent_station', 'level_id' as NGSI URN
    - Mapping of GTFS stop fields to NGSI-LD Properties
    Args:
        entity (dict[str, Any]): A parsed GTFS stop entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsStop.
    """
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
    """
    Converts a parsed GTFS transfer rule into an NGSI-LD GtfsTransferRule entity.

    This function performs:
    - Construction of a unique NGSI-LD entity ID based on available transfer attributes
    - Conversion of GTFS stop and trip identifiers into NGSI-LD URNs
    - Mapping of GTFS transfer fields to NGSI-LD Properties and Relationships

    Args:
        entity (dict[str, Any]): A parsed GTFS transfer rule entity

    Returns:
        dict[str, Any]: An NGSI-LD entity of type GtfsTransferRule.
    """
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
    """
    Maps a parsed GTFS trip entity to an NGSI-LD GtfsTrip entity.

    This function performs:
    - Writing 'trip_id', 'route_id', 'service_id', 'block_id', 'shape_id' as NGSI URN
    - Mapping of GTFS trip fields to NGSI-LD Properties and Relationships
    Args:
        entity (dict[str, Any]): A parsed GTFS trip entity.

    Returns:
        dict: An NGSI-LD entity of type GtfsTrip.
    """
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
# Aggregate GTFS Shape Points
# -----------------------------------------------------

def collect_shape_points(shapes_dict: dict[str, Any], entity: dict[str, Any]) -> None:
    """
    Aggregates points and distances travelled into lists for each shape.
    Those lists are sorted by point sequence number.
    
    Args:
        shapes_dict (dict): Dictionary grouping points by shape_id. 
                            Keys are shape_id strings, values are lists of points and distances.
        entity (dict): Dictionary with data for a single shape point, including:
                       - shape_id: the identifier of the shape
                       - shape_pt_sequence: sequence number of the point
                       - shape_pt_lon: longitude
                       - shape_pt_lat: latitude
                       - shape_dist_traveled (optional): distance traveled along the shape
    """
    
    # Get shape_id and point and distance data from the entity
    shape_id = entity["shape_id"]
    point = {
        "seq": entity["shape_pt_sequence"],
        "coords": [entity["shape_pt_lon"], entity["shape_pt_lat"]],
        "dist": entity.get("shape_dist_traveled"),
    }
    
    # Append the point and distance to the corresponding shape_id in shapes_dict
    shapes_dict.setdefault(shape_id, []).append(point)

# -----------------------------------------------------
# Remove None values
# -----------------------------------------------------

def remove_none_values(entity: dict[str, Any]) -> dict[str, Any]:
    """
    Removes NGSI-LD attributes whose values contain None.

    Args:
        entity (dict[str, Any]): A dictionary representing an NGSI-LD entity.

    Returns:
        dict[str, Any]: A new dictionary with invalid attributes removed.
    """
    entity = {
            k: v for k, v in entity.items()
            if not (isinstance(v, dict) and None in v.values())
        }

    return entity

# -----------------------------------------------------
# Main conversion functions
# ----------------------------------------------------- 

def gtfs_static_agency_to_ngsi_ld(raw_data: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    """
    Converts GTFS static agency data into NGSI-LD entities.

    The function processes each GTFS agency entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed agency entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsAgency entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS agency entities
        city (str):
            The city name to be included in the NGSI-LD entity ID for uniqueness

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing 'GtfsAgency'
    Raises:
        ValueError:
            If any parsed agency entity does not satisfy the GTFS validation rules.
    """

    # Container for the resulting NGSI-LD GtfsAgency entities
    ngsi_ld_data = []

    # Process each GTFS agency entity
    for agency in raw_data:

        # Parse raw GTFS agency data to the according data types
        parsed_entity = parse_gtfs_agency_data(agency)

        # Validate the parsed agency entity (mandatory fields, data types, etc.)
        validate_gtfs_agency_entity(parsed_entity)

        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_agency_to_ngsi_ld(parsed_entity, city)

        # Remove attributes with None values to ensure a clean NGSI-LD payload
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)

        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)

    # Return the list of NGSI-LD GtfsAgency entities
    return ngsi_ld_data

def gtfs_static_calendar_dates_to_ngsi_ld(raw_data: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    """
    Converts GTFS static calendar date rules into NGSI-LD entities.

    The function processes each GTFS calendar date entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed calendar date entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsCalendarDateRule entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS calendar date entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing 'GtfsCalendarDateRule'

    Raises:
        ValueError:
            If any parsed calendar date entity does not satisfy the GTFS validation rules.
    """

    # Container for the resulting NGSI-LD calendar date rule entities
    ngsi_ld_data = []

    # Process each GTFS calendar date entity
    for calendar_date in raw_data:

        # Parse raw GTFS calendar date data to the according data types
        parsed_entity = parse_gtfs_calendar_dates_data(calendar_date)

        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_calendar_dates_entity(parsed_entity)

        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_calendar_dates_to_ngsi_ld(parsed_entity, city)

        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)

        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)

    # Return the list of NGSI-LD GtfsCalendarDateRule entities
    return ngsi_ld_data
    
def gtfs_static_fare_attributes_to_ngsi_ld(raw_data: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    """
    Converts GTFS static fare attributes into NGSI-LD entities.

    The function processes each GTFS fare attribute entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed fare attribute entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsFareAttributes entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS fare attribute entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsFareAttributes

    Raises:
        ValueError:
            If any parsed fare attribute entity does not satisfy the GTFS validation rules.
    """
    
    # Container for the resulting NGSI-LD fare attribute entities
    ngsi_ld_data = []
    
    # Process each GTFS fare attributes entity
    for fare in raw_data:

        # Parse raw GTFS fare atributes data to the according data types
        parsed_entity = parse_gtfs_fare_attributes_data(fare)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_fare_attributes_entity(parsed_entity, city)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_fare_attributes_to_ngsi_ld(parsed_entity, city)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsFareAttributes entities
    return ngsi_ld_data

def gtfs_static_levels_to_ngsi_ld(raw_data: list[dict[str, Any]], city: str) -> list[dict[str, Any]]:
    """
    Converts GTFS static levels into NGSI-LD entities.

    The function processes each GTFS level entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed level entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsLevel entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS level entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsLevel

    Raises:
        ValueError:
            If any parsed level entity does not satisfy the GTFS validation rules.
    """
    
    # Container for the resulting NGSI-LD level entities
    ngsi_ld_data = []
    
    # Process each GTFS levels entity
    for level in raw_data:

        # Parse raw GTFS levels data to the according data types
        parsed_entity = parse_gtfs_levels_data(level)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_levels_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_levels_to_ngsi_ld(parsed_entity, city)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsLevel entities
    return ngsi_ld_data
    
def gtfs_static_pathways_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static pathways into NGSI-LD entities.

    The function processes each GTFS pathway entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed pathway entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsPathway entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS pathway entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsPathway

    Raises:
        ValueError:
            If any parsed pathway entity does not satisfy the GTFS validation rules.
    """
    # Container for the resulting NGSI-LD pathway entities
    ngsi_ld_data = []

    # Process each GTFS pathway entity
    for pathway in raw_data:
        
        # Parse raw GTFS pathway data to the according data types
        parsed_entity = parse_gtfs_pathways_data(pathway)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_pathways_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_pathways_to_ngsi_ld(parsed_entity)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsPathway entities
    return ngsi_ld_data
    
def gtfs_static_routes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static routes into NGSI-LD entities.

    The function processes each GTFS route entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed route entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsRoute entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS route entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsRoute

    Raises:
        ValueError:
            If any parsed route entity does not satisfy the GTFS validation rules.
    """
    # Container for the resulting NGSI-LD route entities
    ngsi_ld_data = []
    
    # Process each GTFS route entity
    for route in raw_data:
        
        # Parse raw GTFS route data to the according data types
        parsed_entity = parse_gtfs_routes_data(route)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_routes_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_routes_to_ngsi_ld(parsed_entity)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsRoute
    return ngsi_ld_data

def gtfs_static_shapes_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static shapes into NGSI-LD entities.

    The function processes each GTFS shape entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed shapes entity against GTFS rules.
    3. Aggregating all points and 'shape_dist_traveled' into lists based on the 'shape_id'
    4. Converting the aggregated entity into an NGSI-LD GtfsShape entity.
    5. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS shape entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsShape

    Raises:
        ValueError:
            If any parsed shape entity does not satisfy the GTFS validation rules.
    """
    # Container for the resulting NGSI-LD shape entities
    ngsi_ld_data = []
    
    # Container for the aggregated points and travelled distance
    shapes_dict = {}

    # Process each GTFS shape entity
    for shape in raw_data:
        
        # Parse raw GTFS shape data to the according data types
        parsed_entity = parse_gtfs_shapes_data(shape)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_shapes_entity(parsed_entity)
        
        # Aggregate the shape points and distance travelled and store it in the shape_dict container
        collect_shape_points(shapes_dict, parsed_entity)

    # Process each record in the shape_dict container                
    for shape_id, points in shapes_dict.items():
        
        # Convert the aggregated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_shapes_to_ngsi_ld(shape_id, points)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)

    # Return the list of NGSI-LD GtfsShape entities
    return ngsi_ld_data

def gtfs_static_stop_times_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static stop times into NGSI-LD entities.

    The function processes each GTFS stop time entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed stop time entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsStopTime entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS stop times entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsStopTime

    Raises:
        ValueError:
            If any parsed stop time entity does not satisfy the GTFS validation rules.
    """
    
    # Container for the resulting NGSI-LD stop time entities
    ngsi_ld_data = []
    
    # Process each GTFS stop time entity
    for stop_time in raw_data:
        
        # Parse raw GTFS stop time data to the according data types
        parsed_entity = parse_gtfs_stop_times_data(stop_time)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_stop_times_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_stop_times_to_ngsi_ld(parsed_entity)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsStopTime entities
    return ngsi_ld_data

def gtfs_static_stops_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static stops into NGSI-LD entities.

    The function processes each GTFS stop entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed stop entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsStop entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS stop entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsStop

    Raises:
        ValueError:
            If any parsed stop entity does not satisfy the GTFS validation rules.
    """
    # Container for the resulting NGSI-LD stop entities
    ngsi_ld_data = []
    
    # Process each GTFS stop entity
    for stop in raw_data:
        
        # Parse raw GTFS stop data to the according data types
        parsed_entity = parse_gtfs_stops_data(stop)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_stops_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_stops_to_ngsi_ld(parsed_entity)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsStop entities
    return ngsi_ld_data

def gtfs_static_transfers_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static transfers into NGSI-LD entities.

    The function processes each GTFS transfer entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed transfer entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsTransfer entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS transfer entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsTransfer

    Raises:
        ValueError:
            If any parsed transfer entity does not satisfy the GTFS validation rules.
    """
    
    # Container for the resulting NGSI-LD transfer entities
    ngsi_ld_data = []
    
    # Process each GTFS transfer entity
    for transfer in raw_data:
        
        # Parse raw GTFS transfer data to the according data types
        parsed_entity = parse_gtfs_transfers_data(transfer)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_transfers_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_transfers_to_ngsi_ld(parsed_entity)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)
        
    # Return the list of NGSI-LD GtfsTransfer entities
    return ngsi_ld_data

def gtfs_static_trips_to_ngsi_ld(raw_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Converts GTFS static trips into NGSI-LD entities.

    The function processes each GTFS trip entity by:
    1. Parsing raw GTFS data transforming it to the according data types
    2. Validating the parsed trip entity against GTFS rules.
    3. Converting the validated entity into an NGSI-LD GtfsTrip entity.
    4. Removing attributes with None values from the resulting NGSI-LD entity.

    Args:
        raw_data (list[dict[str, Any]]):
            A list of dictionaries representing GTFS trip entities

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities, each representing GtfsTrip

    Raises:
        ValueError:
            If any parsed trip entity does not satisfy the GTFS validation rules.
    """
    
    # Container for the resulting NGSI-LD trip entities
    ngsi_ld_data = []
    
    # Process each GTFS trip entity
    for trip in raw_data:
        
        # Parse raw GTFS trip data to the according data types
        parsed_entity = parse_gtfs_trips_data(trip)
        
        # Validate the parsed entity (mandatory fields, formats, domain constraints)
        validate_gtfs_trips_entity(parsed_entity)
        
        # Convert the validated entity into NGSI-LD representation
        ngsi_ld_entity = convert_gtfs_trips_to_ngsi_ld(parsed_entity)
        
        # Remove attributes with None values for NGSI-LD compliance
        ngsi_ld_entity = remove_none_values(ngsi_ld_entity)
        
        # Append the final NGSI-LD entity to the result list
        ngsi_ld_data.append(ngsi_ld_entity)

    # Return the list of NGSI-LD GtfsTrip entities
    return ngsi_ld_data

# -----------------------------------------------------
# High-level function to get NGSI-LD data
# -----------------------------------------------------  
  
def gtfs_static_get_ngsi_ld_data(file_type: str, city: str, base_dir: str = "gtfs_static") -> list[dict[str, Any]]:
    """
    Reads GTFS static data from the local filesystem and converts it
    into NGSI-LD entities based on the specified GTFS file type.

    This function assumes that GTFS static data has already been downloaded
    and extracted using gtfs_static_download_and_extract_zip

    Based on the provided file_type, the function:
    1. Selects the corresponding GTFS .txt file.
    2. Reads its contents into a list of dictionaries.
    3. Applies the appropriate GTFS → NGSI-LD transformation function.

    Args:
        file_type (str):
            Identifier of the GTFS static file to process.

            Allowed values:
            - "agency"
            - "calendar_dates"
            - "fare_attributes"
            - "levels"
            - "pathways"
            - "routes"
            - "shapes"
            - "stop_times"
            - "stops"
            - "transfers"
            - "trips"

        base_dir (str, optional):
            Base directory where the GTFS static data is stored.
            "gtfs_static_download_and_extract_zip" always 
            creates a data subdirectory inside the base_dir
            Default directory is "gtfs_static".
            
        city (str):
            The city name to be included in the NGSI-LD entity ID for uniqueness.

    Returns:
        list[dict[str, Any]]:
            A list of NGSI-LD compliant entities corresponding to the selected
            GTFS static file type.

    Raises:
        ValueError:
            If the provided "file_type" is not supported.
        FileNotFoundError:
            If the expected GTFS file does not exist in `<base_dir>/data`.
    """
    
    # Mapping between GTFS file types, their filenames, and transformation functions
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

    # Validate requested GTFS file type
    if file_type not in mapping:
        raise FileNotFoundError(f"Unsupported GTFS static file type: {file_type}")

    # Resolve filename and corresponding transformation function
    filename, transformer = mapping[file_type]
    
    # Build the absolute path to the GTFS static file
    filepath = os.path.join(base_dir, "data", filename)

    # Read raw GTFS data from file
    raw_data = gtfs_static_read_file(filepath)
    
    # Convert raw GTFS data to NGSI-LD entities
    return transformer(raw_data, city)

if __name__ == "__main__":
    print(json.dumps(gtfs_static_get_ngsi_ld_data("fare_attributes", "Sofia"), indent=2, ensure_ascii=False))