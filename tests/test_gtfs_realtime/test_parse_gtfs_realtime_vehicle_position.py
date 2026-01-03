from gtfs_realtime.gtfs_realtime_utils import parse_gtfs_realtime_vehicle_position

def test_parse_gtfs_realtime_vehicle_position_full_payload():
    """
    Check that the entries with data are parsed correctly and the remaining fields have None values
    """
    entity = {
        "id": "VP1",
        "vehicle": {
            "trip": {"trip_id": "T1"},
            "vehicle": {"id": "V1", "label": "Bus 42"},
            "position": {"latitude": 42.0, "longitude": 24.0, "speed": 50},
            "current_stop_sequence": 10,
            "stop_id": "S1",
            "timestamp": 0,
            "multi_carriage_details": [
                {"id": "C1", "label": "Carriage A", "occupancy_status": "FULL", "occupancy_percentage": 100, "carriage_sequence": 1}
            ]
        }
    }
    
    expected = {
        "id": "urn:ngsi-ld:GtfsRealtimeVehiclePosition:VP1",
        "trip": {
            "trip_id": "urn:ngsi-ld:GtfsTrip:T1",
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
                }
            },
        "vehicle": {
            "id": "urn:ngsi-ld:GtfsVehicle:V1",
            "label": "Bus 42",
            "license_plate": None,
            "wheelchair_accessible": None
        },
        "position": {
            "latitude": 42.0,
            "longitude": 24.0,
            "bearing": None,
            "odometer": None,
            "speed": 50},
        "current_stop_sequence": 10,
        "stop_id": "urn:ngsi-ld:GtfsStop:S1",
        "current_status": None,
        "timestamp": "1970-01-01T00:00:00Z",
        "congestion_level": None,
        "occupancy_status": None,
        "occupancy_percentage": None,
        "multi_carriage_details": [
            {"id": "urn:ngsi-ld:GtfsRealtimeCarriage:C1", "label": "Carriage A", "occupancy_status": "FULL", "occupancy_percentage": 100, "carriage_sequence": 1}
        ]
        }
    
    
    result = parse_gtfs_realtime_vehicle_position(entity)
   
    assert result == expected

def test_parse_gtfs_realtime_vehicle_position_empty_entity():
    """
    Check that if the VehiclePosition entity is empty, all fields have None values
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
        }
            },
        "vehicle": {
            "id": None,
            "label": None,
            "license_plate": None,
            "wheelchair_accessible": None
            },
        "position": {
            "latitude": None,
            "longitude": None,
            "bearing": None,
            "odometer": None,
            "speed": None
            },
        "current_stop_sequence": None,
        "stop_id": None,
        "current_status": None,
        "timestamp": None,
        "congestion_level": None,
        "occupancy_status": None,
        "occupancy_percentage": None,
        "multi_carriage_details": []
        
    }
    result = parse_gtfs_realtime_vehicle_position(entity)
    
    assert result == expected
