from unittest import result

import pytest
from shapely.geometry import LineString
from netex.netex_utils import netex_helper_transform_line_string_to_wgs84

Point = tuple[float, float]

def test_transform_line_string_returns_list():
    """
    Test that the function returns a list of transformed points.
    """

    line = LineString([
        (4840000.0, 8500000.0),
        (4840100.0, 8500100.0),
    ])

    result = netex_helper_transform_line_string_to_wgs84(line)

    assert isinstance(result, LineString)
    assert len(result.coords) == 2


def test_transform_line_string_point_structure():
    """
    Test that each transformed point is a tuple of two floats.
    """

    line = LineString([
        (4840000.0, 8500000.0),
        (4840100.0, 8500100.0),
    ])

    result = netex_helper_transform_line_string_to_wgs84(line)

    for point in result.coords:
        assert isinstance(point, tuple)
        assert len(point) == 2
        assert all(isinstance(coord, float) for coord in point)

def test_transform_empty_line_string():
    """
    Test transforming an empty LineString.
    """

    line = LineString([])

    result = netex_helper_transform_line_string_to_wgs84(line)

    assert isinstance(result, LineString)
    assert result.is_empty


def test_transform_line_string_to_wgs84_changes_coordinates():
    """
    Test that coordinates are actually transformed.
    """

    line = LineString([
        (4730000, 8500000),
        (4730100, 8500100)
    ])

    result = netex_helper_transform_line_string_to_wgs84(line)

    original_coords = list(line.coords)
    transformed_coords = list(result.coords)

    assert transformed_coords != original_coords
