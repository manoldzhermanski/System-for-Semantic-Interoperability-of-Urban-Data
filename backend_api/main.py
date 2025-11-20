import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from orion_ld.orion_ld_crud_operations import (
    orion_ld_get_entities_by_type,
    orion_ld_define_header,
    orion_ld_batch_replace_entity_data
)

from gtfs_realtime.gtfs_realtime_utils import (
    get_gtfs_realtime_feed,
    parse_gtfs_realtime_feed,
    gtfs_realtime_feed_to_dict,
    gtfs_realtime_vehicle_position_to_ngsi_ld
)

import config


# -----------------------------------------------------
# Globals
# -----------------------------------------------------

latest_vehicle_positions_geojson = {
    "type": "FeatureCollection",
    "features": []
}


# -----------------------------------------------------
# NGSI-LD → GeoJSON conversion
# -----------------------------------------------------

def ngsi_ld_entity_to_geojson_feature(entity: dict) -> dict:
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

        if attr_type == "GeoProperty":
            feature["geometry"] = value.get("value")

        elif attr_type == "Property":
            feature["properties"][attr] = value.get("value")

        elif attr_type == "Relationship":
            feature["properties"][attr] = value.get("object")

    feature["properties"]["entityType"] = entity.get("type")
    return feature


# -----------------------------------------------------
# Background Loop (NO deprecated APIs)
# -----------------------------------------------------

async def update_vehicle_positions_loop():
    global latest_vehicle_positions_geojson

    while True:
        try:
            # 1. fetch GTFS RT
            api_response = get_gtfs_realtime_feed(
                config.GtfsSource.GTFS_REALTIME_VEHICLE_POSITIONS_URL
            )

            feed_data = parse_gtfs_realtime_feed(
                api_response,
                config.GtfsSource.GTFS_REALTIME_VEHICLE_POSITIONS_URL
            )

            feed_dict = gtfs_realtime_feed_to_dict(feed_data)

            # 2. transform to NGSI-LD
            ngsild_entities = gtfs_realtime_vehicle_position_to_ngsi_ld(feed_dict)

            # 3. update Orion-LD
            header = orion_ld_define_header("gtfs_realtime")
            response = orion_ld_batch_replace_entity_data(ngsild_entities, header)
            print(response)
            # 4. read back from Orion
            entities = orion_ld_get_entities_by_type("GtfsVehiclePosition", header)

            # 5. generate GeoJSON
            latest_vehicle_positions_geojson = {
                "type": "FeatureCollection",
                "features": [
                    ngsi_ld_entity_to_geojson_feature(e)
                    for e in entities
                    if "position" in e and e["position"].get("value")
                ]
            }

        except Exception as e:
            print("Vehicle update failed:", e)

        await asyncio.sleep(30)


# -----------------------------------------------------
# Lifespan (this replaces @startup)
# -----------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(update_vehicle_positions_loop())
    yield
    task.cancel()


# -----------------------------------------------------
# FastAPI App
# -----------------------------------------------------

app = FastAPI(title="GTFS + FIWARE API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------
# Vehicle Positions
# -----------------------------------------------------

@app.get("/api/gtfs/vehicles.geojson")
async def get_geojson():
    return latest_vehicle_positions_geojson

# -----------------------------------------------------
# GTFS Static Stops and Shapes
# -----------------------------------------------------

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
    
# -----------------------------------------------------
# Sofia Points Of Interest
# -----------------------------------------------------
    
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

    return {
        "type": "FeatureCollection",
        "features": features
    }