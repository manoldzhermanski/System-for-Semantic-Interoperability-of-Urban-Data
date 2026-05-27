import logging
import pytest
import netex.netex_utils as netex_utils
from shapely.geometry import LineString
from unittest.mock import MagicMock


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

    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
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

    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
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

    netex_utils.logger.error = MagicMock()
    
    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
        {},
        {},
        {},
        {}
    )

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Missing required input data for computing stop distances along shapes")


def test_skips_trip_when_shape_id_missing():
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

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
        stops_per_trip,
        stop_coordinates,
        shape_geometries,
        shape_per_trip
    )

    assert result == {}
    netex_utils.logger.error.assert_called_once_with("Missing shape ID for trip %s", "TRIP1")


def test_skips_trip_when_shape_geometry_missing():
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

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
        stops_per_trip,
        stop_coordinates,
        shape_geometries,
            shape_per_trip
        )

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid shape geometry for trip %s", "TRIP1")


def test_skips_trip_when_shape_geometry_is_empty():
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

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
        stops_per_trip,
        stop_coordinates,
        shape_geometries,
        shape_per_trip
    )

    assert result == {}
    netex_utils.logger.error.assert_called_once_with("Invalid shape geometry for trip %s", "TRIP1")


def test_partial_success_when_one_trip_fails():
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

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_for_every_trip_compute_stop_distances_along_shapes(
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

    netex_utils.logger.error.assert_called_once_with("Missing shape ID for trip %s", "TRIP2")