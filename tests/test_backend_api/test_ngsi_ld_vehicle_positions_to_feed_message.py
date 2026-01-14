from unittest.mock import patch
from backend_api.main import ngsi_ld_vehicle_positions_to_feed_message
from google.transit import gtfs_realtime_pb2

def test_ngsi_ld_vehicle_positions_to_feed_message_happy_path():
    """
    Check Happy Path
    """
    ngsi_entities = [
        {
            "id": "veh1",
            "vehicle": {
                "type": "Property",
                "value": {
                    "id": "V1",
                    "label": "Bus 1",
                    "license_plate": "ABC123"
                    }
                },
            "position": {
                "type": "Property",
                "value": {
                    "latitude": 42.0,
                    "longitude": 23.0,
                    "speed": 36.0,
                    "bearing": 90.0
                    }
                },
            "trip": {
                "type": "Property",
                "value": {
                    "trip_id": "T1",
                    "route_id": "R1",
                    "direction_id": 1,
                    "start_time": "08:00:00",
                    "start_date": "20260114", 
                    "schedule_relationship": "SCHEDULED"
                    }
                },
            "current_status": {
                "type": "Property",
                "value": "IN_TRANSIT_TO"
                },
            "congestion_level": {
                "type": "Property",
                "value": "UNKNOWN_CONGESTION_LEVEL"
                },
            "occupancy_status": {
                "type": "Property",
                "value": "EMPTY"
                },
            "timestamp": {
                "type": "Property",
                "value": "2026-01-14T12:00:00Z"
                },
            "current_stop_sequence": {
                "type": "Property",
                "value": 5
                },
            "stop_id": {
                "type": "Relationship",
                "object": "S1"
                }
        }
    ]

    with patch("gtfs_realtime.gtfs_realtime_utils.iso8601_to_unix", return_value=1673707200):
        feed = ngsi_ld_vehicle_positions_to_feed_message(ngsi_entities)

    assert len(feed.entity) == 1
    v = feed.entity[0].vehicle
    assert v.vehicle.id == "V1"
    assert v.vehicle.label == "Bus 1"
    assert v.vehicle.license_plate == "ABC123"
    assert v.position.latitude == 42.0
    assert v.position.longitude == 23.0
    assert v.position.speed == 36.0 / 3.6
    assert v.position.bearing == 90.0
    assert v.trip.trip_id == "T1"
    assert v.trip.route_id == "R1"
    assert v.trip.direction_id == 1
    assert v.trip.start_time == "08:00:00"
    assert v.trip.start_date == "20260114"
    assert v.trip.schedule_relationship == gtfs_realtime_pb2.TripDescriptor.SCHEDULED
    assert v.current_status == gtfs_realtime_pb2.VehiclePosition.IN_TRANSIT_TO
    assert v.congestion_level == gtfs_realtime_pb2.VehiclePosition.UNKNOWN_CONGESTION_LEVEL
    assert v.occupancy_status == gtfs_realtime_pb2.VehiclePosition.EMPTY
    assert v.timestamp == 1768392000
    assert v.current_stop_sequence == 5
    assert v.stop_id == "S1"

def test_ngsi_ld_vehicle_positions_to_feed_message_missing_vehicle_id_skipped():
    """
    Check that entity is not transformed to GTFS Realtime if Vehicle ID is missing
    """
    ngsi_entities = [
        {"id": "veh1",
        "vehicle": {
            "type": "Property",
            "value": {
                "label": "Bus"
                }
            }
        }
    ]

    feed = ngsi_ld_vehicle_positions_to_feed_message(ngsi_entities)
    assert len(feed.entity) == 0

def test_ngsi_ld_vehicle_positions_to_feed_message_missing_lat_lon_skipped():
    """
    Check that entity is not transformed to GTFS Realtime if longitudinal and lateral position are missing
    """
    ngsi_entities = [
        {
            "id": "veh1",
            "vehicle": {
                "type": "Property",
                "value": {
                    "id": "v1"
                    }
                },
            "position": {
                "type": "Property",
                "value": {
                    "speed": 36.0
                    }
                }
        }
    ]
    feed = ngsi_ld_vehicle_positions_to_feed_message(ngsi_entities)
    assert len(feed.entity) == 0

def test_ngsi_ld_vehicle_positions_to_feed_message_missing_entity_id_skipped():
    """
    Check that entity is not transformed to GTFS Realtime if Entity ID are missing
    """
    ngsi_entities = [
        {"vehicle": {
            "type": "Property",
            "value": {
                "id": "v1"
                }
            },
            "position": {
                "type": "Property",
                "value": {
                    "latitude": 1.0,
                    "longitude": 2.0
                    }
                }
            }
        ]
    
    feed = ngsi_ld_vehicle_positions_to_feed_message(ngsi_entities)
    assert len(feed.entity) == 0
