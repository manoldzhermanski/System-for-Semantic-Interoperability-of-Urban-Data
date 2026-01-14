import os
import json
from typing import Any
from pyproj import Transformer

def json_ld_read_file(file_path: str) -> list[dict[str, Any]]:
    """
    Load NGSI-LD entities from a JSON-LD file.

    Args:
        file_path (str): Path to the JSON-LD file.

    Returns:
        list[dict[str, Any]]: List of NGSI-LD entities.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON is malformed or missing the "entities" key.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    try:
        # Open the file and load JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File at path '{file_path}' is not found")

    # Validate that the root is a dictionary
    if not isinstance(data, dict):
        raise ValueError("Invalid NGSI-LD file structure — expected a JSON object")
        
    # Validate that "entities" key exists and is a list
    entities = data.get("entities")
    if not isinstance(entities, list):
        raise ValueError("Invalid NGSI-LD file structure — expected 'entities' key with a list value")    
    
    # Return the list of entities
    return entities

def json_ld_transform_coordinates_to_wgs84_coordinates(raw_data: list[dict[str, Any]]) -> None:
    """
    Transform NGSI-LD entity coordinates from EPSG:7801 to WGS84 (EPSG:4326).

    Supported geometry types:
    - Point: directly transformed
    - MultiPoint: the first point is selected and converted to Point

    Args:
        raw_data (List[Dict[str, Any]]):
            List of NGSI-LD entities whose coordinates will be transformed.

    Returns:
        None

    Notes:
        - Only entities containing a "location" attribute with a GeoProperty
          of type "Point" or "MultiPoint" are affected.
        - For "MultiPoint", only the first coordinate pair is preserved.
    """

    # Initialize CRS transformer: local CRS (EPSG:7801) -> WGS84 (EPSG:4326)
    # always_xy=True ensures (x, y) = (lon, lat) ordering
    transformer = Transformer.from_crs("EPSG:7801", "EPSG:4326", always_xy=True)

    # Iterate over all entities
    for entity in raw_data:

        # Skip entities without a location attribute
        if "location" not in entity:
            continue

        location_value = entity.get("location", {}).get("value", {})

        geometry_type = location_value.get("type")
        coordinates = location_value.get("coordinates")

        # Handle Point geometry
        if geometry_type == "Point" and isinstance(coordinates, list):
            x, y = coordinates
            location_value["coordinates"] = list(
                transformer.transform(x, y)
            )

        # Handle MultiPoint geometry
        elif geometry_type == "MultiPoint" and isinstance(coordinates, list):
            # Convert MultiPoint to Point using the first coordinate
            x, y = coordinates[0]
            location_value["type"] = "Point"
            location_value["coordinates"] = list(
                transformer.transform(x, y)
            )


def json_ld_get_ngsi_ld_data(keyword: str, base_dir: str = "json_ld") -> list[dict[str, Any]]:
    """
    Load NGSI-LD Point of Interest (PoI) entities based on a category keyword.

    The function:
    1. Maps a given keyword to a corresponding JSON-LD file
    2. Reads NGSI-LD entities from the file
    3. Transforms entity coordinates to WGS84 (EPSG:4326)
    4. Returns the transformed entities

    Args:
        keyword (str):
            Category identifier for PoIs.

            Allowed values:
            - "culture"
            - "health"
            - "kids"
            - "parks_gardens"
            - "public_transport"
            - "schools"
            - "sport"
            - "other"

    Returns:
        List[Dict[str, Any]]:
            List of NGSI-LD entities for the selected category,
            with coordinates transformed to WGS84.

    Raises:
        ValueError:
            If the provided keyword is not a supported PoI category.
        FileNotFoundError:
            If the mapped JSON-LD file does not exist.
        ValueError:
            If the JSON-LD file structure is invalid.
    """

    # Mapping between category keywords and JSON-LD filenames
    mapping = {
        "culture": "pois_culture_ngsi.jsonld",
        "health": "pois_health_ngsi.jsonld",
        "kids": "pois_kids_ngsi.jsonld",
        "parks_gardens": "pois_parks_gardens_ngsi.jsonld",
        "public_transport": "pois_public_transport_ngsi.jsonld",
        "schools": "pois_schools_ngsi.jsonld",
        "sport": "pois_sport_ngsi.jsonld",
        "other": "pois_other_ngsi.jsonld",
    }

    # Validate keyword
    if keyword not in mapping:
        raise ValueError(f"Unsupported PoIs category: {keyword}")

    # Build file path to the JSON-LD source
    file_name = mapping[keyword]
    file_path = os.path.join(base_dir, "data", file_name)

    # Read NGSI-LD entities from file
    ngsi_ld_data = json_ld_read_file(file_path)

    # Transform coordinates to WGS84
    json_ld_transform_coordinates_to_wgs84_coordinates(ngsi_ld_data)

    # Return processed entities
    return ngsi_ld_data