import asyncio
from contextlib import asynccontextmanager
from typing import Any, List, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Response
from google.transit import gtfs_realtime_pb2

from orion_ld.orion_ld_crud_operations import (
    orion_ld_get_entities_by_type,
    orion_ld_define_header,
    orion_ld_batch_replace_entity_data
)

from gtfs_realtime.gtfs_realtime_utils import (
    gtfs_realtime_get_ngsi_ld_data,
    iso8601_to_unix
)

import config
import time


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
# NGSI-LD → GTFS Realtime conversion
# -----------------------------------------------------

def ngsi_ld_entity_to_gtfs_realtime_feed(entity_list: List[Dict[str,Any]]) -> Dict[str,Any]:
    
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    feed.header.timestamp = int(time.time())
    
    gtfs_realtime_entities = []
    
    for ent in entity_list:
        
        gtfs_vehicle_position = feed.entity.add()
        gtfs_vehicle_position.id = ent.get('id')
        vehicle = gtfs_vehicle_position.vehicle
        vehicle.trip.trip_id = ent.get('trip_id', {}).get('object') or None
        vehicle.trip.schedule_relationship = ent.get('schedule_relationship', {}).get('value') or 'SCHEDULED'
        vehicle.trip.route_id = ent.get('route_id', {}).get('object') or None
        vehicle.position.latitude = ent.get('position', {}).get('value', {}).get('coordinates', [None, None])[1]
        vehicle.position.longitude = ent.get('position', {}).get('value', {}).get('coordinates', [None, None])[0]
        vehicle.position.speed = ent.get('speed', {}).get('value') or -1.0
        vehicle.current_status = ent.get('current_status', {}).get('value') or 'IN_TRANSIT_TO'
        vehicle.timestamp = iso8601_to_unix(ent.get('timestamp', {}).get('value'))
        vehicle.congestion_level = ent.get('congestion_level', {}).get('value') or 'UNKNOWN_CONGESTION_LEVEL'
        vehicle.stop_id = ent.get('stop_id', {}).get('object') or None
        vehicle.vehicle.id = ent.get('vehicle_id', {}).get('object') or None
        vehicle.occupancy_status = ent.get('occupancy_status', {}).get('value') or 'EMPTY'
  
    return feed
    
# -----------------------------------------------------
# Background Loop (NO deprecated APIs)
# -----------------------------------------------------

async def update_vehicle_positions_loop():
    global gtfs_realtime_feed

    while True:
        try:
            # 2. transform to NGSI-LD
            ngsild_entities = gtfs_realtime_get_ngsi_ld_data("VehiclePosition")

            # 3. update Orion-LD
            header = orion_ld_define_header("gtfs_realtime")
            orion_ld_batch_replace_entity_data(ngsild_entities, header)
            # 4. read back from Orion
            entities = orion_ld_get_entities_by_type("GtfsRealtimeVehiclePosition", header)

            # 5. generate GTFS Realtime Feed
            gtfs_realtime_feed = ngsi_ld_entity_to_gtfs_realtime_feed(entities)
                        
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

@app.get("/api/gtfs/vehicles")
async def get_gtfs_realtime_feed_endpoint():
    return Response(
        content=gtfs_realtime_feed.SerializeToString(),
        media_type="application/x-protobuf"
    )

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