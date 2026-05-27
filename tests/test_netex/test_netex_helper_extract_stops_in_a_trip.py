import pytest
import logging
import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_helper_extract_stops_in_a_trip_with_single_trip_and_multiple_stops():
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:2",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop1"},
            "stopSequence": {"type": "Property", "value": 2},
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop2"},
            "stopSequence": {"type": "Property", "value": 1},
        },
    ]

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {"Trip1": ["Stop2", "Stop1"]}

def test_netex_helper_extract_stops_in_a_trip_with_multiple_trips():
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop1"},
            "stopSequence": {"type": "Property", "value": 1},
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip2:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip2"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop2"},
            "stopSequence": {"type": "Property", "value": 1},
        },
    ]

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {
        "Trip1": ["Stop1"],
        "Trip2": ["Stop2"],
    }

def test_netex_helper_extract_stops_in_a_trip_with_empty_input():
    assert netex_utils.netex_helper_extract_stops_in_a_trip([]) == {}

def test_netex_helper_extract_stops_in_a_trip_with_none_values():
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": None},
            "hasStop": {"type": "Relationship", "object": None},
            "stopSequence": {"type": "Property", "value": None},
        }
    ]

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}

def test_netex_helper_extract_stops_in_a_trip_skips_unsupported_entity_type():
    """
    Test that unsupported entity types are skipped.
    """

    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:1",
            "type": "GtfsStop",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop1"},
            "stopSequence": {"type": "Property", "value": 1},
        }
    ]
    
    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}
    netex_utils.logger.error.assert_called_once_with("Unsupported entity type, expected GtfsStopTime: %s", "GtfsStop")

def test_netex_helper_extract_stops_in_a_trip_skips_invalid_trip_id():
    """
    Test that malformed trip IDs are skipped.
    """

    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:broken_trip_id:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "broken_trip_id"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "stopSequence": {"type": "Property", "value": 1},
        }
    ]
    
    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}
    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsTrip: %r", "broken_trip_id")

def test_netex_helper_extract_stops_in_a_trip_skips_invalid_stop_id():
    """
    Test that malformed stop IDs are skipped.
    """

    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "broken_stop_id"},
            "stopSequence": {"type": "Property", "value": 1},
        }
    ]
    
    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}
    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsStop: %r", "broken_stop_id")

def test_netex_helper_extract_stops_in_a_trip_skips_invalid_sequence():
    """
    Test that non-integer stop sequences are skipped.
    """

    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:not_an_int",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "stopSequence": {"type": "Property", "value": "not_an_int"},
        }
    ]
    
    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {}
    netex_utils.logger.error.assert_called_once_with("Invalid or missing stop sequence: %r", "not_an_int")

def test_netex_helper_extract_stops_in_a_trip_correctly_sorts_many_stops():
    """
    Test that stops are sorted correctly by stopSequence.
    """

    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:3",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop3"},
            "stopSequence": {"type": "Property", "value": 3},
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:1",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "stopSequence": {"type": "Property", "value": 1},
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:TEST:Trip1:2",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship","object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "stopSequence": {"type": "Property", "value": 2},
        },
    ]

    result = netex_utils.netex_helper_extract_stops_in_a_trip(stop_times)

    assert result == {
        "Trip1": ["Stop1", "Stop2", "Stop3"]
    }