from gtfs_realtime.gtfs_realtime_utils import parse_gtfs_realtime_trip_updates

def test_parse_gtfs_realtime_trip_update_full_payload():
    """
    Check that the entries with data are parsed correctly and the remaining fields have None values
    """
    entity = {
        "id": "A1",
        "trip_update": {
            "trip": {
                "trip_id": "T1",
                "route_id": "R1",
                "schedule_relationship": "SCHEDULED",
                },
            "vehicle": {
                "id": "V1"
                },
            "timestamp": 0,
            "delay": 0
            }  
        }
        
    expected = {
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
    
    result = parse_gtfs_realtime_trip_updates(entity)
   
    assert result == expected

def test_parse_gtfs_realtime_alerts_empty_entity():
    """
    Check that if the TripUpdate entity is empty, all fields have None values
    """
    entity = {}
    
    expected = {
        "id": None,
        "trip": {
            "trip_id": None,
            "route_id": None,
            "direction_id": None,
            "start_time": None,
            "start_date": None,
            "schedule_relationship": None,
            "modified_trip": {
                "modifications_id": None,
                "affected_trip_id": None,
                "start_time": None,
                "start_date": None,
                },
            },
        "vehicle": {
            "id": None,
            "label": None,
            "license_plate": None,
            "wheelchair_accessible": None
            },
        "stop_time_update":  [],
        "timestamp": None,
        "delay": None,
        "trip_properties": {
            "trip_id": None,
            "start_date": None,
            "start_time": None,
            "trip_headsign": None,
            "trip_short_name": None,
            "shape_id": None
            }
        }
    
    result = parse_gtfs_realtime_trip_updates(entity)
    
    assert result == expected
