from netex.netex_utils import netex_helper_collect_shapes_by_trip

def test_netex_helper_collect_shapes_by_trip_collects_shape_ids():
    """
    Test happy path
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"},
    ]

    shape_by_trip = {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": "urn:ngsi-ld:GtfsShape:Sofia:Shape1",
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip2": "urn:ngsi-ld:GtfsShape:Sofia:Shape2",
    }

    result = netex_helper_collect_shapes_by_trip(trips, shape_by_trip)

    assert result == ["urn:ngsi-ld:GtfsShape:Sofia:Shape1", "urn:ngsi-ld:GtfsShape:Sofia:Shape2"]
    
def test_netex_helper_collect_shapes_by_trip_skips_invalid_trip_id(caplog):
    """
    Test that warnings are logged if invalid IDs are given as input
    """
    trips = [
        {"id": 123},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
    ]

    shape_by_trip = {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": "urn:ngsi-ld:GtfsShape:Sofia:Shape1",
    }

    result = netex_helper_collect_shapes_by_trip(trips, shape_by_trip)

    assert result == ["urn:ngsi-ld:GtfsShape:Sofia:Shape1"]
    assert "Invalid trip id" in caplog.text
    
def test_netex_helper_collect_shapes_by_trip_logs_missing_shape(caplog):
    """
    Test that an warning is logged when no entities for a specific trip are found
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
    ]

    result = netex_helper_collect_shapes_by_trip(trips, {})

    assert result == []
    assert "No shape found for trip urn:ngsi-ld:GtfsTrip:Sofia:Trip1" in caplog.text
    
def test_netex_helper_collect_shapes_by_trip_empty_input():
    """
    Test that empty list is returned when empty input is given
    """
    result = netex_helper_collect_shapes_by_trip([], {})

    assert result == []