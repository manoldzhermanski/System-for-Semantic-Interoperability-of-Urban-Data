from gtfs_realtime.gtfs_realtime_utils import covert_gtfs_realtime_vehicle_position_to_ngsi_ld

def test_covert_gtfs_realtime_vehicle_position_to_ngsi_ld_partial_payload():
    """
    Check that the normalized entity is converted to a NGSI-LD representation
    """
    entity = {
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
            "speed": 50
            },
        "current_stop_sequence": 10,
        "stop_id": "urn:ngsi-ld:GtfsStop:S1",
        "current_status": None,
        "timestamp": "1970-01-01T00:00:00Z",
        "congestion_level": None,
        "occupancy_status": None,
        "occupancy_percentage": None,
        "multi_carriage_details": [
            {
                "id": "urn:ngsi-ld:GtfsRealtimeCarriage:C1",
                "label": "Carriage A",
                "occupancy_status": "FULL",
                "occupancy_percentage": 100,
                "carriage_sequence": 1
                }
            ]
        }
    
    expected = {
        "id": entity.get("id"),
        "type": "GtfsRealtimeVehiclePosition",
        "trip": {
            "type": "Property",
            "value": {
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
                }
            },
        "vehicle": {
            "type": "Property",
            "value": {
                "id": "urn:ngsi-ld:GtfsVehicle:V1",
                "label": "Bus 42",
                "license_plate": None,
                "wheelchair_accessible": None
                }
            },
        "position": {
            "type": "Property",
            "value": {
                "latitude": 42.0,
                "longitude": 24.0,
                "bearing": None,
                "odometer": None,
                "speed": 50
                }
            },
        "current_stop_sequence": {
            "type": "Property",
            "value": 10
            },
        "stop_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:S1"
            },
        "current_status": {
            "type": "Property",
            "value": None
            },
        "timestamp": {
            "type": "Property",
            "value": "1970-01-01T00:00:00Z"
            },
        "congestion_level": {
            "type": "Property",
            "value": None
            },
        "occupancy_status": {
            "type": "Property",
            "value": None
            },
        "occupancy_percentage": {
            "type": "Property",
            "value": None
            },
        "multi_carriage_details": {
            "type": "Property",
            "value": [
                {
                    "id": "urn:ngsi-ld:GtfsRealtimeCarriage:C1",
                    "label": "Carriage A",
                    "occupancy_status": "FULL",
                    "occupancy_percentage": 100,
                    "carriage_sequence": 1
                    }
                ]
            }
        }
    
    result = covert_gtfs_realtime_vehicle_position_to_ngsi_ld(entity)
    
    assert result == expected