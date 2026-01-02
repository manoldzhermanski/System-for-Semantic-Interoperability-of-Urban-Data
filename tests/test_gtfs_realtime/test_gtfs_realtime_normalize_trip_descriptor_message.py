from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_normalize_trip_descriptor_message

def test_normalize_trip_full_payload():
    """
    Check that if all fields in a TripDescriptor message are present,
    the result of the function call should be have all fields and all id's should be GTFS URNs
    """
    trip = {
        "trip_id": "123",
        "route_id": "10",
        "direction_id": "1",
        "start_time": "08:00:00",
        "start_date": "20240101",
        "schedule_relationship": "SCHEDULED",
        "modified_trip": {
            "modifications_id": "mod-1",
            "affected_trip_id": "trip-456",
            "start_time": "08:10:00",
            "start_date": "20240102",
        },
    }

    result = gtfs_realtime_normalize_trip_descriptor_message(trip)
    
    expected = {
        "trip_id": "urn:ngsi-ld:GtfsTrip:123",
        "route_id": "urn:ngsi-ld:GtfsRoute:10",
        "direction_id": "1",
        "start_time": "08:00:00",
        "start_date": "20240101",
        "schedule_relationship": "SCHEDULED",
        "modified_trip": {
            "modifications_id": "mod-1",
            "affected_trip_id": "urn:ngsi-ld:GtfsTrip:trip-456",
            "start_time": "08:10:00",
            "start_date": "20240102",
        },
    }
    
    assert result == expected
    
def test_normalize_trip_with_missing_fields():
    """
    Check that if fields are missing from a TripDescriptor message,
    the normalized dictionary structure has replaced those fields with None values
    """
    trip = {
        "trip_id": "123",
        "route_id": "10",
        "start_time": "08:00:00",
        "start_date": "20240101",
        "schedule_relationship": "SCHEDULED",
        "modified_trip": {
            "modifications_id": "mod-1",
        },
    }

    expected = {
        "trip_id": "urn:ngsi-ld:GtfsTrip:123",
        "route_id": "urn:ngsi-ld:GtfsRoute:10",
        "direction_id": None,
        "start_time": "08:00:00",
        "start_date": "20240101",
        "schedule_relationship": "SCHEDULED",
        "modified_trip": {
            "modifications_id": "mod-1",
            "affected_trip_id": None,
            "start_time": None,
            "start_date": None,
        },
    }
    
    result = gtfs_realtime_normalize_trip_descriptor_message(trip)
    
    assert result == expected
    
def test_normalize_empty_trip():
    """
    Check that if the TripDescriptor message is empty,
    all fields of the TripDescriptor are None values
    """
    result = gtfs_realtime_normalize_trip_descriptor_message({})

    expected = {
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
    }
    
    assert result == expected
