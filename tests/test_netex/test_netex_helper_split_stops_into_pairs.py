import pytest
from netex.netex_utils import netex_helper_split_stops_into_pairs

def test_split_stops_into_pairs_returns_dictionary():
    """
    Test that the function returns a dictionary.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1", "STOP_2", "STOP_3"]
    }

    result = netex_helper_split_stops_into_pairs(stops_per_trip)

    assert isinstance(result, dict)
    assert result == {
        "TRIP_1": [
            ("STOP_1", "STOP_2"),
            ("STOP_2", "STOP_3"),
        ]
    }

def test_split_stops_into_pairs_handles_multiple_trips():
    """
    Test creating stop pairs for multiple trips.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1", "STOP_2", "STOP_3"],
        "TRIP_2": ["STOP_A", "STOP_B"],
    }

    result = netex_helper_split_stops_into_pairs(stops_per_trip)

    assert result == {
        "TRIP_1": [
            ("STOP_1", "STOP_2"),
            ("STOP_2", "STOP_3"),
        ],
        "TRIP_2": [
            ("STOP_A", "STOP_B"),
        ],
    }


def test_split_stops_into_pairs_handles_single_stop_trip():
    """
    Test that a trip with only one stop returns an empty pair list.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1"]
    }

    result = netex_helper_split_stops_into_pairs(stops_per_trip)

    assert result == {
        "TRIP_1": []
    }


def test_split_stops_into_pairs_handles_empty_stop_list():
    """
    Test that an empty stop list returns an empty pair list.
    """

    stops_per_trip = {
        "TRIP_1": []
    }

    result = netex_helper_split_stops_into_pairs(stops_per_trip)

    assert result == {
        "TRIP_1": []
    }


def test_split_stops_into_pairs_handles_empty_input():
    """
    Test that empty input returns an empty dictionary.
    """

    result = netex_helper_split_stops_into_pairs({})

    assert result == {}