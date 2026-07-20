import os
import re
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

OPERATING_CITY = None

PROJECT_ROOT = Path(__file__).resolve().parent

NETEX_OUTPUT_DIR = PROJECT_ROOT / "netex" / "output"
OTP_DATA_DIR = PROJECT_ROOT / "otp" / "data"

def set_operating_city(city: str) -> None:
    """
    Set the parameter OPERATING_CITY to the city for which we want to get data
    
    Args:
        city (str): Operating city for which we want to get data

    Returns:
        None

    Raises:
        TypeError: If `city` is not a string
        ValueError: If `city` is empty or contains invalid characters
    """
    global OPERATING_CITY
    # If not a string, raise TypeError
    if not isinstance(city, str):
        raise TypeError("City must be a string")

    # Remove whitespaces around and set to title case
    city = city.strip().title().replace(" ", "_").replace("-", "_")

    # If empty, raise ValueError
    if not city:
        raise ValueError("City cannot be empty")

    # Check that the city contains valid characters
    if not re.fullmatch(r"[A-Za-zА-Яа-я_]+", city):
        raise ValueError("City contains invalid characters")
    
    # Set the parameter
    OPERATING_CITY = city

def get_operating_city() -> str:
    if OPERATING_CITY is None:
        raise RuntimeError("Operating city has not been set")

    return OPERATING_CITY