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
    "Sofia", 
    "Helsinki"
)

LOAD_GTFS = "gtfs"
LOAD_POIS = "pois"

# -----------------------------------------------------
# Load GTFS Static Data in Orion-LD
# ----------------------------------------------------- 
def load_gtfs_static(cities: list[str]):
    """
    Load GTFS Static data into Orion-LD for the supported cities

    Args:
        cities (list[str]): Supported cities for which GTFS data is available
    """
    
    print("Loading GTFS static data...")
    
    # Define GTFS Static Context Header for Orion-LD
    header = olcd.orion_ld_define_header("gtfs_static")

    # Iterate through the selected cities
    for city in cities:
        print(f"\nCity: {city}")

        # Iterate through the selected GTFS Static Data Types
        for entity_type in GTFS_STATIC_TYPES:
            print(f"  • {entity_type}")

            # Read GTFS Static Data Sources and get the data in NGSI-LD format
            data = gsu.gtfs_static_get_ngsi_ld_batches(entity_type, city)

            # Skip the unsupported Data Types
            if not data:
                print(f"Warning: Didn't find a data source of type {entity_type} for the city of {city}")
                continue

            # Load data into Orion-LD
            olcd.orion_ld_batch_load_to_context_broker(data, header)

# -----------------------------------------------------
# Load PoI data in Orion-LD
# ----------------------------------------------------- 
def load_pois():
    """
    Load PoI data provided by GATE Institute
    """
    
    print("Loading Points of Interest...")
    
    # Define PoI Context Header for Orion-LD
    header = olcd.orion_ld_define_header("pois")

    # Iterate through the supported PoI Types
    for entity_type in POIS_TYPES:
        
        print(f"  • {entity_type}")
        
        # Read PoI Data Sources and get data in NGSI-LD format
        data = jlu.json_ld_get_ngsi_ld_data(entity_type)
        
        # Load data into Orion-LD
        olcd.orion_ld_batch_load_to_context_broker(data, header)

def main():
    # Read command-line arguments
    args = sys.argv[1:]

    # If no arguments are provided, show usage instructions
    if not args:
        print("Usage:")
        print("  python load_orion_ld_data.py gtfs <city> [city...]")
        print("  python load_orion_ld_data.py pois")
        sys.exit(1)

    # Handle loading of GTFS static data
    if LOAD_GTFS in args:
        # Find the position of the "gtfs" argument
        idx = args.index(LOAD_GTFS)

        # All arguments after "gtfs" are treated as city names
        cities = args[idx + 1:]

        # Ensure at least one city was provided
        if not cities:
            print("Error: specify at least one city")
            sys.exit(1)

        # Build a lookup dictionary for valid cities
        # Key   -> lowercase city name
        # Value -> correctly formatted city name
        valid = {c.lower(): c for c in GTFS_CITIES}

        normalized = []

        for c in cities:
            # Normalize user input to lowercase for validation
            key = c.lower()

            # Validate that the provided city is supported
            if key not in valid:
                print(f"Unknown city: {c}")
                print("Allowed:", ", ".join(GTFS_CITIES))
                sys.exit(1)

            # Store the properly formatted city name
            normalized.append(valid[key])

        # Load GTFS data for the validated and normalized cities
        load_gtfs_static(normalized)

    # Handle loading of PoI data
    if LOAD_POIS in args:
        load_pois()

    # Final confirmation message
    print("Initial data successfully loaded.")


if __name__ == "__main__":
    main()
