from gtfs_static.gtfs_static_utils import convert_gtfs_stops_to_ngsi_ld

def test_convert_gtfs_stops_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for stops.txt
    """
    entity = {
        "stop_id": "urn:ngsi-ld:GtfsStop:STOP_1",
        "stop_code": "S1",
        "stop_name": "Central Station",
        "tts_stop_name": "Central Station",
        "stop_desc": "Main railway station",
        "stop_lon": 23.3219,
        "stop_lat": 42.6977,
        "zone_id": "urn:ngsi-ld:GtfsZone:Z1",
        "stop_url": "https://example.com/stops/1",
        "location_type": 1,
        "parent_station": "urn:ngsi-ld:GtfsStop:STATION_1",
        "stop_timezone": "Europe/Sofia",
        "wheelchair_boarding": 1,
        "level_id": "urn:ngsi-ld:GtfsLevel:L1",
        "platform_code": "1A",
        "stop_access": 0,
    }

    result = convert_gtfs_stops_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsStop:STOP_1",
        "type": "GtfsStop",
        "code": {
            "type": "Property",
            "value": "S1",
        },
        "name": {
            "type": "Property",
            "value": "Central Station",
        },
        "tts_stop_name": {
            "type": "Property",
            "value": "Central Station",
        },
        "description": {
            "type": "Property",
            "value": "Main railway station",
        },
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [23.3219, 42.6977],
            },
        },
        "zone_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsZone:Z1",
        },
        "stop_url": {
            "type": "Property",
            "value": "https://example.com/stops/1",
        },
        "locationType": {
            "type": "Property",
            "value": 1,
        },
        "hasParentStation": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:STATION_1",
        },
        "timezone": {
            "type": "Property",
            "value": "Europe/Sofia",
        },
        "wheelchair_boarding": {
            "type": "Property",
            "value": 1,
        },
        "level": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsLevel:L1",
        },
        "platform_code": {
            "type": "Property",
            "value": "1A",
        },
        "stop_access": {
            "type": "Property",
            "value": 0,
        },
    }

def test_convert_gtfs_stops_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for stops.txt when optional fileds are missing
    """
    entity = {
        "stop_id": "urn:ngsi-ld:GtfsStop:STOP_1",
        "stop_name": "Central Station",
        "stop_lon": 23.3219,
        "stop_lat": 42.6977,
        "parent_station": "urn:ngsi-ld:GtfsStop:STATION_1",
        "stop_access": 0,
    }

    result = convert_gtfs_stops_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsStop:STOP_1",
        "type": "GtfsStop",
        "code": {
            "type": "Property",
            "value": None,
        },
        "name": {
            "type": "Property",
            "value": "Central Station",
        },
        "tts_stop_name": {
            "type": "Property",
            "value": None,
        },
        "description": {
            "type": "Property",
            "value": None,
        },
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [23.3219, 42.6977],
            },
        },
        "zone_id": {
            "type": "Relationship",
            "object": None,
        },
        "stop_url": {
            "type": "Property",
            "value": None,
        },
        "locationType": {
            "type": "Property",
            "value": None,
        },
        "hasParentStation": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:STATION_1",
        },
        "timezone": {
            "type": "Property",
            "value": None,
        },
        "wheelchair_boarding": {
            "type": "Property",
            "value": None,
        },
        "level": {
            "type": "Relationship",
            "object": None,
        },
        "platform_code": {
            "type": "Property",
            "value": None,
        },
        "stop_access": {
            "type": "Property",
            "value": 0,
        },
    }
