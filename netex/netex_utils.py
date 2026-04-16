import sys
import json
import math
import logging
import xml.etree.ElementTree as ET
from typing import Iterator, Any
from pathlib import Path
from lxml import etree # type: ignore
from pyproj import Transformer
#from shapely.geometry import LineString, Point as ShapelyPoint
#from shapely.ops import substring
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_batches
from orion_ld.orion_ld_crud_operations import (
    orion_ld_define_header,
    orion_ld_get_entities_by_type
    )

logger = logging.getLogger("NeTEx_Converter")

NS = "http://www.netex.org.uk/netex"
GIS_NS = "http://www.opengis.net/gml/3.2"
NSMAP = {None: NS, "gis": GIS_NS}

Point = tuple[float, float]

wgs84_to_projected = Transformer.from_crs("EPSG:4326", "EPSG:7801", always_xy=True)
projected_to_wgs84 = Transformer.from_crs("EPSG:7801", "EPSG:4326", always_xy=True)

def netex_helper_transform_point_between_coordinate_systems(point: Point, to_epsg_7801: bool = True) -> Point:
    """
    Convert point between EPSG:4326 (lon, lat) and EPSG:7801 projected CRS.

    Args:
        point: (x, y) coordinates in the source CRS
        to_epsg_7801: If True, converts from WGS84 to projected CRS; if False, converts from projected CRS to WGS84
        
    Returns:
        Point: (x, y) coordinates in the target CRS
    """

    x, y = point
    transformer = wgs84_to_projected if to_epsg_7801 else projected_to_wgs84
    return transformer.transform(x, y)

def netex_helper_transform_line_string_to_wgs84(polyline_projected: list[Point]) -> list[Point]:
    """
    Transform a LineString from projected CRS (EPSG:7801) to WGS84 (EPSG:4326).
    Args:
        polyline_projected (list[Point]): LineString represented as a list of (x, y) coordinates in projected CRS

    Returns:
        list[Point]: LineString represented as a list of (x, y) coordinates in WGS84 CRS
    """

    polyline_wgs84 = []

    for point in polyline_projected:
        polyline_wgs84.append(netex_helper_transform_point_between_coordinate_systems(point, to_epsg_7801=False))

    return polyline_wgs84

def netex_helper_extract_stops_in_a_trip(stop_times: list[dict[str, Any]]) -> dict[str, list[str]]:
    """
    Create a lookup of all stops in a trip, ordered by their stop sequence.
    Args:
        stop_times (list[dict[str, Any]]): A list of stop time dictionaries

    Returns:
        dict[str, list[str]]: A dictionary mapping trip IDs to lists of stop IDs in order
    """
    
    # Create a lookup of all stops in a trip, ordered by their stop sequence
    stops_per_trip = {}
    
    # Traverse the retrieved stop times and populate the stops_per_trip dictionary
    for stop in stop_times:
        
        # Get trip ID
        trip_id = stop.get("hasTrip", {}).get("object")
        
        # Get stop ID
        stop_id = stop.get("hasStop", {}).get("object")
        
        # Get stop sequence number
        sequence = stop.get("stopSequence", {}).get("value")
        
        # Only consider stop times that have valid trip ID, stop ID, and stop sequence
        if trip_id and stop_id and sequence is not None:
            
            # If the trip ID is not already in the stops_per_trip dictionary, initialize it with an empty list
            if trip_id not in stops_per_trip:
                stops_per_trip[trip_id] = []
                
            # Append the stop ID and its sequence to the list of stops for the corresponding trip ID
            stops_per_trip[trip_id].append((stop_id, sequence))
            
    # After populating the stops_per_trip dictionary, sort the stops for each trip by their stop sequence
    for trip in stops_per_trip:
        stops_per_trip[trip].sort(key=lambda x: x[1])
        
        # Keep only the stop IDs
        stops_per_trip[trip] = [stop_id for stop_id, seq in stops_per_trip[trip]]  # Keep only stop IDs
            
    # Return the lookup of stops per trip
    return stops_per_trip

def netex_helper_extract_stop_coordinates(stops: list[dict[str, Any]]) -> dict[str, Point]:
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
    for stop in stops:

        # Get stop ID
        stop_id = stop.get("id")

        # Get stop coordinates
        longitude, latitude = stop.get("location", {}).get("value", {}).get("coordinates")

        # Only consider stops that have valid stop ID and coordinates
        if stop_id and longitude is not None and latitude is not None:

            # Transform the stop coordinates from WGS84 to the projected CRS (EPSG:7801)
            projected_point = netex_helper_transform_point_between_coordinate_systems((float(longitude), float(latitude)), \
                                                                                        to_epsg_7801=True)

            # Populate the stop_coordinates_projected dictionary with the stop ID and its projected coordinates
            stop_coordinates_projected[stop_id] = projected_point

    # Return the lookup of stop IDs to their projected coordinates
    return stop_coordinates_projected

def netex_helper_extract_shapes_linestrings(shapes: list[dict[str, Any]]) -> dict[str, list[Point]]:
    """
    For every shape, extract its LineString geometry as a list of (x, y) coordinates in the projected CRS (EPSG:7801).
    
    Args:
        shapes (list[dict[str, Any]]): A list of shape dictionaries

    Returns:
        dict[str, list[Point]]: A dictionary mapping shape IDs to their projected line strings.
    """
    
    # Create a lookup of shape ID to its LineString geometry in projected CRS
    shape_line_strings = {}

    # Traverse the retrieved shapes and populate the shape_line_strings dictionary
    for shape in shapes:

        # Get shape ID
        shape_id = shape.get("id")

        # Get shape points
        points = shape.get("location", {}).get("value", {}).get("coordinates", [])

        # Only consider shapes that have valid shape ID and points
        if shape_id is not None and points is not None:

            # Create a list to store the transformed points of the shape's LineString geometry
            transformed_line_string = []

            # Traverse each point from the LineString geometry
            for point in points:

                # Transform the point from WGS84 to the projected CRS (EPSG:7801)
                projected_point = netex_helper_transform_point_between_coordinate_systems(
                    (float(point[0]), float(point[1])), to_epsg_7801=True)

                # Append the transformed point
                transformed_line_string.append(projected_point)

            # Populate the shape_line_strings dictionary with the shape ID and its transformed LineString geometry
            shape_line_strings[shape_id] = transformed_line_string

    # Return the lookup of shape IDs to their LineString geometries in projected CRS
    return shape_line_strings

def netex_helper_map_trips_to_shapes(trips: list[dict[str, Any]]) -> dict[str, str]:
    """
    For every trip, extract the associated shape ID
    
    Args:
        trips (list[dict[str, Any]]): A list of trip dictionaries

    Returns:
        dict[str, str]: A dictionary mapping trip IDs to their associated shape IDs.
    """
    # Create a lookup of trip ID to its associated shape ID
    shapes_per_trip = {}

    # Traverse the retrieved trips and populate the shapes_per_trip dictionary
    for trip in trips:
        # Get trip ID
        trip_id = trip.get("id")
        
        # Get shape ID
        shape_id = trip.get("hasShape", {}).get("object")

        # Only consider trips that have valid trip ID and shape ID
        if trip_id and shape_id:
            
            # Populate the shapes_per_trip dictionary with the trip ID and its associated shape ID
            shapes_per_trip[trip_id] = shape_id

    # Return the lookup of trip IDs to their associated shape IDs
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
    trip_stop_pairs = {}

    # Traverse each trip and split its ordered list of stops into pairs of consecutive stops
    for trip, stops in stops_per_trip.items():

        # Create a list to store the stop pairs for the current trip
        pairs = []

        # Iterate through the list of stops and create pairs of consecutive stops
        for i in range(len(stops)-1):
            pairs.append((stops[i], stops[i+1]))

        # Populate the trip_stop_pairs dictionary with the trip ID and its list of stop pairs
        trip_stop_pairs[trip] = pairs

    # Return the dictionary mapping trip IDs to their lists of stop pairs
    return trip_stop_pairs

def netex_helper_cut_shape_between_distances(gtfs_shape: list[Point], start_d: float, end_d: float) -> list[Point]:
    """
    Cuts a LineString shape between two distances (in meters) along the shape.

    Args:
        gtfs_shape (list[Point]): List of (x, y) coordinates representing the shape's LineString in projected CRS
        start_d (float): Starting distance along the shape in meters
        end_d (float): Ending distance along the shape in meters

    Returns:
        list[Point]: List of (x, y) coordinates representing the cut shape's LineString in projected CRS
    """
    
    # If the end distance is less than or equal to the start distance, return an empty list
    if end_d <= start_d:
        return []

    # Create a LineString object from the GTFS shape coordinates
    line = LineString(gtfs_shape)

    # Use the substring function to cut the LineString between the specified distances
    subline = substring(line, start_d, end_d)

    # Convert the resulting subline back to a list of (x, y) coordinates
    return [(x, y) for x, y in subline.coords]
 
def netex_helper_calculate_stop_distance_along_shape(stop_coordinates: Point, gtfs_shape: list[Point]) -> float:
    """
    Calculates the distance along the shape for a given stop coordinate by projecting it onto the shape's LineString.

    Args:
        stop_coordinates (Point): (x, y) coordinates of the stop in projected CRS
        gtfs_shape (list[Point]): LineString represented as a list of (x, y) coordinates in projected CRS

    Returns:
        float: The distance along the shape for the given stop coordinate
    """
    # Create a LineString object from the GTFS shape coordinates
    line = LineString(gtfs_shape)
    
    # Create a Point object from the stop coordinates
    point = ShapelyPoint(stop_coordinates)

    # Project the point onto the LineString and get the distance along the line
    return line.project(point)

def netex_helper_map_stops_to_shape_distances(stop_ids: list[str], stop_coordinates_lookup: dict[str, Point], \
                            gtfs_shape: list[Point]) -> dict[str, float]:
    """
    For every stop in the trip, calculate the distance along the shape
    by projecting the stop coordinates onto the shape's LineString.
    
    Args:
    stop_ids: List of stop IDs in the trip
    stop_coordinates_lookup: Dictionary mapping stop IDs to their (x, y) coordinates in projected CRS
    gtfs_shape: List of (x, y) coordinates representing the shape's LineString in projected CRS
    
    Returns:
    Dictionary mapping stop IDs to their distance along the shape in meters
    """

    # Create a dictionary to store the distance along the shape for each stop
    stop_distances_along_shape = {}

    # Traverse each stop in the trip and calculate its distance along the shape
    for stop_id in stop_ids:

        # Get the stop coordinates from the lookup
        stop_coordinates = stop_coordinates_lookup[stop_id]

        # Calculate the distance along the shape for the stop by projecting it onto the shape's LineString
        distance_along_shape = netex_helper_calculate_stop_distance_along_shape(stop_coordinates, gtfs_shape)

        # Create a lookup of stop ID to distance along the shape
        stop_distances_along_shape[stop_id] = distance_along_shape

    # Return the lookup of stop IDs to their distance along the shape
    return stop_distances_along_shape
      
def netex_helper_for_every_trip_compute_stop_distances_along_shapes(stop_times: list[dict[str, Any]], stops: list[dict[str, Any]], shapes:list[dict[str, Any]], trips: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """
    For every trip, compute the distance along the shape for each stop in the trip 
    by projecting the stop coordinates onto the shape's LineString geometry.
    
    Args:
    stop_times (list[dict[str, Any]]): List of stop time dictionaries
    stops (list[dict[str, Any]]): List of stop dictionaries
    shapes (list[dict[str, Any]]): List of shape dictionaries
    trips (list[dict[str, Any]]): List of trip dictionaries
    
    Returns:
    Dictionary mapping trip IDs to dictionaries that map stop IDs to their distance along the shape in meters
    """

    # Extract the stops along side a trips
    stops_per_trip = netex_helper_extract_stops_in_a_trip(stop_times)

    # Extract all the stop coordinates
    stop_coordinates_lookup = netex_helper_extract_stop_coordinates(stops)

    # Extract all shape LineString geometries
    shape_line_strings = netex_helper_extract_shapes_linestrings(shapes)

    # Create a trip ID - shape ID look up dictionary
    shape_per_trip = netex_helper_map_trips_to_shapes(trips)

    stop_projections_per_trip = {}

    # Traverse each trip and calculate the distance along the shape for each stop in the trip 
    # by projecting the stop coordinates onto the shape's LineString geometry
    for trip_id, stop_ids in stops_per_trip.items():

        # Get the shape ID associated with the trip from the lookup
        shape_id = shape_per_trip.get(trip_id)

        # Only consider trips that have an associated shape ID and a LineString geometry for the shape
        if not shape_id:
            continue

        # Get the LineString geometry for the shape ID
        shape_line_string = shape_line_strings.get(shape_id)

        # Only consider valid LineString geometries
        if not shape_line_string:
            continue

        # For every stop in the trip, calculate the distance along the shape 
        # by projecting the stop coordinates onto the shape's LineString geometry
        stop_distances_along_shape = netex_helper_map_stops_to_shape_distances(
            stop_ids,
            stop_coordinates_lookup,
            shape_line_string
        )

        # Associate the calculated stop distances along the shape with the trip ID in the stop_projections_per_trip dictionary
        stop_projections_per_trip[trip_id] = stop_distances_along_shape

    # Return the dictionary mapping trip IDs to their stops and corresponding distances along the shape
    return stop_projections_per_trip    

def netex_helper_create_line_string_segments_between_stop_pairs(stop_pair: tuple[str, str],\
    stop_distances_along_shape: dict[str, float], gtfs_shape: list[Point]) -> list[Point]:
    """
    Build the geometry of a ServiceLink between two stops
    
    Args:
    stop_pair tuple[str, str]: A tuple containing the IDs of the from and to stops
    stop_distances_along_shape dict[str, float]: A dictionary mapping stop IDs to their distance along the shape in meters
    gtfs_shape list[Point]: List of (x, y) coordinates representing the shape's LineString in projected CRS
    
    Returns:
    list[Point]: A LineString segment between the two stops represented as a list of (x, y) coordinates in projected CRS
    """
    # Extract the stop IDs that form a pair
    from_stop, to_stop = stop_pair

    # Get the distance along the shape for each stop in the pair from the lookup
    start_distance = stop_distances_along_shape[from_stop]
    end_distance = stop_distances_along_shape[to_stop]

    # Return the LineString segment formed between the stop pair
    # by cutting the shape's LineString geometry between the two distances
    return netex_helper_cut_shape_between_distances(gtfs_shape, start_distance, end_distance)
    
def netex_helper_create_service_link_info(stop_times: list[dict[str, Any]], stops: list[dict[str, Any]],
                        shapes: list[dict[str, Any]], trips: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Create a list that contains information for each ServiceLink.
    The function extracts all the needed trips, the stops that comprises the trip and the LineString geometry 
    of the shape associated with the trip.
    Then, for every pair of consecutive stops in the trip, it calculates the segment of the shape's LineString geometry
    between them and its distance to be used as the ServiceLink geometry and distance respectively.
    Args:
        stop_times (list[dict[str, Any]]): List of stop time dictionaries
        stops (list[dict[str, Any]]): List of stop dictionaries
        shapes (list[dict[str, Any]]): List of shape dictionaries
        trips (list[dict[str, Any]]): List of trip dictionaries

    Returns:
        _type_: List of ServiceLink information dictionaries
    """
    # Extract all stops in a trip
    stops_per_trip = netex_helper_extract_stops_in_a_trip(stop_times)
    
    # Split the stops into pairs that form segments
    stop_pairs = netex_helper_split_stops_into_pairs(stops_per_trip)

    # Extract all LineString geometries of the shapes
    shape_line_strings = netex_helper_extract_shapes_linestrings(shapes)
    
    # Extract all shape IDs associated with trips
    shape_per_trip = netex_helper_map_trips_to_shapes(trips)

    # For every trip, compute the distance along the shape for each stop in the trip
    stop_projections_per_trip = netex_helper_for_every_trip_compute_stop_distances_along_shapes(stop_times, stops, shapes, trips)

    # Store the needed info to generate a ServiceLink
    service_links = []

    # Traverse each trip and for every pair of stops in the trip, build the geometry of the ServiceLink segment between them
    for trip_id, stop_pairs in stop_pairs.items():

        # Get shape ID associated with the trip ID
        shape_id = shape_per_trip.get(trip_id)

        if not shape_id:
            continue

        # Get the LineString geometry for the shape ID
        shape_line_string = shape_line_strings.get(shape_id)

        # Get the stop distances for every stop in the trip
        stop_distances = stop_projections_per_trip.get(trip_id)

        if not shape_line_string or not stop_distances:
            continue

        # Traverse every stop pair in the trip and create a LineString geometry segment between them
        for pair in stop_pairs:

            # Get the 2 stops that form a pair
            from_stop, to_stop = pair

            # Create the LineString geometry segment between them
            geometry = netex_helper_create_line_string_segments_between_stop_pairs(pair, stop_distances, shape_line_string)

            # Calculate the distance of the LineString segment
            distance = stop_distances[to_stop] - stop_distances[from_stop]

            # Append the generated ServiceLink info to the service_links list
            service_links.append(
                {
                "trip_id": trip_id,
                "from_stop": from_stop,
                "to_stop": to_stop,
                "distance": distance,
                "geometry": geometry
                }
            )

    # Return the ServiceLink info
    return service_links
    
def netex_helper_convert_line_string_to_string(gtfs_shape_line_string: list[Point]) -> str:
    """
    Convert a LineString from WGS84 (EPSG:4326) to a string representation.
    Args:
        gtfs_shape_line_string (list[Point]): LineString represented as a list of (x, y) coordinates in WGS84 CRS

    Returns:
        str: String representation of the LineString
    """
    return " ".join(f"{lon:.6f} {lat:.6f}" for lon, lat in gtfs_shape_line_string)

def netex_helper_build_service_link(service_link_data: dict[str, Any], city: str, index: int) -> etree.Element:

    geometry_projected = service_link_data["geometry"]

    gtfs_shape_line_string_geometry = netex_helper_transform_line_string_to_wgs84(geometry_projected)

    pos_list = netex_helper_convert_line_string_to_string(gtfs_shape_line_string_geometry)

    distance = service_link_data["distance"]

    from_stop = service_link_data["from_stop"]
    from_stop = from_stop.split(":")[-1]
    
    to_stop = service_link_data["to_stop"]
    to_stop = to_stop.split(":")[-1]

    service_link = etree.Element("ServiceLink")
    service_link.set("id", f"{city}:ServiceLink:{index}")
    service_link.set("version", "1")
    
    link_distance = etree.SubElement(service_link, "Distance")
    link_distance.text = f"{distance:.6f}"

    projections = etree.SubElement(service_link, "projections")
    link_sequence_projection = etree.SubElement(projections, "LinkSequenceProjection")
    link_sequence_projection.set("id", f"{city}:LinkSequenceProjection:{index}")
    link_sequence_projection.set("version", "1")
    
    line_string_info = etree.SubElement(link_sequence_projection, f"{{{GIS_NS}}}LineString")
    line_string_info.set("srsName", "4326")
    line_string_info.set("srsDimension", "2")
    line_string_info.set(f"{{{GIS_NS}}}id", f"LS_{index}")

    line_string = etree.SubElement(line_string_info, f"{{{GIS_NS}}}posList")
    line_string.set("count", str(len(gtfs_shape_line_string_geometry)))
    line_string.set("srsDimension", "2")
    line_string.text = pos_list
    
    from_point_ref = etree.SubElement(service_link, "FromPointRef")
    from_point_ref.set("ref", f"{city}:ScheduledStopPoint:{from_stop}")
    from_point_ref.set("version", "1")

    to_point_ref = etree.SubElement(service_link, "ToPointRef")
    to_point_ref.set("ref", f"{city}:ScheduledStopPoint:{to_stop}")
    to_point_ref.set("version", "1")

    return service_link
    
def netex_convert_shapes_to_service_link(service_links: list[dict], city: str) -> etree.Element:
    
    root = etree.Element("serviceLinks", nsmap=NSMAP)

    for index, service_link_data in enumerate(service_links, start=1):

        service_link_xml = netex_helper_build_service_link(service_link_data, city, index)

        root.append(service_link_xml)

    return root

def main():

    city = "Sofia"

    print("Building ServiceLinks...")
    
    header = orion_ld_define_header("gtfs_static")
    stop_times = orion_ld_get_entities_by_type("GtfsStopTime", header, city)
    stops = orion_ld_get_entities_by_type("GtfsStop", header, city)
    shapes = orion_ld_get_entities_by_type("GtfsShape", header, city)
    trips = orion_ld_get_entities_by_type("GtfsTrip", header, city)

    service_links = netex_helper_create_service_link_info(stop_times, stops, shapes, trips)

    print(f"Generated {len(service_links)} service links")

    print("Building XML...")

    xml_tree = netex_convert_shapes_to_service_link(service_links, city)

    print(etree.tostring(xml_tree, pretty_print=True, encoding="unicode"))

def netex_helper_build_points_in_sequence_for_route(stops_per_trip: dict[str, list[str]], trip_id: str, city: str) -> etree.Element:
    
    points_in_sequence = etree.Element("pointsInSequence")

    stops = stops_per_trip.get(trip_id, [])
    
    for index, stop in enumerate(stops, start=1):
        point_on_route = etree.SubElement(points_in_sequence, "PointOnRoute")
        point_on_route.set("order", str(index))
        point_on_route.set("version", "1")
        point_on_route.set("id", f"{city}:PointOnRoute:{trip_id}_{index}")
        
        route_point_ref = etree.SubElement(point_on_route, "RoutePointRef")
        route_point_ref.set("ref", f"{city}:RoutePoint:{stop}")
        
    return points_in_sequence

##########################################################
# GtfsAgency
# For FrameDefaults: How should I handle the timezone and default language and if there are multiple timezones in agency.txt
# Questions: Observing the Netur Dataset we see a mapping of GTFS Agency to NeTEx Authority.
# We already discussed that we will map GTFS Agency also to Operator but this begs the question - In general where does the Operator data come from if not observed in the GTFS files ?

def netex_build_frame_defaults(agency: dict[str, Any]) -> etree.Element:
    """
    Builds the NeTEx FrameDefaults element from a GtfsAgency entity

    Args:
        agency: GtfsAgency entity

    Returns:
        An lxml.etree.Element object representing the <FrameDefaults> XML structure.
    """
    # Extract from the entity it's timezone (required field) and language (optional field)
    time_zone = agency.get("agency_timezone", {}).get("value")
    language = agency.get("agency_lang", {}).get("value")

    # Build FrameDefaults
    frame_defaults = etree.Element("FrameDefaults")

    # Add DefaultLocale element
    frame_default_locale = etree.SubElement(frame_defaults, "DefaultLocale")

    # Add TimeZone element
    frame_default_time_zone = etree.SubElement(frame_default_locale, "TimeZone")
    frame_default_time_zone.text = time_zone

    # If the optional language field is provided, add the DefaultLanguage element
    if language:
        frame_default_default_language = etree.SubElement(frame_default_locale, "DefaultLanguage")
        frame_default_default_language.text = language

    # Return FrameDefaults
    return frame_defaults

def netex_convert_agency_to_authority(entities: list[dict[str, Any]]) -> list[etree.Element]:
    """Converts a list of GtfsAgency entities into NeTEx Nordic 'Authority' XML elements.

    Args:
        entities: A list of GtfsAgency entities
    Returns:
        A list of lxml.etree.Element objects, where each element is a fully
        formed NeTEx <Authority> representing an agency from the input list.
    """
    # List to store Authority elements
    authority_list = []

    # Iterate through all agencies
    for index, entity in enumerate(entities, start = 1):

        # Get the agency id value
        try:
            agency_id = entity.get("id")
            agency_id_value = agency_id.split(":")[-1]
        except IndexError:
                logger.error("Invalid ID for GtfsAgency: %s", agency_id_value)

        # Get agency name
        agency_name = entity.get("agency_name", {}).get("value")

        # Build Authority XML element
        authority = etree.Element("Authority", version = "1", id = f"{agency_id_value}:Authority:{agency_id_value}_ID")

        # Set mandatory company number to index at which the element is at the input list
        authority_company_number = etree.SubElement(authority, "CompanyNumber")
        authority_company_number.text = str(index)

        # Set Name element
        authority_name = etree.SubElement(authority, "Name")
        authority_name.text = agency_name

        # Set LegalName element
        authority_legal_name = etree.SubElement(authority, "LegalName")
        authority_legal_name.text = agency_name

        # Get agency_fare_url (mandatory field), agency_phone (optional field) and agency_email (optional field)
        agency_phone = entity.get("agency_phone", {}).get("value")
        agency_fare_url = entity.get("agency_fare_url", {}).get("value")
        agency_email = entity.get("agency_email", {}).get("value")

        # Set ContactDetails element
        authority_contact_details = etree.SubElement(authority, "ContactDetails")

        # Set authority email if provided
        if agency_email:
            agency_email_address = etree.SubElement(authority_contact_details, "Email")
            agency_email_address.text = agency_email

        # Set authority phone if provided
        if agency_phone:
            authority_phone = etree.SubElement(authority_contact_details, "Phone")
            authority_phone.text = agency_phone

        # Set authority url
        authority_url = etree.SubElement(authority_contact_details, "Url")
        authority_url.text = agency_fare_url

        # Set OrganisationType to authority
        authority_organisation_type = etree.SubElement(authority, "OrganisationType")
        authority_organisation_type.text = "authority"

        # Append authority
        authority_list.append(authority)
   
    # Return authority_list
    return authority_list

def netex_convert_agency_to_operator(entities: list[dict[str, Any]]) -> list[etree.Element]:
    """Converts a list of GtfsAgency entities into NeTEx Nordic 'Operator' XML elements.

    Args:
        entities: A list of GtfsAgency entities
    Returns:
        A list of lxml.etree.Element objects, where each element is a fully
        formed NeTEx <Operator> representing an agency from the input list.
    """
    # List to store Operator elements
    operator_list = []

    # Iterate through all agencies
    for index, entity in enumerate(entities, start = 1):

        # Get the agency id value
        try:
            agency_id = entity.get("id")
            agency_id_value = agency_id.split(":")[-1]
        except IndexError:
                logger.error("Invalid ID for GtfsAgency: %s", agency_id_value)

        # Get agency name
        agency_name = entity.get("agency_name", {}).get("value")

        # Build Operator XML element
        operator = etree.Element("Operator", version = "1", id = f"{agency_id_value}:Operator:{agency_id_value}")

        # Set mandatory company number to index at which the element is at the input list
        operator_company_number = etree.SubElement(operator, "CompanyNumber")
        operator_company_number.text = str(index)

        # Set Name element
        operator_name = etree.SubElement(operator, "Name")
        operator_name.text = agency_name

        # Set LegalName element
        operator_legal_name = etree.SubElement(operator, "LegalName")
        operator_legal_name.text = agency_name

        # Get agency_fare_url (mandatory field), agency_phone (optional field) and agency_email (optional field)
        agency_phone = entity.get("agency_phone", {}).get("value")
        agency_fare_url = entity.get("agency_fare_url", {}).get("value")
        agency_email = entity.get("agency_email", {}).get("value")

        # Set ContactDetails element
        operator_contact_details = etree.SubElement(operator, "ContactDetails")

        # Set authority email if provided
        if agency_email:
            agency_email_address = etree.SubElement(operator_contact_details, "Email")
            agency_email_address.text = agency_email

        # Set authority phone if provided
        if agency_phone:
            authority_phone = etree.SubElement(operator_contact_details, "Phone")
            authority_phone.text = agency_phone

        # Set authority url
        authority_url = etree.SubElement(operator_contact_details, "Url")
        authority_url.text = agency_fare_url

        # Set OrganisationType to operator
        authority_organisation_type = etree.SubElement(operator, "OrganisationType")
        authority_organisation_type.text = "operator"

        # Append operator
        operator_list.append(operator)

    # Return operator_list
    return operator_list

def netex_build_resource_frame(agency: list[dict[str, Any]], city: str) -> etree.Element:
    """
    Builds a NeTEx ResourceFrame .

    This function acts as an orchestrator to create a complete ResourceFrame.
    It populates the frame by converting a list of GtfsAgency entities into both
    <Authority> and <Operator> XML elements, and then appends them under the
    <organisations> collection.

    Args:
        agency: A list of GtfsAgency entities
        city: The name of the city for which the transport data is
    Returns:
        An lxml.etree.Element object representing the complete <ResourceFrame>.
    """
    # Create ResourceFrame element and add it's organisations sub-element
    resource_frame = etree.Element("ResourceFrame", version = "1", id = f"{city}:ResourceFrame:1")
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

def netex_build_networks(agencies: list[dict[str, Any]]) -> list[etree.Element]:
    """Builds a list of NeTEx <Network> elements from GtfsAgency entities.

    Args:
        agencies: A list of GtfsAgency entities

    Returns:
        A list of lxml.etree.Element objects, where each element is a
        <Network> for an agency.
    """
    # List to store the Network elements
    network_list = []

    # Traverse through all agencies
    for agency in agencies:

        # Get network id value
        try:
            network_id = agency.get("id")
            network_id_value = network_id.split(":")[-1]
        except IndexError:
                logger.error("Invalid ID for GtfsAgency: %s", network_id_value)

        # Get network name
        agency_name = agency.get("agency_name",{}).get("value")

        network = etree.Element("Network", version = "1", id = f"{network_id_value}:Network:{network_id_value}Nett")
        network_name = etree.SubElement(network, "Name")
        network_name.text = agency_name

        # Make authority reference
        network_authority_ref = etree.SubElement(network, "AuthorityRef", ref = f"{network_id_value}:Authority:{network_id_value}_ID", version = "1")

        # Append network
        network_list.append(network)

    # Return network_list
    return network_list
   
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

def netex_convert_calendar_or_calendar_dates_to_day_type(entities: list[dict[str, Any]]) -> etree.Element:
    """
    Converts a list of GtfsCalendarRule or GtfsCalendarDateRule entities into a NeTEx <dayType> XML element.

    Args:
        entities: A list of GtfsCalendarRule or GtfsCalendarDateRule entites which are validated beforehand

    Returns:
        An lxml.etree.Element object representing the <dayTypes> container
        with <DayType> children for each valid entity.
    """
    logger.debug("Converting %d GtfsCalendarDateRule / GtfsCalendarRule entities to DayTypes", len(entities))

    # Used to store unique DayType XML elements
    day_types_dict = {}

    for entity in entities:
       
        # Get the Gtfs NGSI-LD entity id and type
        day_type_id = entity.get("id")
        entity_type = entity.get("type")

        if not entity_type or not day_type_id:
            continue
       
        # Used to generate the DayType id
        final_id = ""

        # Process the GtfsCalendarRule as it's of higher priority
        if entity_type == "GtfsCalendarRule":

            try:
                # Get id value and city
                day_type_id_value = day_type_id.split(":")[-1]
                city = day_type_id.split(":")[-2]
            except IndexError:
                logger.error("Invalid ID for GtfsCalendarRule: %s", day_type_id_value)
                continue

            # Generate the DayType id
            final_id = f"{city}:DayType:{day_type_id_value}"
           
            logger.debug("Creating DayType for %s (%s)", day_type_id_value, entity_type)
       
            # Create DayType element and it's meta-data
            day_type = etree.Element("DayType", version = "1", id = final_id)
            day_type_properties = etree.SubElement(day_type, "properties")
            day_type__property_of_day = etree.SubElement(day_type_properties, "PropertyOfDay")
            day_type_days_of_week = etree.SubElement(day_type__property_of_day, "DaysOfWeek")
            day_type_days_of_week.text = netex_helper_day_type_get_active_days(entity)

            # Add DayType element generated by GtfsCalendarRule as it's of higher priority
            day_types_dict[final_id] = day_type

        # Process the GtfsCalendarDateRule as it's of lower priority
        elif entity_type == "GtfsCalendarDateRule":

            try:
                # Get id value and city
                day_type_id_value = day_type_id.split(":")[-2]
                city = day_type_id.split(":")[-3]
            except IndexError:
                logger.error("Invalid ID for GtfsCalendarRule: %s", day_type_id_value)
                continue

            # Generate the DayType id
            final_id = f"{city}:DayType:{day_type_id_value}"
           
            logger.debug("Creating DayType for %s (%s)", day_type_id_value, entity_type)

            # Add DayType ONLY if one doesn't already exist.
            if final_id not in day_types_dict:
                day_type = etree.Element("DayType", version = "1", id = final_id)
                day_types_dict[final_id] = day_type
                           
        else:
            logger.error("Unsupported entity type: %s, id: %s", entity_type, day_type_id)

    # Create dayTypes container and populate it with the DayType XML elements
    day_types = etree.Element("dayTypes")
    for final_id in day_types_dict.keys():
        day_types.append(day_types_dict[final_id])
   
    logger.info("DayType conversion completed")
    logger.info("Created %d DayTypes", len(day_types))
   
    return day_types

def netex_convert_calendar_to_operating_period(entities: list[dict[str, Any]]) -> etree.Element:
    """
    Converts a list of GtfsCalendarRule entities into a NeTEx <OperatingPeriod> XML element.

    Args:
        entities: A list of GtfsCalendarRule entities

    Returns:
        An lxml.etree.Element object for the <operatingPeriods> container,
        containing a unique set of <OperatingPeriod> children.
    """
    # Used to store unique OperatingPeriod XML elements
    operating_period_dict = {}

    logger.debug("Converting %d GtfsCalendarRule entities to OperatingPeriod", len(entities))

    for period in entities:

        # Get the Gtfs NGSI-LD entity id
        period_id = period.get("id")
       
        # Used to generate the OperatingPeriod id
        final_id = ""
       
        try:
            # Get id value and city
            period_id_value = period_id.split(":")[-1]
            city = period_id.split(":")[-2]
        except IndexError:
                logger.error("Invalid ID for GtfsCalendarRule: %s", period_id_value)
                continue
       
        logger.debug("Creating OperatingPeriod for %s", period_id_value)
       
        # Generate the OperatingPeriod id
        final_id = f"{city}:OperatingPeriod:{period_id_value}"

        # Get FromDate and convert it from YYYYMMDD to ISO 8601 format
        from_date = period.get("startDate", {}).get("value")
        from_date_iso = netex_helper_convert_yyyymmdd_date_to_iso_date(from_date)

        # Get ToDate and convert it from YYYYMMDD to ISO 8601 format
        to_date = period.get("endDate", {}).get("value")
        to_date_iso = netex_helper_convert_yyyymmdd_date_to_iso_date(to_date)

        # Generate OperatingPeriod XML elements
        operating_period = etree.Element("OperatingPeriod", version = "1", id = final_id)

        operating_period_from_date = etree.SubElement(operating_period, "FromDate")
        operating_period_from_date.text = from_date_iso

        operating_period_to_date = etree.SubElement(operating_period, "ToDate")
        operating_period_to_date.text = to_date_iso

        # If the XML element is unique, add it to the dict so we remove duplicates
        if final_id not in operating_period_dict:
            operating_period_dict[final_id] = operating_period

    # Create operatingPeriods container and populate it with the OperatingPeriod XML elements
    operating_periods = etree.Element("operatingPeriods")
    for final_id in operating_period_dict.keys():
        operating_periods.append(operating_period_dict[final_id])

    logger.info("OperatingPeriod conversion completed")
    logger.info("Created %d OperatingPeriods", len(operating_periods))

    return operating_periods

def netex_convert_calendar_or_calendar_dates_to_day_type_assignment(entities: list[dict[str, Any]]):
    """
    Converts a list of GtfsCalendarRule or GtfsCalendarDateRule entities into a NeTEx <dayTypeAssignments> element.

    Args:
        entities: A list of dictionaries representing GtfsCalendarRule and
                  GtfsCalendarDateRule entities.

    Returns:
        An lxml.etree.Element for the <dayTypeAssignments> container
        containing a unique set of <DayTypeAssignment> children.
    """
    logger.debug("Converting %d GtfsCalendarDateRule / GtfsCalendarRule entities to DayTypeAssignments", len(entities))
   
    day_type_assignments = etree.Element("dayTypeAssignments")
   
    for index, entity in enumerate(entities):
       
        entity_type = entity.get("type")
        day_type_assignment_id = entity.get("id")
       
        if entity_type == "GtfsCalendarDateRule":
                       
            if day_type_assignment_id:
                day_type_id_value = day_type_assignment_id.split(":")[-2]
                city = day_type_assignment_id.split(":")[-3]
                raw_date = day_type_assignment_id.split(":")[-1]
               
                exception_type = entity.get("exceptionType", {}).get("value")
                is_available = exception_type == 1
                is_available_value = "true" if is_available else "false"
               
                logger.debug("Creating DayTypeAssignment for %s (%s)", day_type_id_value, entity_type)
           
                day_type_assignment = etree.SubElement(day_type_assignments, "DayTypeAssignment")
                day_type_assignment.set("order", str(index))
                day_type_assignment.set("version", "1")
                day_type_assignment.set("id", f"{city}:DayTypeAssignment:{day_type_id_value}-{index}")
               
                date = etree.SubElement(day_type_assignment, "Date")
                date.text = datetime.strptime(raw_date, "%Y%m%d").strftime("%Y-%m-%d")
               
                day_type_ref = etree.SubElement(day_type_assignment, "DayTypeRef")
                day_type_ref.set("version", "1")
                day_type_ref.set("ref", f"{city}:DayType:{day_type_id_value}")
               
                is_available_el = etree.SubElement(day_type_assignment, "IsAvailable")
                is_available_el.text = is_available_value
               
        elif entity_type == "GtfsCalendarRule":
           
            if day_type_assignment_id:
                day_type_id_value = day_type_assignment_id.split(":")[-1]
                city = day_type_assignment_id.split(":")[-2]
               
                logger.debug("Creating DayType for %s (%s)", day_type_id_value, entity_type)
           
                day_type_assignment = etree.SubElement(day_type_assignments, "DayTypeAssignment")
                day_type_assignment.set("order", str(index))
                day_type_assignment.set("version", "1")
                day_type_assignment.set("id", f"{city}:DayTypeAssignment:{day_type_id_value}")
               
                operating_period_ref = etree.SubElement(day_type_assignment, "OperatingPeriodRef")
                operating_period_ref.set("version", "1")
                operating_period_ref.set("ref", f"{city}:OperatingPeriod:{day_type_id_value}")
               
                day_type_ref = etree.SubElement(day_type_assignment, "DayTypeRef")
                day_type_ref.set("version", "1")
                day_type_ref.set("ref", f"{city}:DayType:{day_type_id_value}-{index}")
               
        else:
            logger.error("Unsupported entity type: %s, id: %s", entity_type, day_type_assignment_id)
   
    logger.info("DayTypeAssignment conversion completed")
    logger.info("Created %d DayTypeAssignments", len(day_type_assignments))
   
    return day_type_assignments

def netex_build_service_calendar_frame(calendars: list[dict[str, Any]], calendar_dates: list[dict[str, Any]], city: str) -> etree.Element:
    """
    Assembles a complete and valid NeTEx <ServiceCalendarFrame>.

    This function orchestrates the creation of the main components of a NeTEx
    ServiceCalendarFrame by calling specialized helper functions. It ensures that all
    definitions are de-duplicated and correctly structured according to the
    NeTEx Nordic standard.

    The process involves:
    1.  Combining all calendar-related entities (`calendars` and `calendar_dates`).
    2.  Creating a single, de-duplicated <dayTypes> container.
    3.  Creating a de-duplicated <operatingPeriods> container from `calendars`.
    4.  Creating a complete <dayTypeAssignments> container from all entities.

    Args:
        calendars: A list of entities from `calendar.txt` (GtfsCalendarRule).
        calendar_dates: A list of entities from `calendar_dates.txt` (GtfsCalendarDateRule).
        city: The city identifier used for creating unique NeTEx IDs.

    Returns:
        A complete and valid lxml.etree.Element for the <ServiceCalendarFrame>.
    """
    logger.info("ServiceCalendarFrame has started")

    # Create ServiceCalendarFrame
    service_calendar_frame = etree.Element("ServiceCalendarFrame", version = "1", id = f"{city}:ServiceCalendarFrame:1")

    # Combine both GtfsCalendarRule and GtfsCalendarDateRule for creating the <DayType> and <DayTypeAssignment> XML elements
    all_entities = calendars + calendar_dates

    # Create and append <DayType> XML elements
    day_types = netex_convert_calendar_or_calendar_dates_to_day_type(all_entities)
    service_calendar_frame.append(day_types)

    # Create and append <OperatingPeriod> XML elements
    operating_periods = netex_convert_calendar_to_operating_period(calendars)
    service_calendar_frame.append(operating_periods)

    # Create and append <DayTypeAssignment> XML elements
    day_type_assignments = netex_convert_calendar_or_calendar_dates_to_day_type_assignment(all_entities)
    service_calendar_frame.append(day_type_assignments)
   
    logger.info("ServiceCalendarFrame creation is completed")
    return service_calendar_frame

##########################################################
# GtfsRoute
# Need to cross-check the transport mode mapping with NeTEx
def netex_helper_get_transport_mode_and_submode(gtfs_route_type_code: int) -> tuple:
    """
    Retrieves the NeTEx transport mode and submode based on the GTFS route type code.

    Args:
        gtfs_route_type_code: The GTFS route type code.

    Returns:
        A tuple containing the NeTEx transport mode and submode, or (None, None) if not found.
    """
    gtfs_to_netex_map = {
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

    # Extract route ID and city from entity ID
    route_id = entity.get("id")
    route_id_value = route_id.split(":")[-1] if route_id else "unknown"
    city = route_id.split(":")[-2] if route_id else "unknown"

    # Create Line element
    line = etree.Element("Line", version="1", id=f"{city}:Line:{route_id_value}")

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

# Questions to ask:
# Tips on ID creation
# For pointsInSequence should I copy the Quay data for the stops along the line
# Tips on IDs for shape segments
def netex_convert_trips_to_journey_patterns(entity: dict[str, Any], stops_per_trip: dict[str, list[str]]):
    
    id_value = entity.get("id")
    trip_id = id_value.split(":")[-1] if id_value else "unknown"
    city = id_value.split(":")[-2] if id_value else "unknown"
    
    journey_pattern = etree.Element("JourneyPattern")
    journey_pattern.set("id", f"{city}:JourneyPattern:{trip_id}")
    journey_pattern.set("version", "1")
    
    name = entity.get("headSign", {}).get("value")
    if name:
        journey_pattern_name = etree.SubElement(journey_pattern, "Name")
        journey_pattern_name.text = name
        
    route = entity.get("route", {}).get("object")
    route_id = route.split(":")[-1]
    
    if route_id:
        journey_pattern_route = etree.SubElement(journey_pattern, "RouteRef")
        journey_pattern_route.set("ref", f"{city}:Route:{route_id}")
        journey_pattern_route.set("version", "1")
    
    points_in_sequence = netex_helper_build_points_in_sequence_for_route(stops_per_trip, trip_id, city)
    
    journey_pattern.append(points_in_sequence)

    links_in_sequence = etree.SubElement(journey_pattern, "linksInSequence")
        
    return journey_pattern
    
def netex_helper_generate_scheduled_stop_points(stops: list[dict[str, Any]]) -> etree.Element:

    scheduled_stop_points = etree.Element("scheduledStopPoints")

    for stop_info in stops:
        stop = stop_info.get("id")
        
        if not stop:
            continue
        
        stop_id = stop.split(":")[-1]
        city = stop.split(":")[-2]
        scheduled_stop_point = etree.SubElement(scheduled_stop_points, "ScheduledStopPoint")
        scheduled_stop_point.set("version", "1")
        scheduled_stop_point.set("id", f"{city}:ScheduledStopPoint:{stop_id}")
        
    return scheduled_stop_points

def netex_convert_stops_to_stop_place(entity: dict) -> etree.Element:
    
    id_value = entity.get("id")
    
    stop_id = id_value.split(":")[-1] if id_value else "unknown"
    city = id_value.split(":")[-2] if id_value else "unknown"
    location_type = entity.get("locationType", {}).get("value", 0)

    name_value = entity.get("name", {}).get("value")
    code_value = entity.get("code", {}).get("value")

    coords = entity.get("location", {}).get("value", {}).get("coordinates")

    parent = entity.get("hasParentStation", {}).get("object")
    wheelchair = entity.get("wheelchair_boarding", {}).get("value")

    # --- CREATE STOPPLACE ---
    stopplace = etree.Element("StopPlace", nsmap=NSMAP)
    stopplace.set("id", f"{city}:StopPlace:{stop_id}")
    stopplace.set("version", "1")

    if name_value:
        name_el = etree.SubElement(stopplace, "Name")
        name_el.text = name_value

    # Parent reference
    if parent:
        parent_ref = etree.SubElement(stopplace, "ParentSiteRef")
        parent_ref.set("ref", f"{city}:StopPlace:{parent}")
        parent_ref.set("version", "1")

    # Coordinates
    if coords:
        centroid = etree.SubElement(stopplace, "Centroid")
        loc = etree.SubElement(centroid, "Location")
        etree.SubElement(loc, "Longitude").text = str(coords[0])
        etree.SubElement(loc, "Latitude").text = str(coords[1])

    # Accessibility
    if wheelchair is not None:
        access = etree.SubElement(stopplace, "AccessibilityAssessment")
        mobility = etree.SubElement(access, "MobilityImpairedAccess")

        if wheelchair == 1:
            mobility.text = "true"
        elif wheelchair == 2:
            mobility.text = "false"
        else:
            mobility.text = "unknown"

    # StopPlaceType (safe fallback for OTP)
    sptype = etree.SubElement(stopplace, "StopPlaceType")

    if location_type == 1:
        sptype.text = "station"
    else:
        sptype.text = "other"

    # --- CREATE QUAY FOR BOARDING POINTS ---
    if location_type in (0, 4):

        quays_container = etree.SubElement(stopplace, "quays")

        quay = etree.SubElement(quays_container, "Quay")
        quay.set("id", f"{city}:Quay:{stop_id}")
        quay.set("version", "1")

        if code_value:
            etree.SubElement(quay, "PublicCode").text = str(code_value)

        if coords:
            centroid = etree.SubElement(quay, "Centroid")
            loc = etree.SubElement(centroid, "Location")
            etree.SubElement(loc, "Longitude").text = str(coords[0])
            etree.SubElement(loc, "Latitude").text = str(coords[1])

    return stopplace
# TO-DO ADD ORDER AFTER GETTING A REPLY
def netex_helper_create_passenger_stop_assignment(stops: list[dict[str, Any]])  -> etree.Element:

    stop_assignments = etree.Element("stopAssignments")
    for stop_info in stops:
        stop = stop_info.get("id")
        
        if not stop:
            continue
        
        stop_id = stop.split(":")[-1]
        city = stop.split(":")[-2]
    
        passenger_stop_assignment = etree.SubElement(stop_assignments, "PassengerStopAssignment")
        passenger_stop_assignment.set("version", "1")
        passenger_stop_assignment.set("id", f"{city}:PassengerStopAssignment:{stop_id}")
        # TO-DO SET ORDER AFTER GETTING A REPLY
        #passenger_stop_assignment.set("order", )

        scheduled_stop_point_ref = etree.SubElement(passenger_stop_assignment, "ScheduledStopPointRef")
        scheduled_stop_point_ref.set("version", "1")
        scheduled_stop_point_ref.set("ref", f"{city}:ScheduledStopPoint:{stop_id}")

        quay_ref = etree.SubElement(passenger_stop_assignment, "QuayRef")
        quay_ref.set("ref", f"{city}:Quay:{stop_id}")

    return stop_assignments
    
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
    city = stop_time.split(":")[-3]

    stop_time_info = grouped_stop_times[search_id]

    service_journey = etree.Element("ServiceJourney")
    service_journey.add("version", "1")
    service_journey.add("id", f"{city}:ServiceJourney:{stop_time_id}")

    journey_pattern_ref = etree.SubElement(service_journey, "JourneyPatternRef")
    journey_pattern_ref.set("ref", f"{city}:JourneyPattern:{stop_time_info[0].get("hasTrip")}")

    passing_times = etree.SubElement(service_journey, "passingTimes")
    
    return service_journey

if __name__ == "__main__":
    #for batch in gtfs_static_get_ngsi_ld_batches("routes", "Sofia"):
    #    for ngsi_entity in batch:
    #        xml_element = netex_convert_routes_to_lines(ngsi_entity)
    #        print(etree.tostring(xml_element, pretty_print=True, encoding="unicode"))
    
    #stops_per_trip = netex_helper_extract_stops_in_a_trip("Sofia")
    #stop_pairs = netex_helper_split_stops_into_pairs(stops_per_trip)
    #print(json.dumps(stop_pairs, indent=2, ensure_ascii=False))
    
    #stops = netex_helper_extract_stop_coordinates("Sofia")
    #print(json.dumps(stops, indent=2, ensure_ascii=False))
    
    #shapes = netex_helper_extract_shapes_linestrings("Sofia")
    #print(json.dumps(shapes, indent=2, ensure_ascii=False))
    
    #shape_per_trip = netex_helper_extract_shape_per_trip("Sofia")
    #print(json.dumps(shape_per_trip, indent=2, ensure_ascii=False))
    
    #city = "Sofia"

    #stop_projections = build_stop_projections_for_trips(city)

    #for trip_id, stop_distances in stop_projections.items():
    #
    #    print(f"\nTrip: {trip_id}")
    #
    #    for stop_id, distance in stop_distances.items():
    #        print(f"  {stop_id} -> {distance:.2f} m")
    
    #main()
    #trip = {
    #        "id": f"urn:ngsi-ld:GtfsTrip:Sofia:T1",
    #        "type": "GtfsTrip",
    #        
    #        "route": {
    #            "type": "Relationship",
    #            "object": "urn:ngsi-ld:GtfsRoute:Sofia:R1"
    #        },
    #        
    #        "service": {
    #            "type": "Relationship",
    #            "object": "urn:ngsi-ld:GtfsService:S1"
    #        },
    #        
    #        "headSign": {
    #            "type": "Property",
    #            "value": "Head Sign"
    #        },
    #
    #        "shortName": {
    #            "type": "Property",
    #            "value": "Short Name"
    #        },
    #        
    #        "direction": {
    #            "type": "Property",
    #            "value": "Direction "
    #        },
    #
    #        "block": {
    #            "type": "Relationship",
    #            "object": "urn:ngsi-ld:GtfsBlock:Sofia:B1"
    #        },
    #        
    #        "hasShape": {
    #            "type": "Relationship",
    #            "object": "urn:ngsi-ld:GtfsShape:Sofia:S1"
    #        },
    #        
    #        "wheelChairAccessible": {
    #            "type": "Property",
    #            "value": "WheelChair"
    #        },
    #        
    #        "bikesAllowed": {
    #            "type": "Property",
    #            "value": "Bike"
    #        },
    #        
    #        "carsAllowed": {
    #            "type": "Property",
    #            "value": "Car"
    #        }
    #    }
    #print(etree.tostring(netex_convert_trips_to_journey_patterns(trip), pretty_print=True, encoding="unicode"))
    
    city = "Sofia"
    stops = [
        {"id": "urn:ngsi-ld:GtfsStop:Sofia:S1"},
        {"id": "urn:ngsi-ld:GtfsStop:Sofia:S2"},
        {"id": "urn:ngsi-ld:GtfsStop:Sofia:S3"},
        {"id": "urn:ngsi-ld:GtfsStop:Sofia:S4"},
        {"id": "urn:ngsi-ld:GtfsStop:Sofia:S5"},
    ]

    print(etree.tostring(netex_helper_generate_scheduled_stop_points(stops), pretty_print=True, encoding="unicode"))
    print(etree.tostring(netex_helper_create_passenger_stop_assignment(stops), pretty_print=True, encoding="unicode"))

    #header = orion_ld_define_header("gtfs_static")
    #stop_times = orion_ld_get_entities_by_type("GtfsStopTime", header, city)
    #stops = orion_ld_get_entities_by_type("GtfsStop", header, city)
    #shapes = orion_ld_get_entities_by_type("GtfsShape", header, city)
    #trips = orion_ld_get_entities_by_type("GtfsTrip", header, city)
    
    #stops_per_trip = netex_helper_extract_stops_in_a_trip(stop_times)

    # Root XML
    #journey_patterns_root = etree.Element("journeyPatterns")

    #for trip in trips:
    #    journey_pattern = netex_convert_trips_to_journey_patterns(
    #        trip,
    #        stops_per_trip
    #    )
    #    
    #    journey_patterns_root.append(journey_pattern)
    #
    #print(etree.tostring(journey_patterns_root, pretty_print=True, encoding="unicode"))