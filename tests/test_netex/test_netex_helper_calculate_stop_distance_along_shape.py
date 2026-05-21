import pytest
from shapely.geometry import LineString, Point as ShapelyPoint

from netex.netex_utils import netex_helper_calculate_stop_distance_along_shape


def test_calculate_distance_on_simple_horizontal_line():
    """
    Point lies exactly on a straight horizontal line.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_calculate_stop_distance_along_shape((5, 0), shape)

    assert result == 5.0


def test_calculate_distance_at_start_of_line():
    """
    Start point should return 0.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_calculate_stop_distance_along_shape((0, 0), shape)

    assert result == 0.0


def test_calculate_distance_at_end_of_line():
    """
    End point should return full length.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_calculate_stop_distance_along_shape((10, 0), shape)

    assert result == 10.0


def test_calculate_distance_on_diagonal_line():
    """
    Distance on a 45-degree line.
    """

    shape = LineString([(0, 0), (3, 4)])  # length = 5

    result = netex_helper_calculate_stop_distance_along_shape((3, 4), shape)

    assert result == 5.0


def test_calculate_distance_on_multisegment_line():
    """
    Ensure projection works on polyline.
    """

    shape = LineString([
        (0, 0),
        (10, 0),
        (10, 10)
    ])

    # Point on second segment
    result = netex_helper_calculate_stop_distance_along_shape((10, 5), shape)

    assert result == 15.0


def test_calculate_distance_when_point_is_not_exactly_on_line():
    """
    Projection should still return closest distance along line.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_calculate_stop_distance_along_shape((5, 5), shape)

    assert result == 5.0


def test_calculate_distance_with_shapely_point_input():
    """
    Ensure function works even if input is already a Point-like tuple.
    """

    shape = LineString([(0, 0), (10, 0)])

    result = netex_helper_calculate_stop_distance_along_shape((7, 0), shape)

    assert result == 7.0