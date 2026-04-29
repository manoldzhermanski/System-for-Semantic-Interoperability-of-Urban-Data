import pytest
from netex.netex_utils import netex_helper_extract_stops_in_a_trip

def test_netex_helper_extract_stops_in_a_trip_with_single_trip_and_multiple_stops():
    stop_times = [
        {
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"},
            "stopSequence": {"type": "Property", "value": 2},
        },
        {
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop2"},
            "stopSequence": {"type": "Property", "value": 1},
        },
    ]

    result = netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {"Trip1": ["Stop2", "Stop1"]}

def test_netex_helper_extract_stops_in_a_trip_with__multiple_trips():
    stop_times = [
        {
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"},
            "stopSequence": {"type": "Property", "value": 1},
        },
        {
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop2"},
            "stopSequence": {"type": "Property", "value": 1},
        },
    ]

    result = netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {
        "Trip1": ["Stop1"],
        "Trip2": ["Stop2"],
    }

def test_invalid_entries_are_skipped():
    stop_times = [
        {
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop1"},
            # stopSequence is missing
        },
        {
            # hasTrip is missing
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Stop2"},
            "stopSequence": {"type": "Property", "value": 1},
        },
    ]

    result = netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}

def test_netex_helper_extract_stops_in_a_trip_with_empty_input():
    assert netex_helper_extract_stops_in_a_trip([]) == {}

def test_netex_helper_extract_stops_in_a_trip_with_none_values():
    stop_times = [
        {
            "hasTrip": {"type": "Relationship", "object": None},
            "hasStop": {"type": "Relationship", "object": None},
            "stopSequence": {"type": "Property", "value": None},
        }
    ]

    result = netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}