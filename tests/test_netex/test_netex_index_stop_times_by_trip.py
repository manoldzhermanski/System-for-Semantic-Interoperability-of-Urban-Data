import netex.netex_utils as netex_utils
from unittest.mock import MagicMock


def test_netex_index_stop_times_by_trip_success():
    """
    Check that proper structure is created
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasTrip": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime2",
            "hasTrip": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime3",
            "hasTrip": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"
            }
        }
    ]

    result = netex_utils.netex_index_stop_times_by_trip(stop_times)

    assert result == {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": [
            stop_times[0],
            stop_times[1]
        ],
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip2": [
            stop_times[2]
        ]
    }


def test_netex_index_stop_times_by_trip_missing_has_trip():
    """
    Check that error is logged when `hasTrip` is missing
    """
    stop_times = [
        {"id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1"}
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_stop_times_by_trip(stop_times)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Stop time missing hasTrip: %r", stop_times[0]["id"])


def test_netex_index_stop_times_by_trip_invalid_has_trip_structure():
    """
    Check that error is logged when hasTrip object is missing
    """
    stop_times = [
        {
            "id": "urn:ngsi-ld:GtfsStopTime:Sofia:StopTime1",
            "hasTrip": {
                "type": "Relationship"
            }
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_stop_times_by_trip(stop_times)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid hasTrip structure: %r", stop_times[0]["id"])


def test_netex_index_stop_times_by_trip_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_stop_times_by_trip([])

    assert result == {}