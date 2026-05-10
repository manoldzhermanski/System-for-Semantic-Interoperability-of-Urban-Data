import pytest
from netex.netex_utils import netex_helper_transform_point

Point = tuple[float, float]

def test_transform_wgs84_to_projected_returns_tuple_of_two_floats():
    
    point: Point = (23.3219, 42.6977)

    result = netex_helper_transform_point(point, from_crs="EPSG:4326", to_crs="EPSG:7801")

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(coord, float) for coord in result)


def test_transform_projected_to_wgs84_returns_tuple_of_two_floats():

    point: Point = (23.3219, 42.6977)

    result = netex_helper_transform_point(point, from_crs="EPSG:7801", to_crs="EPSG:4326")

    assert isinstance(result, tuple)
    assert len(result) == 2
    assert all(isinstance(coord, float) for coord in result)
    

def test_transformed_coordinates_are_different():
    
    point: Point = (23.3219, 42.6977)
    
    result = netex_helper_transform_point(point, from_crs="EPSG:4326", to_crs="EPSG:7801")
    
    assert point[0] != result[0]
    assert point[1] != result[1]

def test_transforming_and_returning_to_original_crs_is_proper():

    original_point: Point = (23.3219, 42.6977)

    projected_point = netex_helper_transform_point(original_point, from_crs="EPSG:4326", to_crs="EPSG:7801")

    restored_point = netex_helper_transform_point(projected_point, from_crs="EPSG:7801", to_crs="EPSG:4326")

    assert restored_point[0] == pytest.approx(original_point[0], abs=1e-6)
    assert restored_point[1] == pytest.approx(original_point[1], abs=1e-6)


def test_unsupported_crs_transformation_raises_value_error():
    """
    Test that unsupported CRS transformations raise ValueError.
    """

    point: Point = (23.3219, 42.6977)

    with pytest.raises(ValueError) as err:
        netex_helper_transform_point(point, from_crs="EPSG:3857", to_crs="EPSG:7801")
        
    assert "Unsupported CRS transformation" in str(err.value)
