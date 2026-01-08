import logging
import asyncio
from datetime import datetime
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

logger = logging.getLogger("BackendAPI")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

gtfs_realtime_feed: gtfs_realtime_pb2.FeedMessage | None = None


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

def ngsi_ld_vehicle_positions_to_feed_message(
    ngsi_entities: list[dict[str, Any]]
) -> gtfs_realtime_pb2.FeedMessage:
    """
    Convert NGSI-LD GtfsRealtimeVehiclePosition entities
    retrieved from Orion-LD into a GTFS-Realtime FeedMessage.
    """

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    feed.header.timestamp = int(time.time())

    created = 0
    skipped = 0

    for ent in ngsi_entities:
        try:
            entity_id = ent.get("id")
            if not entity_id:
                skipped += 1
                continue

            # ---------- vehicle ----------
            vehicle_val = ent.get("vehicle", {}).get("value")
            vehicle_id = (
                vehicle_val.get("id")
                if isinstance(vehicle_val, dict)
                else None
            )
            if not vehicle_id:
                skipped += 1
                continue

            # ---------- position ----------
            pos_val = ent.get("position", {}).get("value")
            if not isinstance(pos_val, dict):
                skipped += 1
                continue

            lat = pos_val.get("latitude")
            lon = pos_val.get("longitude")
            if lat is None or lon is None:
                skipped += 1
                continue

            # ---------- create GTFS entity ----------
            e = feed.entity.add()
            e.id = entity_id

            v = e.vehicle
            v.vehicle.id = vehicle_id
            v.position.latitude = float(lat)
            v.position.longitude = float(lon)

            # ---------- speed ----------
            speed = pos_val.get("speed")
            if isinstance(speed, (int, float)):
                v.position.speed = float(speed)

            # ---------- trip ----------
            trip_val = ent.get("trip", {}).get("value")
            if isinstance(trip_val, dict):
                trip_id = trip_val.get("trip_id")
                if trip_id:
                    v.trip.trip_id = trip_id

            # ---------- timestamp ----------
            ts = ent.get("timestamp", {}).get("value")
            if ts:
                # вече е ISO → при теб вероятно го пазиш като unix string
                v.timestamp = int(time.time())

            # ---------- current status ----------
            status = ent.get("current_status", {}).get("value")
            if status:
                v.current_status = getattr(
                    gtfs_realtime_pb2.VehiclePosition,
                    status,
                    gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO
                )

            # ---------- occupancy ----------
            occ = ent.get("occupancy_status", {}).get("value")
            if occ:
                v.occupancy_status = getattr(
                    gtfs_realtime_pb2.VehiclePosition,
                    occ,
                    gtfs_realtime_pb2.VehiclePosition.EMPTY
                )

            created += 1

        except Exception:
            skipped += 1

    logger.info(
        "GTFS feed built: entities=%d, skipped=%d",
        created,
        skipped
    )

    return feed


    
# -----------------------------------------------------
# Background Loop (NO deprecated APIs)
# -----------------------------------------------------

async def update_vehicle_positions_loop():
    global gtfs_realtime_feed

    while True:
        try:
            ngsild_entities = gtfs_realtime_get_ngsi_ld_data("VehiclePosition")

            header = orion_ld_define_header("gtfs_realtime")
            orion_ld_batch_replace_entity_data(ngsild_entities, header)

            entities = orion_ld_get_entities_by_type("GtfsRealtimeVehiclePosition", header)

            gtfs_realtime_feed = ngsi_ld_vehicle_positions_to_feed_message(entities)

            logger.info("GTFS feed built: entities=%d", len(gtfs_realtime_feed.entity)
)

        except Exception as e:
            logger.exception("Vehicle update failed: %s", e)

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
    logger.info("Serving GTFS feed: entities=%d", len(gtfs_realtime_feed.entity) if gtfs_realtime_feed else -1)
    
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