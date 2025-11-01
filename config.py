from dotenv import load_dotenv
from enum import Enum
import os

load_dotenv()

class GtfsSource(Enum):
    GTFS_REALTIME_ALERTS_URL = os.getenv("GTFS_REALTIME_ALERTS_URL")
    GTFS_REALTIME_TRIP_UPDATES_URL = os.getenv("GTFS_REALTIME_TRIP_UPDATES_URL")
    GTFS_REALTIME_VEHICLE_POSITIONS_URL = os.getenv("GTFS_REALTIME_VEHICLE_POSITIONS_URL")
    GTFS_STATIC_ZIP_URL = os.getenv("GTFS_STATIC_ZIP_URL")
