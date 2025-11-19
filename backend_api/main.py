from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orion_ld.orion_ld_crud_operations import orion_ld_get_entities_by_type
from orion_ld.orion_ld_crud_operations import orion_ld_define_header
import json

app = FastAPI(title="GTFS + FIWARE API")

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/gtfs/stops.geojson")
def get_gtfs_stops():
    """Return GTFS Stops as GeoJSON."""
    header = orion_ld_define_header("gtfs_static")
    entities = orion_ld_get_entities_by_type("GtfsStop", header)

    features = [
        ngsi_ld_entity_to_geojson_feature(entity)
        for entity in entities
        if "location" in entity and entity["location"].get("value")
    ]

    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.get("/api/gtfs/shapes.geojson")
def get_gtfs_shape():
    """Return GTFS Shapes as GeoJSON."""
    header = orion_ld_define_header("gtfs_static")
    entities = orion_ld_get_entities_by_type("GtfsShape", header)

    features = [
        ngsi_ld_entity_to_geojson_feature(entity)
        for entity in entities
        if "location" in entity and entity["location"].get("value")
    ]

    return {
        "type": "FeatureCollection",
        "features": features
    }
    
@app.get("/api/pois/pois.geojson")
def get_json_ld_pois():
    """Return PoIs as GeoJSON."""
    header = orion_ld_define_header("pois")
    entities = orion_ld_get_entities_by_type("PointOfInterest", header)
    

    features = [
        ngsi_ld_entity_to_geojson_feature(entity)
        for entity in entities
        if "location" in entity and entity["location"].get("value")
    ]
    print(json.dumps(features, indent=2, ensure_ascii=False))
    return {
        "type": "FeatureCollection",
        "features": features
    }

def ngsi_ld_entity_to_geojson_feature(entity: dict) -> dict:
    """Transform NGSI-LD entity to GeoJSON Feature."""
    
    feature = {
        "type": "Feature",
        "id": entity.get("id"),
        "geometry": None,
        "properties": {}
    }

    for attr, value in entity.items():
        if attr in {"id", "type"}:
            continue
        if not isinstance(value, dict):
            continue

        attr_type = value.get("type")

        # GeoProperty → geometry
        if attr_type == "GeoProperty":
            feature["geometry"] = value.get("value")

        # Property → add to properties
        elif attr_type == "Property":
            feature["properties"][attr] = value.get("value")

        # Relationship → add reference ID
        elif attr_type == "Relationship":
            feature["properties"][attr] = value.get("object")

    # Always include entityType for clarity
    feature["properties"]["entityType"] = entity.get("type")

    return feature