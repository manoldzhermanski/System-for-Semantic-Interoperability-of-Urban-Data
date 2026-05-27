import pytest
import netex.netex_utils as netex_utils
from unittest.mock import MagicMock, call

def test_service_link_info_happy_path():
    """
    Test that the function yields correct ServiceLink information for a simple case.
    """
    stops_per_trip = {
        "Trip1": ["Stop1", "Stop2"]
    }

    stop_coordinates = {
        "Stop1": (0.0, 0.0),
        "Stop2": (10.0, 0.0),
    }

    shape_geometries = {
        "Shape1": netex_utils.LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "Trip1": "Shape1"
    }

    result = list(
        netex_utils.netex_helper_create_service_link_info(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip,
        )
    )

    assert len(result) == 1

    item = result[0]
    assert item["trip_id"] == "Trip1"
    assert item["from_stop"] == "Stop1"
    assert item["to_stop"] == "Stop2"
    assert "geometry" in item
    assert item["distance"] == pytest.approx(10.0)


def test_service_link_info_missing_input():
    """
    Test that the function handles missing input data.
    """
    netex_utils.logger.error = MagicMock()
    
    result = list(netex_utils.netex_helper_create_service_link_info({}, {}, {}, {}))

    assert result == []
    netex_utils.logger.error.assert_called_once_with("Missing required input data")


def test_service_link_info_missing_shape():
    """
    Test that the function handles missing shape mapping for a trip.
    """
    stops_per_trip = {"Trip1": ["Stop1", "Stop2"]}

    stop_coordinates = {
        "Stop1": (0.0, 0.0),
        "Stop2": (10.0, 0.0),
    }

    shape_geometries = {
        "Shape1": netex_utils.LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "Trip1": "Shape2"
    }

    netex_utils.logger.error = MagicMock()
    
    result = list(netex_utils.netex_helper_create_service_link_info(stops_per_trip, stop_coordinates, shape_geometries, shape_per_trip))

    assert result == []
    netex_utils.logger.error.assert_has_calls([
        call("Invalid shape geometry for trip %s", "Trip1"),
        call("Missing shape ID for trip %s", "Trip1")
    ])


def test_service_link_info_multiple_trips():
    """
    Test that the function can handle multiple trips.
    """
    stops_per_trip = {
        "Trip1": ["Stop1", "Stop2"],
        "Trip2": ["Stop3", "Stop4"],
    }

    stop_coordinates = {
        "Stop1": (0.0, 0.0),
        "Stop2": (10.0, 0.0),
        "Stop3": (0.0, 0.0),
        "Stop4": (5.0, 0.0),
    }

    shape_geometries = {
        "Shape1": netex_utils.LineString([(0, 0), (10, 0)]),
        "Shape2": netex_utils.LineString([(0, 0), (5, 0)]),
    }

    shape_per_trip = {
        "Trip1": "Shape1",
        "Trip2": "Shape2",
    }

    result = list(netex_utils.netex_helper_create_service_link_info(stops_per_trip, stop_coordinates, shape_geometries,shape_per_trip))

    assert len(result) == 2
    trip_ids = {res["trip_id"] for res in result}
    assert trip_ids == {"Trip1", "Trip2"}
