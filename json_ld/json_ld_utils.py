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
        raise FileNotFoundError(f"File at path '{file_path}' is not found.")

    # Validate that the root is a dictionary
    if not isinstance(data, dict):
        raise ValueError("Invalid NGSI-LD file structure — expected a JSON object.")
        
    # Validate that "entities" key exists and is a list
    entities = data.get("entities")
    if not isinstance(entities, list):
        raise ValueError("Invalid NGSI-LD file structure — expected 'entities' key with a list value.")    
    
    # Return the list of entities
    return entities
        


def json_ld_transform_coordinates_to_wgs84_coordinates(raw_data: list[dict[str, Any]]) -> None:
    transformer = Transformer.from_crs("EPSG:7801", "EPSG:4326", always_xy=True)
    for entity in raw_data:
        if "location" in entity and entity["location"]["value"]["type"] == "Point":
            entity["location"]["value"]["coordinates"] = list(transformer.transform(
                entity["location"]["value"]["coordinates"][0],
                entity["location"]["value"]["coordinates"][1]
            ))
        elif "location" in entity and entity["location"]["value"]["type"] == "MultiPoint":
            entity["location"]["value"]["type"] = "Point"
            entity["location"]["value"]["coordinates"] = list(transformer.transform(
                entity["location"]["value"]["coordinates"][0][0],
                entity["location"]["value"]["coordinates"][0][1]
            ))
            #transformed_coordinates = []
            #for coord in entity["location"]["value"]["coordinates"]:
            #    transformed_coord = list(transformer.transform(coord[0], coord[1]))
            #    transformed_coordinates.append(transformed_coord)
            #entity["location"]["value"]["coordinates"] = transformed_coordinates

def json_ld_get_ngsi_ld_data(keyword: str) -> list[dict[str, Any]]:
    """
    Based on a given keyword, the function extracts PoI data from different files
    Args:
        keyword (str): String which specifies which .json file to be read
    Allowed values:
        culture, health, kids, parks_gardens, public_transport, schools, sport, other
    Returns:
        list[dict[str, Any]]: Function call from pois_read_file
    """
    # Mapping base
    mapping = {
        "culture": ("pois_culture_ngsi.jsonld"),
        "heath": ("pois_health_ngsi.jsonld"),
        "kids": ("pois_kids_ngsi.jsonld"),
        "parks_gardens": ("pois_parks_gardens_ngsi.jsonld"),
        "public_transport": ("pois_public_transport_ngsi.jsonld"),
        "schools": ("pois_schools_ngsi.jsonld"),
        "sport": ("pois_sport_ngsi.jsonld"),
        "other": ("pois_other_ngsi.jsonld"),
    }
    
    # If keyword not in mapping dictionary, raise error
    if keyword not in mapping:
        raise ValueError(f"Unsupported PoIs category: {keyword}")
    
    # Extract file name and create file path
    file_name = mapping[keyword]
    file_path = os.path.join("json_ld", "data", file_name)
    
    # Function call to pois_read_file with the extracted file path
    ngsi_ld_data = json_ld_read_file(file_path)
    json_ld_transform_coordinates_to_wgs84_coordinates(ngsi_ld_data)
    
    # Returned PoI entites from specified file
    return ngsi_ld_data


if __name__ == "__main__":
    ngsi_ld_data = json_ld_get_ngsi_ld_data("parks_gardens")
    print(json.dumps(ngsi_ld_data, indent=2, ensure_ascii=False))
