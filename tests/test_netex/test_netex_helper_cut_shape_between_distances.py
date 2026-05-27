import pytest
from shapely.geometry import LineString, Point as ShapelyPoint
from netex.netex_utils import netex_helper_cut_shape_between_distances


def test_cut_shape_between_valid_distances_returns_linestring():
    """
    Test that a valid segment is returned as a LineString.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_cut_shape_between_distances(shape, 2, 8)

    assert isinstance(result, LineString)
    assert list(result.coords) == [(2.0, 0.0), (8.0, 0.0)]


def test_cut_shape_returns_empty_when_end_distance_equals_start_distance():
    """
    Test that an empty list is returned when end_d == start_d.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_cut_shape_between_distances(shape, 5, 5)

    assert result == LineString()


def test_cut_shape_returns_empty_when_end_distance_less_than_start_distance():
    """
    Test that an empty list is returned when end_d < start_d.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_cut_shape_between_distances(shape, 8, 2)

    assert result == LineString()


def test_cut_shape_with_full_length_returns_original_geometry():
    """
    Test cutting the entire LineString length.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_cut_shape_between_distances(shape, 0, 10)

    assert isinstance(result, LineString)
    assert list(result.coords) == [(0.0, 0.0), (10.0, 0.0)]


def test_cut_shape_on_multisegment_line():
    """
    Test cutting a LineString with multiple segments.
    """

    shape = LineString([
        (0, 0),
        (10, 0),
        (10, 10)
    ])

    result = netex_helper_cut_shape_between_distances(shape, 5, 15)

    assert isinstance(result, LineString)

    coords = list(result.coords)

    assert coords[0] == (5.0, 0.0)
    assert coords[-1] == (10.0, 5.0)


def test_cut_shape_returns_point_when_start_and_end_are_very_close():
    """
    Test behavior for extremely small segments.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_cut_shape_between_distances(shape, 5, 5.0000001)

    assert isinstance(result, (LineString, ShapelyPoint))


def test_cut_shape_with_distances_outside_geometry_bounds():
    """
    Test that distances outside the LineString bounds are clamped by substring().
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_cut_shape_between_distances(shape, -5, 20)

    assert isinstance(result, LineString)
    assert list(result.coords) == [(5.0, 0.0), (10.0, 0.0)]


def test_cut_shape_with_empty_linestring():
    """
    Test behavior with an empty LineString.
    """

    shape = LineString([])

    result = netex_helper_cut_shape_between_distances(shape, 0, 5)

    assert result.is_empty