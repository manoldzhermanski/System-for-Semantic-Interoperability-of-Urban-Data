import pytest
from netex.netex_utils import netex_helper_transform_line_string_to_wgs84

Point = tuple[float, float]

def test_transform_line_string_returns_list():
    """
    Test that the function returns a list of transformed points.
    """

    polyline_projected: list[Point] = [
        (4840000.0, 8500000.0),
        (4840100.0, 8500100.0),
    ]

    result = netex_helper_transform_line_string_to_wgs84(polyline_projected)

    assert isinstance(result, list)
    assert len(result) == 2


def test_transform_line_string_point_structure():
    """
    Test that each transformed point is a tuple of two floats.
    """

    polyline_projected: list[Point] = [
        (4840000.0, 8500000.0),
        (4840100.0, 8500100.0),
    ]

    result = netex_helper_transform_line_string_to_wgs84(polyline_projected)

    for point in result:
        assert isinstance(point, tuple)
        assert len(point) == 2
        assert all(isinstance(coord, float) for coord in point)

def test_transform_empty_line_string():
    """
    Test transforming an empty LineString.
    """

    polyline_projected: list[Point] = []

    result = netex_helper_transform_line_string_to_wgs84(polyline_projected)

    assert result == []


def test_transformed_coordinates_are_different():
    """
    Test that transformed coordinates differ from projected coordinates.
    """

    polyline_projected: list[Point] = [
        (4840000.0, 8500000.0),
    ]

    result = netex_helper_transform_line_string_to_wgs84(polyline_projected)

    assert result[0] != polyline_projected[0]