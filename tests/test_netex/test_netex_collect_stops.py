import pytest
from netex.netex_utils import netex_collect_stops


def test_netex_collect_stops_returns_only_referenced_stops():
    """
    Test that all GtfsStop entities who have a connection with a GtfsStopTime entity are collected
    """
    stop_times = [
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime2:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop2"}},
    ]

    stops = [
        {"id": "urn:ngsi-ld:GtfsStop:Stop1", "name": "Stop 1"},
        {"id": "urn:ngsi-ld:GtfsStop:Stop2", "name": "Stop 2"},
        {"id": "urn:ngsi-ld:GtfsStop:Stop3", "name": "Stop 3"},
    ]

    result = netex_collect_stops(stop_times, stops)

    assert result == [
        {"id": "urn:ngsi-ld:GtfsStop:Stop1", "name": "Stop 1"},
        {"id": "urn:ngsi-ld:GtfsStop:Stop2", "name": "Stop 2"},
    ]
    
def test_netex_collect_stops_returns_unique_stops():
    """
    Test that no duplicates are added
    """
    stop_times = [
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime2:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime3:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
    ]

    stops = [
        {"id": "urn:ngsi-ld:GtfsStop:Stop1", "name": "Central Station"},
    ]

    result = netex_collect_stops(stop_times, stops)

    assert result == [
        {"id": "urn:ngsi-ld:GtfsStop:Stop1", "name": "Central Station"},
    ]
    
def test_netex_collect_stops_ignores_stop_time_without_has_stop(caplog):
    """
    Test that an error is logged when a GtfsStopTime entity has a missing `hasStop` attribute
    """
    stop_times = [
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1:1"},
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime2:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
    ]

    stops = [
        {"id": "urn:ngsi-ld:GtfsStop:Stop1"},
    ]

    result = netex_collect_stops(stop_times, stops)

    assert result == [{"id": "urn:ngsi-ld:GtfsStop:Stop1"}]

    assert "missing or invalid hasStop" in caplog.text
    
def test_netex_collect_stops_ignores_invalid_has_stop(caplog):
    """
    Test that an error is logged when the `hasStop` attribute is not proper
    """
    stop_times = [
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1:1", "hasStop": {}},
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime2:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
    ]

    stops = [
        {"id": "urn:ngsi-ld:GtfsStop:Stop1"},
    ]

    result = netex_collect_stops(stop_times, stops)

    assert result == [{"id": "urn:ngsi-ld:GtfsStop:Stop1"}]

    assert "missing or invalid hasStop" in caplog.text
    
def test_netex_collect_stops_returns_empty_list_when_no_matching_stop():
    """
    Test that if there aren't any GtfsStop entites who have a relationship with a GtfsStopTime entity, an empty list is returned
    """
    stop_times = [
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1:1", "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"}},
    ]

    stops = [
        {"id": "urn:ngsi-ld:GtfsStop:Stop2"},
    ]

    result = netex_collect_stops(stop_times, stops)

    assert result == []