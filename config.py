import os
from enum import Enum
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class GtfsSource(Enum):
    SOFIA_GTFS_REALTIME_ALERTS_URL = os.getenv("SOFIA_GTFS_REALTIME_ALERTS_URL")
    SOFIA_GTFS_REALTIME_TRIP_UPDATES_URL = os.getenv("SOFIA_GTFS_REALTIME_TRIP_UPDATES_URL")
    SOFIA_GTFS_REALTIME_VEHICLE_POSITIONS_URL = os.getenv("SOFIA_GTFS_REALTIME_VEHICLE_POSITIONS_URL")
    SOFIA_GTFS_STATIC_ZIP_URL = os.getenv("SOFIA_GTFS_STATIC_ZIP_URL")
    HELSINKI_GTFS_REALTIME_VEHICLE_POSITIONS_URL = os.getenv("HELSINKI_GTFS_REALTIME_VEHICLE_POSITIONS_URL")
    HELSINKI_GTFS_STATIC_ZIP_URL = os.getenv("HELSINKI_GTFS_STATIC_ZIP_URL")

ORION_LD_BASE_URL = os.getenv("ORION_LD_BASE_URL")

class OrionLDEndpoint(Enum):
    ENTITIES_ENDPOINT = f"{ORION_LD_BASE_URL}/entities"
    BATCH_CREATE_ENDPOINT = f"{ORION_LD_BASE_URL}/entityOperations/create"
    BATCH_DELETE_ENDPOINT = f"{ORION_LD_BASE_URL}/entityOperations/delete"
    BATCH_UPDATE_ENDPOINT = f"{ORION_LD_BASE_URL}/entityOperations/upsert?options=update"

NETEX_AUTHORITY = None

NETEX_OPERATING_CITY = None

PROJECT_ROOT = Path(__file__).resolve().parent

NETEX_OUTPUT_DIR = PROJECT_ROOT / "netex" / "output"
OTP_DATA_DIR = PROJECT_ROOT / "otp" / "data"