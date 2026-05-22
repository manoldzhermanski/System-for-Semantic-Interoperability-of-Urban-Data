import pytest
from shapely.geometry import LineString

from netex.netex_utils import netex_helper_create_service_link_info

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
        "Shape1": LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "Trip1": "Shape1"
    }

    result = list(
        netex_helper_create_service_link_info(
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


def test_service_link_info_missing_input(caplog):
    """
    Test that the function handles missing input data.
    """
    with caplog.at_level("ERROR"):
        result = list(netex_helper_create_service_link_info({}, {}, {}, {}))

    assert result == []
    assert "Missing required input data" in caplog.text



def test_service_link_info_missing_shape(caplog):
    """
    Test that the function handles missing shape mapping for a trip.
    """
    stops_per_trip = {"Trip1": ["Stop1", "Stop2"]}

    stop_coordinates = {
        "Stop1": (0.0, 0.0),
        "Stop2": (10.0, 0.0),
    }

    shape_geometries = {
        "Shape1": LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "Trip1": "Shape2"
    }

    with caplog.at_level("ERROR"):
        result = list(netex_helper_create_service_link_info(stops_per_trip, stop_coordinates, shape_geometries, shape_per_trip))

    assert result == []
    assert "Missing shape ID for trip Trip1" in caplog.text


def test_service_link_info_multiple_trips():
    """
    Test that the function can handle multiple trips.
    """
    stops_per_trip = {
        "Trip1": ["Stop1", "Stop2"],
        "Trip2": ["Stop3", "Stop4"],
    }

    stop_coordinates = {
        "Stop1": (0, 0),
        "Stop2": (10, 0),
        "Stop3": (0, 0),
        "Stop4": (5, 0),
    }

    shape_geometries = {
        "Shape1": LineString([(0, 0), (10, 0)]),
        "Shape2": LineString([(0, 0), (5, 0)]),
    }

    shape_per_trip = {
        "Trip1": "Shape1",
        "Trip2": "Shape2",
    }

    result = list(netex_helper_create_service_link_info(stops_per_trip, stop_coordinates, shape_geometries,shape_per_trip))

    assert len(result) == 2
    trip_ids = {res["trip_id"] for res in result}
    assert trip_ids == {"Trip1", "Trip2"}
