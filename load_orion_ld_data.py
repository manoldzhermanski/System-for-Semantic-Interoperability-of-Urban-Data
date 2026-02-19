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

GTFS_CITIES = (
    "sofia", 
    "helsinki"
)

LOAD_GTFS = "gtfs"
LOAD_POIS = "pois"


def load_gtfs_static(cities: list[str]):
    print("Loading GTFS static data...")
    header = olcd.orion_ld_define_header("gtfs_static")

    for city in cities:
        print(f"\nCity: {city}")

        for entity_type in GTFS_STATIC_TYPES:
            print(f"  • {entity_type}")

            data = gsu.gtfs_static_get_ngsi_ld_batches(entity_type, city)

            if not data:
                continue

            olcd.orion_ld_batch_load_to_context_broker(data, header)

def load_pois():
    print("Loading Points of Interest...")
    header = olcd.orion_ld_define_header("pois")

    for entity_type in POIS_TYPES:
        print(f"  • {entity_type}")
        data = jlu.json_ld_get_ngsi_ld_data(entity_type)
        olcd.orion_ld_batch_load_to_context_broker(data, header)

def main():
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python load_orion_ld_data.py gtfs <city> [city...]")
        print("  python load_orion_ld_data.py pois")
        sys.exit(1)

    if LOAD_GTFS in args:
        idx = args.index(LOAD_GTFS)
        cities = args[idx + 1:]

        if not cities:
            print("Error: specify at least one city")
            print("Example: gtfs sofia helsinki")
            sys.exit(1)

        load_gtfs_static(cities)

    if LOAD_POIS in args:
        load_pois()

    print("Initial data successfully loaded.")

if __name__ == "__main__":
    main()
