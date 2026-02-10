import io
import os
import csv
import sys
import zipfile
import logging
import asyncio
from typing import Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi import Response
from contextlib import asynccontextmanager
from google.transit import gtfs_realtime_pb2
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

STORAGE_DIR = os.path.join(project_root, "otp", "data")
os.makedirs(STORAGE_DIR, exist_ok=True)


from orion_ld.orion_ld_crud_operations import (
    orion_ld_get_entities_by_type,
    orion_ld_define_header,
    orion_ld_batch_replace_entity_data
)

from gtfs_realtime.gtfs_realtime_utils import (
    gtfs_realtime_get_ngsi_ld_data,
    iso8601_to_unix
)

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
    """
    Convert an NGSI-LD entity into a GeoJSON Feature.

    GeoProperties are mapped to the GeoJSON geometry field.
    Properties and Relationships are flattened into the feature properties.
    The original NGSI-LD entity type is preserved as `entityType`.

    Args:
        entity (dict): NGSI-LD entity representation.

    Returns:
        dict: GeoJSON Feature derived from the given entity.
    """
    # Base GeoJSON Feature structure
    feature = {
        "type": "Feature",
        "id": entity.get("id"),
        "geometry": None,
        "properties": {}
    }

    for attr, value in entity.items():
        # Skip "id" and "type" keys
        if attr in {"id", "type"}:
            continue

        # If not the correct structure, skip
        if not isinstance(value, dict):
            continue

        # Extract field
        attr_type = value.get("type")

        # Geometry is extracted from GeoProperty
        if attr_type == "GeoProperty":
            feature["geometry"] = value.get("value")

        # Regular attributes are flattened into properties
        elif attr_type == "Property":
            feature["properties"][attr] = value.get("value")

        # Relationships expose their target as a property
        elif attr_type == "Relationship":
            feature["properties"][attr] = value.get("object")

    # Preserve original NGSI-LD entity type
    feature["properties"]["entityType"] = entity.get("type")

    return feature

# -----------------------------------------------------
# NGSI-LD → GTFS Realtime conversion
# -----------------------------------------------------

def ngsi_ld_vehicle_positions_to_feed_message(ngsi_entities: list[dict[str, Any]]) -> gtfs_realtime_pb2.FeedMessage: # type: ignore
    """
    Convert NGSI-LD GtfsRealtimeVehiclePosition entities from Orion-LD
    into a GTFS-Realtime FeedMessage.

    Each entity is transformed into a VehiclePosition entry in the feed.
    Entities missing required fields (vehicle ID, latitude, longitude) are skipped.
    Additional fields (trip, status, occupancy, congestion, stop info) are mapped
    if present.

    Args:
        ngsi_entities (List[Dict[str, Any]]): NGSI-LD entities representing vehicle positions.

    Returns:
        gtfs_realtime_pb2.FeedMessage: GTFS-Realtime feed containing VehiclePosition entities.
    """
    # Initialize GTFS-Realtime feed and header metadata
    feed = gtfs_realtime_pb2.FeedMessage() # type: ignore
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET # type: ignore
    feed.header.timestamp = int(time.time())

    # Counters for logging and diagnostics
    created = 0
    skipped = 0

    for ngsi_entity in ngsi_entities:
        try:

            entity_id = ngsi_entity.get("id")
            
            # Skip if entity id is not present
            if not entity_id:
                skipped += 1
                continue

            # vehicle
            vehicle_val = ngsi_entity.get("vehicle", {}).get("value")
            vehicle_id = vehicle_val.get("id")
            label = vehicle_val.get("label")
            license_plate = vehicle_val.get("license_plate")
                
            # Skip entity creation if vehicle id is not present
            if not vehicle_id:
                skipped += 1
                continue

            # Get position data
            pos_val = ngsi_entity.get("position", {}).get("value")
            if not isinstance(pos_val, dict):
                skipped += 1
                continue

            latitude = pos_val.get("latitude")
            longitude = pos_val.get("longitude")
            bearing = pos_val.get("bearing")
            odometer = pos_val.get("odometer")
            speed = pos_val.get("speed")
            
            # If mandatory position data is not present, skip entity creation
            if latitude is None or longitude is None:
                skipped += 1
                continue

            # create GTFS entity
            e = feed.entity.add()
            e.id = entity_id
            v = e.vehicle
            
            # Populate vehicle descriptor
            if vehicle_id is not None:
                v.vehicle.id = vehicle_id
            if label is not None:
                v.vehicle.label = label
            if license_plate is not None:
                v.vehicle.license_plate = license_plate

            # Populate vehicle position
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

            # Populate trip descriptor
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
                
            # Populate schedule_relationship
            schedule_relationship = trip_val.get("schedule_relationship")
            if schedule_relationship is not None:
                v.trip.schedule_relationship =  getattr(
                    gtfs_realtime_pb2.TripDescriptor, # type: ignore
                    schedule_relationship,
                    gtfs_realtime_pb2.TripDescriptor.SCHEDULED # type: ignore
                )

            # Populate current_stop_sequence    
            current_stop_sequence = ngsi_entity.get("current_stop_sequence", {}).get("value")
            if current_stop_sequence is not None:
                v.current_stop_sequence = int(current_stop_sequence)
                
            # Populate stop_id    
            stop_id = ngsi_entity.get("stop_id", {}).get("object")
            if stop_id is not None:
                v.stop_id = stop_id
                
            # Populate current status
            status = ngsi_entity.get("current_status", {}).get("value")
            if status:
                v.current_status = getattr(
                    gtfs_realtime_pb2.VehiclePosition, # type: ignore
                    status,
                    gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO # type: ignore
                )
                
            # Populate timestamp
            timestamp = ngsi_entity.get("timestamp", {}).get("value")
            if timestamp is not None:  
                v.timestamp = iso8601_to_unix(timestamp)

            # Populate congestion_level
            congestion_level = ngsi_entity.get("congestion_level", {}).get("value")
            if congestion_level is not None:
                v.congestion_level = getattr(
                    gtfs_realtime_pb2.VehiclePosition, # type: ignore
                    congestion_level,
                    gtfs_realtime_pb2.VehiclePosition.UNKNOWN_CONGESTION_LEVEL # type: ignore
                )

            # Populate occupancy_status
            occupancy_status = ngsi_entity.get("occupancy_status", {}).get("value")
            if occupancy_status is not None:
                v.occupancy_status = getattr(
                    gtfs_realtime_pb2.VehiclePosition, # type: ignore
                    occupancy_status,
                    gtfs_realtime_pb2.VehiclePosition.EMPTY # type: ignore
                )

            # Increment populated counter
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

async def update_vehicle_positions_loop(interval: int = 30):
    """
    Periodically update the GTFS-Realtime vehicle positions feed.

    The function runs in an infinite asynchronous loop and performs the following steps
    on each iteration:
    1. Retrieve NGSI-LD vehicle position entities.
    2. Push the retrieved data to Orion-LD using a batch replace operation.
    3. Fetch the updated GtfsRealtimeVehiclePosition entities from Orion-LD.
    4. Convert the entities into a GTFS-Realtime FeedMessage and store it globally.

    Any exception raised during a single iteration is logged and does not stop
    the loop execution. The update cycle is repeated every 30 seconds.

    Args:
        interval (int): Time interval for the continous background update loop
    """
    global gtfs_realtime_feed

    # Run continuously as a background update loop
    while True:
        try:
            # Retrieve raw NGSI-LD GtfsRealtimeVehiclePosition entities
            ngsild_entities = gtfs_realtime_get_ngsi_ld_data("VehiclePosition")

            # Set correct header for Orion-LD operations
            header = orion_ld_define_header("gtfs_realtime")

             # Replace existing entity data in Orion-LD with the new batch
            orion_ld_batch_replace_entity_data(ngsild_entities, header)

            # Fetch the processed GtfsRealtimeVehiclePosition entities
            entities = orion_ld_get_entities_by_type("GtfsRealtimeVehiclePosition", header)

            # Convert NGSI-LD entities into a GTFS-Realtime feed
            gtfs_realtime_feed = ngsi_ld_vehicle_positions_to_feed_message(entities)

            # Log successful feed creation
            logger.info("GTFS feed built: entities=%d", len(gtfs_realtime_feed.entity) # type: ignore
)

        except Exception as e:
            logger.exception("Vehicle update failed: %s", e)

        # Wait before the next update cycle
        await asyncio.sleep(interval)

# -----------------------------------------------------
# Lifespan (this replaces @startup)
# -----------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown lifecycle.

    On startup, this lifespan context starts a background task responsible for
    periodically updating the GTFS-Realtime vehicle positions feed.
    On shutdown, the background task is cancelled to allow for a graceful
    application termination.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        AsyncIterator[None]: An asynchronous context manager controlling the application lifespan.
    """

    # Start background task for updating vehicle positions
    task = asyncio.create_task(update_vehicle_positions_loop())

    # Yield control back to FastAPI while the application is running
    yield

    # Cancel background task on application shutdown
    task.cancel()


# -----------------------------------------------------
# FastAPI App
# -----------------------------------------------------

# Create FastAPI application instance
# The lifespan handler manages startup and shutdown logic
app = FastAPI(title="GTFS + FIWARE API", lifespan=lifespan)

# Enable Cross-Origin Resource Sharing (CORS)
# This allows the API to be accessed from web clients hosted on different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow requests from any origin
    allow_methods=["*"],   # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],   # Allow all request headers
)

# -----------------------------------------------------
# Vehicle Positions
# -----------------------------------------------------

@app.get("/api/gtfs/vehicles")
async def get_gtfs_realtime_feed_endpoint():
    """
    Serve the current GTFS-Realtime vehicle positions feed.

    The endpoint returns the latest GTFS-Realtime FeedMessage generated by the
    background update loop. The feed is serialized as Protocol Buffers and
    returned with the appropriate media type.

    Returns:
        Response:
            A Protobuf-encoded GTFS-Realtime feed with vehicle position entities.
    """

    # Log number of entities currently available in the feed
    logger.info("Serving GTFS feed: entities=%d", len(gtfs_realtime_feed.entity) if gtfs_realtime_feed else -1)

    # Return serialized GTFS-Realtime FeedMessage
    return Response(
        content=gtfs_realtime_feed.SerializeToString(),  # type: ignore
        media_type="application/x-protobuf"
    )

# -----------------------------------------------------
# GTFS Static Stops and Shapes
# -----------------------------------------------------

@app.get("/api/gtfs/stops.geojson")
def get_gtfs_stops():
    """
    Return GTFS Stop entities as a GeoJSON FeatureCollection.

    The endpoint retrieves GTFS stop entities from Orion-LD, converts those
    containing valid location data into GeoJSON Features, and returns them
    as a GeoJSON FeatureCollection.
    """

    # Select proper header for Orion-LD operations
    header = orion_ld_define_header("gtfs_static")

    # Fetch GTFS stop entities from Orion-LD
    entities = orion_ld_get_entities_by_type("GtfsStop", header)

    # Convert entities with valid location data into GeoJSON features
    features = [
        ngsi_ld_entity_to_geojson_feature(entity)
        for entity in entities
        if "location" in entity and entity["location"].get("value")
    ]

    # Return GeoJSON FeatureCollection
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.get("/api/gtfs/shapes.geojson")
def get_gtfs_shape():
    """
    Return GTFS Shape entities as a GeoJSON FeatureCollection.

    The endpoint retrieves GTFS shape entities from Orion-LD, converts those
    containing valid location data into GeoJSON Features, and returns them
    as a GeoJSON FeatureCollection.
    """
    # Select proper header for Orion-LD operations
    header = orion_ld_define_header("gtfs_static")

    # Fetch GTFS shape entities from Orion-LD
    entities = orion_ld_get_entities_by_type("GtfsShape", header)

    # Convert entities with valid location data into GeoJSON features
    features = [
        ngsi_ld_entity_to_geojson_feature(entity)
        for entity in entities
        if "location" in entity and entity["location"].get("value")
    ]

    # Return GeoJSON FeatureCollection
    return {
        "type": "FeatureCollection",
        "features": features
    }
    
# -----------------------------------------------------
# Sofia Points Of Interest
# -----------------------------------------------------
    
@app.get("/api/pois/pois.geojson")
def get_json_ld_pois():
    """
    Return provided PoI entities as a GeoJSON FeatureCollection.

    The endpoint retrieves PoI entities from Orion-LD, converts those
    containing valid location data into GeoJSON Features, and returns them
    as a GeoJSON FeatureCollection.
    """
    # Select proper header for Orion-LD operations
    header = orion_ld_define_header("pois")

    # Fetch PoI entities from Orion-LD
    entities = orion_ld_get_entities_by_type("PointOfInterest", header)

    # Convert entities with valid location data into GeoJSON features
    features = [
        ngsi_ld_entity_to_geojson_feature(entity)
        for entity in entities
        if "location" in entity and entity["location"].get("value")
    ]

    # Return GeoJSON FeatureCollection
    return {
        "type": "FeatureCollection",
        "features": features
    }

# -----------------------------------------------------
# NGSI-LD → GTFS Static conversion
# -----------------------------------------------------

def ngsi_ld_extract_data_for_csv_conversion(entity: dict[str, Any]) -> dict[str, Any]:

    row = {}
    
    entity_type = entity.get("type")
    entity_id = entity.get("id")
    if isinstance(entity_type, str) and isinstance(entity_id, str) and entity_type in ("GtfsAgency", "GtfsFareAttributes", "GtfsLevel"):
        if entity_type == "GtfsAgency":
            row["agency_id"] = entity_id.rsplit(":", 1)[-1]
        elif entity_type == "GtfsFareAttributes":
            row["fare_id"] = entity_id.rsplit(":", 1)[-1]
        elif entity_type == "GtfsLevel":
            row["level_id"] = entity_id.rsplit(":", 1)[-1]
            
    if entity_type == "GtfsCalendarDateRule":

        has_service = entity.get("hasService")
        if isinstance(has_service, dict):
            obj = has_service.get("object")
            if isinstance(obj, str) and obj.startswith("urn:ngsi-ld:"):
                obj = obj.rsplit(":", 1)[-1]
            row["service_id"] = obj

        applies_on = entity.get("appliesOn")
        if isinstance(applies_on, dict):
            row["date"] = applies_on.get("value")

        exc_type = entity.get("exceptionType")
        if isinstance(exc_type, dict):
            row["exception_type"] = exc_type.get("value")

    elif entity_type == "GtfsFareAttributes":

        agency = entity.get("agency")
        if isinstance(agency, dict):
            agency_id = agency.get("object")
            if isinstance(agency_id, str) and agency_id.startswith("urn:ngsi-ld:"):
                agency_id = agency_id.rsplit(":", 1)[-1]
            row["agency_id"] = agency_id
    
    elif entity_type == "GtfsLevel":
        name = entity.get("name")
        if isinstance(name, dict):
            level_name = name.get("value")
            row["level_name"] = level_name
    else:
        for attr, value in entity.items():
            if attr in ("id", "type", "@context"):
                continue
            
            if isinstance(value, dict) and "type" in value:
                attr_type = value.get("type")

                if attr_type == "Property":
                    row[attr] = value.get("value")

                if attr_type == "Relationship":
                    obj = value.get("object")

                    if isinstance(obj, str) and obj.startswith("urn:ngsi-ld:"):
                        obj = obj.rsplit(":", 1)[-1]

                    row[attr] = obj
            else:
                row[attr] = value

    return row

def entities_to_csv_bytes(entities: list[dict[str, Any]]) -> bytes:
    if not entities:
        return b""

    rows = [ngsi_ld_extract_data_for_csv_conversion(entity) for entity in entities]

    all_fields = set()
    for r in rows:
        all_fields.update(r.keys())

    fieldnames = sorted(all_fields)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    return output.getvalue().encode("utf-8")

def build_gtfs_zip() -> str:
    """
    data_by_file:
    {
        "agency.txt": [entities...],
        "routes.txt": [entities...],
        "stops.txt": [...]
    }
    """
    zip_path = os.path.join(STORAGE_DIR, f"gtfs.zip")
    
    header = orion_ld_define_header("gtfs_static")
    agencies = orion_ld_get_entities_by_type("GtfsAgency", header)
    #stops = orion_ld_get_entities_by_type("GtfsStop", header)
    #routes = orion_ld_get_entities_by_type("GtfsRoute", header)
    #trips = orion_ld_get_entities_by_type("GtfsTrip", header)
    #stop_times = orion_ld_get_entities_by_type("GtfsStopTime", header)
    calendar_dates = orion_ld_get_entities_by_type("GtfsCalendarDateRule", header)
    #fare_attributes = orion_ld_get_entities_by_type("GtfsFareAttributes", header)
    #shapes = orion_ld_get_entities_by_type("GtfsShape", header)
    #transfers = orion_ld_get_entities_by_type("GtfsTransferRule", header)
    #pathways = orion_ld_get_entities_by_type("GtfsPathway", header)
    #levels = orion_ld_get_entities_by_type("GtfsLevel", header)

    data = {
        "agency.txt": agencies,
        #"stops.txt": stops,
        #"routes.txt": routes,
        #"trips.txt": trips,
        #"stop_times.txt": stop_times,
        "calendar_dates.txt": calendar_dates,
        #"fare_attributes.txt": fare_attributes,
        #"shapes.txt": shapes,
        #"transfers.txt": transfers,
        #"pathways.txt": pathways,
        #"levels.txt": levels,
    }

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:

        for filename, entities in data.items():
            csv_bytes = entities_to_csv_bytes(entities)
            z.writestr(filename, csv_bytes)
                        
    return zip_path

@app.post("/api/gtfs_static/rebuild")
def rebuild(bg: BackgroundTasks):
    bg.add_task(build_gtfs_zip)
    return {"status": "rebuild started"}

@app.get("/api/gtfs_static/download")
def download():
    path = os.path.join(STORAGE_DIR, f"gtfs.zip")

    if not os.path.exists(path):
        raise HTTPException(404, "GTFS not built yet")

    return FileResponse(
        path,
        media_type="application/zip",
        filename=f"gtfs.zip",
    )