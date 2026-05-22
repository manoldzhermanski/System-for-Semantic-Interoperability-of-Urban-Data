import logging
import pytest
from shapely.geometry import LineString

from netex.netex_utils import netex_helper_map_stops_to_shape_distances


def test_map_stops_to_shape_distances_with_valid_input():
    """
    Test successful calculation of stop distances.
    """

    stop_ids = ["STOP1", "STOP2"]

    stop_coordinates = {
        "STOP1": (2.0, 0.0),
        "STOP2": (7.0, 0.0),
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    result = netex_helper_map_stops_to_shape_distances(
        stop_ids,
        stop_coordinates,
        shape_geometry
    )

    assert result == {
        "STOP1": 2.0,
        "STOP2": 7.0,
    }


def test_map_stops_to_shape_distances_skips_missing_coordinates(caplog):
    """
    Test that stops without coordinates are skipped and logged.
    """

    stop_ids = ["STOP1", "STOP2"]

    stop_coordinates = {
        "STOP1": (3.0, 0.0),
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    with caplog.at_level(logging.ERROR):

        result = netex_helper_map_stops_to_shape_distances(
            stop_ids,
            stop_coordinates,
            shape_geometry
        )

    assert result == {
        "STOP1": 3.0
    }

    assert "Missing coordinates for stop STOP2" in caplog.text


def test_map_stops_to_shape_distances_returns_empty_when_shape_is_empty(caplog):
    """
    Test that empty shapes return an empty dictionary.
    """

    stop_ids = ["STOP1"]

    stop_coordinates = {
        "STOP1": (1.0, 1.0),
    }

    shape_geometry = LineString([])

    with caplog.at_level(logging.ERROR):

        result = netex_helper_map_stops_to_shape_distances(
            stop_ids,
            stop_coordinates,
            shape_geometry
        )

    assert result == {}

    assert "Cannot calculate stop distances: shape is empty" in caplog.text


def test_map_stops_to_shape_distances_returns_empty_when_stop_ids_missing(caplog):
    """
    Test that missing stop IDs return an empty dictionary and log an error.
    """

    stop_ids = []

    stop_coordinates = {
        "STOP1": (1.0, 1.0),
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    with caplog.at_level(logging.ERROR):

        result = netex_helper_map_stops_to_shape_distances(
            stop_ids,
            stop_coordinates,
            shape_geometry
        )

    assert result == {}

    assert "Missing stop IDs" in caplog.text


def test_map_stops_to_shape_distances_on_multisegment_shape():
    """
    Test distance calculation on a polyline.
    """

    stop_ids = ["STOP1"]

    stop_coordinates = {
        "STOP1": (10.0, 5.0),
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0),
        (10, 10)
    ])

    result = netex_helper_map_stops_to_shape_distances(
        stop_ids,
        stop_coordinates,
        shape_geometry
    )

    assert result == {
        "STOP1": 15.0
    }