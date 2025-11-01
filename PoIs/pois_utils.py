import os
import json
from typing import Any

def pois_read_file(file_path: str) -> list[dict[str, Any]]:
    """
    Extract NGSI-LD Entities from PoI file
    Args:
        file_path (str): Path to PoI file
    Returns:
        list[dict[str, Any]]: List of PoI entites in NGSI-LD format 
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File at path '{file_path}' is not found.")

    # Initialize an empty list to hold entities
    entities = []
    # Check if the data is an instance of a dictionary 
    if isinstance(data, dict):
        # If data is a dictionary, the entities should be under the "entities" key and be a list
        if "entities" in data and isinstance(data["entities"], list):
            entities = data["entities"]
        else:
            raise ValueError("Invalid NGSI-LD file structure — expected 'entities' key with a list value.")
    else:
        raise ValueError("Invalid NGSI-LD file structure — expected a JSON object.")

    # Returned entities or []
    return entities

def pois_get_ngsi_ld_data(keyword: str) -> list[dict[str, Any]]:
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
    file_path = os.path.join("PoIs", "data", file_name)
    
    # Function call to pois_read_file with the extracted file path
    ngsi_ld_data = pois_read_file(file_path)
    
    # Returned PoI entites from specified file
    return ngsi_ld_data


if __name__ == "__main__":
    ngsi_ld_data = pois_get_ngsi_ld_data("parks_gardens")
    print(json.dumps(ngsi_ld_data, indent=2, ensure_ascii=False))
