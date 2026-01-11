import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Any

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

gtfs_realtime_feed: gtfs_realtime_pb2.FeedMessage | None = None # type: ignore


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
) -> gtfs_realtime_pb2.FeedMessage: # type: ignore
    """
    Convert NGSI-LD GtfsRealtimeVehiclePosition entities
    retrieved from Orion-LD into a GTFS-Realtime FeedMessage.
    """

    feed = gtfs_realtime_pb2.FeedMessage() # type: ignore
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET # type: ignore
    feed.header.timestamp = int(time.time())

    created = 0
    skipped = 0

    for ngsi_entity in ngsi_entities:
        try:
            entity_id = ngsi_entity.get("id")
            
            if not entity_id:
                skipped += 1
                continue

            # vehicle
            vehicle_val = ngsi_entity.get("vehicle", {}).get("value")
            vehicle_id = vehicle_val.get("id")
            label = vehicle_val.get("label")
            license_plate = vehicle_val.get("license_plate")
                
            if not vehicle_id:
                skipped += 1
                continue

            # position
            pos_val = ngsi_entity.get("position", {}).get("value")
            if not isinstance(pos_val, dict):
                skipped += 1
                continue

            latitude = pos_val.get("latitude")
            longitude = pos_val.get("longitude")
            bearing = pos_val.get("bearing")
            odometer = pos_val.get("odometer")
            speed = pos_val.get("speed")
            
            if latitude is None or longitude is None:
                skipped += 1
                continue

            # ---------- create GTFS entity ----------
            e = feed.entity.add()
            e.id = entity_id
            v = e.vehicle
            
            # vehicle
            if vehicle_id is not None:
                v.vehicle.id = vehicle_id
            if label is not None:
                v.vehicle.label = label
            if license_plate is not None:
                v.vehicle.license_plate = license_plate

            # position
            if latitude is not None:
                v.position.latitude = float(latitude)
            if longitude is not None:
                v.position.longitude = float(longitude)
            if bearing is not None:
                v.position.bearing = float(bearing)
            if odometer is not None:
                v.position.odometer = float(odometer)
            if speed is not None:
                v.position.speed = float(speed) / 3.6

            # trip 
            trip_val = ngsi_entity.get("trip", {}).get("value")
            
            trip_id = trip_val.get("trip_id")
            if trip_id is not None:
                v.trip.trip_id = trip_id
                
            route_id = trip_val.get("route_id")
            if route_id is not None:
                v.trip.route_id = route_id
                
            direction_id = trip_val.get("direction_id")
            if direction_id is not None:
                v.trip.direction_id = int(direction_id)
                
            start_time = trip_val.get("start_time")
            if start_time is not None:
                v.trip.start_time = start_time
                
            start_date = trip_val.get("start_date")
            if start_date is not None:
                v.trip.start_date = start_date
                
            schedule_relationship = trip_val.get("schedule_relationship")
            if schedule_relationship is not None:
                v.trip.schedule_relationship =  getattr(
                    gtfs_realtime_pb2.TripDescriptor, # type: ignore
                    schedule_relationship,
                    gtfs_realtime_pb2.TripDescriptor.SCHEDULED # type: ignore
                )
            # current_stop_sequence    
            current_stop_sequence = ngsi_entity.get("current_stop_sequence", {}).get("value")
            if current_stop_sequence is not None:
                v.current_stop_sequence = int(current_stop_sequence)
                
            # stop_id    
            stop_id = ngsi_entity.get("stop_id", {}).get("object")
            if stop_id is not None:
                v.stop_id = stop_id
                
            # current status
            status = ngsi_entity.get("current_status", {}).get("value")
            if status:
                v.current_status = getattr(
                    gtfs_realtime_pb2.VehiclePosition, # type: ignore
                    status,
                    gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO # type: ignore
                )
                
            # timestamp
            timestamp = ngsi_entity.get("timestamp", {}).get("value")
            if timestamp is not None:  
                v.timestamp = iso8601_to_unix(timestamp)

            # congestion_level
            congestion_level = ngsi_entity.get("congestion_level", {}).get("value")
            if congestion_level is not None:
                v.congestion_level = getattr(
                    gtfs_realtime_pb2.VehiclePosition, # type: ignore
                    congestion_level,
                    gtfs_realtime_pb2.VehiclePosition.UNKNOWN_CONGESTION_LEVEL # type: ignore
                )

            # occupancy_status
            occupancy_status = ngsi_entity.get("occupancy_status", {}).get("value")
            if occupancy_status is not None:
                v.occupancy_status = getattr(
                    gtfs_realtime_pb2.VehiclePosition, # type: ignore
                    occupancy_status,
                    gtfs_realtime_pb2.VehiclePosition.EMPTY # type: ignore
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

            logger.info("GTFS feed built: entities=%d", len(gtfs_realtime_feed.entity) # type: ignore
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
        content=gtfs_realtime_feed.SerializeToString(), # type: ignore
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