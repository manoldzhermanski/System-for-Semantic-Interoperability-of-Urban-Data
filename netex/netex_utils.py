import sys
import json
import math
import logging
from typing import Iterator, Any
from pathlib import Path
from lxml import etree # type: ignore
from pyproj import Transformer
from shapely.geometry import LineString, Point as ShapelyPoint
from shapely.geometry.base import BaseGeometry
from shapely.ops import substring
from datetime import datetime
from pprint import pprint


project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import config

from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_batches
from orion_ld.orion_ld_crud_operations import (
    orion_ld_define_header,
    orion_ld_get_entities_by_type
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
        raise ValueError(
            "The provided entity for NeTEx Authority setting should be of type GtfsAgency"
        )

    # Try setting config.NETEX_Authority
    try:
        config.NETEX_AUTHORITY = agency["id"].split(":")[-1]
    except KeyError:
        raise ValueError("Entity should have an ID")

# -----------------------------------------------------
# Generate <FrameDefaults>
# -----------------------------------------------------

# For FrameDefaults: How should I handle the timezone and default language and if there are multiple timezones in agency.txt
def netex_build_frame_defaults(agency: dict[str, Any]) -> etree.Element:
    """
    Builds the NeTEx <FrameDefaults> element from a GtfsAgency entity

    Args:
        agency (dict[str, Any]): GtfsAgency entity

    Returns:
        An lxml.etree.Element object representing the <FrameDefaults> XML structure.
        
    Raises:
        ValueError: If the entity is not of type `GtfsAgency`
    """
    # Check if entity is of GtfsAgency type
    if agency["type"] != "GtfsAgency":
        raise ValueError(
            "The provided entity for NeTEx Authority setting should be of type GtfsAgency"
        )
        
    # Extract from the entity it's timezone (required field) and language (optional field)
    time_zone = agency.get("agency_timezone", {}).get("value")
    language = agency.get("agency_lang", {}).get("value")

    # Build FrameDefaults
    frame_defaults = etree.Element("FrameDefaults")

    # Add DefaultLocale element
    frame_default_locale = etree.SubElement(frame_defaults, "DefaultLocale")

    # Add TimeZone element
    default_time_zone = etree.SubElement(frame_default_locale, "TimeZone").text = time_zone

    # If the optional language field is provided, add the DefaultLanguage element
    if language:
        default_language = etree.SubElement(frame_default_locale, "DefaultLanguage").text = language

    # Return FrameDefaults
    return frame_defaults

# -----------------------------------------------------
# GtfsAgency to NeTex <Authority> and <Operator>
# -----------------------------------------------------
##########################################################
# Questions: 
# Observing the Netur Dataset we see a mapping of GTFS Agency to NeTEx Authority.
# We already discussed that we will map GTFS Agency also to Operator but this begs the question - In general where does the Operator data come from if not observed in the GTFS files ?
# Plus thete are multiple operators and 1 authority that combines them

def netex_convert_agency_to_authority(entities: list[dict[str, Any]] | dict[str, Any]) -> list[etree.Element]:
    """
    Converts a list of GtfsAgency entities into NeTEx Nordic <Authority> elements.

    Args:
        entities (list[dict[str, Any]]): A list of GtfsAgency entities
        
    Returns:
        A list of lxml.etree.Element objects, where each element is a fully
        formed NeTEx <Authority> element.
    """
    if isinstance(entities, dict):
        entities = [entities]

    # List to store Authority elements
    authority_list = []

    # Iterate through all agencies
    for index, entity in enumerate(entities, start = 1):

        # Get the agency id value
        agency_id = entity["id"]
        if not isinstance(agency_id, str) or ":" not in agency_id:
            logger.error("Invalid or missing ID for GtfsAgency: %r", agency_id)
            continue
        agency_id_value = agency_id.split(":")[-1]

        # Get agency name
        agency_name = entity.get("agency_name", {}).get("value")

        # Build Authority XML element
        authority = etree.Element("Authority", version = "1", id = f"{config.NETEX_AUTHORITY}:Authority:{agency_id_value}_ID")

        # Set mandatory company number to index at which the element is at the input list
        etree.SubElement(authority, "CompanyNumber").text = str(index)

        # Set Name element
        etree.SubElement(authority, "Name").text = agency_name
        
        # Set LegalName element
        etree.SubElement(authority, "LegalName").text = agency_name

        # Get agency_fare_url (mandatory field), agency_phone (optional field) and agency_email (optional field)
        agency_phone = entity.get("agency_phone", {}).get("value")
        agency_fare_url = entity.get("agency_fare_url", {}).get("value")
        agency_email = entity.get("agency_email", {}).get("value")

        # Set ContactDetails element
        authority_contact_details = etree.SubElement(authority, "ContactDetails")

        # Set authority email if provided
        if agency_email:
            etree.SubElement(authority_contact_details, "Email").text = agency_email

        # Set authority phone if provided
        if agency_phone:
            etree.SubElement(authority_contact_details, "Phone").text = agency_phone

        # Set authority url
        etree.SubElement(authority_contact_details, "Url").text = agency_fare_url
        

        # Set OrganisationType to authority
        etree.SubElement(authority, "OrganisationType").text = "authority"

        # Append authority
        authority_list.append(authority)
   
    # Return authority_list
    return authority_list

def netex_convert_agency_to_operator(entities: list[dict[str, Any]]) -> list[etree.Element]:
    """
    Converts a list of GtfsAgency entities into NeTEx Nordic <Operator> elements.

    Args:
        entities (list[dict[str, Any]]): A list of GtfsAgency entities
    Returns:
        A list of lxml.etree.Element objects, where each element is a fully
        formed NeTEx <Operator> element
    """
    if isinstance(entities, dict):
        entities = [entities]
    # List to store Operator elements
    operator_list = []

    # Iterate through all agencies
    for index, entity in enumerate(entities, start = 1):

        # Get the agency id value
        agency_id = entity.get("id")
        if not isinstance(agency_id, str) or ":" not in agency_id:
            logger.error("Invalid or missing ID for GtfsAgency: %r", agency_id)
            continue
        agency_id_value = agency_id.split(":")[-1]

        # Get agency name
        agency_name = entity.get("agency_name", {}).get("value")

        # Build Operator XML element
        operator = etree.Element("Operator", version = "1", id = f"{config.NETEX_AUTHORITY}:Operator:{agency_id_value}")

        # Set mandatory company number to index at which the element is at the input list
        etree.SubElement(operator, "CompanyNumber").text = str(index)

        # Set Name element
        etree.SubElement(operator, "Name").text = agency_name

        # Set LegalName element
        etree.SubElement(operator, "LegalName").text = agency_name

        # Get agency_fare_url (mandatory field), agency_phone (optional field) and agency_email (optional field)
        agency_phone = entity.get("agency_phone", {}).get("value")
        agency_fare_url = entity.get("agency_fare_url", {}).get("value")
        agency_email = entity.get("agency_email", {}).get("value")

        # Set ContactDetails element
        operator_contact_details = etree.SubElement(operator, "ContactDetails")

        # Set authority email if provided
        if agency_email:
            etree.SubElement(operator_contact_details, "Email").text = agency_email

        # Set authority phone if provided
        if agency_phone:
            etree.SubElement(operator_contact_details, "Phone").text = agency_phone

        # Set authority url
        etree.SubElement(operator_contact_details, "Url").text = agency_fare_url

        # Set OrganisationType to operator
        etree.SubElement(operator, "OrganisationType").text = "operator"

        # Append operator
        operator_list.append(operator)

    # Return operator_list
    return operator_list

# -----------------------------------------------------
# Generate <ResourceFrame>
# -----------------------------------------------------

def netex_build_resource_frame(agency: list[dict[str, Any]]) -> etree.Element:
    """
    Builds the NeTEx <ResourceFrame> element which contains all <Authority> and <Operator> elements

    Args:
        agency (list[dict[str, Any]]): A list of GtfsAgency entities
        
    Returns:
        An lxml.etree.Element object representing the complete <ResourceFrame>.
    """
    # Create ResourceFrame element and add it's organisations sub-element
    resource_frame = etree.Element("ResourceFrame", version = "1", id = f"{config.NETEX_AUTHORITY}:ResourceFrame:1")
    organisations = etree.SubElement(resource_frame, "organisations")

    # Append all authorites to organisations
    authorities = netex_convert_agency_to_authority(agency)
    for authority in authorities:
        organisations.append(authority)

    # Append all operators to organisations
    operators = netex_convert_agency_to_operator(agency)
    for operator in operators:
        organisations.append(operator)

    # Return ResourceFrame
    return resource_frame

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

    network_id = agency["id"]
    entity_type = agency["type"]

    if entity_type != "GtfsAgency":
        logger.error("Unsupported entity type for Network conversion: %s", entity_type)
        return None
    
    if not isinstance(network_id, str) or ":" not in network_id:
        logger.error("Invalid or missing ID for GtfsAgency: %r", network_id)
        return None
    
    parts = network_id.split(":")

    if len(parts) != 5:
            logger.error("Invalid ID for GtfsAgency: %r", network_id)
            return None

    network_id_value = network_id.split(":")[-1]
    agency_name = agency.get("agency_name", {}).get("value")

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

def netex_helper_transform_point_to_wgs84(point: Point) -> Point:
    """
    Transforms a point from the projected CRS (EPSG:7801) to WGS84 (EPSG:4326)
    
    Args:
        point (Point): A tuple representing the (x, y) coordinates of the point in the projected CRS

    Returns:
        Point: A tuple representing the (longitude, latitude) coordinates of the point in WGS84 CRS
    """
    return projected_to_wgs84.transform(*point)

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

        trip_id_parts = trip_id.split(":")

        if len(trip_id_parts) != 5:
            logger.error("Invalid ID for GtfsTrip: %r", trip_id)
            continue

        trip_id_value = trip_id_parts[-1]

        if not isinstance(stop_id, str) or ":" not in stop_id:
            logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
            continue
        
        stop_id_parts = stop_id.split(":")

        if len(stop_id_parts) != 5:
            logger.error("Invalid ID for GtfsStop: %r", stop_id)
            continue
        
        stop_id_value = stop_id_parts[-1]
        
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

        stop_id_parts = stop_id.split(":")

        if len(stop_id_parts) != 5:
            logger.error("Invalid ID for GtfsStop: %r", stop_id)
            continue
        
        stop_id_value = stop_id_parts[-1]

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
        return []

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

    point = ShapelyPoint(stop_coordinates)

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

    if shape_geometry.is_empty:
        logger.error("Cannot calculate stop distances: shape is empty")
        return {}

    stop_distances: dict[str, float] = {}

    if not stop_ids:
        logger.error("Missing stop IDs")
        return {}

    for stop_id in stop_ids:

        coordinates = stop_coordinates.get(stop_id)

        if coordinates is None:
            logger.error("Missing coordinates for stop %s", stop_id)
            continue

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
    """

    stop_projections_per_trip: dict[str, dict[str, float]] = {}

    for trip_id, stop_ids in stops_per_trip.items():

        shape_id = shape_per_trip.get(trip_id)

        if not shape_id:
            continue

        shape_geometry = shape_geometries.get(shape_id)

        if shape_geometry is None or shape_geometry.is_empty:
            continue

        stop_projections_per_trip[trip_id] = (
            netex_helper_map_stops_to_shape_distances(
                stop_ids,
                stop_coordinates,
                shape_geometry,
            )
        )

    return stop_projections_per_trip   

def netex_helper_create_line_string_segments_between_stop_pairs(
    stop_pair: tuple[str, str],
    stop_distances_along_shape: dict[str, float],
    shape_geometry: LineString,
) -> BaseGeometry:
    """
    Build ServiceLink geometry between two stops.
    """

    from_stop, to_stop = stop_pair

    start_distance = stop_distances_along_shape[from_stop]
    end_distance = stop_distances_along_shape[to_stop]

    return netex_helper_cut_shape_between_distances(
        shape_geometry,
        start_distance,
        end_distance,
    )
    
    
def netex_helper_create_service_link_info(
    stops_per_trip: dict[str, list[str]],
    stop_coordinates: dict[str, Point],
    shape_geometries: dict[str, LineString],
    shape_per_trip: dict[str, str],
):
    """
    Yield ServiceLink information objects.
    """

    if (
        not stops_per_trip
        or not stop_coordinates
        or not shape_geometries
        or not shape_per_trip
    ):
        logger.error("Missing required input data")
        return

    stop_pairs_per_trip = (
        netex_helper_split_stops_into_pairs(
            stops_per_trip
        )
    )

    stop_projections_per_trip = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip,
        )
    )

    for trip_id, stop_pairs in stop_pairs_per_trip.items():

        shape_id = shape_per_trip.get(trip_id)

        if not shape_id:
            continue

        shape_geometry = shape_geometries.get(shape_id)

        stop_distances = (
            stop_projections_per_trip.get(trip_id)
        )

        if (
            shape_geometry is None
            or shape_geometry.is_empty
            or not stop_distances
        ):
            continue

        for pair in stop_pairs:

            from_stop, to_stop = pair

            geometry = (
                netex_helper_create_line_string_segments_between_stop_pairs(
                    pair,
                    stop_distances,
                    shape_geometry,
                )
            )

            yield {
                "trip_id": trip_id,
                "from_stop": from_stop,
                "to_stop": to_stop,
                "distance": (
                    stop_distances[to_stop]
                    - stop_distances[from_stop]
                ),
                "geometry": geometry,
            }
    
def netex_helper_convert_line_string_to_string(line: LineString) -> str:
    """
    Convert LineString geometry to GML posList string.
    """

    return " ".join(f"{x:.6f} {y:.6f}" for x, y in line.coords)

def netex_helper_build_service_link(service_link_data: dict[str, Any]) -> etree.Element:
    
    geometry_projected = service_link_data["geometry"]

    gtfs_shape_line_string_geometry = netex_helper_transform_line_string_to_wgs84(geometry_projected)

    pos_list = netex_helper_convert_line_string_to_string(gtfs_shape_line_string_geometry)

    distance = service_link_data["distance"]
    from_stop = service_link_data["from_stop"]
    to_stop = service_link_data["to_stop"]

    service_link = etree.Element("ServiceLink", id = f"{config.NETEX_AUTHORITY}:ServiceLink:{from_stop}_{to_stop}", version = "1", nsmap=NSMAP)
    
    etree.SubElement(service_link, "Distance").text = f"{distance:.6f}"

    projections = etree.SubElement(service_link, "projections")
    link_sequence_projection = etree.SubElement(projections, "LinkSequenceProjection", id = f"{config.NETEX_AUTHORITY}:LinkSequenceProjection:{from_stop}_{to_stop}", version = "1")
    
    line_string_info = etree.SubElement(link_sequence_projection, f"{{{GIS_NS}}}LineString", srcName = "4326", srcDimension = "2")
    line_string_info.set(f"{{{GIS_NS}}}id", f"LS_{from_stop}_{to_stop}")

    etree.SubElement(line_string_info, f"{{{GIS_NS}}}posList", count = str(len(gtfs_shape_line_string_geometry.coords)), srcDimension = "2").text = pos_list
    
    etree.SubElement(service_link, "FromPointRef", ref = f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{from_stop}", version = "1")
    etree.SubElement(service_link, "ToPointRef", ref = f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{to_stop}", version = "1")


    return service_link
    
def netex_convert_shapes_to_service_link(service_links: list[dict]) -> etree.Element:

    for service_link_data in service_links:

        xml_element = netex_helper_build_service_link(
            service_link_data
        )

        xml_string = etree.tostring(
            xml_element,
            encoding="unicode",
        )

        yield xml_string
    

##########################################################
# GtfsCalendarRule and GtfsCalendarDateRule

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

        parts = day_type_id.split(":")

        if len(parts) != 5:
            logger.error("Invalid ID for GtfsCalendarRule: %r", day_type_id)
            return None

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

        # Split the ID and extract value from NGSI-LD URN
        parts = day_type_id.split(":")

        if len(parts) != 6:
            logger.error("Invalid ID for GtfsCalendarDateRule: %r", day_type_id)
            return None

        day_type_id_value = parts[-2]

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

    parts = period_id.split(":")
    if len(parts) != 5:
        logger.error("Invalid ID for GtfsCalendarRule: %r", period_id)
        return None

    # Extract value from NGSI-LD URN
    period_id_value = parts[-1]

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

        if len(parts) != 6:
            logger.error("Invalid ID for GtfsCalendarRule: %r", day_type_assignment_id)
            return None

        day_type_id_value = parts[-2]
        raw_date = parts[-1]

        # Determine availability based on the exception type (1 for added service, 2 for removed service)
        exception_type = entity.get("exceptionType", {}).get("value")
        is_available = exception_type == 1
        is_available_value = "true" if is_available else "false"

        # Build DayTypeAssignment element with the extracted ID value, date, day type reference and availability
        day_type_assignment = etree.Element("DayTypeAssignment", order = str(index), version = "1", id = f"{config.NETEX_AUTHORITY}:DayTypeAssignment:{day_type_id_value}-{index}")

        etree.SubElement(day_type_assignment, "Date").text = datetime.strptime(raw_date, "%Y%m%d").strftime("%Y-%m-%d")

        etree.SubElement(day_type_assignment, "DayTypeRef", version = "1", ref = f"{config.NETEX_AUTHORITY}:DayType:{day_type_id_value}")

        etree.SubElement(day_type_assignment, "IsAvailable").text = is_available_value

        return day_type_assignment

    # ----------------------------------------
    # GtfsCalendarRule
    # ----------------------------------------
    elif entity_type == "GtfsCalendarRule":

        parts = day_type_assignment_id.split(":")
        if len(parts) != 5:
            logger.error("Invalid ID for GtfsCalendarRule: %r", day_type_assignment_id)
            return None

        day_type_id_value = parts[-1]

        # Build DayTypeAssignment element with the extracted ID value, operating period reference and day type reference
        day_type_assignment = etree.Element("DayTypeAssignment", order=str(index), version="1", id=f"{config.NETEX_AUTHORITY}:DayTypeAssignment:{day_type_id_value}-{index}")

        etree.SubElement(day_type_assignment, "OperatingPeriodRef", version = "1", ref = f"{config.NETEX_AUTHORITY}:OperatingPeriod:{day_type_id_value}")

        etree.SubElement(day_type_assignment, "DayTypeRef", version = "1", ref = f"{config.NETEX_AUTHORITY}:DayType:{day_type_id_value}-{index}")

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

# -------------------------------------------------------------
# NeTEx <ServiceCalendarFrame> containing <DayType>, <OperatingPeriod> and <DayTypeAssignment>
# -------------------------------------------------------------
def stream_service_calendar_frame(xml_file, calendars, calendar_dates) -> None:
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
    with xml_file.element("ServiceCalendarFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ServiceCalendarFrame:1"):

        netex_helper_stream_day_types(xml_file, all_entities)

        netex_helper_stream_operating_periods(xml_file, calendars)

        netex_helper_stream_day_type_assignments(xml_file, all_entities)

##########################################################
# GtfsRoute
# Need to cross-check the transport mode mapping with NeTEx
def netex_helper_get_gtfs_route_type_code(routes: list[dict[str, Any]]) -> dict[str, int]:
    
    route_type_per_route = {}
    
    for route in routes:
        
        route_id = route["id"]
        route_type = route["routeType"]["value"]
        
        if route_id not in route_type_per_route.keys():
            route_type_per_route[route_id] = route_type
            
    return route_type_per_route
        
def netex_helper_get_transport_mode_and_submode(gtfs_route_type_code: int) -> tuple:
    """
    Retrieves the NeTEx transport mode and submode based on the GTFS route type code.

    Args:
        gtfs_route_type_code: The GTFS route type code.

    Returns:
        A tuple containing the NeTEx transport mode and submode, or (None, None) if not found.
    """
    gtfs_to_netex_map = {
        0: ('tram', 'unknown'),
        1: ('metro', 'unknown'),
        2: ('rail', 'unknown'),
        3: ('bus', 'unknown'),
        4: ('water', 'unknown'),
        5: ('cableway', 'unkown'),
        6: ('cableway', 'unknown'),
        7: ('funicular', 'unknown'),
        11: ('trolleyBus', 'unknown'),
        12: ('rail', 'unknown'),
        100: ('rail', 'unknown'),
        101: ('rail', 'airportLinkRail'),
        102: ('rail', 'longDistance'),
        103: ('rail', 'interregionalRail'),
        105: ('rail', 'nightRail'),
        106: ('rail', 'regionalRail'),
        107: ('rail', 'touristRailway'),
        108: ('rail', 'airportLinkRail'),
        109: ('rail', 'regionalRail'),
        200: ('coach', 'unknown'),
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
        800: ('trolleyBus', 'unknown'), # not in the official documentation but found here https://github.com/entur/netex-gtfs-converter-java
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

def netex_convert_routes_to_lines(entity: dict[str, Any]) -> etree.Element:
    """
    Converts a GTFS Route entity into a NeTEx Line XML element.

    Args:
        entity (dict[str, Any]): GtfsRoute entity

    Returns:
        etree.Element: A NeTEx Line XML element populated with the corresponding
        route information.
    """

    # Extract route ID
    route_id = entity.get("id")
    route_id_value = route_id.split(":")[-1] if route_id else "unknown"

    # Create Line element
    line = etree.Element("Line", version="1", id=f"{config.NETEX_AUTHORITY}:Line:{route_id_value}")

    # Add line Name
    route_long_name = entity.get("name", {}).get("value")
    if route_long_name:
        line_name = etree.SubElement(line, "Name")
        line_name.text = route_long_name

    # Add line Description
    route_description = entity.get("description", {}).get("value")
    if route_description:
        line_description = etree.SubElement(line, "Description")
        line_description.text = route_description

    # Mapping between transport mode and NeTEx submode tags
    SUBMODE_TAG_MAP = {
        'rail': 'RailSubmode',
        'coach': 'CoachSubmode',
        'metro': 'MetroSubmode',
        'bus': 'BusSubmode',
        'trolleyBus': 'TrolleyBusSubmode',
        'tram': 'TramSubmode',
        'water': 'WaterSubmode',
        'cableway': 'TelecabinSubmode',
        'funicular': 'FunicularSubmode',
        'taxi': 'TaxiSubMode',
        'other': 'OtherSubMode'
    }

    # Get transport mode and submode from route type
    route_type = entity.get("routeType", {}).get("value")
    transport_mode_and_submode = netex_helper_get_transport_mode_and_submode(route_type)

    try:
        mode_text, submode_text = transport_mode_and_submode
    except (ValueError, TypeError):
        raise ValueError("transport_mode_and_submode must be a tuple of two strings.")

    # Add TransportMode element
    transport_mode = etree.SubElement(line, "TransportMode")
    transport_mode.text = mode_text

    # Get submode tag based on transport mode
    submode_tag = SUBMODE_TAG_MAP.get(mode_text)

    if not submode_tag:
        raise ValueError(f"Unknown Transport Mode: '{mode_text}'")

    # Add TransportSubmode element
    transport_submode_parent = etree.SubElement(line, "TransportSubmode")
    submode = etree.SubElement(transport_submode_parent, submode_tag)
    submode.text = submode_text

    # TODO: Move TransportMode and TransportSubmode logic to a helper function
    # Reference: https://github.com/entur/netex-gtfs-converter-java

    # Add line URL
    route_url = entity.get("route_url", {}).get("value")
    if route_url:
        line_url = etree.SubElement(line, "Url")
        line_url.text = route_url

    # Add line short name (PublicCode)
    route_short_name = entity.get("shortName", {}).get("value")
    if route_short_name:
        line_name = etree.SubElement(line, "PublicCode")
        line_name.text = route_short_name

    # Add operator references
    agency = entity.get("operatedBy", {}).get("object")
    if agency:
        agency_id = agency.split(":")[-1]

        line_operator_ref = etree.SubElement(line, "OperatorRef", ref=f"{agency_id}:Operator:{agency_id}")

        line_represented_by_group_ref = etree.SubElement(line,"RepresentedByGroupRef",ref=f"{agency_id}:Authority:{agency_id}Nett"
        )

    # Add presentation (colors)
    route_colour = entity.get("routeColor", {}).get("value")
    route_text_colour = entity.get("routeTextColor", {}).get("value")

    if route_colour or route_text_colour:
        presentation = etree.SubElement(line, "Presentation")

        if route_colour:
            line_colour = etree.SubElement(presentation, "Colour")
            line_colour.text = route_colour

        if route_text_colour:
            line_text_colour = etree.SubElement(presentation, "TextColour")
            line_text_colour.text = route_text_colour

    return line

def netex_helper_build_points_in_sequence_for_route(stops_per_trip: dict[str, list[str]], trip_id: str) -> etree.Element:
    
    points_in_sequence = etree.Element("pointsInSequence")

    stops = stops_per_trip.get(trip_id, [])
    
    for index, stop in enumerate(stops, start=1):
        point_on_route = etree.SubElement(points_in_sequence, "PointOnRoute", order = str(index), version = "1", id = f"{config.NETEX_AUTHORITY}:PointOnRoute:{trip_id}_{index}")
        
        route_point_ref = etree.SubElement(point_on_route, "RoutePointRef")
        route_point_ref.set("ref", f"{config.NETEX_AUTHORITY}:RoutePoint:{stop}")
        
    return points_in_sequence

# Questions to ask:
# Tips on ID creation
# For pointsInSequence should I copy the Quay data for the stops along the line
# Tips on IDs for shape segments
def netex_convert_trips_to_journey_patterns(entity: dict[str, Any], stops_per_trip: dict[str, list[str]]):
    
    id_value = entity.get("id")
    trip_id = id_value.split(":")[-1] if id_value else "unknown"
    
    journey_pattern = etree.Element("JourneyPattern", id = f"{config.NETEX_AUTHORITY}:JourneyPattern:{trip_id}", version = "1")
    
    name = entity.get("headSign", {}).get("value")
    if name:
        journey_pattern_name = etree.SubElement(journey_pattern, "Name")
        journey_pattern_name.text = name
        
    route = entity.get("route", {}).get("object")
    route_id = route.split(":")[-1]
    
    if route_id:
        journey_pattern_route = etree.SubElement(journey_pattern, "RouteRef")
        journey_pattern_route.set("ref", f"{config.NETEX_AUTHORITY}:Route:{route_id}")
        journey_pattern_route.set("version", "1")
    
    points_in_sequence = netex_helper_build_points_in_sequence_for_route(stops_per_trip, trip_id)
    
    journey_pattern.append(points_in_sequence)

    links_in_sequence = etree.SubElement(journey_pattern, "linksInSequence")
        
    return journey_pattern

# -----------------------------------------------------
# GtfsStop to NeTEx <ScheduledStopPoint>
# ----------------------------------------------------- 
def netex_helper_build_scheduled_stop_point(entity: dict[str, Any]) -> etree.Element | None:
    """
    Builds a NeTEx <ScheduledStopPoint> element from a GtfsStop entity.

    Args:
        entity: A single GtfsStop entity

    Returns:
        etree.Element | None
    """

    # Get entity type and ID
    entity_type = entity.get("type")
    stop_id = entity.get("id")

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
    stop_name = entity.get("stop_name", {}).get("value")

    # Build and return the <ScheduledStopPoint> element with the extracted ID value, name and location reference
    scheduled_stop_point = etree.Element("ScheduledStopPoint", version="1", 
                                         id=f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{stop_id_value}")

    if stop_name:
        etree.SubElement(scheduled_stop_point,"Name").text = stop_name

    etree.SubElement(scheduled_stop_point,"LocationRef", ref=f"{config.NETEX_AUTHORITY}:StopPlace:{stop_id_value}", version="1")

    return scheduled_stop_point

def netex_helper_stream_scheduled_stop_points(xml_file, entities: list[dict[str, Any]]) -> None:
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

        for entity in entities:

            # Build <ScheduledStopPoint> element
            scheduled_stop_point = netex_helper_build_scheduled_stop_point(entity)

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
def netex_helper_extract_routes_in_a_trip(trips: list[dict[str, Any]]) -> dict[str, str]:
    """
    Create a lookup dictionary which shows for each trip what is it's associated route

    Args:
        trips (list[dict[str, Any]]): list of GtfsTrip entities

    Returns:
        dict[str, str]: dictionary of `trip_id - route_id` 
    """
    # Create dictionary to store the data
    route_per_trip = {}
    
    for trip in trips:
        
        # Extract trip_id
        trip_id = trip["id"]
        
        # Extract route_id
        route_id = trip["route"]["object"]
        
        # Populate dictionary
        if trip_id not in route_per_trip.keys():
            route_per_trip[trip_id] = route_id
    
    # Return dictionary
    return route_per_trip

def netex_helper_get_transport_modes_per_stop(
    stops_per_trip: dict[str, list[str]],
    route_per_trip: dict[str, str],
    route_type_per_route: dict[str, int]
) -> dict[str, set[tuple[str, str]]]:
    """
    Creates a mapping of stop_id -> set of (transport_mode, submode)

    Returns:
        dict[str, set[tuple[str, str]]]
    """

    transport_modes_per_stop = {}

    for trip_id, stops in stops_per_trip.items():

        # Get route_id
        route_id = route_per_trip.get(trip_id)
        if not route_id:
            continue

        # Get route_type
        route_type = route_type_per_route.get(route_id)
        if route_type is None:
            continue

        # Convert to NetEx mode/submode
        transport_mode = netex_helper_get_transport_mode_and_submode(route_type)

        for stop_id in stops:

            if stop_id not in transport_modes_per_stop:
                transport_modes_per_stop[stop_id] = set()

            transport_modes_per_stop[stop_id].add(transport_mode)

    return transport_modes_per_stop

def netex_convert_stops_to_stop_place(entities: list[dict[str, Any]], transport_modes_per_stop: dict[str, set[tuple[str, str]]]) -> etree.Element:
    """
    Create <StopPlace> elements from a list of GtfsStop entities and store them in a <stopPlaces> container.

    Args:
        entities (list[dict[str, Any]]): List of GtfsStop entities

    Returns:
        etree.Element: <stopPlaces> container with <StopPlace> elements
    """
    # Used to store unique StopPlace XML elements
    stop_places_dict = {}

    # Iterate through the list of GtfsStop entities
    for index, entity in enumerate(entities, start = 1):

        # Check if entity is of proper type
        entity_type = entity["type"]
        if entity_type != "GtfsStop":
            continue
        
        # Extract stop_id
        stop_id = entity["id"]
        if not isinstance(stop_id, str) or ":" not in stop_id:
            logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
            continue
        stop_id_value = stop_id.split(":")[-1]
       
        # Create StopPlace element
        stop_place = etree.Element("StopPlace", version = "1", id = f"{config.NETEX_AUTHORITY}:StopPlace:{stop_id_value}")

        # Extract location type, name, code, description and coordinates
        location_type = entity.get("locationType", {}).get("value", 0)
        name_value = entity.get("name", {}).get("value")
        stop_code_value = entity.get("code", {}).get("value")
        description_value = entity.get("description", {}).get("value")
        coords = entity.get("location", {}).get("value", {}).get("coordinates")

        # Add Name, Description, PublicCode and Centroid elements if values are present
        if name_value:
            etree.SubElement(stop_place, "Name").text = name_value

        if description_value:
            etree.SubElement(stop_place, "Description").text = description_value

        if stop_code_value:
            etree.SubElement(stop_place, "PublicCode").text = str(stop_code_value)

        if coords:
            centroid = etree.SubElement(stop_place, "Centroid")
            location = etree.SubElement(centroid, "Location")
            etree.SubElement(location, "Longitude").text = str(coords[0])
            etree.SubElement(location, "Latitude").text = str(coords[1])

        # Extract wheelchair boarding and tts_stop_name for accessibility information
        wheelchair = entity.get("wheelchair_boarding", {}).get("value")
        tts_stop_name = entity.get("tts_stop_name", {}).get("value")

        # Add AccessibilityAssessment and AccessibilityLimitation elements if wheelchair boarding information is present
        if wheelchair:
            accessibility_assessment = etree.SubElement(stop_place, "AccessibilityAssessment", version = "1", id = f"{config.NETEX_AUTHORITY}:AccessibilityAssessment:{str(index)}")
            etree.SubElement(accessibility_assessment, "MobilityImpairedAccess").text = "partial"
            limitations = etree.SubElement(accessibility_assessment, "limitations")
            accessibility_limitation = etree.SubElement(limitations, "AccessibilityLimitation", version = "1", id = str(index))
            etree.SubElement(accessibility_limitation, "WheelchairAccess").text = "true"
            etree.SubElement(accessibility_limitation, "StepFreeAccess").text = "unknown"
            etree.SubElement(accessibility_limitation, "EscalatorFreeAccess").text = "unknown"
            etree.SubElement(accessibility_limitation, "LiftFreeAccess").text = "unknown"
            
            # If tts_stop_name is present, we can assume that audible signs are available, otherwise we set it to unknown
            if tts_stop_name:
                etree.SubElement(accessibility_limitation, "AudibleSignsAvailable").text = "true"
            else:
                etree.SubElement(accessibility_limitation, "AudibleSignsAvailable").text = "unknown"
            etree.SubElement(accessibility_limitation, "VisualSignsAvailable").text = "unknown"

        # Extract parent station information and add ParentSiteRef element if present
        parent_station = entity.get("hasParentStation", {}).get("object")
       
        if parent_station:
            parent_station_value = parent_station.split(":")[-1]
            etree.SubElement(stop_place, "ParentSiteRef", ref = f"{config.NETEX_AUTHORITY}:StopPlace:{parent_station_value}", version = "1")

        # Determine transport mode and submode for the stop based on the routes that pass through it
        mode = "unknown"
        submode = "unknown"
        
        # Get transport modes for the stop from the provided mapping
        transport_modes = transport_modes_per_stop.get(stop_id, set())

        # Choose the first transport mode and submode
        if transport_modes:
            mode, submode = sorted(transport_modes)[0]  
    
        # Add TransportMode and StopPlaceType elements
        etree.SubElement(stop_place, "TransportMode").text = mode
        etree.SubElement(stop_place, "StopPlaceType").text = submode
           
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

        # If the XML element is unique, add it to the dict so we remove duplicates
        if stop_id not in stop_places_dict:
            stop_places_dict[stop_id] = stop_place

    # Create stopPlaces container and populate it with the StopPlace XML elements
    stop_places = etree.Element("stopPlaces")
    for stop_place in stop_places_dict.values():
        stop_places.append(stop_place)

    # Return the stopPlaces container with all StopPlace elements
    return stop_places

# -----------------------------------------------------
# GtfsStop to NeTex <PassengerStopAssignment>
# Note: Have to ask if this is the correct way to add order
# -----------------------------------------------------
def netex_convert_stops_to_passenger_stop_assignment(entities: list[dict[str, Any]])  -> etree.Element:
    """
    Create <PassengerStopAssignment> elements from a list of GtfsStop entities and store them in a <stopAssignments> container.

    Args:
        entities (list[dict[str, Any]]): List of GtfsStop entities

    Returns:
        etree.Element: <stopAssignments> container with <PassengerStopAssignment> elements
    """
    # Used to store unique PassengerStopAssignment XML elements
    passenger_stop_assignment_dict = {}
        
    # Iterate through the list of GtfsStop entities
    for index, entity in enumerate(entities, start=1):
        
        # Check if entity is of proper type
        entity_type = entity["type"]
        if entity_type != "GtfsStop":
            continue
        
        # Extract stop_id
        stop_id = entity["id"]
        if not isinstance(stop_id, str) or ":" not in stop_id:
            logger.error("Invalid or missing ID for GtfsStop: %r", stop_id)
            continue
        stop_id_value = stop_id.split(":")[-1]
    
        # Create PassengerStopAssignment element
        passenger_stop_assignment = etree.Element("PassengerStopAssignment", order = str(index), version = "1", 
                                                id = f"{config.NETEX_AUTHORITY}:PassengerStopAssignment:{stop_id_value}")

        # Add ScheduledStopPointRef elements
        etree.SubElement(passenger_stop_assignment, "ScheduledStopPointRef", 
                        ref = f"{config.NETEX_AUTHORITY}:ScheduledStopPoint:{stop_id_value}", versionRef = "1")

        # Add QuayRef elements
        etree.SubElement(passenger_stop_assignment, "QuayRef", 
                         ref = f"{config.NETEX_AUTHORITY}:Quay:{stop_id_value}", version = "1")
        
        # If the XML element is unique, add it to the dict so we remove duplicates
        if stop_id not in passenger_stop_assignment_dict:
            passenger_stop_assignment_dict[stop_id] = passenger_stop_assignment
            
    # Create stopAssignments container
    stop_assignments = etree.Element("stopAssignments")
    
    # Append unique PassengerStopAssignment elements to the stopAssignments container
    for stop_id in passenger_stop_assignment_dict.values():
        stop_assignments.append(stop_id)

    # Return the stopAssignments container with all PassengerStopAssignment elements
    return stop_assignments
    
# -----------------------------------------------------
# GtfsStop to NeTex <RoutePoint> and <PointProjection>
# -----------------------------------------------------
def netex_helper_build_route_point(entity: dict[str, Any]) -> etree.Element | None:
    """
    Builds a NeTEx <RoutePoint> element from a single GtfsStop entity.

    Args:
        entity: A single GtfsStop entity

    Returns:
        etree.Element | None
    """
    # Get entity type and ID
    entity_type = entity.get("type")
    stop_id = entity.get("id")

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

def netex_helper_stream_route_points(xml_file, entities: list[dict[str, Any]]) -> None:
    """
    Streams RoutePoint elements into a <routePoints> container.

    Args:
        xml_file: Streaming XML writer
        entities: List of GtfsStop entities

    Returns:
        None
    """

    logger.info("Streaming RoutePoints")

    seen_ids = set()

    # Create container for <RoutePoint> elements
    with xml_file.element("routePoints"):

        for entity in entities:

            # Build <RoutePoint> element
            route_point = netex_helper_build_route_point(entity)

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
def netex_helper_get_route_id_and_name(gtfs_route_entities: list[dict[str, Any]]) -> dict[str, dict[str, str]]:

    general_route_info = {}

    for route_entity in gtfs_route_entities:

        entity_type = route_entity["type"]
        if entity_type != "GtfsRoute":
            continue

        route_id = route_entity["id"]
        if not isinstance(route_id, str) or ":" not in route_id:
            logger.error("Invalid or missing ID for GtfsRoute: %r", route_id)
            continue
        route_id_value = route_id.split(":")[-1]

        route_short_name = route_entity.get("shortName", {}).get("value")
        route_long_name = route_entity.get("name", {}).get("value")

        route_names = {}

        if route_short_name:
            route_names["route_short_name"] = route_short_name

        if route_long_name:
            route_names["route_long_name"] = route_long_name

        general_route_info[route_id_value] = route_names

    return general_route_info

def netex_helper_get_trip_direction(gtfs_trips_entites: list[dict[str, Any]]) -> dict[str, dict[str, str]]:

    trip_info = {}

    for trip_entity in gtfs_trips_entites:

        entity_type = trip_entity["type"]
        if entity_type != "GtfsTrip":
            continue

        trip_id = trip_entity["id"]
        if not isinstance(trip_id, str) or ":" not in trip_id:
            logger.error("Invalid or missing ID for GtfsTrip: %r", trip_id)
            continue
        trip_id_value = trip_id.split(":")[-1]

        route_id = trip_entity["route"]["object"]
        route_id_value = route_id.split(":")[-1]

        direction_string = ""
        direction_id = trip_entity.get("direction", {}).get("value")
        if direction_id:
            direction_string = "outbound" if direction_id == 0 else "inbound"

        info = {}

        info["route_id"] = route_id_value
        if direction_id:
            info["direction"] = direction_string

        trip_info[trip_id_value] = info

    return trip_info

def netex_helper_group_trips_by_route_direction_and_sequence(route_id_and_direction: dict[str, dict[str, str]], stop_sequence: dict[str, list[str]]):

    groups = {}

    for trip_id in route_id_and_direction:

        route_id = route_id_and_direction[trip_id]["route_id"]
        direction = route_id_and_direction[trip_id].get("direction")

        sequence = stop_sequence[trip_id]
        if not sequence:
            continue

        key = (route_id, direction, tuple(sequence))

        if key not in groups:
            groups[key] = []

        groups[key].append(trip_id)

    return groups

def netex_helper_create_route_structures(trip_groups: dict, route_names: dict[str, dict[str, str]]):
    routes = []

    for key, trip_ids in trip_groups.items():

        route_id, direction, sequence = key

        names = route_names.get(route_id, {})
        route_short_name = names.get("route_short_name")
        route_long_name = names.get("route_long_name")
 

        route_data = {}

        route_data["route_id"] = route_id
        route_data["direction"] = direction
        if route_short_name:
            route_data["route_short_name"] = route_short_name

        if route_long_name:
            route_data["route_long_name"] = route_long_name

        route_data["stop_sequence"] = list(sequence)
        route_data["trip_ids"] = trip_ids

        routes.append(route_data)

    return routes

def netex_generate_routes(routes_structures):

    route_id_to_xml = {}

    route_groups = {}
    for route_structure in routes_structures:

        route_id = route_structure["route_id"]
        if route_id not in route_groups:
            route_groups[route_id] = []

        route_groups[route_id].append(route_structure)

    for route_id, route_candidates in route_groups.items():

        routes = etree.Element("routes")

        for index, route_info in enumerate(route_candidates, start = 1):
            sequence = route_info["stop_sequence"]

            route = etree.SubElement(routes, "Route", version = "1", id = f"{config.NETEX_AUTHORITY}:Route:{route_id}_{sequence[0]}_{sequence[-1]}")
            route_long_name = route_info.get("route_long_name")
            if route_long_name:
                etree.SubElement(route, "Name").text = route_long_name

            route_short_name = route_info.get("route_short_name")
            if route_short_name:
                etree.SubElement(route, "ShortName").text = route_short_name

            etree.SubElement(route, "LineRef", ref = f"{config.NETEX_AUTHORITY}:Line:{route_id}", version = "1")

            direction = route_info["direction"]
            if direction:
                etree.SubElement(route, "DirectionType").text = direction

            points_in_sequence = etree.SubElement(route, "pointsInSequence")

            for index, stop_id in enumerate(sequence, start = 1):
                point_on_route = etree.SubElement(points_in_sequence, "PointOnRoute", order = str(index), version = "1", 
                                                id = f"{config.NETEX_AUTHORITY}:PointOnRoute:{stop_id}")
                etree.SubElement(point_on_route, "RoutePointRef", ref = f"{config.NETEX_AUTHORITY}:RoutePoint:{stop_id}")

        route_id_to_xml[route_id] = routes

    return route_id_to_xml

def netex_helper_process_and_group_stop_times(stop_time_entities: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Groups NGSI-LD GtfsStopTime entities by trip, sorts them by stop sequence,
    and extracts specified fields.

    Args:
        stop_time_entities: A list of GtfsStopTime entities, each as a dictionary.

    Returns:
        A dictionary where keys are trip IDs and values are lists of
        stop information, sorted by stopSequence.
    """
    grouped_by_trip = {}

    # 1. Group entities by the 'hasTrip' relationship object
    for entity in stop_time_entities:
        trip_id = entity.get("hasTrip", {}).get("object")
        if trip_id:
            # If the trip_id is not yet a key in the dictionary, create it with an empty list
            grouped_by_trip.setdefault(trip_id, []).append(entity)

    processed_data = {}

    # 2. Sort each group and extract the required information
    for trip_id, stops in grouped_by_trip.items():
        # Sort the list of stops in-place based on the 'stopSequence' value
        stops.sort(key=lambda s: s.get("stopSequence", {}).get("value", 0))

        # 3. Extract only the fields you need
        extracted_stops = []
        for stop in stops:
            extracted_info = {
                "arrivalTime": stop.get("arrivalTime", {}).get("value"),
                "departureTime": stop.get("departureTime", {}).get("value"),
                "hasTrip": stop.get("hasTrip", {}).get("object").split(":")[-1],
                "hasStop": stop.get("hasStop", {}).get("object").split(":")[-1],
                "pickupType": stop.get("pickupType", {}).get("value"),
                "dropOffType": stop.get("dropOffType", {}).get("value"),
                "shapeDistTraveled": stop.get("shapeDistTraveled", {}).get("value"),
                "stopSequence": stop.get("stopSequence", {}).get("value") # Included for verification
            }
            extracted_stops.append(extracted_info)
        
        processed_data[trip_id] = extracted_stops

    return processed_data

def netex_convert_stop_times_to_service_journey(stop_times: dict[str, Any], grouped_stop_times: dict[str, list[dict[str, Any]]]):

    stop_time = stop_times.get("id")
    search_id = ":".join(stop_time.split(":")[:-1])
    stop_time_id = stop_time.split(":")[-2]

    stop_time_info = grouped_stop_times[search_id]

    service_journey = etree.Element("ServiceJourney", version = "1", id = f"{config.NETEX_AUTHORITY}:ServiceJourney:{stop_time_id}")

    journey_pattern_ref = etree.SubElement(service_journey, "JourneyPatternRef")
    journey_pattern_ref.set("ref", f"{config.NETEX_AUTHORITY}:JourneyPattern:{stop_time_info[0].get("hasTrip")}")

    passing_times = etree.SubElement(service_journey, "passingTimes")
    
    return service_journey

def netex_build_service_frame(xml_file, agency, stops, stop_coordinates, shape_linestrings, shape_per_trip, stops_per_trip):
    # Create ServiceFrame element and add it's subelements
    with xml_file.element("ServiceFrame", version="1", id=f"{config.NETEX_AUTHORITY}:ServiceCalendarFrame:1"):
        netex_helper_stream_networks(xml_file, agency)

        netex_helper_stream_route_points(xml_file, stops)

        netex_helper_stream_scheduled_stop_points(xml_file, stops)

    # service_links = etree.SubElement(service_frame, f"{{{NETEX_NS}}}serviceLinks")

    # service_links_data = netex_helper_create_service_link_info(stops_per_trip, stop_coordinates, shape_linestrings, shape_per_trip)

    # seen = set()

    # for service_link_data in service_links_data:

    #     key = (service_link_data["from_stop"], service_link_data["to_stop"], round(service_link_data["distance"], 6))

    #     if key in seen:
    #         continue

    #     seen.add(key)

    #     service_link = netex_helper_build_service_link(service_link_data)

    #     service_links.append(service_link)

    # passenger_stop_assignment = netex_convert_stops_to_passenger_stop_assignment(stops)
    # service_frame.append(passenger_stop_assignment)

    # return service_frame


def netex_create_shared_data_xml(
        agency: dict[str, Any], 
        stops: list[dict[str, Any]], 
        stop_coordinates: dict[str, Any], 
        shape_linestrings: dict[str, Any], 
        shape_per_trip: dict[str, Any], 
        stops_per_trip: dict[str, Any], 
        calendar: list[dict[str, Any]], 
        calendar_dates: list[dict[str, Any]]):
    
    with etree.xmlfile(f"_{config.NETEX_AUTHORITY}_shared_data.xml", encoding="utf-8") as xml_file:
        xml_file.write_declaration()

        with xml_file.element(f"{{{NETEX_NS}}}PublicationDelivery", nsmap=NSMAP, version="1"):
            xml_file.write(b"\n")
            with xml_file.element("dataObjects"):
                xml_file.write(b"\n")
                frame = netex_build_frame_defaults(agency)
                xml_file.write(frame, pretty_print=True)
                with xml_file.element("frames"):
                    resource_frame = netex_build_resource_frame(agency)
                    xml_file.write(resource_frame, pretty_print=True)
                    service_frame = netex_build_service_frame(xml_file, agency, stops, stop_coordinates, shape_linestrings, shape_per_trip, stops_per_trip)
                    xml_file.write(service_frame, pretty_print=True)
                    
                    stream_service_calendar_frame(xml_file, calendar, calendar_dates)

if __name__ == "__main__":

    city = "Sofia"
    header = orion_ld_define_header("gtfs_static")
    agencies = orion_ld_get_entities_by_type("GtfsAgency", header, city)
    stops = orion_ld_get_entities_by_type("GtfsStop", header, city)
    stop_times = orion_ld_get_entities_by_type("GtfsStopTime", header, city)
    shapes = orion_ld_get_entities_by_type("GtfsShape", header, city)
    trips = orion_ld_get_entities_by_type("GtfsTrip", header, city)
    routes = orion_ld_get_entities_by_type("GtfsRoute", header, city)
    calendar = orion_ld_get_entities_by_type("GtfsCalendarRule", header, city)
    calendar_dates = orion_ld_get_entities_by_type("GtfsCalendarDateRule", header, city)

    stop_coordinates = netex_helper_extract_stop_coordinates(stops)
    shape_linestrings = netex_helper_extract_shape_linestrings(shapes)
    shape_per_trip = netex_helper_map_trips_to_shapes(trips)
    stops_per_trip = netex_helper_extract_stops_in_a_trip(stop_times)

    for agency in agencies:
        netex_helper_set_netex_authority(agency)
        netex_create_shared_data_xml(agency, stops, stop_coordinates, shape_linestrings, shape_per_trip, stops_per_trip, calendar, calendar_dates)

    

    # print(len(seen))
    # # route_names = netex_helper_get_route_id_and_name(routes)
    # # trip_directions = netex_helper_get_trip_direction(trips)
    # # groups = netex_helper_group_trips_by_route_direction_and_sequence(trip_directions, stops_per_trip)
    # # route_data = netex_helper_create_route_structures(groups, route_names)
    # # netex_routes =netex_generate_routes(route_data)

    # # #pprint(stops_per_trip)
    # # #pprint(groups)
    # # pprint(route_data)

    # #for route_id, routes_xml in netex_routes.items():
    # #    xml_str = etree.tostring(
    # #        routes_xml,
    # #        pretty_print=True,
    # #        encoding="unicode"
    # #    )

    # #    print(f"--- Route group: {route_id} ---")
    # #    print(xml_str)

