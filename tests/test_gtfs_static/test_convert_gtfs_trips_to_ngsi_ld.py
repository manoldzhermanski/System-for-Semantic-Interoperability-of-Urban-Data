from gtfs_static.gtfs_static_utils import convert_gtfs_trips_to_ngsi_ld

def test_convert_gtfs_trips_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for trips.txt
    """
    entity = {
        "trip_id": "TRIP_42",
        "route_id": "urn:ngsi-ld:GtfsRoute:R1",
        "service_id": "urn:ngsi-ld:GtfsService:S1",
        "trip_headsign": "Downtown",
        "trip_short_name": "D42",
        "direction_id": 1,
        "block_id": "urn:ngsi-ld:GtfsBlock:B1",
        "shape_id": "urn:ngsi-ld:GtfsShape:SH1",
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0,
    }

    result = convert_gtfs_trips_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsTrip:TRIP_42",
        "type": "GtfsTrip",

        "route": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsRoute:R1",
        },

        "service": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsService:S1",
        },

        "headSign": {
            "type": "Property",
            "value": "Downtown",
        },

        "shortName": {
            "type": "Property",
            "value": "D42",
        },

        "direction": {
            "type": "Property",
            "value": 1,
        },

        "block": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsBlock:B1",
        },

        "hasShape": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsShape:SH1",
        },

        "wheelChairAccessible": {
            "type": "Property",
            "value": 1,
        },

        "bikesAllowed": {
            "type": "Property",
            "value": 2,
        },

        "carsAllowed": {
            "type": "Property",
            "value": 0,
        },
    }

def test_convert_gtfs_trips_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for trips.txt when optional fileds are missing
    """
    entity = {
        "trip_id": "TRIP_42",
        "route_id": "urn:ngsi-ld:GtfsRoute:R1",
        "service_id": "urn:ngsi-ld:GtfsService:S1",
        "shape_id": "urn:ngsi-ld:GtfsShape:SH1",
    }

    result = convert_gtfs_trips_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsTrip:TRIP_42",
        "type": "GtfsTrip",

        "route": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsRoute:R1",
        },

        "service": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsService:S1",
        },

        "headSign": {
            "type": "Property",
            "value": None,
        },

        "shortName": {
            "type": "Property",
            "value": None,
        },

        "direction": {
            "type": "Property",
            "value": None,
        },

        "block": {
            "type": "Relationship",
            "object": None,
        },

        "hasShape": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsShape:SH1",
        },

        "wheelChairAccessible": {
            "type": "Property",
            "value": None,
        },

        "bikesAllowed": {
            "type": "Property",
            "value": None,
        },

        "carsAllowed": {
            "type": "Property",
            "value": None,
        },
    }