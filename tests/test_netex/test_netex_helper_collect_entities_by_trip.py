import pytest
from netex.netex_utils import netex_helper_collect_entities_by_trip

def test_netex_helper_collect_entities_by_trip_collects_entities():
    """
    Test happy path
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"},
    ]

    index = {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": [{"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime1:1"}, {"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime2:1"}],
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip2": [{"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime3:1"}],
    }

    result = netex_helper_collect_entities_by_trip(trips, index, "stop times")

    assert result == [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime1:1"},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime2:1"},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime3:1"},
    ]
    
def test_netex_helper_collect_entities_by_trip_skips_invalid_trip_id(caplog):
    """
    Test that warnings are logged if invalid IDs are given as input
    """
    trips = [
        {},
        {"id": 123},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
    ]

    index = {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": [{"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime1:1"}],
    }

    result = netex_helper_collect_entities_by_trip(trips, index, "stop times")

    assert result == [{"id": "urn:ngsi-ld:GtfsTrip:Sofia:GtfsStopTime1:1"}]
    assert "Invalid or missing trip id" in caplog.text
    
def test_netex_helper_collect_entities_by_trip_logs_when_no_entities(caplog):
    """
    Test that an warning is logged when no entities for a specific trip are found
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
    ]

    result = netex_helper_collect_entities_by_trip(trips, {}, "stop times")

    assert result == []
    assert "No stop times found for trip urn:ngsi-ld:GtfsTrip:Sofia:Trip1" in caplog.text
    
def test_netex_helper_collect_entities_by_trip_empty_trips():
    """
    Test that empty list is returned when empty input is given
    """
    result = netex_helper_collect_entities_by_trip([], {}, "stop times")

    assert result == []