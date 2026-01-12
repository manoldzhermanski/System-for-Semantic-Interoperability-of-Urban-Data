import sys

from orion_ld import orion_ld_crud_operations as olcd
from gtfs_static import gtfs_static_utils as gsu
from json_ld import json_ld_utils as jlu


GTFS_STATIC_TYPES = (
    "agency",
    "calendar_dates",
    "fare_attributes",
    "levels",
    "pathways",
    "routes",
    "shapes",
    "stop_times",
    "stops",
    "transfers",
    "trips",
)

POIS_TYPES = (
    "culture",
    "health",
    "kids",
    "parks_gardens",
    "public_transport",
    "schools",
    "sport",
    "other",
)

LOAD_GTFS = "gtfs"
LOAD_POIS = "pois"


def load_gtfs_static():
    print("🚍 Loading GTFS static data...")
    header = olcd.orion_ld_define_header("gtfs_static")

    for entity_type in GTFS_STATIC_TYPES:
        print(f"  • {entity_type}")
        data = gsu.gtfs_static_get_ngsi_ld_data(entity_type)
        olcd.orion_ld_batch_load_to_context_broker(data, header)


def load_pois():
    print("📍 Loading Points of Interest...")
    header = olcd.orion_ld_define_header("pois")

    for entity_type in POIS_TYPES:
        print(f"  • {entity_type}")
        data = jlu.json_ld_get_ngsi_ld_data(entity_type)
        olcd.orion_ld_batch_load_to_context_broker(data, header)


def main():
    args = set(sys.argv[1:])
    load_all = not args

    if load_all or LOAD_GTFS in args:
        load_gtfs_static()

    if load_all or LOAD_POIS in args:
        load_pois()

    print("✅ Initial data successfully loaded.")


if __name__ == "__main__":
    main()
