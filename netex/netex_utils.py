import json
import re
import sys
import uuid
import shutil
import hashlib
import logging
import zipfile
from typing import Any
from pathlib import Path
from lxml import etree # type: ignore
from pyproj import Transformer
from collections import defaultdict
from shapely.geometry import LineString, Point as ShapelyPoint
from shapely.ops import substring
from datetime import datetime, timedelta

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import config

from fiware_scorpio.fiware_scorpio_crud_operations import (
    fiware_scorpio_define_header,
    fiware_scorpio_get_entities_by_type,
    fiware_scorpio_get_entity_by_id
    )

logger = logging.getLogger("NeTEx_Converter")

NETEX_NS = "http://www.netex.org.uk/netex"
GIS_NS = "http://www.opengis.net/gml/3.2"
SIRI_NS = "http://www.siri.org.uk/siri"

NSMAP = {
    None: NETEX_NS,
    "gis": GIS_NS,
    "siri": SIRI_NS
}

etree.register_namespace("gis", GIS_NS)

ROUTE_COUNTER = 0
LINE_COUNTER = 0
JOURNEY_PATTERN_COUNTER = 0
SERVICE_JOURNEY_COUNTER = 0
SERVICE_JOURNEY_INTERCHANGE_COUNTER = 0

now_time = datetime.now()

# -----------------------------------------------------
# Output Functions
# -----------------------------------------------------

def netex_helper_prepare_output_directory() -> None:
    """
    Recreate NeTEx output directory.
    """
    # Remove existing content if the output directory already exists
    if config.NETEX_OUTPUT_DIR.exists():
        shutil.rmtree(config.NETEX_OUTPUT_DIR)

    # Create the output directory
    config.NETEX_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def netex_helper_create_otp_zip() -> None:
    """
    Create a ZIP archive containing all generated NeTEx XML files.
    """

    # Define the path for the ZIP archive
    zip_path = config.OTP_DATA_DIR / "netex.zip"

    # Create a ZIP archive and add all XML files from the output directory
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:

        # Add each XML file in the output directory to the archive
        for xml_file in config.NETEX_OUTPUT_DIR.glob("*.xml"):
            archive.write(xml_file, arcname=xml_file.name)

    logger.info("Created OTP archive: %s", zip_path)

# -----------------------------------------------------
# Get Data Functions
# -----------------------------------------------------
def netex_helper_set_operating_city(city: str) -> None:
    """
    Set the parameter config.NETEX_OPERATING_CITY to the city for which we want to get data
    
    Args:
        city (str): Operating city for which we want to get data

    Returns:
        None

    Raises:
        TypeError: If `city` is not a string
        ValueError: If `city` is empty or contains invalid characters
    """
    # If not a string, raise TypeError
    if not isinstance(city, str):
        raise TypeError("City must be a string")

    # Remove whitespaces around and set to title case
    city = city.strip().title().replace(" ", "_").replace("-", "_")

    # If empty, raise ValueError
    if not city:
        raise ValueError("City cannot be empty")

    # Check that the city contains valid characters
    if not re.fullmatch(r"[A-Za-zА-Яа-я_]+", city):
        raise ValueError("City contains invalid characters")
    
    # Set the parameter
    config.NETEX_OPERATING_CITY = city

def netex_get_all_gtfs_agencies_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsAgency entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsAgency entities
    for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsAgency entities for the operating city

    Raises:
        ValueError: When config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")

    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsAgency", header, config.NETEX_OPERATING_CITY)
    
def netex_get_all_gtfs_routes_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsRoute entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsRoute entities
    for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsRoute entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    # Define header
    header = fiware_scorpio_define_header("gtfs_static")

    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsRoute", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_trips_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsTrip entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsTrip entities
    for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsTrip entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsTrip", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_calendar_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsCalendarRule entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsCalendarRule
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsCalendarRule entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsCalendarRule", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_calendar_dates_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsCalendarDateRule entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsCalendarDateRule
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsCalendarDateRule entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsCalendarDateRule", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_shapes_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsShape entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsShape
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsShape entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsShape", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_stop_times_of_a_city() -> list[dict[str, Any]]:
    """
    Get all GtfsStopTime entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsStopTime
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsStopTime entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsStopTime", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_stops_of_city() -> list[dict[str, Any]]:
    """
    Get all GtfsStop entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsStop
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsStop entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsStop", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_transfers_of_city() -> list[dict[str, Any]]:
    """
    Get all GtfsTransfer entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsTransfer
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsTransfer entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsTransfer", header, config.NETEX_OPERATING_CITY)

def netex_get_all_gtfs_translations_of_city() -> list[dict[str, Any]]:
    """
    Get all GtfsTranslation entities of a city

    Based on the set parameter config.NETEX_OPERATING_CITY, the function sets a GET request to retrieve all GtfsTransfer
    entities for the operating city.
    
    Returns:
        list[dict[str, Any]]: A list of all GtfsTranslation entities for the operating city
        
    Raises:
        ValueError: If config.NETEX_OPERATING_CITY is not set
    """
    header = fiware_scorpio_define_header("gtfs_static")
    
    if not config.NETEX_OPERATING_CITY:
        raise ValueError("Parameter config.NETEX_OPERATING_CITY is not set ")
    
    return fiware_scorpio_get_entities_by_type("GtfsTranslation", header, config.NETEX_OPERATING_CITY)

def netex_load_city_dataset() -> dict[str, Any]:
    
    return {
        "agencies": netex_get_all_gtfs_agencies_of_a_city(),
        "routes": netex_get_all_gtfs_routes_of_a_city(),
        "trips": netex_get_all_gtfs_trips_of_a_city(),
        "calendar": netex_get_all_gtfs_calendar_of_a_city(),
        "calendar_dates": netex_get_all_gtfs_calendar_dates_of_a_city(),
        "shapes": netex_get_all_gtfs_shapes_of_a_city(),
        "stop_times": netex_get_all_gtfs_stop_times_of_a_city(),
        "stops": netex_get_all_gtfs_stops_of_city(),
        "transfers": netex_get_all_gtfs_transfers_of_city(),
        "translations": netex_get_all_gtfs_translations_of_city()
    }

# -----------------------------------------------------
# Index Functions
# -----------------------------------------------------

def netex_index_routes_by_agency(routes: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group the GtfsRoute entities based on the agencies who support them
    
    Args:
        routes (list[dict[str, Any]]): List of GtfsRoute entities who are to be grouped
        
    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping agency IDs to lists of routes
    """

    # Group container
    routes_by_agency = defaultdict(list)

    # Traverse all routes
    for route in routes:
        
        # Get the agency relationship and extract the agency ID
        operated_by = route.get("operatedBy")
        agency_id = operated_by.get("object") if operated_by else None

        # If missing, log error and continue
        if not agency_id:
            logger.error("Invalid or missing operatedBy: %r", route.get("id"))
            continue

        # Add route for the coresponding agency
        routes_by_agency[agency_id].append(route)

    return dict(routes_by_agency)

def netex_index_trips_by_route(trips: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group GtfsTrip entities based on the route they belong to.

    Args:
        trips (list[dict[str, Any]]): List of GtfsTrip entities to group

    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping route IDs to lists of trips
    """

    # Group container
    trips_by_route = defaultdict(list)

    # Traverse all trips
    for trip in trips:

        # Get route relationship and extract the route ID
        route = trip.get("route")
        route_id = route.get("object") if route else None

        # If missing, log error and continue
        if not route_id:
            logger.error("Trip missing or invalid route: %r", trip["id"])
            continue

        # Add trip to corresponding route
        trips_by_route[route_id].append(trip)

    return dict(trips_by_route)
 
def netex_index_calendar_or_calendar_dates_by_service(calendar_or_calendar_dates: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group GtfsCalendarRule / GtfsCalendarDateRule entities based on the service they belong to.

    Args:
        calendar_or_calendar_dates (list[dict[str, Any]]): List of GtfsCalendarRule / GtfsCalendarDateRule entities to group

    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping service IDs to lists of calendar / calendar dates
    """

    # Group container
    calendar_or_calendar_dates_by_service = defaultdict(list)

    # Traverse all calendar dates
    for calendar_or_calendar_date in calendar_or_calendar_dates:

        # Get service relationship and extract service ID
        service = calendar_or_calendar_date.get("hasService")
        service_id = service.get("object") if service else None

        # If missing, log error and continue
        if not service_id:
            logger.error("Calendar / Calendar Date has missing or invalid service: %r", calendar_or_calendar_date["id"])
            continue

        # Add calendar date to corresponding service
        calendar_or_calendar_dates_by_service[service_id].append(calendar_or_calendar_date)

    return dict(calendar_or_calendar_dates_by_service)

def netex_index_shape_by_trip(trips: list[dict[str, Any]], shapes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Map each GtfsTrip to the GtfsShape it follows.

    Args:
        trips (list[dict[str, Any]]): List of GtfsTrip entities
        shapes (list[dict[str, Any]]): List of GtfsShape entities
    Returns:
        dict[str, str]: Dictionary mapping trip ID to shapes
    """
    shape_by_id = { shape["id"]: shape for shape in shapes if shape.get("id") is not None}

    # Container
    shape_by_trip = {}

    # Traverse through all trips
    for trip in trips:

        # Get trip ID and shape relationship
        trip_id = trip.get("id")
        shape_ref = trip.get("hasShape")

        # From trips get it's ID and the shape it refers to
        if not trip_id or not shape_ref:
            logger.error("Trip missing data: %r", trip_id)
            continue

        # Extract shape ID
        shape_id = shape_ref.get("object")
        if not shape_id:
            logger.error("Invalid hasShape structure: %r", trip_id)
            continue

        # Extract shape entity 
        shape = shape_by_id.get(shape_id)
        if not shape:
            logger.error("Shape not found: %s for trip %s", shape_id, trip_id)
            continue

        # Create the trip ID - Shape entity relationship
        shape_by_trip[trip_id] = shape

    return shape_by_trip

def netex_index_stop_times_by_trip(stop_times: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group GtfsStopTimes entities based on the trips they follow.

    Args:
        stop_times (list[dict[str, Any]]): List of GtfsStopTimes entities to group

    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping stop time IDs to lists of trips
    """
    # Group container
    stop_times_by_trip = defaultdict(list)

    # Traverse all stop times
    for stop_time in stop_times:

        # Get trip relationship and extract trip ID
        trip = stop_time.get("hasTrip")
        trip_id = trip.get("object") if trip else None

        # If missing, log error and continue
        if not trip_id:
            logger.error("Stop time missing or invalid hasTrip: %r", stop_time["id"])
            continue

        # Add stop time to corresponding trip
        stop_times_by_trip[trip_id].append(stop_time)
        
    # Sort by stopSequence as it will be needed later on
    for trip_id in stop_times_by_trip:
        stop_times_by_trip[trip_id].sort(key=lambda st: st.get("stopSequence", {}).get("value", 0))

    return dict(stop_times_by_trip)

# def netex_index_stops_by_trip(stop_times: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
#     """
#     Group GtfsStop entities based on the trip they follow

#     Args:
#         stop_times (list[dict[str, Any]]): List of GtfsStopTime entities where the relationship stop - trip could be found

#     Returns:
#         dict[str, list[dict[str, Any]]]: Dictionary mapping trip ID to list of stops
#     """
#     # Group container
#     stops_by_trip = {}

#     # Traverse all stop times
#     for stop_time in stop_times:

#         # Get trip relationship
#         trip = stop_time.get("hasTrip")

#         # If missing, log error and continue
#         if not trip:
#             logger.error("Stop time missing hasTrip: %r", stop_time["id"])
#             continue

#         # Extract trip ID
#         trip_id = trip.get("object")
        
#         # If invalid, log error and continue
#         if not trip_id:
#             logger.error("Invalid hasTrip structure: %r", stop_time["id"])
#             continue

#         trip_id_value = trip_id.split(":")[-1]
        
#         # Get stop relationship
#         stop = stop_time.get("hasStop")
        
#         # If missing, log error and continue
#         if not stop:
#             logger.error("Stop time missing hasStop: %r", stop_time["id"])
#             continue
        
#         # Extract stop ID
#         stop_id = stop.get("object")
        
#         # If invalid, log error and continue
#         if not stop_id:
#             logger.error("Invalid hasStop structure: %r", stop_time["id"])
#             continue 

#         stop_id_value = stop_id.split(":")[-1]

#         # Get stop sequence
#         sequence = stop_time.get("stopSequence", {}).get("value")

#         # If invalid, log error and continue
#         if not isinstance(sequence, int):
#             logger.error("Invalid stopSequence: %r", stop_time["id"])
#             continue

#         # Create container if trip id is encountered for the first time
#         if trip_id_value not in stops_by_trip:
#             stops_by_trip[trip_id_value] = []

#         # Add sequence and stop ID tuple
#         stops_by_trip[trip_id_value].append((sequence, stop_id_value))

#     for trip_id_value in stops_by_trip:

#         # Sort stops by sequence number
#         stops_by_trip[trip_id_value].sort(key=lambda x: x[0])

#         # Keep only the stop IDs in the final output
#         stops_by_trip[trip_id_value] = [stop_id_value for _, stop_id_value in stops_by_trip[trip_id_value]]

#     return stops_by_trip

def netex_collect_stops(stop_times: list[dict[str, Any]], stops: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Collect all unique stop entities referenced by stop times.

    Args:
        stop_times (list[dict[str, Any]]): List of GtfsStopTime entities where the relationship stop - trip could be found

        stops (list[dict[str, Any]]): List of all GtfsStop entities for the city

    Returns:
        list[dict[str, Any]]: List of unique GtfsStop entities that are referenced by the stop times
    """

    # Set to store unique IDs
    stop_ids = set()

    # Traverse all stop times and collect unique stop IDs
    for stop_time in stop_times:

        # Get stop relationship
        stop = stop_time.get("hasStop")
        stop_id = stop.get("object") if stop else None

        # If missing, log error and continue
        if not stop_id:
            logger.error("Stop time missing or invalid hasStop: %r", stop_time.get("id"))
            continue

        stop_ids.add(stop_id)

    return [stop for stop in stops if stop.get("id") in stop_ids]
   
def netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filter GtfsTransferRule entities that can be represented as NeTEx ServiceJourneyInterchange.

    A valid ServiceJourneyInterchange requires:
    - from_stop_id
    - to_stop_id
    - from_trip_id
    - to_trip_id

    Args:
        transfers (list[dict[str, Any]]):
            List of GtfsTransferRule entities.

    Returns:
        list[dict[str, Any]]:
            List containing only valid ServiceJourneyInterchange candidates.
    """
    # Container for valid transfers
    valid_transfers = []

    for transfer in transfers:

        # Get transfer id
        transfer_id = transfer.get("id")

        # If `hasOrigin` (from_stop_id) is missing, continue
        has_origin = transfer.get("hasOrigin", {}).get("object")
        if not has_origin:
            logger.error("Transfer cannot be converted to ServiceJourneyInterchange. Missing hasOrigin: %r", transfer_id)
            continue

        # If `hasDestination` (to_stop_id) is missing, continue
        has_destination = transfer.get("hasDestination", {}).get("object")
        if not has_destination:
            logger.error("Transfer cannot be converted to ServiceJourneyInterchange. Missing hasDestination: %r",transfer_id)
            continue

        # If from_trip_id is missing, continue
        from_trip = transfer.get("from_trip_id", {}).get("object")
        if not from_trip:
            logger.error("Transfer cannot be converted to ServiceJourneyInterchange. Missing from_trip_id: %r",transfer_id)
            continue

        # If to_trip_id is missing, continue
        to_trip = transfer.get("to_trip_id", {}).get("object")
        if not to_trip:
            logger.error("Transfer cannot be converted to ServiceJourneyInterchange. Missing to_trip_id: %r", transfer_id)
            continue

        # If trip has the needed data, add to valid
        valid_transfers.append(transfer)

    return valid_transfers

def netex_index_transfers_by_origin_trip(transfers: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group valid GtfsTransferRule entities by their origin trip.

    The function filters out transfers that cannot be converted to
    NeTEx ServiceJourneyInterchange and groups the remaining transfers
    by their from_trip_id.

    Args:
        transfers (list[dict[str, Any]]): List of GtfsTransferRule entities.

    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping origin trip IDs to transfer entities.
    """

    # Keep only transfers that can be represented in NeTEx
    valid_transfers = netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers)

    # Group container
    transfers_by_origin_trip = defaultdict(list)

    # Traverse all valid transfers
    for transfer in valid_transfers:

        # Extract origin trip ID
        from_trip_id = transfer["from_trip_id"]["object"]
        
        # Add transfer
        transfers_by_origin_trip[from_trip_id].append(transfer)

    return dict(transfers_by_origin_trip)

def netex_build_field_value_index(translations: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, str]]:

    index = defaultdict(dict)

    for tr in translations:
        table_name = tr.get("table_name", {}).get("value")
        field_name = tr.get("field_name", {}).get("value")
        language = tr.get("language", {}).get("value")
        translation = tr.get("translation", {}).get("value")
        field_value = tr.get("field_value", {}).get("value")

        # only valid field-based translations
        if not field_value:
            continue

        field_value = field_value.strip().replace(" ", "_")
        
        key = (table_name, field_name, field_value)
        index[key][language] = translation

    return dict(index)

def netex_build_record_id_index(translations: list[dict[str, Any]]) -> dict[tuple[str, str, str, str | None], dict[str, str]]:

    index = defaultdict(dict)

    for tr in translations:
        table_name = tr.get("table_name", {}).get("value")
        field_name = tr.get("field_name", {}).get("value")
        language = tr.get("language", {}).get("value")
        translation = tr.get("translation", {}).get("value")

        record_id = tr.get("record_id", {}).get("value")
        record_sub_id = tr.get("record_sub_id", {}).get("value")

        # only valid record-based translations
        if not record_id:
            continue

        key = (table_name, field_name, record_id, record_sub_id)
        index[key][language] = translation

    return dict(index)

def netex_build_translation_indexes(translations: list[dict[str, Any]]) -> dict[str, Any]:

    return {
        "by_field_value": netex_build_field_value_index(translations),
        "by_record_id": netex_build_record_id_index(translations)
    }
    
def netex_resolve_translation(indexes, table_name, field_name, 
                              field_value=None, record_id=None, record_sub_id=None, language: str = "en") -> str | None:

    translations = {}
    
    # 1. record-based index
    if record_id is not None:
        key = (table_name, field_name, record_id, record_sub_id)
        translations = indexes["by_record_id"].get(key, {})
        
    # 2. field-based index
    if not translations and field_value is not None:
        key = (table_name, field_name, field_value)
        field_value = field_value.strip().replace(" ", "_")
        translations = indexes["by_field_value"].get(key, {})

    return translations.get(language)
    
def netex_build_indexes_and_collections(city_dataset: dict[str, Any]) -> dict[str, Any]:
    """
    Build all lookup indexes required for NeTEx generation.

    Args:
        city_dataset (dict[str, Any]): Complete GTFS dataset for a city

    Returns:
        dict[str, Any]: Collection of lookup indexes
    """

    return {
        "routes_by_agency": netex_index_routes_by_agency(city_dataset["routes"]),
        "trips_by_route": netex_index_trips_by_route(city_dataset["trips"]),
        "shape_by_trip": netex_index_shape_by_trip(city_dataset["trips"], city_dataset["shapes"]),
        "calendar_by_service": netex_index_calendar_or_calendar_dates_by_service(city_dataset["calendar"]),
        "calendar_dates_by_service": netex_index_calendar_or_calendar_dates_by_service(city_dataset["calendar_dates"]),
        "stop_times_by_trip": netex_index_stop_times_by_trip(city_dataset["stop_times"]),
        "transfers_by_origin_trip": netex_index_transfers_by_origin_trip(city_dataset["transfers"]),
        "translations": netex_build_translation_indexes(city_dataset["translations"])    
    }

# -----------------------------------------------------
# Build Dataset for a Single Authority
# -----------------------------------------------------
def netex_helper_collect_entities_by_trip(trips: list[dict[str, Any]], index: dict[str, list[dict[str, Any]]], entity_name: str) -> list[dict[str, Any]]:
    """
    Collect entities related to trips from a pre-built index.

    Args:
        trips (list[dict[str, Any]]): List of GtfsTrip entities

        index (dict[str, list[dict[str, Any]]]): Lookup index

        entity_name (str): Entity type for logging

    Returns:
        list[dict[str, Any]]: List of entities of different Gtfs types, related to different trips
    """

    # Container to store entities
    collected = []

    # Traverse all trips
    for trip in trips:

        # Get trip id
        trip_id = trip.get("id")

        if not isinstance(trip_id, str):
            logger.warning("Invalid or missing trip id for %s", trip)
            continue

        # Collect from the index all entities related to a specific trip
        entities = index.get(trip_id, [])

        # Log if no entities of a specific type are found
        if not entities:
            logger.warning("No %s found for trip %s", entity_name, trip_id)

        # Extend container
        collected.extend(entities)

    return collected

def netex_helper_collect_entities_by_service(trips: list[dict[str, Any]], index: dict[str, list[dict[str, Any]]], entity_name: str) -> list[dict[str, Any]]:
    """
    Collect entities related to services - GtfsCalendarRule and GtfsCalendarDateRule.

    Args:
        trips (list[dict[str, Any]]): List of GtfsTrip entities

        index (dict[str, list[dict[str, Any]]]): Lookup index

        entity_name (str): Entity type for logging

    Returns:
        list[dict[str, Any]]: List of entities of different Gtfs types, related to different services - GtfsCalendarRule and GtfsCalendarDateRule.
    """

    # Container to store entities
    collected = []

    # Traverse all trips
    for trip in trips:

        # Get service id
        service = trip.get("service") or trip.get("hasService")
        service_id = service.get("object") if service else None
        
        if not isinstance(service_id, str):
            logger.warning("Invalid or missing service id for trip %s", trip.get("id"))
            continue

        # Collect from the index all entities related to a specific service
        entities = index.get(service_id, [])

        # Log if no entities of a specific type are found
        if not entities:
            pass
            # logger.warning("No %s found for service %s", entity_name, service_id)

        # Extend container
        collected.extend(entities)

    return collected

def netex_helper_collect_shapes_by_trip(trips: list[dict[str, Any]], shape_by_trip: dict[str, str]) -> list[str]:
    """
    Collect all GtfsShape entity ID's based on a trip

    Args:
        trips (list[dict[str, Any]]): List of GtfsTrip entities

        shape_by_trip (dict[str, str]): Lookup index

    Returns:
        list[str]: List of GtfsShape entity ID's based on the trip they are associated with
    """

    # Container to store entities
    shape_ids = []

    # Traverse all trips
    for trip in trips:

        # Get trip ID
        trip_id = trip.get("id")

        if not isinstance(trip_id, str):
            logger.warning("Invalid trip id %s", trip_id)
            continue

        # Collect all shape IDs associated with the trip
        shape_id = shape_by_trip.get(trip_id)

        # Log if no shapes are associated with the trip
        if not shape_id:
            logger.warning("No shape found for trip %s", trip_id)
            continue

        # Append to the container
        shape_ids.append(shape_id)

    return shape_ids

def netex_build_authority_dataset(agency: dict[str, Any], indexes: dict[str, Any]) -> dict[str, Any]:
    """
    Builds a fully resolved data context for a single GTFS Agency.

    Args:
        agency (dict[str, Any]): GTFS Agency entity
        indexes (dict[str, Any]): Precomputed index structures

    Returns:
        dict[str, Any]: Fully resolved authority context
    """

    agency_id = agency.get("id")

    if not agency_id:
        logger.error("Agency missing ID: %r", agency)
        return {}

    dataset = {
        "agency": agency,
        "routes": [],
        "trips": [],
        "calendar": [],
        "calendar_dates": [],
        "stop_times": [],
        "stops": [],
        "shapes": [],
        "transfers": [],
        "translations": []
    }

    # -----------------------------
    # ROUTES
    # -----------------------------
    routes = indexes["routes_by_agency"].get(agency_id, [])

    if not routes:
        logger.warning("No routes found for agency: %s", agency_id)

    dataset["routes"] = routes

    # -----------------------------
    # TRIPS
    # -----------------------------
    trips_by_route = indexes.get("trips_by_route", {})

    trips = []

    for route in routes:
        route_id = route.get("id")
        route_trips = trips_by_route.get(route_id, [])

        if not route_trips:
            logger.warning("No trips found for route %s", route_id)

        trips.extend(route_trips)

    dataset["trips"] = trips

    # -----------------------------
    # CALENDAR
    # -----------------------------
    dataset["calendar"] = netex_helper_collect_entities_by_service(trips, indexes.get("calendar_by_service", {}), "calendars")

    # -----------------------------
    # CALENDAR DATES
    # -----------------------------
    dataset["calendar_dates"] = netex_helper_collect_entities_by_service(trips, indexes.get("calendar_dates_by_service", {}), "calendar dates")

    # -----------------------------
    # STOP TIMES
    # -----------------------------
    dataset["stop_times"] = netex_helper_collect_entities_by_trip(trips, indexes.get("stop_times_by_trip", {}), "stop times")
    # -----------------------------
    # STOPS
    # -----------------------------
    dataset["stops"] = netex_get_all_gtfs_stops_of_city()

    # -----------------------------
    # SHAPES
    # -----------------------------
    dataset["shapes"] = netex_helper_collect_shapes_by_trip(trips, indexes.get("shape_by_trip", {}))

    # -----------------------------
    # TRANSFERS
    # -----------------------------

    dataset["transfers"] = netex_helper_collect_entities_by_trip(trips, indexes.get("transfers_by_origin_trip", {}), "transfers")

    # -----------------------------
    # TRANSLATIONS
    # -----------------------------
    
    dataset["translations"] = indexes.get("translations", {})
    
    return dataset

def netex_build_route_dataset(route: dict[str, Any], authority_dataset: dict[str, Any]) -> dict[str, Any]:
    """
    Build a dataset containing all data needed to create the NeTEx Line files

    Args:
        route (dict[str, Any]): GtfsRoute entity for which the dataset is built
        authority_dataset (dict[str, Any]): Fully resolved authority context

    Returns:
        dict[str, Any]: Fully resolved route context
    """

    route_id = route.get("id")

    if not route_id:
        logger.error("Route missing ID: %r", route)
        return {}

    trips = [trip for trip in authority_dataset.get("trips", []) if trip.get("route", {}).get("object") == route_id]
    
    if not trips:
        logger.warning("Skipping route %s: no trips found.", route_id)
        return {}

    trip_ids = {trip["id"] for trip in trips if trip.get("id")}
    
    trip_shapes = {}

    for trip in trips:
        trip_id = trip.get("id")
        shape_ref = trip.get("hasShape", {}).get("object")

        if trip_id and shape_ref:
            trip_shapes[trip_id] = shape_ref.split(":")[-1]
    

    stop_times = authority_dataset.get("stop_times", [])

    stop_times_by_trip = {}

    for stop_time in stop_times:
        trip_id = stop_time.get("hasTrip", {}).get("object")
        if trip_id in trip_ids:
            stop_times_by_trip.setdefault(trip_id, []).append(stop_time)
            
    # if not stop_times_by_trip:
    #     logger.warning("Skipping route %s: no stop times found.", route_id)
    #     return {}

    transfers = [transfer for transfer in authority_dataset.get("transfers", []) 
                 if transfer.get("from_trip_id", {}).get("object") in trip_ids
                 ]

    service_ids = {trip.get("service", {}).get("object") for trip in trips}
        
    calendars = [calendar for calendar in authority_dataset["calendar"] if calendar.get("hasService", {}).get("object") in service_ids]

    calendar_dates = [calendar_date for calendar_date in authority_dataset["calendar_dates"] if calendar_date.get("hasService", {}).get("object") in service_ids]
    
    return {
        "agency": authority_dataset["agency"],
        "route": route,
        "trips": trips,
        "trip_shapes": trip_shapes,
        "stop_times": stop_times_by_trip,
        "transfers": transfers,
        "calendar": calendars,
        "calendar_dates": calendar_dates,
    }

# -----------------------------------------------------
# Set NeTEx Authority for ID Generation
# -----------------------------------------------------

def netex_helper_set_netex_authority(agency: dict[str, Any]) -> None:
    """
    Set the global config.NETEX_AUTHORITY used for GTFS to NeTEx Nordic conversion
    Args:
        agency (dict[str, Any]): GtfsAgency entity from which the ID is extracted

    Raises:
        ValueError: If the entity is not of type `GtfsAgency`
        ValueError: If the entity doesn't have an `id` field
    """
    # Check if entity is of GtfsAgency type
    if agency["type"] != "GtfsAgency":
        raise ValueError("The provided entity for NeTEx Authority setting should be of type GtfsAgency")

    # Try setting config.NETEX_Authority
    try:
        raw_id = agency["id"].split(":")[-1]
    except KeyError:
        raise ValueError("Entity should have an ID")

    # Normalize to exactly 3 characters
    if len(raw_id) < 3:
        authority = raw_id.ljust(3, "X")  # padding if too short
    else:
        authority = raw_id[:3]  # truncate if longer than 3

    config.NETEX_AUTHORITY = authority

# -----------------------------------------------------
# Generate <validityConditions>
# -----------------------------------------------------
def netex_helper_build_validity_conditions(now_time) -> etree.Element:
    """
    Build validityConditions container for all NeTEx files

    Returns:
        etree.Element
    """
    validity_conditions = etree.Element("validityConditions")
    availability_condition = etree.SubElement(validity_conditions, "AvailabilityCondition", version = "1",
                                              id = f"{config.NETEX_AUTHORITY}:AvailabilityCondition:{uuid.uuid4()}")
    etree.SubElement(availability_condition, "FromDate").text = now_time.isoformat(timespec="milliseconds")
    etree.SubElement(availability_condition, "ToDate").text = (now_time + timedelta(days=365)).isoformat(timespec="milliseconds")
    
    return validity_conditions
    
def netex_helper_stream_validity_conditions(xml_file, now_time) -> None:
    """
    Stream <validityConditions> in NeTEx files
    
    Returns:
        None
    """
    # Build <validityConditions>
    validity_condition = netex_helper_build_validity_conditions(now_time)
    
    # Stream <validityConditions> into NeTEx file
    xml_file.write(validity_condition, pretty_print=True)
    
# -----------------------------------------------------
# Generate <FrameDefaults>
# -----------------------------------------------------
def netex_helper_build_frame_defaults(agency: dict[str, Any]) -> etree.Element | None:
    """
    Builds a NeTEx <FrameDefaults> element.

    Args:
        agency (dict[str, Any]): GtfsAgency entity

    Returns:
        etree.Element | None
    """

    entity_type = agency.get("type")

    if entity_type != "GtfsAgency":
        logger.error("Unsupported entity type for FrameDefaults conversion: %s", entity_type)
        return None

    time_zone = agency.get("agency_timezone", {}).get("value")
    language = agency.get("agency_lang", {}).get("value")

    frame_defaults = etree.Element("FrameDefaults")

    default_locale = etree.SubElement(frame_defaults, "DefaultLocale")
    etree.SubElement(default_locale, "TimeZone").text = time_zone

    if language:
        etree.SubElement(default_locale, "DefaultLanguage").text = language

    return frame_defaults

def netex_helper_stream_frame_defaults(xml_file, agency: dict[str, Any]) -> None:
    """
    Streams a FrameDefaults element into XML.

    Args:
        xml_file: XML writer instance
        agency (dict[str, Any]): GtfsAgency entity

    Returns:
        None
    """
    # Get the frame defaults
    frame_defaults = netex_helper_build_frame_defaults(agency)

    if frame_defaults is None:
        return

    # Write <FrameDefaults> into XML file
    xml_file.write(frame_defaults, pretty_print=True)
    
# -----------------------------------------------------
# GtfsAgency to NeTex <Authority> and <Operator>
# -----------------------------------------------------
##########################################################
# Questions: 
# Observing the Netur Dataset we see a mapping of GTFS Agency to NeTEx Authority.
# We already discussed that we will map GTFS Agency also to Operator but this begs the question - In general where does the Operator data come from if not observed in the GTFS files ?
# Plus thete are multiple operators and 1 authority that combines them
def netex_helper_build_authority(gtfs_agency: dict[str, Any], company_number: int) -> etree.Element | None:
    """
    Builds a single NeTEx <Authority> element.

    Args:
        entity (dict[str, Any]): A GtfsAgency entity
        company_number (int): Index of the entity in the input stream

    Returns:
        etree.Element | None
    """

    # Get entity type and ID
    entity_type = gtfs_agency.get("type")
    agency_id = gtfs_agency.get("id")

    # If not the correct entity type, return None
    if entity_type != "GtfsAgency":
        logger.error("Unsupported entity type for Authority conversion: %s", entity_type)
        return None

    # If not in the correct format, log an error and return None
    if not isinstance(agency_id, str) or ":" not in agency_id:
        logger.error("Invalid or missing ID for GtfsAgency: %r", agency_id)
        return None

    agency_id_value = agency_id.split(":")[-1]
    agency_name = gtfs_agency.get("agency_name", {}).get("value")

    # Build <Authority> element with it's info
    authority = etree.Element("Authority", version="1", id=f"{config.NETEX_AUTHORITY}:Authority:{agency_id_value}_ID")

    etree.SubElement(authority, "CompanyNumber").text = str(company_number)
    etree.SubElement(authority, "Name").text = agency_name
    etree.SubElement(authority, "LegalName").text = agency_name

    agency_phone = gtfs_agency.get("agency_phone", {}).get("value")
    agency_fare_url = gtfs_agency.get("agency_fare_url", {}).get("value")
    agency_email = gtfs_agency.get("agency_email", {}).get("value")

    contact = etree.SubElement(authority, "ContactDetails")

    if agency_email:
        etree.SubElement(contact, "Email").text = agency_email

    if agency_phone:
        etree.SubElement(contact, "Phone").text = agency_phone

    etree.SubElement(contact, "Url").text = agency_fare_url

    etree.SubElement(authority, "OrganisationType").text = "authority"

    return authority

def netex_helper_stream_authorities(xml_file, agencies: list[dict[str, Any]]) -> None:
    """
    Streams Authority elements into XML.

    Args:
        xml_file: XML writer instance
        agencies (list[dict[str, Any]]): List of GtfsAgency entities

    Returns:
        None
    """
    # Set used to not introduce duplicates
    seen_ids = set()

    for index, entity in enumerate(agencies, start=1):

        # Build <Authority> element
        authority = netex_helper_build_authority(entity, index)

        # Skip when unsuccessful
        if authority is None:
            continue

        # Get <Authority> element's ID
        authority_id = authority.get("id")

        # If encountered already, skip
        if authority_id in seen_ids:
            continue

        # Add ID to seen IDs set
        seen_ids.add(authority_id)

        # Stream <Authority> element in XML file
        xml_file.write(authority, pretty_print=True)

def netex_helper_build_operator(entity: dict[str, Any], company_number: int) -> etree.Element | None:
    """
    Builds a single NeTEx <Operator> element.

    Args:
        entity (dict[str, Any]): A GtfsAgency entity
        company_number (int): Index of the entity in the input stream

    Returns:
        etree.Element | None
    """
    # Get entity type and ID
    entity_type = entity.get("type")
    agency_id = entity.get("id")

    # If not the correct entity type, return None
    if entity_type != "GtfsAgency":
        logger.error("Unsupported entity type for Operator conversion: %s", entity_type)
        return None

    # If not in the correct format, log an error and return None
    if not isinstance(agency_id, str) or ":" not in agency_id:
        logger.error("Invalid or missing ID for GtfsAgency: %r", agency_id)
        return None

    agency_id_value = agency_id.split(":")[-1]
    agency_name = entity.get("agency_name", {}).get("value")

    # Build <Operator> element with it's info
    operator = etree.Element("Operator", version="1", id=f"{config.NETEX_AUTHORITY}:Operator:{agency_id_value}")

    etree.SubElement(operator, "CompanyNumber").text = str(company_number)
    etree.SubElement(operator, "Name").text = agency_name
    etree.SubElement(operator, "LegalName").text = agency_name

    agency_phone = entity.get("agency_phone", {}).get("value")
    agency_fare_url = entity.get("agency_fare_url", {}).get("value")
    agency_email = entity.get("agency_email", {}).get("value")

    contact = etree.SubElement(operator, "ContactDetails")

    if agency_email:
        etree.SubElement(contact, "Email").text = agency_email

    if agency_phone:
        etree.SubElement(contact, "Phone").text = agency_phone

    etree.SubElement(contact, "Url").text = agency_fare_url

    etree.SubElement(operator, "OrganisationType").text = "operator"

    return operator

def netex_helper_stream_operators(xml_file, agencies: list[dict[str, Any]]) -> None:
    """
    Streams Operator elements into XML.

    Args:
        xml_file: XML writer instance
        agencies (list[dict[str, Any]]): List of GtfsAgency entities

    Returns:
        None
    """
    # Set used to not introduce duplicates
    seen_ids = set()

    for index, entity in enumerate(agencies, start=1):

        # Build <Operator> element
        operator = netex_helper_build_operator(entity, index)

        # Skip when unsuccessful
        if operator is None:
            continue
     
        # Get <Operator> element's ID
        operator_id = operator.get("id")

        # If encountered already, skip
        if operator_id in seen_ids:
            continue

        # Add ID to seen IDs set
        seen_ids.add(operator_id)

        # Stream <Operator> element in XML file
        xml_file.write(operator, pretty_print=True)

# -----------------------------------------------------
# Generate <ResourceFrame>
# -----------------------------------------------------

def netex_stream_resource_frame_for_shared_data_xml(xml_file, agencies: list[dict[str, Any]] | dict[str, Any]) -> None:
    """
    Streams NeTEx <ResourceFrame> into XML.

    Args:
        xml_file: XML writer instance
        agencies (list[dict[str, Any]] | dict[str, Any]): GtfsAgency entities

    Returns:
        None
    """
    if not isinstance(agencies, list):
        agencies = [agencies]

    
    with xml_file.element("ResourceFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ResourceFrame:{uuid.uuid4()}"):
        with xml_file.element("organisations"):

            # Stream Authorities
            netex_helper_stream_authorities(xml_file, agencies)

            # Stream Operators
            netex_helper_stream_operators(xml_file, agencies)

# -----------------------------------------------------
# Generate <Network>
# -----------------------------------------------------

def netex_helper_build_network(agency: dict[str, Any]) -> etree.Element | None:
    """
    Builds a single NeTEx <Network> element.

    Args:
        agency (dict[str, Any]): A GtfsAgency entity from which the Network information is extracted

    Returns:
        etree.Element | None
    """

    # Get entity type and ID
    network_id = agency["id"]
    entity_type = agency["type"]

    # If not the correct entity type, return None
    if entity_type != "GtfsAgency":
        logger.error("Unsupported entity type for Network conversion: %s", entity_type)
        return None
    
    # If not in the correct format, log an error and return None
    if not isinstance(network_id, str) or ":" not in network_id:
        logger.error("Invalid or missing ID for GtfsAgency: %r", network_id)
        return None
    
    # Extract ID value and agency name
    network_id_value = network_id.split(":")[-1]
    agency_name = agency.get("agency_name", {}).get("value")

    # Build <Network> element with it's info
    network = etree.Element("Network", version="1", id=f"{config.NETEX_AUTHORITY}:Network:{network_id_value}Nett")

    etree.SubElement(network, "Name").text = agency_name

    etree.SubElement(network, "AuthorityRef", ref = f"{config.NETEX_AUTHORITY}:Authority:{network_id_value}_ID", version="1")

    return network

def netex_helper_stream_networks(xml_file, agency: dict[str, Any]) -> None:
    """
    Streams Network elements into XML.

    Args:
        xml_file: An instance of the XML file writer
        agencies: A list of GtfsAgency entities

    Returns:
        None
    """
    # Build <Network> element
    network = netex_helper_build_network(agency)

    # Return if unsuccessful
    if network is None:
        return

    # Stream the <Network> element into the XML file
    xml_file.write(network, pretty_print=True)

# -----------------------------------------------------
# GtfsShape to <ServiceLink>
# -----------------------------------------------------

Point = tuple[float, float]

wgs84_to_projected = Transformer.from_crs("EPSG:4326", "EPSG:7801", always_xy=True)
projected_to_wgs84 = Transformer.from_crs("EPSG:7801", "EPSG:4326", always_xy=True)

def netex_helper_transform_point_to_projected(point: Point) -> Point:
    """
    Transforms a point from WGS84 (EPSG:4326) to the projected CRS (EPSG:7801)

    Args:
        point (Point): A tuple representing the (longitude, latitude) coordinates of the point in WGS84 CRS

    Returns:
        Point: A tuple representing the (x, y) coordinates of the point in the projected CRS
    """
    return wgs84_to_projected.transform(*point)

def netex_helper_transform_line_string_to_wgs84(polyline_projected: LineString) -> LineString:
    """
    Transform a LineString from projected CRS (EPSG:7801) to WGS84 (EPSG:4326)
    
    Args:
        polyline_projected (LineString): LineString represented as a list of (x, y) coordinates in projected CRS

    Returns:
        LineString: LineString represented as a list of (x, y) coordinates in WGS84 CRS
    """
    # Extract x and y coordinates from the input LineString
    xs, ys = polyline_projected.xy

    # Transform the coordinates from projected CRS to WGS84
    tx, ty = projected_to_wgs84.transform(xs, ys)

    # Return a new LineString with the transformed coordinates
    return LineString(zip(tx, ty))

def netex_helper_extract_stops_in_a_trip(gtfs_stop_time_entities: list[dict[str, Any]]) -> dict[str, list[str]]:
    """
    For every trip, extract the ordered list of stops that comprise the trip based on the stop times information
    
    Args:
        stop_times (list[dict[str, Any]]): A list of GtfsStopTime entities

    Returns:
        dict[str, list[str]]: A dictionary mapping trip IDs to lists of stop IDs in order
    """
    
    # Create a lookup of all stops in a trip, ordered by their stop sequence
    stops_per_trip = {}
    
    # Traverse the retrieved stop times and populate the stops_per_trip dictionary
    for stop_time in gtfs_stop_time_entities:

        entity_type = stop_time["type"]
        if entity_type != "GtfsStopTime":
            logger.error("Unsupported entity type, expected GtfsStopTime: %s", entity_type)
            continue
        
        # Get trip id, stop id and sequence
        trip_id = stop_time.get("hasTrip", {}).get("object")
        stop_id = stop_time.get("hasStop", {}).get("object")
        sequence = stop_time.get("stopSequence", {}).get("value")

        if not isinstance(trip_id, str) or ":" not in trip_id:
            logger.error("Invalid or missing ID for GtfsTrip: %r", trip_id)
            continue

        trip_id_value = trip_id.split(":")[-1]

        if not isinstance(stop_id, str) or ":" not in stop_id:
            logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
            continue

        stop_id_value = stop_id.split(":")[-1]
        
        if not isinstance(sequence, int):
            logger.error("Invalid or missing stop sequence: %r", sequence)
            continue
                
        # If the trip ID is not already in the stops_per_trip dictionary, initialize it with an empty list
        if trip_id_value not in stops_per_trip:
            stops_per_trip[trip_id_value] = []
            
        # Append the stop ID and its sequence to the list of stops for the corresponding trip ID
        stops_per_trip[trip_id_value].append((stop_id_value, sequence))
            
    # After populating the stops_per_trip dictionary, sort the stops for each trip by their stop sequence
    for trip in stops_per_trip:
        stops_per_trip[trip].sort(key=lambda x: x[1])
        
        # Keep only the stop IDs
        stops_per_trip[trip] = [stop_id for stop_id, seq in stops_per_trip[trip]]  # Keep only stop IDs
            
    # Return the lookup of stops per trip
    return stops_per_trip

def netex_helper_extract_stop_coordinates(gtfs_stop_entities: list[dict[str, Any]]) -> dict[str, Point]:
    """
    For every stop, extract its coordinates and transform them to the projected CRS (EPSG:7801).
    
    Args:
        stops (list[dict[str, Any]]): A list of stop dictionaries

    Returns:
        dict[str, Point]: A dictionary mapping stop IDs to their projected coordinates.
    """
    # Create a lookup of stop ID to its projected coordinates
    stop_coordinates_projected = {}

    # Traverse the retrieved stops and populate the stop_coordinates_projected dictionary
    for stop in gtfs_stop_entities:
        
        entity_type = stop["type"]
        if entity_type != "GtfsStop":
            logger.error("Unsupported entity type, expected GtfsStop: %s", entity_type)
            continue
        
        stop_id = stop["id"]
        if not isinstance(stop_id, str) or ":" not in stop_id:
            logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
            continue

        stop_id_value = stop_id.split(":")[-1]

        # Get stop coordinates
        coordinates = stop.get("location", {}).get("value", {}).get("coordinates")

        # Only consider stops that have valid stop ID and coordinates
        if not coordinates or len(coordinates) != 2:
            logger.error("Missing or invalid coordinates for GtfsStop %s", stop_id)
            continue
        
        longitude, latitude = coordinates

        # Transform the stop coordinates from WGS84 to the projected CRS (EPSG:7801)
        projected_point = netex_helper_transform_point_to_projected((float(longitude), float(latitude)))

        # Populate the stop_coordinates_projected dictionary with the stop ID and its projected coordinates
        stop_coordinates_projected[stop_id_value] = projected_point

    # Return the lookup of stop IDs to their projected coordinates
    return stop_coordinates_projected

def netex_helper_extract_shape_linestrings(gtfs_shapes: list[dict[str, Any]]) -> dict[str, LineString]:
    """
    For every shape, extract its LineString geometry as a list of (x, y) coordinates in the projected CRS (EPSG:7801).
    
    Args:
        shapes (list[dict[str, Any]]): A list of shape dictionaries

    Returns:
        dict[str, LineString]: A dictionary mapping shape IDs to their projected line strings.
    """
    
    # Create a lookup of shape ID to its LineString geometry in projected CRS
    shape_geometries = {}

    # Traverse the retrieved shapes and populate the shape_line_strings dictionary
    for shape in gtfs_shapes:
        
        entity_type = shape["type"]
        if entity_type != "GtfsShape":
            logger.error("Unsupported entity type, expected GtfsShape: %s", entity_type)
            continue

        # Get shape ID
        shape_id = shape["id"]
        if not isinstance(shape_id, str) or ":" not in shape_id:
            logger.error("Invalid or missing ID for GtfsShape: %r", shape_id)
            continue
        shape_id_value = shape_id.split(":")[-1]

        # Get shape points
        points = shape.get("location", {}).get("value", {}).get("coordinates", [])
        if not isinstance(points, list):
            logger.error("Missing or invalid coordinates for shape %s", shape_id)
            continue
        
        # Check that at least 2 points are present
        if (not isinstance(points, list) or len(points) < 2):
            logger.error("Invalid or insufficient coordinates for shape %s", shape_id)
            continue
        
        # Keep only valid points
        valid_points = [
            point
            for point in points
            if isinstance(point, (list, tuple))
            and len(point) == 2
        ]

        if len(valid_points) < 2:
            logger.error("Shape %s contains fewer than 2 valid points", shape_id)
            continue

        try:
            # Vectorized coordinate transformation
            lons, lats = zip(*valid_points)

            xs, ys = wgs84_to_projected.transform(lons, lats)

            # Create geometry once
            shape_geometries[shape_id_value] = LineString(zip(xs, ys))

        except (TypeError, ValueError) as exc:
            logger.error("Failed to transform shape %s: %s", shape_id, exc)

    return shape_geometries

def netex_helper_map_trips_to_shapes(gtfs_trips: list[dict[str, Any]]) -> dict[str, str]:
    """
    For every trip, extract the associated shape ID
    
    Args:
        trips (list[dict[str, Any]]): A list of trip dictionaries

    Returns:
        dict[str, str]: A dictionary mapping trip IDs to their associated shape IDs.
    """
    # Create a dictionary that assiciates a trip ID with it's shape ID
    shapes_per_trip = {}

    # Traverse the retrieved trips and populate the shapes_per_trip dictionary
    for trip in gtfs_trips:
        
        entity_type = trip["type"]
        if entity_type != "GtfsTrip":
            logger.error("Unsupported entity type, expected GtfsTrip: %s", entity_type)
            continue
        
        # Get trip ID
        trip_id = trip["id"]
        if not isinstance(trip_id, str) or ":" not in trip_id:
            logger.error("Invalid or missing ID for GtfsTrip: %r", trip_id)
            continue
        trip_id_value = trip_id.split(":")[-1]
        
        # Get shape ID
        shape_id = trip.get("hasShape", {}).get("object")
        if not isinstance(shape_id, str) or ":" not in shape_id:
            logger.error("Invalid or missing ID for GtfsShape: %r", shape_id)
            continue
        shape_id_value = shape_id.split(":")[-1]
            
        # Populate the shapes_per_trip dictionary with the trip ID and its associated shape ID
        shapes_per_trip[trip_id_value] = shape_id_value

    # Return the dictionary
    return shapes_per_trip

def netex_helper_split_stops_into_pairs(stops_per_trip: dict[str, list[str]]) -> dict[str, list[tuple[str, str]]]:
    """
    For every trip, split the ordered list of stops into pairs of consecutive stops to represent the segments between them.
    
    Args:
        stops_per_trip (dict[str, list[str]]): A dictionary mapping trip IDs to lists of stop IDs in order

    Returns:
        dict[str, list[tuple[str, str]]]: A dictionary mapping trip IDs to lists of stop pairs representing the segments between them.
    """
    # Create a dictionary to store the stop pairs for each trip
    stop_pairs_in_a_trip = {}

    # Traverse each trip and split its ordered list of stops into pairs of consecutive stops
    for trip, stops in stops_per_trip.items():

        # Create a list to store the stop pairs for the current trip
        pairs = []

        # Iterate through the list of stops and create pairs of consecutive stops
        for i in range(len(stops)-1):
            pairs.append((stops[i], stops[i+1]))

        # Populate the trip_stop_pairs dictionary with the trip ID and its list of stop pairs
        stop_pairs_in_a_trip[trip] = pairs

    # Return the dictionary mapping trip IDs to their lists of stop pairs
    return stop_pairs_in_a_trip

def netex_helper_cut_shape_between_distances(shape_geometry: LineString, start_d: float, end_d: float) -> ShapelyPoint | LineString:
    """
    Cuts a LineString shape between two distances (in meters) along the shape.

    Args:
        shape_geometry (LineString): Precomputed LineString geometry in projected CRS.
        start_d (float): Starting distance along the shape in meters
        end_d (float): Ending distance along the shape in meters

    Returns:
        ShapelyPoint | LineString: The cut shape's geometry in projected CRS
    """
    
    # If the end distance is less than or equal to the start distance, return an empty list
    if end_d <= start_d:
        return LineString()

    # Return the segment of the shape's LineString geometry between the two distances
    return substring(shape_geometry, start_d, end_d)
 
def netex_helper_calculate_stop_distance_along_shape(stop_coordinates: Point, shape_geometry: LineString) -> float:
    """
    Calculate the distance along a shape for a stop coordinate.

    Args:
        stop_coordinates:
            Stop coordinates in projected CRS.

        shape_geometry:
            Precomputed LineString geometry.

    Returns:
        Distance along the shape in meters.
    """

    # Convert the stop coordinates to a Shapely Point
    point = ShapelyPoint(stop_coordinates)

    # Calculate and return the distance along the shape geometry for the stop coordinate
    return shape_geometry.project(point)

def netex_helper_map_stops_to_shape_distances(stop_ids: list[str], stop_coordinates: dict[str, Point], shape_geometry: LineString) -> dict[str, float]:
    """
    Calculate stop distances along a shape geometry.

    Args:
    stop_ids (list[str]): List of stop IDs to calculate distances for.

    stop_coordinates (dict[str, Point]): Dictionary mapping stop IDs to their coordinates in projected CRS.

    shape_geometry (LineString): Precomputed LineString geometry of the shape in projected CRS.

    Returns:
    Dictionary mapping stop IDs to their distance along the shape in meters.
    """

    # If the shape geometry is empty, log an error and return an empty dictionary
    if shape_geometry.is_empty:
        logger.error("Cannot calculate stop distances: shape is empty")
        return {}

    stop_distances: dict[str, float] = {}

    # If the list of stop IDs is empty, log an error and return an empty dictionary
    if not stop_ids:
        logger.error("Missing stop IDs")
        return {}

    for stop_id in stop_ids:

        # Get the coordinates for the current stop ID
        coordinates = stop_coordinates.get(stop_id)

        # If the coordinates are missing for the current stop ID, log an error and skip to the next stop ID
        if coordinates is None:
            logger.error("Missing coordinates for stop %s", stop_id)
            continue

        # Calculate the distance along the shape for the current stop and populate the stop_distances dictionary
        stop_distances[stop_id] = netex_helper_calculate_stop_distance_along_shape(coordinates, shape_geometry)

    return stop_distances
      
def netex_helper_for_every_trip_compute_stop_distances_along_shapes(
    stops_per_trip: dict[str, list[str]],
    stop_coordinates: dict[str, Point],
    shape_geometries: dict[str, LineString],
    shape_per_trip: dict[str, str],
) -> dict[str, dict[str, float]]:
    """
    Compute stop distances along shapes for every trip.

    Args:
        stops_per_trip (dict[str, list[str]]): A dictionary mapping trip IDs to lists of stop IDs in order.
        stop_coordinates (dict[str, Point]): A dictionary mapping stop IDs to their coordinates in projected CRS.
        shape_geometries (dict[str, LineString]): A dictionary mapping shape IDs to their geometries in projected CRS.
        shape_per_trip (dict[str, str]): A dictionary mapping trip IDs to shape IDs.

    Returns:
        A dictionary mapping trip IDs to dictionaries that map stop IDs to their distance along the shape in meters.
    """

    stop_projections_per_trip: dict[str, dict[str, float]] = {}

    # Validate that all required input data is present before processing
    if not stops_per_trip or not stop_coordinates or not shape_geometries or not shape_per_trip:
        logger.error("Missing required input data for computing stop distances along shapes")
        return {}

    # Go through each trip and it's stops
    for trip_id, stop_ids in stops_per_trip.items():

        # Get the shape ID for the current trip
        shape_id = shape_per_trip.get(trip_id)

        # If the shape ID is missing for the current trip, log an error and skip to the next trip
        if not shape_id:
            logger.error("Missing shape ID for trip %s", trip_id)
            continue

        # Get the shape geometry for the current trip's shape ID
        shape_geometry = shape_geometries.get(shape_id)

        # If the shape geometry is missing or empty for the current trip, log an error and skip to the next trip
        if shape_geometry is None or shape_geometry.is_empty:
            logger.error("Invalid shape geometry for trip %s", trip_id)
            continue

        # For every stop in the current trip, calculate its distance along the shape and populate the stop_projections_per_trip dictionary
        stop_projections_per_trip[trip_id] = netex_helper_map_stops_to_shape_distances(stop_ids, stop_coordinates, shape_geometry)

    return stop_projections_per_trip   

def netex_helper_create_line_string_segments_between_stop_pairs(
    stop_pair: tuple[str, str],
    stop_distances_along_shape: dict[str, float],
    shape_geometry: LineString,
) -> LineString | ShapelyPoint | None:
    """
    Build ServiceLink geometry between two stops.

    Args:
        stop_pair (tuple[str, str]): A tuple containing the IDs of the two stops.
        stop_distances_along_shape (dict[str, float]): A dictionary mapping stop IDs to their distance along the shape in meters.
        shape_geometry (LineString): The geometry of the shape in projected CRS.

    Returns:
        LineString | ShapelyPoint | None: The geometry segment between the two stops, which can be a LineString or a Point
    """
    
    # If stop_pair is not valid, log an error and return None
    if stop_pair is None or len(stop_pair) != 2:
        logger.error("Invalid stop pair: %r", stop_pair)
        return None

    # Unpack the stop pair into from_stop and to_stop
    from_stop, to_stop = stop_pair

    # If the stop distances along shape are missing, log an error and return None
    if not stop_distances_along_shape:
        logger.error("Missing stop distances along shape")
        return None

    # Get the distances along the shape for the from and to stops
    start_distance = stop_distances_along_shape[from_stop]
    end_distance = stop_distances_along_shape[to_stop]

    # If the shape geometry is empty, log an error and return None
    if shape_geometry.is_empty:
        logger.error("Cannot create line string segment: shape geometry is empty")
        return None
    
    # Return the segment of the shape geometry between the two stops
    return netex_helper_cut_shape_between_distances(shape_geometry, start_distance, end_distance)
    
def netex_helper_create_service_link_info(stops_per_trip: dict[str, list[str]], stop_coordinates: dict[str, Point],
                                          shape_geometries: dict[str, LineString], shape_per_trip: dict[str, str]):
    """
    Yield ServiceLink information objects.

    Args:
        stops_per_trip (dict[str, list[str]]): A dictionary mapping trip IDs to lists of stop IDs.
        stop_coordinates (dict[str, Point]): A dictionary mapping stop IDs to their coordinates.
        shape_geometries (dict[str, LineString]): A dictionary mapping shape IDs to their geometries.
        shape_per_trip (dict[str, str]): A dictionary mapping trip IDs to shape IDs.

    Returns:
        None
    """

    if not(stops_per_trip and stop_coordinates and shape_geometries and shape_per_trip):
        logger.error("Missing required input data")
        return
    
    stop_pairs_per_trip = netex_helper_split_stops_into_pairs(stops_per_trip)

    stop_projections_per_trip = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip
        )
    )

    for trip_id, stop_pairs in stop_pairs_per_trip.items():

        shape_id = shape_per_trip.get(trip_id)

        if not shape_id or shape_id not in shape_geometries:
            logger.error("Missing shape ID for trip %s", trip_id)
            continue

        shape_geometry = shape_geometries[shape_id]

        stop_distances = stop_projections_per_trip.get(trip_id)

        if shape_geometry is None or shape_geometry.is_empty or not stop_distances:
            logger.error("Missing or invalid shape geometry for trip %s", trip_id)
            continue

        for pair in stop_pairs:

            from_stop, to_stop = pair

            geometry = netex_helper_create_line_string_segments_between_stop_pairs(pair, stop_distances, shape_geometry)

            yield {
                "trip_id": trip_id,
                "shape_id": shape_id,
                "from_stop": from_stop,
                "to_stop": to_stop,
                "distance": (stop_distances[to_stop] - stop_distances[from_stop]),
                "geometry": geometry,
            }
    
def netex_helper_convert_line_string_to_string(line: LineString) -> str:
    """
    Convert LineString geometry to GML posList string.

    Args:
        line (LineString): The LineString geometry to convert.

    Returns:
        str: A string representation of the LineString in GML posList format
    """

    return " ".join(f"{x:.6f} {y:.6f}" for x, y in line.coords)

def netex_helper_build_service_link(service_link_data: dict[str, Any]) -> etree.Element:
    """
    Build a NeTEx <ServiceLink> element from the provided service link data.

    Args:
        service_link_data (dict[str, Any]): A dictionary containing the necessary information to build a <ServiceLink> element

    Returns:
        etree.Element: An lxml.etree.Element object representing the <ServiceLink> element
    """
    # Get geometry in projected CRS
    geometry_projected = service_link_data["geometry"]

    # Transform geometry to WGS84 and convert it to a GML posList string
    geometry_wgs84 = netex_helper_transform_line_string_to_wgs84(geometry_projected)

    # Convert the LineString geometry to a GML posList string
    pos_list = netex_helper_convert_line_string_to_string(geometry_wgs84)

    # Get distance and stop IDs for <ServiceLink> 
    distance = service_link_data["distance"]
    from_stop = service_link_data["from_stop"]
    to_stop = service_link_data["to_stop"]
    shape_id = service_link_data["shape_id"]

    # Build the <ServiceLink> element
    service_link = etree.Element(f"ServiceLink", id=f"{config.NETEX_AUTHORITY}:ServiceLink:{from_stop}_{to_stop}_{shape_id}", version="1")
    
    etree.SubElement(service_link, f"Distance").text = f"{distance:.6f}"

    projections = etree.SubElement(service_link, f"projections")
    link_seq = etree.SubElement(projections, f"LinkSequenceProjection",
                                id=f"{config.NETEX_AUTHORITY}:LinkSequenceProjection:{from_stop}_{to_stop}_{shape_id}", version="1")

    line_string = etree.SubElement(link_seq, f"{{{GIS_NS}}}LineString", srsName="4326", srsDimension="2")
    line_string.set(f"{{{GIS_NS}}}id", f"LS_{from_stop}_{to_stop}_{shape_id}")

    etree.SubElement(line_string, f"{{{GIS_NS}}}posList", count=str(len(geometry_wgs84.coords)), srsDimension="2").text = pos_list

    etree.SubElement(service_link, f"FromPointRef", ref=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{from_stop}", version="1")

    etree.SubElement(service_link, f"ToPointRef", ref=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{to_stop}", version="1")

    return service_link

def netex_stream_service_links(xml_file, service_links_data: list[dict]) -> None:
    """
    Stream <ServiceLink> elements into XML.
    Args:       
        xml_file: An instance of the XML file writer
        service_links_data: A list of dictionaries containing the necessary information to build <ServiceLink> elements

    Returns:
        None
        """
    logger.info("Streaming ServiceLinks")

    # Used to avoid duplicates
    seen = set()

    with xml_file.element("serviceLinks"):

        for data in service_links_data:

            # Create a unique key for the stop pair and distance to avoid duplicates
            key = (
                data["from_stop"],
                data["to_stop"],
                round(data["distance"], 6),
            )

            # If seen, skip
            if key in seen:
                continue

            # Add the key to the seen set
            seen.add(key)

            # Build the <ServiceLink> element
            service_link = netex_helper_build_service_link(data)

            # Stream <ServiceLink> into the XML file
            xml_file.write(service_link, pretty_print=True)

    logger.info("Finished streaming %d ServiceLinks", len(seen))

# --------------------------------------------
# Helper Functions for <OperatingPeriod> creation
# --------------------------------------------

def netex_helper_convert_yyyymmdd_date_to_iso_date(date_str: str) -> str:
    """
    Converts a date string from YYYYMMDD format to YYYY-MM-DDTHH:MM:SS format.

    Args:
        date_str: The date string in "YYYYMMDD" format.

    Returns:
        The date and time string in ISO 8601 format.
    """
    if not isinstance(date_str, str) or len(date_str) != 8:
        raise ValueError("Input must be a string in YYYYMMDD format.")
       
    # Parse the string into a datetime object
    date_obj = datetime.strptime(date_str, '%Y%m%d')
   
    # Format the object into an ISO string
    return date_obj.isoformat()

def netex_helper_day_type_get_active_days(entity: dict[str, Any]) -> str:
    """
    Determines a human-readable string for active days from a GtfsCalendarRule entity.

    This function processes a GtfsCalendarRule entity and identifies
    which days of the week are active. It returns special keywords for common
    combinations like "Everyday", "Weekdays", or "Weekend". Otherwise, it returns
    a space-separated string of the active day names.

    Args:
        entity: A GtfsCalendarRule entity

    Returns:
        A string representing the active days:
        - "Everyday" if all 7 days are active.
        - "Weekdays" if Monday to Friday are active.
        - "Weekend" if Saturday and Sunday are active.
        - A space-separated list of day names (e.g., "Monday Wednesday") for other combinations.
        - An empty string if no days are active or the entity is malformed.
    """
    # Map lowercase day keys to their proper capitalized names.
    days_map = {
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday"
    }

    # Build a list of active day names from the entity.
    active_days = [name for key, name in days_map.items() if entity.get(key, {}).get("value") == 1]

    # Everyday
    if len(active_days) == 7:
        return "Everyday"

    # Weekdays
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if set(active_days) == set(weekdays):
        return "Weekdays"

    # Weekend
    weekends = ["Saturday", "Sunday"]
    if set(active_days) == set(weekends):
        return "Weekend"

    # Specific days
    return " ".join(active_days)

# -------------------------------------------------------------
# GtfsCalendarRule and GtfsCalendarDateRule to NeTEx <DayType>
# -------------------------------------------------------------

def netex_helper_build_day_type(entity: dict[str, Any]) -> etree.Element | None:
    """
    Builds a single NeTEx <DayType> element from either:
    - GtfsCalendarRule
    - GtfsCalendarDateRule

    Args:
        entity: A GtfsCalendarRule or GtfsCalendarDateRule entity

    Returns:
        etree.Element | None
    """

    # Get entity type and ID
    entity_type = entity.get("type")
    day_type_id = entity.get("id")

    # If not present, return None
    if not entity_type or not day_type_id:
        return None

    # If not in the correct format, log an error and return None
    if not isinstance(day_type_id, str) or ":" not in day_type_id:
        logger.error("Invalid ID for %s: %r", entity_type, day_type_id)
        return None

    # ----------------------------------------
    # GtfsCalendarRule
    # ----------------------------------------
    if entity_type == "GtfsCalendarRule":

        # Extract value fron NGSI-LD URN
        day_type_id_value = day_type_id.split(":")[-1]

        # Build DayType element with the extracted ID value and it's properties
        day_type = etree.Element("DayType", version="1", id= f"{config.NETEX_AUTHORITY}:DayType:{day_type_id_value}")

        properties = etree.SubElement(day_type, "properties")

        property_of_day = etree.SubElement(properties, "PropertyOfDay")

        etree.SubElement(property_of_day,"DaysOfWeek").text = netex_helper_day_type_get_active_days(entity)

        return day_type

    # ----------------------------------------
    # GtfsCalendarDateRule
    # ----------------------------------------
    elif entity_type == "GtfsCalendarDateRule":

        day_type_id_value = day_type_id.split(":")[-2]

        # Build DayType element with the extracted ID value
        day_type = etree.Element("DayType", version="1", id=f"{config.NETEX_AUTHORITY}:DayType:{day_type_id_value}")

        return day_type

    # If the entity type is not supported, log an error and return None
    logger.error("Unsupported entity type: %s", entity_type)

    return None

def netex_helper_stream_day_types(xml_file, entities: list[dict[str, Any]]) -> None:
    """
    Streams NeTEx <DayType> elements into a <dayTypes> container.

    Args:
        xml_file: An instance of a streaming XML writer
        entities: A list of GtfsCalendarRule and GtfsCalendarDateRule entities

    Returns:
        None (the function writes directly to the provided xml_file)
    """

    logger.info("Streaming DayTypes")

    seen_ids = set()

    # Create container for <DayType> elements
    with xml_file.element("dayTypes"):

        for entity in entities:

            # Create <DayType> elements
            day_type = netex_helper_build_day_type(entity)

            # Continue when unsuccessful
            if day_type is None:
                continue

            # Get <DayType> element's ID
            day_type_id = day_type.get("id")

            # If encountered already, skip
            if day_type_id in seen_ids:
                continue

            # Add ID to seen IDs set
            seen_ids.add(day_type_id)

            # Stream the <DayType> element into the XML file
            xml_file.write(day_type, pretty_print=True)

    logger.info("Finished streaming %d DayTypes", len(seen_ids))

# --------------------------------------------
# GtfsCalendarRule to NeTEx <OperatingPeriod>
# --------------------------------------------

def netex_helper_build_operating_period(entity: dict[str, Any]) -> etree.Element | None:
    """
    Builds a NeTEx <OperatingPeriod> element from a GtfsCalendarRule entity.

    Args:
        entity: A GtfsCalendarRule entity

    Returns:
        etree.Element | None
    """
    # Throw an error and return None if the entity is not a GtfsCalendarRule
    if entity.get("type") != "GtfsCalendarRule":
        logger.error("Unsupported entity type for OperatingPeriod: %s", entity.get("type"))
        return None

    # Get and validate ID
    period_id = entity.get("id")

    if not isinstance(period_id, str) or ":" not in period_id:
        logger.error("Invalid ID for GtfsCalendarRule: %r", period_id)
        return None

    # Extract value from NGSI-LD URN
    period_id_value = period_id.split(":")[-1]

    # Get and convert start and end dates to ISO format
    from_date = entity.get("startDate", {}).get("value")
    from_date_iso = netex_helper_convert_yyyymmdd_date_to_iso_date(from_date)

    to_date = entity.get("endDate", {}).get("value")
    to_date_iso = netex_helper_convert_yyyymmdd_date_to_iso_date(to_date)

    # Build and return the <OperatingPeriod> element with the extracted ID value and date properties
    operating_period = etree.Element("OperatingPeriod", version = "1", id=f"{config.NETEX_AUTHORITY}:OperatingPeriod:{period_id_value}")

    etree.SubElement(operating_period, "FromDate").text = from_date_iso
    etree.SubElement(operating_period, "ToDate").text = to_date_iso

    return operating_period

def netex_helper_stream_operating_periods(xml_file, entities: list[dict[str, Any]]) -> None:
    """
    Streams NeTEx <OperatingPeriod> elements into an <operatingPeriods> container.

    Args:
        xml_file: An instance of a streaming XML writer
        entities: A list of GtfsCalendarRule entities

    Returns:
        None (the function writes directly to the provided xml_file)
    """
    logger.info("Streaming OperatingPeriods")

    seen_ids = set()

    # Create container for <OperatingPeriod> elements
    with xml_file.element("operatingPeriods"):

        for entity in entities:

            # Build <OperatingPeriod> element
            operating_period = netex_helper_build_operating_period(entity)

            # Continue when unsuccessful
            if operating_period is None:
                continue

            # Get <OperatingPeriod> element's ID
            period_id = operating_period.get("id")

            # If encountered already, skip
            if period_id in seen_ids:
                continue

            # Add ID to seen IDs set
            seen_ids.add(period_id)

            # Stream the <OperatingPeriod> element into the XML file
            xml_file.write(operating_period, pretty_print=True)

    logger.info("Finished streaming %d OperatingPeriods", len(seen_ids))

# -----------------------------------------------------------------------
# GtfsCalendarRule and GtfsCalendarDateRule to NeTEx <DayTypeAssignment>
# -----------------------------------------------------------------------

def netex_helper_build_day_type_assignment(entity: dict[str, Any], index: int) -> etree.Element | None:
    """
    Builds a NeTEx <DayTypeAssignment> element from either a GtfsCalendarRule or GtfsCalendarDateRule entity.

    Args:
        entity: A GtfsCalendarRule or GtfsCalendarDateRule entity
        index: The index of the entity in the original list (used for ordering and ID generation)

    Returns:
        etree.Element | None
    """
    # Get entity type and ID
    entity_type = entity.get("type")
    day_type_assignment_id = entity.get("id")

    # If not present, return None
    if not entity_type or not day_type_assignment_id:
        return None

    # If not in the correct format, log an error and return None
    if not isinstance(day_type_assignment_id, str) or ":" not in day_type_assignment_id:
        logger.error("Invalid ID for %s: %r", entity_type, day_type_assignment_id)
        return None

    # ----------------------------------------
    # GtfsCalendarDateRule
    # ----------------------------------------
    if entity_type == "GtfsCalendarDateRule":

        parts = day_type_assignment_id.split(":")

        day_type_id_value = parts[-2]
        raw_date = parts[-1]

        # Determine availability based on the exception type (1 for added service, 2 for removed service)
        exception_type = entity.get("exceptionType", {}).get("value")
        is_available = exception_type == 1
        is_available_value = "true" if is_available else "false"

        # Build DayTypeAssignment element with the extracted ID value, date, day type reference and availability
        day_type_assignment = etree.Element("DayTypeAssignment", order = str(index), version = "1", id = f"{config.NETEX_AUTHORITY}:DayTypeAssignment:{day_type_id_value}_{index}")

        etree.SubElement(day_type_assignment, "Date").text = datetime.strptime(raw_date, "%Y%m%d").strftime("%Y-%m-%d")

        etree.SubElement(day_type_assignment, "DayTypeRef", version = "1", ref = f"{config.NETEX_AUTHORITY}:DayType:{day_type_id_value}")

        etree.SubElement(day_type_assignment, "IsAvailable").text = is_available_value

        return day_type_assignment

    # ----------------------------------------
    # GtfsCalendarRule
    # ----------------------------------------
    elif entity_type == "GtfsCalendarRule":

        day_type_id_value = day_type_assignment_id.split(":")[-1]

        # Build DayTypeAssignment element with the extracted ID value, operating period reference and day type reference
        day_type_assignment = etree.Element("DayTypeAssignment", order=str(index), version="1", id=f"{config.NETEX_AUTHORITY}:DayTypeAssignment:{day_type_id_value}_{index}")

        etree.SubElement(day_type_assignment, "OperatingPeriodRef", version = "1", ref = f"{config.NETEX_AUTHORITY}:OperatingPeriod:{day_type_id_value}")

        etree.SubElement(day_type_assignment, "DayTypeRef", version = "1", ref = f"{config.NETEX_AUTHORITY}:DayType:{day_type_id_value}_{index}")

        return day_type_assignment
    
    logger.error("Unsupported entity type: %s, id: %s", entity_type, day_type_assignment_id)
    return None

def netex_helper_stream_day_type_assignments(xml_file, entities: list[dict[str, Any]]) -> None:
    """
    Streams NeTEx <DayTypeAssignment> elements into a <dayTypeAssignments> container.

    Args:
        xml_file: An instance of a streaming XML writer
        entities: A list of GtfsCalendarRule and GtfsCalendarDateRule entities

    Returns:
        None (the function writes directly to the provided xml_file)
    """
    logger.info("Streaming DayTypeAssignments")

    written_count = 0
    # Create container for <DayTypeAssignment> elements
    with xml_file.element("dayTypeAssignments"):

        for index, entity in enumerate(entities, start=1):

            # Build <DayTypeAssignment> element
            day_type_assignment = netex_helper_build_day_type_assignment(entity, index)

            # Continue when unsuccessful
            if day_type_assignment is None:
                continue

            # Stream the <DayTypeAssignment> element into the XML file
            xml_file.write(day_type_assignment, pretty_print=True)
            written_count += 1

    logger.info("Finished streaming %d DayTypeAssignments", written_count)

# ----------------------------------------------------------------------------------------------
# NeTEx <ServiceCalendarFrame> containing <DayType>, <OperatingPeriod> and <DayTypeAssignment>
# ----------------------------------------------------------------------------------------------

def netex_stream_service_calendar_frame_for_shared_data_xml(xml_file, calendars, calendar_dates) -> None:
    """
    Streams a NeTEx <ServiceCalendarFrame> element containing <DayType>, <OperatingPeriod> and <DayTypeAssignment> elements.
    Args:
        xml_file: An instance of a streaming XML writer
        calendars: A list of GtfsCalendarRule entities
        calendar_dates: A list of GtfsCalendarDateRule entities
        
    Returns:
        None (the function writes directly to the provided xml_file)
    """
    # Combine calendar and calendar date entities for processing
    all_entities = calendars + calendar_dates

    # Stream the <ServiceCalendarFrame> element with its child elements
    with xml_file.element("ServiceCalendarFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ServiceCalendarFrame:{uuid.uuid4()}"):

        netex_helper_stream_day_types(xml_file, all_entities)

        netex_helper_stream_operating_periods(xml_file, calendars)

        netex_helper_stream_day_type_assignments(xml_file, all_entities)

# -----------------------------------------------------------------------
# GtfsRoute to NeTEx <Line>
# -----------------------------------------------------------------------

def netex_helper_get_transport_mode_and_submode(gtfs_route_type_code: int) -> tuple[str, str] | tuple[None, None]:
    """
    Retrieves the NeTEx transport mode and submode based on the GTFS route type code.

    Args:
        gtfs_route_type_code: The GTFS route type code.

    Returns:
        A tuple containing the NeTEx transport mode and submode, or (None, None) if not found.
    """
    gtfs_to_netex_map = {
        0: ('tram', 'cityTram'),
        1: ('metro', 'metro'),
        2: ('rail', 'local'),
        3: ('bus', 'localBus'),
        4: ('water', 'localPassengerFerry'),
        5: ('cableway', 'telecabin'),
        6: ('cableway', 'telecabin'),
        7: ('funicular', 'telecabin'),
        11: ('bus', 'localBus'),
        12: ('rail', 'local'),
        100: ('rail', 'local'),
        101: ('rail', 'airportLinkRail'),
        102: ('rail', 'longDistance'),
        103: ('rail', 'interregionalRail'),
        105: ('rail', 'nightRail'),
        106: ('rail', 'regionalRail'),
        107: ('rail', 'touristRailway'),
        108: ('rail', 'airportLinkRail'),
        109: ('rail', 'regionalRail'),
        200: ('coach', 'nationalCoach'),
        201: ('coach', 'internationalCoach'),
        202: ('coach', 'nationalCoach'),
        204: ('coach', 'touristCoach'),
        400: ('metro', 'urbanRailway'),
        401: ('metro', 'metro'),
        402: ('metro', 'metro'),
        403: ('metro', 'urbanRailway'),
        405: ('metro', 'urbanRailway'),
        700: ('bus', 'unknown'),
        701: ('bus', 'regionalBus'),
        702: ('bus', 'expressBus'),
        704: ('bus', 'localBus'),
        715: ('bus', 'unknown'),
        800: ('bus', 'unknown'), # (renamed to bus as otp has problems) not in the official documentation but found here https://github.com/entur/netex-gtfs-converter-java
        900: ('tram', 'unknown'),
        1000: ('water', 'unknown'),
        1200: ('water', 'unknown'),
        1300: ('cableway', 'unknown'),
        1301: ('cableway', 'telecabin'),
        1400: ('funicular', 'funicular'),
        1501: ('taxi', 'communalTaxi'),
        1700: ('other', 'unknown'), # not in the official documentation but found here https://github.com/entur/netex-gtfs-converter-java
        1702: ('other', 'unknown'), # not in the official documentation but found here https://github.com/entur/netex-gtfs-converter-java
    }
    return gtfs_to_netex_map.get(gtfs_route_type_code, (None, None))

def netex_helper_build_line(route: dict[str, Any]) -> etree.Element | None:
    """
    Build a single NeTEx Line element from a GtfsRoute entity.
    
    Args:
        route: A GtfsRoute entity

    Returns:
        etree.Element | None
    """
    # Get entity id and type
    route_id = route.get("id")
    entity_type = route.get("type")
    
    # If unsupported entity type, log an error and return None
    if entity_type != "GtfsRoute":
        logger.error("Unsupported entity type for Line conversion: %s", entity_type)
        return None
    
    # If not correctly formatted, log an error and return None
    if not isinstance(route_id, str) or ":" not in route_id:
        logger.error("Invalid or missing ID for GtfsRoute: %r", route_id)
        return None

    # Extract ID Value
    route_id_value = route_id.split(":")[-1]

    # Build Line XML
    line = etree.Element("Line", version="1", id = f"{config.NETEX_AUTHORITY}:Line:{route_id_value}")

    route_long_name = route.get("name", {}).get("value")
    if route_long_name:
        etree.SubElement(line, "Name").text = route_long_name

    route_description = route.get("description", {}).get("value")
    if route_description:
        etree.SubElement(line, "Description").text = route_description

    route_type = route.get("routeType", {}).get("value")

    transport_mode, transport_submode = netex_helper_get_transport_mode_and_submode(route_type)

    etree.SubElement(line, "TransportMode").text = transport_mode

    submode_tag_map = {
        "rail": "RailSubmode",
        "coach": "CoachSubmode",
        "metro": "MetroSubmode",
        "bus": "BusSubmode",
        # "trolleyBus": "TrolleyBusSubmode",
        "tram": "TramSubmode",
        "water": "WaterSubmode",
        "cableway": "TelecabinSubmode",
        "funicular": "FunicularSubmode",
        "taxi": "TaxiSubMode",
        "other": "OtherSubMode",
    }

    if transport_mode is None or transport_submode is None:
        raise ValueError(
            f"Invalid or unknown transport mode and submode: {route_type}"
        )

    if transport_mode != "trolleyBus":
        submode_tag = submode_tag_map.get(transport_mode)

        transport_submode_element = etree.SubElement(line, "TransportSubmode")

        etree.SubElement(transport_submode_element, submode_tag).text = transport_submode

    route_url = route.get("route_url", {}).get("value")

    if route_url:
        etree.SubElement(line, "Url").text = route_url

    route_short_name = route.get("shortName", {}).get("value")

    if route_short_name:
        etree.SubElement(line, "PublicCode").text = route_short_name

    agency_id = route.get("operatedBy", {}).get("object")

    if agency_id:
        agency_id_value = agency_id.split(":")[-1]

        etree.SubElement(line, "OperatorRef", ref = f"{config.NETEX_AUTHORITY}:Operator:{agency_id_value}")

        etree.SubElement(line,"RepresentedByGroupRef",
                         ref = f"{config.NETEX_AUTHORITY}:Network:{agency_id_value}Nett")

    route_colour = route.get("routeColor", {}).get("value")
    route_text_colour = route.get("routeTextColor", {}).get("value")

    if route_colour or route_text_colour:

        presentation = etree.SubElement(line, "Presentation")

        if route_colour:
            etree.SubElement(presentation, "Colour").text = route_colour

        if route_text_colour:
            etree.SubElement(presentation, "TextColour").text = route_text_colour

    return line

def netex_helper_stream_line(xml_file, route: dict[str, Any]) -> None:
    """
    Stream NeTEx <Line> entity into a <lines> container
    Args:
        xml_file: An instance of a streaming XML writer
        route (dict[str, Any]): A GtfsRoute entity
    """
        
    global LINE_COUNTER
    
    line = netex_helper_build_line(route)
    
    if line is not None:
        with xml_file.element("lines"):
            xml_file.write(line, pretty_print=True)      
            LINE_COUNTER += 1
                
# -----------------------------------------------------
# GtfsRoute to NeTEx <DestinationDisplay>
# ----------------------------------------------------- 
def netex_helper_build_destionation_display(stop: dict[str, Any]) -> etree.Element | None:
    """
    Build a single <DestinationDisplay> element from a GtfsRoute entity

    Args:
        route (dict[str, Any]): A GtfsRoute entity

    Returns:
        etree.Element | None
    """
    # Get entity id and type
    route_id = stop.get("id")
    entity_type = stop.get("type")
    
    # If unsupported entity type, log an error and return None
    if entity_type != "GtfsStop":
        logger.error("Unsupported entity type for DestinationDisplay conversion: %s", entity_type)
        return None
    
    # If not correctly formatted, log an error and return None
    if not isinstance(route_id, str) or ":" not in route_id:
        logger.error("Invalid or missing ID for GtfsStop: %r", route_id)
        return None

    # Extract ID Value
    stop_id_value = route_id.split(":")[-1]
    
    # Bild <DestinationDisplay> element
    stop_name = stop.get("name", {}).get("value")
    
    destination_display = etree.Element("DestinationDisplay", version="1", id=f"{config.NETEX_AUTHORITY}:DestinationDisplay:{stop_id_value}")
    etree.SubElement(destination_display, "Name").text = stop_name
    etree.SubElement(destination_display, "SideText").text = stop_name
    etree.SubElement(destination_display, "FrontText").text = stop_name
    
    return destination_display

def netex_helper_stream_destination_displays(xml_file, gtfs_stops):
    """
    Streams DestinationDisplay elements into a <destinationDisplays> container.

    Args:
        xml_file: Streaming XML writer
        gtfs_stops: List of GtfsStop entities

    Returns:
        None
    """
    logger.info("Streaming DestinationDisplays")

    seen_ids = set()

    # Create container for <DestinationDisplay> elements
    with xml_file.element("destinationDisplays"):

        for stop in gtfs_stops:

            # Build <DestinationDisplay> element
            destination_display = netex_helper_build_destionation_display(stop)

            # Continue when unsuccessful
            if destination_display is None:
                continue

            # Get <DestinationDisplay> element's ID
            destination_display_id = destination_display.get("id")

            # If encountered already, skip
            if destination_display_id in seen_ids:
                continue

            # Add ID to seen IDs set
            seen_ids.add(destination_display_id)

            # Stream the <ScheduledStopPoint> element into the XML file
            xml_file.write(destination_display,pretty_print=True)

    logger.info("Finished streaming %d DestinationDisplays", len(seen_ids))

# -----------------------------------------------------
# GtfsStop to NeTEx <ScheduledStopPoint>
# ----------------------------------------------------- 

def netex_helper_build_scheduled_stop_point(gtfs_stop: dict[str, Any]) -> etree.Element | None:
    """
    Builds a NeTEx <ScheduledStopPoint> element from a GtfsStop entity.

    Args:
        gtfs_stop: A single GtfsStop entity

    Returns:
        etree.Element | None
    """

    # Get entity type and ID
    entity_type = gtfs_stop.get("type")
    stop_id = gtfs_stop.get("id")

    # If unsupported entity type, log an error and return None
    if entity_type != "GtfsStop":
        logger.error("Unsupported entity type: %s", entity_type)
        return None

    # If not correctly formatted, log an error and return None
    if not isinstance(stop_id, str) or ":" not in stop_id:
        logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
        return None

    stop_id_value = stop_id.split(":")[-1]

    # Extract stop name if available
    stop_name = gtfs_stop.get("name", {}).get("value")

    # Build and return the <ScheduledStopPoint> element with the extracted ID value, name and location reference
    scheduled_stop_point = etree.Element("ScheduledStopPoint", version="1", 
                                         id=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{stop_id_value}")

    if stop_name:
        etree.SubElement(scheduled_stop_point,"Name").text = stop_name

    return scheduled_stop_point

def netex_helper_stream_scheduled_stop_points(xml_file, gtfs_stops: list[dict[str, Any]]) -> None:
    """
    Streams ScheduledStopPoint elements into a <scheduledStopPoints> container.

    Args:
        xml_file: Streaming XML writer
        entities: List of GtfsStop entities

    Returns:
        None
    """

    logger.info("Streaming ScheduledStopPoints")

    seen_ids = set()

    # Create container for <ScheduledStopPoint> elements
    with xml_file.element("scheduledStopPoints"):

        for gtfs_stop in gtfs_stops:

            # Build <ScheduledStopPoint> element
            scheduled_stop_point = netex_helper_build_scheduled_stop_point(gtfs_stop)

            # Continue when unsuccessful
            if scheduled_stop_point is None:
                continue

            # Get <ScheduledStopPoint> element's ID
            scheduled_stop_point_id = scheduled_stop_point.get("id")

            # If encountered already, skip
            if scheduled_stop_point_id in seen_ids:
                continue

            # Add ID to seen IDs set
            seen_ids.add(scheduled_stop_point_id)

            # Stream the <ScheduledStopPoint> element into the XML file
            xml_file.write(scheduled_stop_point,pretty_print=True)

    logger.info("Finished streaming %d ScheduledStopPoints", len(seen_ids))

# -----------------------------------------------------
# GtfsStop to NeTEx <StopPlace>
# -----------------------------------------------------
def netex_helper_get_transport_modes_per_stop(authority_dataset: dict[str, Any]) -> dict[str, set[tuple[str, str]]]:
    """
    Create a lookup for each stop how it is categorized in terms of transport mode based on
    the routes that go through them

    Args:
        authority_dataset (dict[str, Any]): Authority dataset which containes the needed data
                                            for lookup creation

    Returns:
        dict[str, set]: Lookup displaying how each stop is categorized in terms of transport mode
    """
    transport_modes_per_stop = {}

    route_modes_and_submodes = {}

    for route in authority_dataset["routes"]:
        route_id = route["id"]
        route_type = route.get("routeType", {}).get("value")

        route_modes_and_submodes[route_id] = netex_helper_get_transport_mode_and_submode(route_type)

    trip_to_route = {}

    for trip in authority_dataset["trips"]:
        trip_id = trip["id"]
        route_id = trip["route"]["object"]

        trip_to_route[trip_id] = route_id

    for stop_time in authority_dataset["stop_times"]:

        trip_id = stop_time["hasTrip"]["object"]
        stop_id = stop_time["hasStop"]["object"]

        route_id = trip_to_route.get(trip_id)
        if route_id is None:
            continue

        mode_and_submode = route_modes_and_submodes.get(route_id)
        if mode_and_submode is None:
            continue

        transport_modes_per_stop.setdefault(stop_id, set()).add(mode_and_submode)

    return transport_modes_per_stop

def netex_helper_build_stop_place(gtfs_stop_entity: dict[str, Any], transport_modes_per_stop: dict[str, set[tuple[str, str]]]) -> etree.Element | None:

    # Get entity type and ID
    stop_id = gtfs_stop_entity["id"]
    entity_type = gtfs_stop_entity["type"]
    
    if entity_type != "GtfsStop":
        logger.error("Unsupported entity type for StopPlace conversion: %s", entity_type)
        return None

    # If not correctly formatted, log an error and return None    
    if not isinstance(stop_id, str) or ":" not in stop_id:
        logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
        return None
    
    stop_id_value = stop_id.split(":")[-1]
    
    # Create StopPlace element
    stop_place = etree.Element("StopPlace", version = "1", id = f"{config.NETEX_AUTHORITY}:StopPlace:{stop_id_value}")

    # Extract  name, code, description and coordinates
    name_value = gtfs_stop_entity.get("name", {}).get("value")
    stop_code_value = gtfs_stop_entity.get("code", {}).get("value")
    description_value = gtfs_stop_entity.get("description", {}).get("value")
    coords = gtfs_stop_entity.get("location", {}).get("value", {}).get("coordinates")

    # Add Name, Description, PublicCode and Centroid elements if values are present
    if name_value:
        etree.SubElement(stop_place, "Name").text = name_value

    if description_value:
        etree.SubElement(stop_place, "Description").text = description_value

    if stop_code_value:
        etree.SubElement(stop_place, "PublicCode").text = str(stop_code_value)

    # if coords:
    #     centroid = etree.SubElement(stop_place, "Centroid")
    #     location = etree.SubElement(centroid, "Location")
    #     etree.SubElement(location, "Longitude").text = str(coords[0])
    #     etree.SubElement(location, "Latitude").text = str(coords[1])

    # Extract wheelchair boarding and tts_stop_name for accessibility information
    wheelchair = gtfs_stop_entity.get("wheelchair_boarding", {}).get("value")
    tts_stop_name = gtfs_stop_entity.get("tts_stop_name", {}).get("value")

    # Add AccessibilityAssessment and AccessibilityLimitation elements if wheelchair boarding information is present
    if wheelchair:
        accessibility_assessment = etree.SubElement(stop_place, "AccessibilityAssessment", version = "1", id = f"{config.NETEX_AUTHORITY}:AccessibilityAssessment:{uuid.uuid4()}")
        etree.SubElement(accessibility_assessment, "MobilityImpairedAccess").text = "partial"
        limitations = etree.SubElement(accessibility_assessment, "limitations")
        accessibility_limitation = etree.SubElement(limitations, "AccessibilityLimitation", version = "1", id = f"{uuid.uuid4()}")
        etree.SubElement(accessibility_limitation, "WheelchairAccess").text = "true"
        etree.SubElement(accessibility_limitation, "StepFreeAccess").text = "unknown"
        etree.SubElement(accessibility_limitation, "EscalatorFreeAccess").text = "unknown"
        etree.SubElement(accessibility_limitation, "LiftFreeAccess").text = "unknown"
        
        # If tts_stop_name is present, we can assume that audible signs are available, otherwise we set it to unknown
        if tts_stop_name:
            etree.SubElement(accessibility_limitation, "AudibleSignalsAvailable").text = "true"
        else:
            etree.SubElement(accessibility_limitation, "AudibleSignsAvailable").text = "unknown"
        etree.SubElement(accessibility_limitation, "VisualSignsAvailable").text = "unknown"

    # Extract parent station information and add ParentSiteRef element if present
    parent_station = gtfs_stop_entity.get("hasParentStation", {}).get("object")
    
    if parent_station:
        parent_station_value = parent_station.split(":")[-1]
        etree.SubElement(stop_place, "ParentSiteRef", ref = f"{config.NETEX_AUTHORITY}:StopPlace:{parent_station_value}", version = "1")

    # Determine transport mode and submode for the stop based on the routes that pass through it
    transport_mode = "unknown"
    transport_submode = "unknown"
    
    # Get transport modes for the stop from the provided mapping
    transport_modes = transport_modes_per_stop.get(stop_id)

    # Choose the first transport mode and submode
    if transport_modes is not None:
        transport_mode, transport_submode = sorted(transport_modes)[0]  

    if transport_mode is None or transport_submode is None:
        raise ValueError(f"Invalid or unknown transport mode and submode for stop {stop_id_value}")
    
    if transport_mode == "unknown" and transport_submode == "unknown":
        logger.warning("Skipping %s with transport mode and submode as unknown as it's not a valid stop for conversion")
        return
    # Add TransportMode and StopPlaceType elements
    etree.SubElement(stop_place, "TransportMode").text = transport_mode
    
    submode_tag_map = {
        "rail": "RailSubmode",
        "coach": "CoachSubmode",
        "metro": "MetroSubmode",
        "bus": "BusSubmode",
        # "trolleyBus": "TrolleyBusSubmode",
        "tram": "TramSubmode",
        "water": "WaterSubmode",
        "cableway": "TelecabinSubmode",
        "funicular": "FunicularSubmode",
        "taxi": "TaxiSubMode",
        "other": "OtherSubMode",
    }
    
    stop_place_tag_map = {
        "rail": "railStation",
        "metro": "metroStation",
        "bus": "onstreetBus",
        "tram": "onstreetTram",
        "water": "ferryStop",
        "cableway": "liftStation",
        "taxi": "taxiStand",
    }

    # Get submode type tag
    if transport_mode != "trolleyBus":
          
        submode_tag = submode_tag_map.get(transport_mode)
            
        # Add transport submode
        etree.SubElement(stop_place, submode_tag).text = transport_submode
    
        #Add StopPlaceType
        stop_place_type = stop_place_tag_map.get(transport_mode)
        
        etree.SubElement(stop_place, "StopPlaceType").text = stop_place_type
        
    # Add Quay element with its data
    quays_container = etree.SubElement(stop_place, "quays")
    quay = etree.SubElement(quays_container, "Quay", version = "1", id = f"{config.NETEX_AUTHORITY}:Quay:{stop_id_value}")

    if stop_code_value:
        stop_public_code = etree.SubElement(quay, "PublicCode")
        stop_public_code.text = str(stop_code_value)

    if coords:
        centroid = etree.SubElement(quay, "Centroid")
        loc = etree.SubElement(centroid, "Location")
        etree.SubElement(loc, "Longitude").text = str(coords[0])
        etree.SubElement(loc, "Latitude").text = str(coords[1])

    return stop_place

def netex_helper_stream_stop_places(xml_file, transport_modes_per_stop: dict[str, set[tuple[str, str]]], gtfs_stop_entities: list[dict[str, Any]]) -> None:

    logger.info("Streaming StopPlaces")
    
    seen = set()

    # Create container for <stopPlaces> elements
    with xml_file.element("stopPlaces"):

        for entity in gtfs_stop_entities:

            # Build <stopPlaces> element
            stop_place = netex_helper_build_stop_place(entity, transport_modes_per_stop)

            # Continue when unsuccessful
            if stop_place is None:
                continue
            
            # Extract <StopPlace> ID
            stop_place_id = stop_place.get("id")

            # Skip if encountered
            if stop_place_id in seen:
                continue

            # Add to encountered
            seen.add(stop_place_id)


            # Stream the <StopPlace> element into the XML file
            xml_file.write(stop_place, pretty_print=True)

    logger.info("Finished streaming %d stopPlaces", len(seen))

# -----------------------------------------------------
# GtfsStop to NeTex <PassengerStopAssignment>
# -----------------------------------------------------

def netex_helper_build_passenger_stop_assignment(entity: dict[str, Any], index: int) -> etree.Element | None:
    """
    Build a single <PassengerStopAssignment> element.

    Args:
        entity (dict[str, Any]): A single GtfsStop entity
        index (int): Index used for ordering

    Returns:
        etree.Element | None: A NeTEx <PassengerStopAssignment> element or None
    """

    entity_type = entity.get("type")
    if entity_type != "GtfsStop":
        logger.error("Unsupported entity type: %s", entity_type)
        return None

    stop_id = entity.get("id")
    if not isinstance(stop_id, str) or ":" not in stop_id:
        logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
        return None

    stop_id_value = stop_id.split(":")[-1]

    passenger_stop_assignment = etree.Element("PassengerStopAssignment", order=str(index), version="1",
                                              id=f"{config.NETEX_AUTHORITY}:PassengerStopAssignment:{stop_id_value}")

    etree.SubElement(passenger_stop_assignment, "ScheduledStopPointRef",
                     ref=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{stop_id_value}", versionRef="1")

    etree.SubElement(passenger_stop_assignment, "QuayRef", 
                     ref=f"{config.NETEX_AUTHORITY}:Quay:{stop_id_value}", version="1")

    return passenger_stop_assignment

def netex_helper_stream_passenger_stop_assignments(xml_file, entities: list[dict[str, Any]]) -> None:
    """
    Stream <PassengerStopAssignment> elements.

    Args:
        xml_file: Streaming XML writer
        entities: List of GtfsStop entities

    Returns:
        None
    """

    logger.info("Streaming PassengerStopAssignments")

    seen = set()

    # Create container for <PassengerStopAssignment> elements
    with xml_file.element("stopAssignments"):

        for index, entity in enumerate(entities, start=1):

            # Build <PassengerStopAssignment> element
            passenger_stop_assignment = netex_helper_build_passenger_stop_assignment(entity, index)

            # Continue when unsuccessful
            if passenger_stop_assignment is None:
                continue

            # Get the ID of the PassengerStopAssignment
            passenger_stop_assignment_id = passenger_stop_assignment.get("id")

            # If we've already seen this ID, skip it to avoid duplicates
            if passenger_stop_assignment_id in seen:
                continue

            # Add the ID to the set of seen IDs
            seen.add(passenger_stop_assignment_id)

            # Stream the <PassengerStopAssignment> element into the XML file
            xml_file.write(passenger_stop_assignment, pretty_print=True)

    logger.info("Finished streaming %d PassengerStopAssignments", len(seen))

# -----------------------------------------------------
# GtfsStop to NeTex <RoutePoint> and <PointProjection>
# -----------------------------------------------------

def netex_helper_build_route_point(gtfs_stop: dict[str, Any]) -> etree.Element | None:
    """
    Builds a NeTEx <RoutePoint> element from a single GtfsStop entity.

    Args:
        gtfs_stop: A single GtfsStop entity

    Returns:
        etree.Element | None
    """
    # Get entity type and ID
    entity_type = gtfs_stop.get("type")
    stop_id = gtfs_stop.get("id")

    # If not supprted type, log an error and return None
    if entity_type != "GtfsStop":
        logger.error("Unsupported entity type: %s", entity_type)
        return None

    # If not correctly formatted ID, log an error and return None
    if not isinstance(stop_id, str) or ":" not in stop_id:
        logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
        return None

    stop_id_value = stop_id.split(":")[-1]

    # Build <RoutePoint> and <PointProjection> elements with the extracted ID value
    route_point = etree.Element("RoutePoint", version="1", id=f"{config.NETEX_AUTHORITY}:RoutePoint:{stop_id_value}")

    projections = etree.SubElement(route_point, "projections")

    point_projection = etree.SubElement( projections, "PointProjection", version="1", id=f"{config.NETEX_AUTHORITY}:PointProjection:{stop_id_value}")

    etree.SubElement(point_projection, "ProjectToPointRef", ref=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{stop_id_value}")

    return route_point

def netex_helper_stream_route_points(xml_file, gtfs_stops: list[dict[str, Any]]) -> None:
    """
    Streams RoutePoint elements into a <routePoints> container.

    Args:
        xml_file: Streaming XML writer
        gtfs_stops: List of GtfsStop entities

    Returns:
        None
    """

    logger.info("Streaming RoutePoints")

    seen_ids = set()

    # Create container for <RoutePoint> elements
    with xml_file.element("routePoints"):

        for gtfs_stop in gtfs_stops:

            # Build <RoutePoint> element
            route_point = netex_helper_build_route_point(gtfs_stop)

            # Continue when unsuccessful
            if route_point is None:
                continue

            # Get the ID of the RoutePoint to check for duplicates
            route_point_id = route_point.get("id")

            # If we've already seen this ID, skip it to avoid duplicates
            if route_point_id in seen_ids:
                continue

            # Add the ID to the set of seen IDs
            seen_ids.add(route_point_id)

            # Stream the <RoutePoint> element into the XML file
            xml_file.write(route_point, pretty_print=True)

    logger.info("Finished streaming %d RoutePoints", len(seen_ids))

# -----------------------------------------------------
# NeTEx <Route>
# -----------------------------------------------------

def netex_build_route_structures(route_dataset: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Build Route structures by grouping trips that share the same
    direction and stop sequence.

    Args:
        route_dataset (dict[str, Any]):
            Dataset for a single route.

    Returns:
        list[dict[str, Any]]:
            Route structures used for NeTEx Route generation.
    """

    route = route_dataset["route"]
    trips = route_dataset["trips"]
    stop_times_by_trip = route_dataset["stop_times"]
    trip_shapes = route_dataset["trip_shapes"]

    route_id = route.get("id")

    route_short_name = route.get("shortName", {}).get("value")
    route_long_name = route.get("name", {}).get("value")
    agency_id = route.get("operatedBy", {}).get("object")

    # Group trips by direction + stop sequence
    trip_groups = {}

    for trip in trips:

        trip_id = trip.get("id")
        shape_id = trip_shapes.get(trip_id)
        
        if not shape_id:
            logger.warning("Trip %s has no shape_id", trip_id)

        if not trip_id:
            logger.error("Trip missing ID: %r", trip)
            continue

        trip_stop_times = stop_times_by_trip.get(trip_id, [])

        if not trip_stop_times:
            logger.warning("No stop times found for trip %s", trip_id)
            continue

        stop_sequence = []

        for stop_time in trip_stop_times:

            stop_id = stop_time.get("hasStop", {}).get("object")

            if not isinstance(stop_id, str) or ":" not in stop_id:
                logger.warning(
                    "Invalid stop reference in stop time %s",
                    stop_time.get("id")
                )
                continue

            stop_sequence.append(stop_id.split(":")[-1])

        if not stop_sequence:
            logger.warning("No stop sequence found for trip %s", trip_id)
            continue

        direction_id = trip.get("direction", {}).get("value")

        direction = None

        if direction_id == 0:
            direction = "outbound"
        elif direction_id == 1:
            direction = "inbound"

        key = (direction, shape_id, tuple(stop_sequence))

        if key not in trip_groups:
            trip_groups[key] = {
                "trips": [],
                "trip_stop_times": trip_stop_times
            }

        trip_groups[key]["trips"].append(
            {
                "trip_id": trip_id,
                "service_id": trip.get("service", {}).get("object"),
                "shape_id": shape_id
            }
        )
        
    # Convert grouped trips to Route structures
    route_structures = []

    # (direction, shape_id, stop_sequence)
    for (direction, shape_id, stop_sequence), group in trip_groups.items():

        route_structure = {
            "route_id": route_id,
            "agency_id": agency_id,
            "stop_sequence": list(stop_sequence),
            "trips": group["trips"],
            "stop_times": group["trip_stop_times"]
        }

        if direction:
            route_structure["direction"] = direction

        if route_short_name:
            route_structure["route_short_name"] = route_short_name

        if route_long_name:
            route_structure["route_long_name"] = route_long_name

        route_structures.append(route_structure)

    return route_structures

def netex_helper_build_route(route_structure: dict[str, Any]) -> etree.Element:

    route_id = route_structure["route_id"]
    route_id_value = route_id.split(":")[-1] if route_id else "unknown"
    shape_id = route_structure["trips"][0]["shape_id"] if route_structure["trips"] else "unknown"

    sequence = route_structure["stop_sequence"]
    
    signature = "|".join(sequence) + f"|{shape_id}"
    unique_identifier = hashlib.blake2b(signature.encode(),digest_size=5).hexdigest()

    route = etree.Element("Route", version="1",id=f"{config.NETEX_AUTHORITY}:Route:{route_id_value}_{sequence[0]}_{sequence[-1]}_{unique_identifier}")

    route_long_name = route_structure.get("route_long_name")

    if route_long_name:
        etree.SubElement(route, "Name").text = route_long_name

    route_short_name = route_structure.get("route_short_name")

    if route_short_name:
        etree.SubElement(route, "ShortName").text = route_short_name

    etree.SubElement(route, "LineRef", ref=f"{config.NETEX_AUTHORITY}:Line:{route_id_value}", version="1")

    direction = route_structure.get("direction")

    if direction:
        etree.SubElement(route, "DirectionType").text = direction

    points_in_sequence = etree.SubElement(route, "pointsInSequence")
    
    seen_stops = set()

    for order, stop_id in enumerate(sequence, start=1):
        
        if stop_id in seen_stops:
            continue

        seen_stops.add(stop_id)

        point_on_route = etree.SubElement(points_in_sequence, "PointOnRoute",
         id=f"{config.NETEX_AUTHORITY}:PointOnRoute:{route_id_value}_{sequence[0]}_{sequence[-1]}_{unique_identifier}_{order}",
         order=str(order), version="1")

        etree.SubElement(point_on_route, "RoutePointRef",
        ref=f"{config.NETEX_AUTHORITY}:RoutePoint:{stop_id}")

    return route

def netex_helper_stream_routes(xml_file, route_structures: list[dict[str, Any]]) -> None:
    
    global ROUTE_COUNTER
    
    valid_routes = []

    for structure in route_structures:
        route = netex_helper_build_route(structure)

        if route is not None:
            valid_routes.append(route)
            
    if not valid_routes:
        return

    with xml_file.element("routes"):

        for route in valid_routes:
            xml_file.write(route, pretty_print=True)
            ROUTE_COUNTER += 1

# -----------------------------------------------------
#  NeTEx <JourneyPattern>
# -----------------------------------------------------

def netex_helper_build_journey_pattern(route_structure: dict[str, Any]) -> etree.Element:

    route_id = route_structure["route_id"]
    route_id_value = route_id.split(":")[-1] if route_id else "unknown"
    shape_id = route_structure["trips"][0]["shape_id"] if route_structure["trips"] else "unknown"
    
    sequence = route_structure["stop_sequence"]
    stop_times = route_structure.get("stop_times", [])
        
    signature = "|".join(sequence) + f"|{shape_id}"
    unique_identifier = hashlib.blake2b(signature.encode(),digest_size=5).hexdigest()

    journey_pattern = etree.Element("JourneyPattern", version="1",
                                    id=f"{config.NETEX_AUTHORITY}:JourneyPattern:{route_id_value}_{sequence[0]}_{sequence[-1]}_{unique_identifier}")

    route_long_name = route_structure.get("route_long_name")

    if route_long_name:
        etree.SubElement(journey_pattern, "Name").text = route_long_name

    etree.SubElement(journey_pattern, "RouteRef", ref=f"{config.NETEX_AUTHORITY}:Route:{route_id_value}_{sequence[0]}_{sequence[-1]}_{unique_identifier}", version="1")

    points_in_sequence = etree.SubElement(journey_pattern, "pointsInSequence")
    
    for order, (stop_id, stop_time) in enumerate(zip(sequence, stop_times), start=1):
        
        is_first = (order == 1)
        is_last = (order == len(sequence))

        pickup_type = stop_time.get("pickupType", {}).get("value")
        drop_off_type = stop_time.get("dropOffType", {}).get("value")

        point_on_route = etree.SubElement(points_in_sequence, "StopPointInJourneyPattern", order=str(order), version="1",
                                          id=f"{config.NETEX_AUTHORITY}:StopPointInJourneyPattern:{route_id_value}_{sequence[0]}_{sequence[-1]}_{stop_id}_{unique_identifier}")

        etree.SubElement(point_on_route, "ScheduledStopPointRef", ref=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{stop_id}")
        
        if not is_last:
            etree.SubElement(point_on_route, "DestinationDisplayRef", ref=f"{config.NETEX_AUTHORITY}:DestinationDisplay:{stop_id}")
        
        # if is_last:
        #     for_boarding = False
        # else:
        #     for_boarding = pickup_type in (" ", 0)

        # etree.SubElement(point_on_route, "ForBoarding").text = str(for_boarding).lower()

        # if is_first:
        #     for_alighting = False
        # else:
        #     for_alighting = drop_off_type in (" ", 0)

        # etree.SubElement(point_on_route, "ForAlighting").text = str(for_alighting).lower()

    links_in_sequence = etree.SubElement(journey_pattern, "linksInSequence")

    for order, (from_stop, to_stop) in enumerate(zip(sequence, sequence[1:]), start=1):

        service_link_in_journey_pattern = etree.SubElement(
            links_in_sequence, "ServiceLinkInJourneyPattern", order=str(order), version="1",
            id=f"{config.NETEX_AUTHORITY}:ServiceLinkInJourneyPattern:{from_stop}_{to_stop}_{unique_identifier}"
        )

        etree.SubElement(service_link_in_journey_pattern, "ServiceLinkRef",
                         ref=f"{config.NETEX_AUTHORITY}:ServiceLink:{from_stop}_{to_stop}_{shape_id}")

    return journey_pattern

def netex_helper_stream_journey_patterns(xml_file, route_structures: list[dict[str, Any]]) -> None:

    global JOURNEY_PATTERN_COUNTER
    
    valid_journey_patterns = []

    for structure in route_structures:
        route = netex_helper_build_journey_pattern(structure)

        if route is not None:
            valid_journey_patterns.append(route)
            
    if not valid_journey_patterns:
        return

    with xml_file.element("journeyPatterns"):
        for journey_pattern in valid_journey_patterns:
            xml_file.write(journey_pattern, pretty_print=True)    
            JOURNEY_PATTERN_COUNTER += 1

# -----------------------------------------------------
#  GtfsTransfers to NeTEx <ServiceJourneyInterchange>
# -----------------------------------------------------

def netex_helper_build_service_journey_interchange(route_tansfer: dict[str, Any]) -> etree.Element:

    from_stop_id = route_tansfer.get("hasOrigin", {}).get("object")
    to_stop_id = route_tansfer.get("hasDestination", {}).get("object")
    from_trip_id = route_tansfer.get("from_trip_id", {}).get("object")
    to_trip_id = route_tansfer.get("to_trip_id", {}).get("object")

    from_stop_id_value = from_stop_id.split(":")[-1]
    to_stop_id_value = to_stop_id.split(":")[-1]
    from_trip_id_id_value = from_trip_id.split(":")[-1]
    to_trip_id_id_value = to_trip_id.split(":")[-1]

    service_journey_interchange = etree.Element("ServiceJourneyInterchange", version = "1",
                                                id = f"{config.NETEX_AUTHORITY}:ServiceJourneyInterchange:{from_stop_id_value}_{to_stop_id_value}_{from_trip_id_id_value}_{to_trip_id_id_value}")
    
    etree.SubElement(service_journey_interchange, "Guaranteed").text = str(True).lower()

    etree.SubElement(service_journey_interchange, "FromPointRef", ref = f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{from_stop_id_value}")

    etree.SubElement(service_journey_interchange, "ToPointRef", ref = f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{to_stop_id_value}")

    etree.SubElement(service_journey_interchange, "FromJourneyRef", ref = f"{config.NETEX_AUTHORITY}:ServiceJourney:{from_trip_id_id_value}")

    etree.SubElement(service_journey_interchange, "ToJourneyRef", ref = f"{config.NETEX_AUTHORITY}:ServiceJourney:{to_trip_id_id_value}")

    return service_journey_interchange

def netex_helper_stream_service_journey_interchange(xml_file, transfers: list[dict[str, Any]]) -> None:

    global SERVICE_JOURNEY_INTERCHANGE_COUNTER
    
    valid_service_journey_interchanges = []
    
    seen = set()

    for transfer in transfers:
        
        transfer_id = transfer.get("id")

        if transfer_id in seen:
            continue

        seen.add(transfer_id)
        
        service_journey_interchanges = netex_helper_build_service_journey_interchange(transfer)

        if service_journey_interchanges is not None:
            valid_service_journey_interchanges.append(service_journey_interchanges)
            
    if not valid_service_journey_interchanges:
        return

    with xml_file.element("journeyInterchanges"):
        for journey_pattern in valid_service_journey_interchanges:
            xml_file.write(journey_pattern, pretty_print=True)    
            SERVICE_JOURNEY_INTERCHANGE_COUNTER += 1

# -----------------------------------------------------
#  NeTEx <ServiceJourney>
# -----------------------------------------------------
def netex_helper_normalize_time(time_value: str) -> tuple[str, int]:
    """
    Convert GTFS extended time format (e.g. 26:30:00) to NeTEx time + day offset.
    
    Args:
        time_value (str): Time which is a normalization candidate

    Returns:
        tuple[str, int]: normalized time, day offset
    """

    if not time_value:
        return time_value, 0

    hours, minutes, seconds = map(int, time_value.split(":"))

    day_offset = hours // 24
    hours = hours % 24

    normalized_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return normalized_time, day_offset

def netex_helper_build_service_journeys(route_structure: dict[str, Any]) -> list[etree.Element]:
    
    route_id = route_structure["route_id"]
    route_id_value = route_id.split(":")[-1] if route_id else "unknown"
    shape_id = route_structure["trips"][0]["shape_id"] if route_structure["trips"] else "unknown"
    
    agency_id = route_structure["agency_id"]
    agency_id_value = agency_id.split(":")[-1] if agency_id else "unknown"

    sequence = route_structure["stop_sequence"]
    stop_times = route_structure.get("stop_times", [])
    
    signature = "|".join(sequence) + f"|{shape_id}"
    unique_identifier = hashlib.blake2b(signature.encode(),digest_size=5).hexdigest()

    service_journeys = []

    for trip in route_structure["trips"]:

        trip_id = trip["trip_id"]
        trip_id_value = trip_id.split(":")[-1] if trip_id else "unknown"
        service_id = trip.get("service_id")

        service_id_value = service_id.split(":")[-1] if service_id else "unknown"

        service_journey = etree.Element("ServiceJourney", version="1",
                                        id=f"{config.NETEX_AUTHORITY}:ServiceJourney:{trip_id_value}")

        route_long_name = route_structure.get("route_long_name")

        if route_long_name:
            etree.SubElement(service_journey, "Name").text = route_long_name

        day_types = etree.SubElement(service_journey, "dayTypes")
        etree.SubElement(day_types, "DayTypeRef", ref=f"{config.NETEX_AUTHORITY}:DayType:{service_id_value}")

        etree.SubElement(service_journey, "JourneyPatternRef",
            ref=f"{config.NETEX_AUTHORITY}:JourneyPattern:{route_id_value}_{sequence[0]}_{sequence[-1]}_{unique_identifier}",
            version="1")

        etree.SubElement(service_journey, "OperatorRef", ref=f"{config.NETEX_AUTHORITY}:Operator:{agency_id_value}")

        etree.SubElement(service_journey, "LineRef", ref=f"{config.NETEX_AUTHORITY}:Line:{route_id_value}", version="1")

        passing_times = etree.SubElement(service_journey, "passingTimes")

        for order, (stop_id, stop_time) in enumerate(zip(sequence, stop_times), start=1):
            
            is_first = (order == 1)
            is_last = (order == len(sequence))

            arrival_time = stop_time.get("arrivalTime", {}).get("value")
            departure_time = stop_time.get("departureTime", {}).get("value")
            
            arrival_offset = 0
            departure_offset = 0

            if arrival_time:
                arrival_time, arrival_offset = netex_helper_normalize_time(arrival_time)

            if departure_time:
                departure_time, departure_offset = netex_helper_normalize_time(departure_time)

            time_tabled_passing_time = etree.SubElement(passing_times, "TimetabledPassingTime",
                version="1", id=f"{config.NETEX_AUTHORITY}:TimetabledPassingTime:{trip_id_value}_{stop_id}")

            etree.SubElement(time_tabled_passing_time, "StopPointInJourneyPatternRef",
                ref=f"{config.NETEX_AUTHORITY}:StopPointInJourneyPattern:{route_id_value}_{sequence[0]}_{sequence[-1]}_{stop_id}_{unique_identifier}", version="1")

            if is_last:
                if not arrival_time:
                    raise ValueError(f"Missing arrival time for last stop {stop_id} in trip {trip_id}")

                etree.SubElement(time_tabled_passing_time, "ArrivalTime").text = arrival_time
                
                if arrival_offset > 0:
                    etree.SubElement(time_tabled_passing_time, "ArrivalDayOffset").text = str(arrival_offset)

                if departure_time and departure_time != arrival_time:
                    etree.SubElement(time_tabled_passing_time, "DepartureTime").text = departure_time
                    
                    if departure_offset > 0:
                         etree.SubElement(time_tabled_passing_time, "DepartureDayOffset").text = str(departure_offset)

            else:
                if arrival_time and departure_time and arrival_time != departure_time:
                    etree.SubElement(time_tabled_passing_time, "ArrivalTime").text = arrival_time

                    if arrival_offset > 0:
                        etree.SubElement(time_tabled_passing_time, "ArrivalDayOffset").text = str(arrival_offset)


                if departure_time:
                    etree.SubElement(time_tabled_passing_time, "DepartureTime").text = departure_time
                    
                    if departure_offset > 0:
                        etree.SubElement(time_tabled_passing_time, "DepartureDayOffset").text = str(departure_offset)
                else:
                    raise ValueError(f"Missing departure time for stop {stop_id} in trip {trip_id}")

        service_journeys.append(service_journey)

    return service_journeys

def netex_helper_stream_service_journey(xml_file, route_structures: list[dict[str, Any]]) -> None:

    global SERVICE_JOURNEY_COUNTER
    
    valid_service_journeys = []
    
    for structure in route_structures:
        service_journeys = netex_helper_build_service_journeys(structure)

        if service_journeys:
            valid_service_journeys.extend(service_journeys)

    if not valid_service_journeys:
        return
    
    with xml_file.element("vehicleJourneys"):
        for service_journey in valid_service_journeys:
            xml_file.write(service_journey, pretty_print=True)
            SERVICE_JOURNEY_COUNTER += 1
        
def netex_stream_service_frame_for_shared_data_xml(xml_file, 
                               agency, 
                               stops,
                               stop_coordinates, 
                               shape_linestrings, 
                               shape_per_trip, 
                               stops_and_info_per_trip
                               ):
    # Create ServiceFrame element and add it's subelements
    
    with xml_file.element("ServiceFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ServiceFrame:{uuid.uuid4()}"):
        netex_helper_stream_networks(xml_file, agency)

        netex_helper_stream_route_points(xml_file, stops)
        
        netex_helper_stream_destination_displays(xml_file, stops)

        netex_helper_stream_scheduled_stop_points(xml_file, stops)

        service_links_data = netex_helper_create_service_link_info(stops_and_info_per_trip, stop_coordinates, shape_linestrings, shape_per_trip)

        netex_stream_service_links(xml_file, list(service_links_data))

        netex_helper_stream_passenger_stop_assignments(xml_file, stops)

def netex_stream_service_frame_for_line_xml(xml_file, route_dataset, route_structure):

    # Create ServiceFrame element and add it's subelements
    
    with xml_file.element("ServiceFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ServiceFrame:{uuid.uuid4()}"):
        netex_helper_stream_routes(xml_file, route_structure)
        
        netex_helper_stream_line(xml_file, route_dataset["route"])
        
        netex_helper_stream_journey_patterns(xml_file, route_structure)

def netex_stream_time_table_frame_for_line_xml(xml_file, route_dataset, route_structure):
    
    with xml_file.element("TimetableFrame", version="1", id=f"{config.NETEX_AUTHORITY}:TimetableFrame:{uuid.uuid4()}"):
        netex_helper_stream_service_journey(xml_file, route_structure)
        
        netex_helper_stream_service_journey_interchange(xml_file, route_dataset["transfers"])
    
def netex_stream_service_frame_for_stops_xml(xml_file, authority_dataset) -> None:

    with xml_file.element("ServiceFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ServiceFrame:{uuid.uuid4()}"):

        netex_helper_stream_scheduled_stop_points(xml_file, authority_dataset["stops"])

        netex_helper_stream_passenger_stop_assignments(xml_file, authority_dataset["stops"])

def netex_stream_site_frame_for_stops_xml(xml_file, agency, authority_dataset):

    transport_modes = netex_helper_get_transport_modes_per_stop(authority_dataset)

    
    with xml_file.element("SiteFrame", version="1", id=f"{config.NETEX_AUTHORITY}:SiteFrame:{uuid.uuid4()}"):
        netex_helper_stream_frame_defaults(xml_file, agency)
        netex_helper_stream_stop_places(xml_file, transport_modes, authority_dataset["stops"])
    
def netex_create_shared_data_xml(
        agency: dict[str, Any], 
        authority_dataset: dict[str, Any]
        ) -> None:
    
    stops_per_trip = netex_helper_extract_stops_in_a_trip(authority_dataset["stop_times"])
    stop_coordinates = netex_helper_extract_stop_coordinates(authority_dataset["stops"])
    shape_linestrings = netex_helper_extract_shape_linestrings(authority_dataset["shapes"])
    shape_per_trip = netex_helper_map_trips_to_shapes(authority_dataset["trips"])
    
    with etree.xmlfile(f"{config.NETEX_OUTPUT_DIR}/{config.NETEX_AUTHORITY}_shared_data.xml", encoding="utf-8") as xml_file:
        xml_file.write_declaration()

        with xml_file.element(f"PublicationDelivery", nsmap=NSMAP, version="1"):
            
            publication_timestamp = etree.Element("PublicationTimestamp")
            publication_timestamp.text = now_time.isoformat(timespec="milliseconds")
            xml_file.write(publication_timestamp)

            participant_ref = etree.Element("ParticipantRef")
            participant_ref.text = config.NETEX_AUTHORITY
            xml_file.write(participant_ref)
            
            with xml_file.element("dataObjects"):
                
                with xml_file.element("CompositeFrame", version="1", id=f"{config.NETEX_AUTHORITY}:CompositeFrame:{uuid.uuid4()}"):
                    netex_helper_stream_validity_conditions(xml_file, now_time)
                    netex_helper_stream_frame_defaults(xml_file, agency)
                    with xml_file.element("frames"):
                        netex_stream_resource_frame_for_shared_data_xml(xml_file, agency)
                        
                        netex_stream_service_frame_for_shared_data_xml(xml_file, agency, authority_dataset["stops"],
                                                                        stop_coordinates, shape_linestrings,
                                                                          shape_per_trip, stops_per_trip)
                        
                        netex_stream_service_calendar_frame_for_shared_data_xml(xml_file, 
                                                                                authority_dataset["calendar"], authority_dataset["calendar_dates"])

def netex_create_line_xmls(authority_dataset: dict[str, Any]) -> None:
    """
    Create one NeTEx Line XML file for every route belonging to the authority.

    Args:
        authority_dataset (dict[str, Any]): Dataset of an authority contianing all the entities involved

    Returns:
        None
    """

    routes = authority_dataset.get("routes", [])

    if not routes:
        logger.warning("Authority dataset contains no routes")
        return

    logger.info("Streaming Routes")
    logger.info("Streaming Lines")
    logger.info("Streaming JourneyPatterns")
    logger.info("Streaming ServiceJourneys")
    logger.info("Streaming ServiceJourneyInterchanges")

    for route in routes:

        route_id = route.get("id")

        if not route_id:
            logger.error("Route missing ID: %r", route)
            continue

        route_dataset = netex_build_route_dataset(route, authority_dataset)
        
        if not route_dataset:
            logger.warning("No dataset found for route %s", route_id)
            continue

        try:
            netex_create_line_xml(route_dataset, authority_dataset)

        except Exception:
            logger.exception("Failed to create Line XML for route %s", route_id)
            
    logger.info("Finished streaming %d Routes", ROUTE_COUNTER)
    logger.info("Finished streaming %d Lines", LINE_COUNTER)
    logger.info("Finished streaming %d JourneyPatterns", JOURNEY_PATTERN_COUNTER)
    logger.info("Finished streaming %d ServiceJourneys", SERVICE_JOURNEY_COUNTER)
    logger.info("Finished streaming %d ServiceJourneyInterchanges", SERVICE_JOURNEY_INTERCHANGE_COUNTER)

def netex_create_line_xml(route_dataset: dict[str, Any], authority_dataset) -> None:
    """
    Create a NeTEx Line XML file for a given route dataset.

    Args:
        route_dataset (dict[str, Any]): Dataset containing all the entities involved in the route

    Returns:
        None
    """
    route_structures = netex_build_route_structures(route_dataset)
    
    if not route_structures:
        logger.warning("Skipping Line XML for route %s: no route structures generated.",route_dataset["route"]["id"])
        return

    route_name = (route_dataset["route"].get("name", {}).get("value") or route_dataset["route"].get("shortName", {}).get("value"))

    route_name = route_name.strip().replace(" ", "_")
    
    translated_route_name = netex_resolve_translation(authority_dataset["translations"], "routes", "long_name", route_name)
            
    route_name_str = translated_route_name if translated_route_name is not None else route_name
        
    route_name_str = re.sub(r"[^\w\s]", "_", route_name_str)
    route_name_str = "_".join(route_name_str.split())
    route_name_str = re.sub(r"_+", "_", route_name_str)

    with etree.xmlfile(f"{config.NETEX_OUTPUT_DIR}/{config.NETEX_AUTHORITY}_{route_name_str}.xml", encoding="utf-8") as xml_file:
        xml_file.write_declaration()

        with xml_file.element(f"PublicationDelivery", nsmap=NSMAP, version="1"):
            
            publication_timestamp = etree.Element("PublicationTimestamp")
            publication_timestamp.text = datetime.now().isoformat(timespec="milliseconds")
            xml_file.write(publication_timestamp)

            participant_ref = etree.Element("ParticipantRef")
            participant_ref.text = config.NETEX_AUTHORITY
            xml_file.write(participant_ref)
            
            with xml_file.element("dataObjects"):
                
                with xml_file.element("CompositeFrame", version="1", id=f"{config.NETEX_AUTHORITY}:CompositeFrame:{uuid.uuid4()}"):
                    netex_helper_stream_validity_conditions(xml_file, now_time)
                    netex_helper_stream_frame_defaults(xml_file, route_dataset["agency"])
                    with xml_file.element("frames"):
                        netex_stream_service_frame_for_line_xml(xml_file, route_dataset, route_structures)
                        
                        netex_stream_time_table_frame_for_line_xml(xml_file, route_dataset, route_structures)

def netex_create_stops_xml(agency, authority_dataset):

    with etree.xmlfile(f"{config.NETEX_OUTPUT_DIR}/_stops.xml", encoding="utf-8") as xml_file:
        xml_file.write_declaration()

        with xml_file.element(f"PublicationDelivery", nsmap=NSMAP, version="1"):
            
            publication_timestamp = etree.Element("PublicationTimestamp")
            publication_timestamp.text = datetime.now().isoformat(timespec="milliseconds")
            xml_file.write(publication_timestamp)

            participant_ref = etree.Element("ParticipantRef")
            participant_ref.text = config.NETEX_AUTHORITY
            xml_file.write(participant_ref)
            
            with xml_file.element("dataObjects"):

                netex_stream_service_frame_for_stops_xml(xml_file, authority_dataset)

                netex_stream_site_frame_for_stops_xml(xml_file, agency, authority_dataset)

if __name__ == "__main__":
    netex_helper_prepare_output_directory()

    netex_helper_set_operating_city("Sofia")

    gtfs_dataset = netex_load_city_dataset()

    gtfs_indexes = netex_build_indexes_and_collections(gtfs_dataset)
    
    for agency in gtfs_dataset["agencies"]:
        authority_dataset = netex_build_authority_dataset(agency, gtfs_indexes)
                
        netex_helper_set_netex_authority(agency)
        netex_create_shared_data_xml(agency, authority_dataset)

        netex_create_line_xmls(authority_dataset)

        netex_create_stops_xml(agency, authority_dataset)

    netex_helper_create_otp_zip()
    
