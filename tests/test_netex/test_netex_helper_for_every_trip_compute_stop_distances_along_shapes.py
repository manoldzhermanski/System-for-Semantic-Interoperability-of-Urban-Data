import logging
import pytest
from shapely.geometry import LineString
from netex.netex_utils import netex_helper_for_every_trip_compute_stop_distances_along_shapes


def test_compute_stop_distances_for_single_trip():
    """
    Test successful computation for a single trip.
    """

    stops_per_trip = {
        "TRIP1": ["STOP1", "STOP2"]
    }

    stop_coordinates = {
        "STOP1": (2.0, 0.0),
        "STOP2": (7.0, 0.0),
    }

    shape_geometries = {
        "SHAPE1": LineString([
            (0, 0),
            (10, 0)
        ])
    }

    shape_per_trip = {
        "TRIP1": "SHAPE1"
    }

    result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
        stops_per_trip,
        stop_coordinates,
        shape_geometries,
        shape_per_trip
    )

    assert result == {
        "TRIP1": {
            "STOP1": 2.0,
            "STOP2": 7.0,
        }
    }


def test_compute_stop_distances_for_multiple_trips():
    """
    Test successful computation for multiple trips.
    """

    stops_per_trip = {
        "TRIP1": ["STOP1"],
        "TRIP2": ["STOP2"]
    }

    stop_coordinates = {
        "STOP1": (2.0, 0.0),
        "STOP2": (5.0, 0.0),
    }

    shape_geometries = {
        "SHAPE1": LineString([(0, 0), (10, 0)]),
        "SHAPE2": LineString([(0, 0), (20, 0)]),
    }

    shape_per_trip = {
        "TRIP1": "SHAPE1",
        "TRIP2": "SHAPE2",
    }

    result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
        stops_per_trip,
        stop_coordinates,
        shape_geometries,
        shape_per_trip
    )

    assert result == {
        "TRIP1": {
            "STOP1": 2.0
        },
        "TRIP2": {
            "STOP2": 5.0
        }
    }


def test_returns_empty_when_required_input_missing(caplog):
    """
    Test that missing required input data returns empty dictionary.
    """

    with caplog.at_level(logging.ERROR):

        result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            {},
            {},
            {},
            {}
        )

    assert result == {}

    assert "Missing required input data for computing stop distances along shapes" in caplog.text


def test_skips_trip_when_shape_id_missing(caplog):
    """
    Test that trips with missing shape IDs are skipped.
    """

    stops_per_trip = {
        "TRIP1": ["STOP1"]
    }

    stop_coordinates = {
        "STOP1": (2.0, 0.0)
    }

    shape_geometries = {
        "SHAPE1": LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "TRIP2": "SHAPE2",
    }

    with caplog.at_level(logging.ERROR):

        result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip
        )

    assert result == {}

    assert "Missing shape ID for trip TRIP1" in caplog.text


def test_skips_trip_when_shape_geometry_missing(caplog):
    """
    Test that trips with missing shape geometries are skipped.
    """

    stops_per_trip = {
        "TRIP1": ["STOP1"]
    }

    stop_coordinates = {
        "STOP1": (2.0, 0.0)
    }

    shape_geometries = {
        "SHAPE2": LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "TRIP1": "SHAPE1"
    }

    with caplog.at_level(logging.ERROR):

        result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip
        )

    assert result == {}

    assert "Invalid shape geometry for trip TRIP1" in caplog.text


def test_skips_trip_when_shape_geometry_is_empty(caplog):
    """
    Test that trips with empty shape geometries are skipped.
    """

    stops_per_trip = {
        "TRIP1": ["STOP1"]
    }

    stop_coordinates = {
        "STOP1": (2.0, 0.0)
    }

    shape_geometries = {
        "SHAPE1": LineString([])
    }

    shape_per_trip = {
        "TRIP1": "SHAPE1"
    }

    with caplog.at_level(logging.ERROR):

        result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip
        )

    assert result == {}

    assert "Invalid shape geometry for trip TRIP1" in caplog.text


def test_partial_success_when_one_trip_fails(caplog):
    """
    Test that valid trips are still processed when another trip fails.
    """

    stops_per_trip = {
        "TRIP1": ["STOP1"],
        "TRIP2": ["STOP2"]
    }

    stop_coordinates = {
        "STOP1": (2.0, 0.0),
        "STOP2": (5.0, 0.0),
    }

    shape_geometries = {
        "SHAPE1": LineString([(0, 0), (10, 0)])
    }

    shape_per_trip = {
        "TRIP1": "SHAPE1"
    }

    with caplog.at_level(logging.ERROR):

        result = netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_geometries,
            shape_per_trip
        )

    assert result == {
        "TRIP1": {
            "STOP1": 2.0
        }
    }

    assert "Missing shape ID for trip TRIP2" in caplog.text