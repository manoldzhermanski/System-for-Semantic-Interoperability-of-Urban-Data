# import logging
import pytest
from shapely.geometry import LineString, Point as ShapelyPoint
from netex.netex_utils import netex_helper_create_line_string_segments_between_stop_pairs


def test_create_line_string_segment_between_valid_stop_pair():
    """
    Test successful creation of a LineString segment.
    """

    stop_pair = ("STOP1", "STOP2")

    stop_distances_along_shape = {
        "STOP1": 2.0,
        "STOP2": 8.0,
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert isinstance(result, LineString)

    assert list(result.coords) == [
        (2.0, 0.0),
        (8.0, 0.0),
    ]


def test_returns_none_when_stop_pair_is_none(caplog):
    """
    Test that None stop pairs are rejected.
    """
    stop_pair = None

    stop_distances_along_shape = {
        "STOP1": 1.0,
        "STOP2": 5.0
        }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])


    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert result is None

    assert "Invalid stop pair" in caplog.text


def test_returns_none_when_stop_pair_has_invalid_length(caplog):
    """
    Test invalid stop pair tuple length.
    """

    stop_pair = ("STOP1",)

    stop_distances_along_shape = {
        "STOP1": 1.0
        }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert result is None

    assert "Invalid stop pair" in caplog.text


def test_returns_none_when_stop_distances_missing(caplog):
    """
    Test missing stop distances dictionary.
    """
    stop_pair = ("STOP1", "STOP2")

    stop_distances_along_shape = {}

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])


    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert result is None

    assert "Missing stop distances along shape" in caplog.text


def test_returns_none_when_shape_geometry_is_empty(caplog):
    """
    Test empty shape geometry.
    """
    stop_pair = ("STOP1", "STOP2")

    stop_distances_along_shape = {
        "STOP1": 2.0,
        "STOP2": 8.0,
    }

    shape_geometry = LineString([])

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert result is None

    assert "Cannot create line string segment: shape geometry is empty" in caplog.text


def test_returns_empty_list_when_end_distance_before_start_distance():
    """
    Test behavior when stop order produces reversed distances.
    """

    stop_pair = ("STOP1", "STOP2")

    stop_distances_along_shape = {
        "STOP1": 8.0,
        "STOP2": 2.0,
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert result == LineString()


def test_create_segment_on_multisegment_shape():
    """
    Test segment extraction on a polyline.
    """

    stop_pair = ("STOP1", "STOP2")

    stop_distances_along_shape = {
        "STOP1": 5.0,
        "STOP2": 15.0,
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0),
        (10, 10)
    ])

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert isinstance(result, LineString)

    coords = list(result.coords)

    assert coords[0] == (5.0, 0.0)

    assert coords[-1] == (10.0, 5.0)


def test_returns_point_for_tiny_segment():
    """
    Test behavior for extremely small distance differences.
    """

    stop_pair = ("STOP1", "STOP2")

    stop_distances_along_shape = {
        "STOP1": 5.0,
        "STOP2": 5.0000001,
    }

    shape_geometry = LineString([
        (0, 0),
        (10, 0)
    ])

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        shape_geometry
    )

    assert isinstance(result, (LineString, ShapelyPoint))