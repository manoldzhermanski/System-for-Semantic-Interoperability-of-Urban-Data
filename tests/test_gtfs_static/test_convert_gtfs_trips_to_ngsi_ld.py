from gtfs_static.gtfs_static_utils import convert_gtfs_trips_to_ngsi_ld

def test_convert_gtfs_trips_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for trips.txt
    """
    city = "Sofia"
    entity = {
        "trip_id": "T1",
        "route_id": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
        "service_id": f"urn:ngsi-ld:GtfsService:{city}:S1",
        "trip_headsign": "Downtown",
        "trip_short_name": "D1",
        "direction_id": 1,
        "block_id": f"urn:ngsi-ld:GtfsBlock:{city}:B1",
        "shape_id": f"urn:ngsi-ld:GtfsShape:{city}:SH1",
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0,
    }

    result = convert_gtfs_trips_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
        "type": "GtfsTrip",

        "route": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
        },

        "service": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsService:{city}:S1",
        },

        "headSign": {
            "type": "Property",
            "value": "Downtown",
        },

        "shortName": {
            "type": "Property",
            "value": "D1",
        },

        "direction": {
            "type": "Property",
            "value": 1,
        },

        "block": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsBlock:{city}:B1",
        },

        "hasShape": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsShape:{city}:SH1",
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
    
    city = "Sofia"
    
    entity = {
        "trip_id": "T1",
        "route_id": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
        "service_id": f"urn:ngsi-ld:GtfsService:{city}:S1",
        "shape_id": f"urn:ngsi-ld:GtfsShape:{city}:SH1",
    }
    
    city = "Sofia"

    result = convert_gtfs_trips_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
        "type": "GtfsTrip",

        "route": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
        },

        "service": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsService:{city}:S1",
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
            "object": f"urn:ngsi-ld:GtfsShape:{city}:SH1",
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