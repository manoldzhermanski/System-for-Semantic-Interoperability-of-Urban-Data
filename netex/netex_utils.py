import sys
import json
import math
import xml.etree.ElementTree as ET
from typing import Iterator, Any
from pathlib import Path
from lxml import etree # type: ignore
from pyproj import Transformer
#from shapely.geometry import LineString, Point as ShapelyPoint
#from shapely.ops import substring

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_batches
from orion_ld.orion_ld_crud_operations import (
    orion_ld_define_header,
    orion_ld_get_entities_by_type
    )


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

############################
def netex_convert_agency_to_operator(entities: Iterator[list[dict[str, Any]]]) -> str:
    """
    Transforms NGSI-LD GtfsAgency entities to NeTEx Operator XML nested in a ResourceFrame.

    Args:
        entities: List iterator of NGSI-LD GtfsAgency
                  Required fields:
                  - agency_name
                  - agency_url
                  - agency_phone
                  - agency_email
                  - id

    Returns:
        XML string with ResourceFrame and Operator objects
    """

    # PublicationDelivery
    pub = etree.Element("PublicationDelivery", nsmap=NSMAP)
    pub.set("version", "1.15:NO-NeTEx-networktimetable:1.5")

    # CompositeFrame
    comp_frame = etree.SubElement(pub, "CompositeFrame", id="CompositeFrame:1", version="1")

    # ResourceFrame
    res_frame = etree.SubElement(comp_frame, "ResourceFrame", id="ResourceFrame:1", version="1")

    # organisations container
    organisations = etree.SubElement(res_frame, "organisations")

    for batch in entities:
        for entity in batch:
            
            id_value = entity.get("id")
    
            entity_id = id_value.split(":")[-1] if id_value else "unknown"
            city = id_value.split(":")[-2] if id_value else "unknown"
            name = entity.get("agency_name", {}).get("value")
            url = entity.get("agency_url", {}).get("value", "")
            phone = entity.get("agency_phone", {}).get("value", "")
            email = entity.get("agency_email", {}).get("value", "")

            operator = etree.SubElement(
                organisations,
                "Operator",
                version="1",
                id=f"{city}:Operator:{entity_id}"
            )

            # Name
            name_el = etree.SubElement(operator, "Name")
            name_el.text = name
            
            # Legal Name
            legal_name_el = etree.SubElement(operator, "LegalName")
            legal_name_el.text = name

            # ContactDetails
            contact = etree.SubElement(operator, "ContactDetails")
            if url:
                url_el = etree.SubElement(contact, "Url")
                url_el.text = url
            if phone:
                phone_el = etree.SubElement(contact, "Phone")
                phone_el.text = phone
            if email:
                email_el = etree.SubElement(contact, "Email")
                email_el.text = email

    return etree.tostring(pub, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")

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

# TO-DO: DayTypeAssignment has to be contained in dayTypeAssignments
#        dayTypeAssignments has to be contained in ServiceCalendarFrame 
def netex_convert_calendar_dates_to_day_type_assignment(entity: dict[str, Any]):

    id_value = entity.get("id", None)
    
    city = id_value.split(":")[-3] if id_value else "Unknown"
    service_id = id_value.split(":")[-2] if id_value else "Unknown"
    date = id_value.split(":")[-1] if id_value else "Unknown"
    
    exception_type = entity.get("exceptionType", {}).get("value")
    is_available = exception_type == 1
    is_available_value = "true" if is_available else "false"

    day_type_assignment = etree.Element("DayTypeAssignment")
    day_type_assignment.set("id", f"{city}:DayTypeAssignment:{service_id}-{date}")
    day_type_assignment.set("version", "0")

    if service_id is not None:
        service = etree.SubElement(day_type_assignment, "DayTypeRef")
        service.set("ref", f"{city}:DayType:{service_id}")
        service.set("version", "0")

    if date is not None:
        service_date = etree.SubElement(day_type_assignment, "Date")
        service_date.text = date

    if exception_type is not None:
        is_available_xml = etree.SubElement(day_type_assignment, "isAvailable")
        is_available_xml.text = is_available_value

    return day_type_assignment

def netex_convert_routes_to_lines(entity: dict[str, Any]):
    id_value = entity.get("id")
    route_id = id_value.split(":")[-1] if id_value else "unknown"
    city = id_value.split(":")[-2] if id_value else "unknown"

    line = etree.Element("Line")
    line.set("id", f"{city}:Line:{route_id}")
    line.set("version", "1")

    route_long_name = entity.get("name", {}).get("value")
    if route_long_name:
        line_name = etree.SubElement(line, "Name")
        line_name.text = route_long_name

    route_description = entity.get("description", {}).get("value")
    if route_description:
        line_description = etree.SubElement(line, "Description")
        line_description.text = route_description

    # TO-DO: WRITE A FUNCTION FOR THE TransportMode AND TransportSubmode
    # REFERENCE: https://github.com/entur/netex-gtfs-converter-java

    route_url = entity.get("route_url", {}).get("value")
    if route_url:
        line_url = etree.SubElement(line, "Url")
        line_url.text = route_url

    route_short_name = entity.get("shortName", {}).get("value")
    if route_short_name:
        line_name = etree.SubElement(line, "PublicCode")
        line_name.text = route_short_name

    agency = entity.get("operatedBy", {}).get("object")
    if agency:
        agency_id = agency.split(":")[-1]
        line_operator_ref = etree.SubElement(line, "OperatorRef")
        line_operator_ref.set("ref", f"{city}:Operator:{agency_id}")

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
    
def netex_helper_generate_scheduled_stop_points(stops: list[dict[str, Any]], city: str) -> etree.Element:

    scheduled_stop_points = etree.Element("scheduledStopPoints")

    for stop_index, stop_info in enumerate(stops, start=1):
        scheduled_stop_point = etree.SubElement(scheduled_stop_points, "ScheduledStopPoint")
        scheduled_stop_point.set("version", "1")
        scheduled_stop_point.set("id", f"{city}:ScheduledStopPoint:{stop_index}")
        
    return scheduled_stop_points
    
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
        {"id": "S1"},
        {"id": "S2"},
        {"id": "S3"},
        {"id": "S4"},
        {"id": "S5"},
    ]

    print(etree.tostring(netex_helper_generate_scheduled_stop_points(stops, city), pretty_print=True, encoding="unicode"))

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