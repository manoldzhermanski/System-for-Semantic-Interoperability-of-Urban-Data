import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_index_stops_by_trip_success():
    """
    Check that stops are properly grouped by trip
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"}
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime2",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"}
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime3",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop3"}
        }
    ]

    result = netex_utils.netex_index_stops_by_trip(stop_times)

    assert result == {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": [ stop_times[0]["hasStop"], stop_times[1]["hasStop"]],
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip2": [stop_times[2]["hasStop"]]
    }

def test_netex_index_stops_by_trip_missing_has_trip():
    """
    Check that error is logged when hasTrip is missing
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_stops_by_trip(stop_times)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Stop time missing hasTrip: %r", stop_times[0]["id"])

def test_netex_index_stops_by_trip_invalid_has_trip_structure():
    """
    Check that error is logged when hasTrip object is missing
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasTrip": { "type": "Relationship"},
            "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_stops_by_trip(stop_times)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid hasTrip structure: %r", stop_times[0]["id"])

def test_netex_index_stops_by_trip_missing_has_stop():
    """
    Check that error is logged when hasStop is missing
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_stops_by_trip(stop_times)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Stop time missing hasStop: %r", stop_times[0]["id"])

def test_netex_index_stops_by_trip_invalid_has_stop_structure():
    """
    Check that error is logged when hasStop object is missing
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "hasStop": {"type": "Relationship"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_stops_by_trip(stop_times)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid hasStop structure: %r", stop_times[0]["id"])

def test_netex_index_stops_by_trip_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_stops_by_trip([])

    assert result == {}