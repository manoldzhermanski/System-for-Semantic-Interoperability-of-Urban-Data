import pytest
from netex.netex_utils import netex_helper_for_every_trip_compute_stop_distances_along_shapes

Point = tuple[float, float]

def test_compute_stop_distances_along_shapes_returns_dictionary():
    """
    Test that the function returns a dictionary.
    """

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip={},
            stop_coordinates={},
            shape_line_strings={},
            shape_per_trip={},
        )
    )

    assert isinstance(result, dict)


def test_compute_stop_distances_along_shapes_single_trip():
    """
    Test computing stop distances for a single trip.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1", "STOP_2"],
    }

    stop_coordinates: dict[str, Point] = {
        "STOP_1": (2.0, 0.0),
        "STOP_2": (8.0, 0.0),
    }

    shape_line_strings = {
        "SHAPE_1": [
            (0.0, 0.0),
            (10.0, 0.0),
        ]
    }

    shape_per_trip = {
        "TRIP_1": "SHAPE_1"
    }

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_line_strings,
            shape_per_trip,
        )
    )

    assert result == {
        "TRIP_1": {
            "STOP_1": pytest.approx(2.0),
            "STOP_2": pytest.approx(8.0),
        }
    }


def test_compute_stop_distances_along_shapes_multiple_trips():
    """
    Test computing stop distances for multiple trips.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1"],
        "TRIP_2": ["STOP_2"],
    }

    stop_coordinates: dict[str, Point] = {
        "STOP_1": (2.0, 0.0),
        "STOP_2": (7.0, 0.0),
    }

    shape_line_strings = {
        "SHAPE_1": [
            (0.0, 0.0),
            (10.0, 0.0),
        ],
        "SHAPE_2": [
            (0.0, 0.0),
            (20.0, 0.0),
        ],
    }

    shape_per_trip = {
        "TRIP_1": "SHAPE_1",
        "TRIP_2": "SHAPE_2",
    }

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_line_strings,
            shape_per_trip,
        )
    )

    assert result == {
        "TRIP_1": {
            "STOP_1": pytest.approx(2.0),
        },
        "TRIP_2": {
            "STOP_2": pytest.approx(7.0),
        },
    }


def test_compute_stop_distances_along_shapes_skips_trip_without_shape_mapping():
    """
    Test that trips without a shape mapping are skipped.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1"],
    }

    stop_coordinates: dict[str, Point] = {
        "STOP_1": (5.0, 0.0),
    }

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_line_strings={},
            shape_per_trip={},
        )
    )

    assert result == {}


def test_compute_stop_distances_along_shapes_skips_missing_shape_geometry():
    """
    Test that trips with missing shape geometries are skipped.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1"],
    }

    stop_coordinates: dict[str, Point] = {
        "STOP_1": (5.0, 0.0),
    }

    shape_per_trip = {
        "TRIP_1": "SHAPE_1"
    }

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_line_strings={},
            shape_per_trip=shape_per_trip,
        )
    )

    assert result == {}


def test_compute_stop_distances_along_shapes_skips_empty_shape_geometry():
    """
    Test that trips with empty shape geometries are skipped.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1"],
    }

    stop_coordinates: dict[str, Point] = {
        "STOP_1": (5.0, 0.0),
    }

    shape_line_strings = {
        "SHAPE_1": []
    }

    shape_per_trip = {
        "TRIP_1": "SHAPE_1"
    }

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates,
            shape_line_strings,
            shape_per_trip,
        )
    )

    assert result == {}


def test_compute_stop_distances_along_shapes_skips_missing_stop_coordinates():
    """
    Test that stops with missing coordinates are skipped.
    """

    stops_per_trip = {
        "TRIP_1": ["STOP_1"],
    }

    shape_line_strings = {
        "SHAPE_1": [
            (0.0, 0.0),
            (10.0, 0.0),
        ]
    }

    shape_per_trip = {
        "TRIP_1": "SHAPE_1"
    }

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip,
            stop_coordinates={},
            shape_line_strings=shape_line_strings,
            shape_per_trip=shape_per_trip,
        )
    )

    assert result == {
        "TRIP_1": {}
    }


def test_compute_stop_distances_along_shapes_handles_empty_input():
    """
    Test that empty input returns an empty dictionary.
    """

    result = (
        netex_helper_for_every_trip_compute_stop_distances_along_shapes(
            stops_per_trip={},
            stop_coordinates={},
            shape_line_strings={},
            shape_per_trip={},
        )
    )

    assert result == {}