from gtfs_realtime.gtfs_realtime_utils import convert_gtfs_realtime_trip_updates_to_ngsi_ld

def test_convert_gtfs_realtime_trip_updates_to_ngsi_ld_partial_payload():
    """
    Check that the normalized entity is converted to a NGSI-LD representation
    """
    entity = {
        "id": "urn:ngsi-ld:GtfsRealtimeTripUpdate:A1",
        "trip": {
            "trip_id": "urn:ngsi-ld:GtfsTrip:T1",
            "route_id": "urn:ngsi-ld:GtfsRoute:R1",
            "direction_id": None,
            "start_time": None,
            "start_date": None,
            "schedule_relationship": "SCHEDULED",
            "modified_trip": {
                "modifications_id": None,
                "affected_trip_id": None,
                "start_time": None,
                "start_date": None,
                },
            },
        "vehicle": {
            "id": "urn:ngsi-ld:GtfsVehicle:V1",
            "label": None,
            "license_plate": None,
            "wheelchair_accessible": None
            },
        "stop_time_update":  [],
        "timestamp": "1970-01-01T00:00:00Z",
        "delay": 0,
        "trip_properties": {
            "trip_id": None,
            "start_date": None,
            "start_time": None,
            "trip_headsign": None,
            "trip_short_name": None,
            "shape_id": None
            }
        }
    
    expected = {
        "id":  "urn:ngsi-ld:GtfsRealtimeTripUpdate:A1",
        "type": "GtfsRealtimeTripUpdate",
        "trip": {
            "type": "Property",
            "value": {
                "trip_id": "urn:ngsi-ld:GtfsTrip:T1",
                "route_id": "urn:ngsi-ld:GtfsRoute:R1",
                "direction_id": None,
                "start_time": None,
                "start_date": None,
                "schedule_relationship": "SCHEDULED",
                "modified_trip": {
                    "modifications_id": None,
                    "affected_trip_id": None,
                    "start_time": None,
                    "start_date": None,
                    },
                }
            },
        "vehicle": {
            "type": "Property",
            "value": {
                "id": "urn:ngsi-ld:GtfsVehicle:V1",
                "label": None,
                "license_plate": None,
                "wheelchair_accessible": None
                }
            },
        "stop_time_update": {
            "type": "Property",
            "value": []
            },
        "timestamp": {
            "type": "Property",
            "value": "1970-01-01T00:00:00Z",
            },
        "delay": {
            "type": "Property",
            "value": 0
            },
        "trip_properties": {
            "type": "Property",
            "value": {
                "trip_id": None,
                "start_date": None,
                "start_time": None,
                "trip_headsign": None,
                "trip_short_name": None,
                "shape_id": None
                }
            }
        }
    
    result = convert_gtfs_realtime_trip_updates_to_ngsi_ld(entity)
    
    assert result == expected
