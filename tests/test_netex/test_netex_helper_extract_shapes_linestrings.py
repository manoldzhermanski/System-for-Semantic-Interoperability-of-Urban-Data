import pytest
from shapely.geometry import LineString
from netex.netex_utils import netex_helper_extract_shape_linestrings

Point = tuple[float, float]

def test_extract_shape_linestrings_returns_proper_structure():

    shapes = [
        {
            "id": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_1",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                    ]
                }
            }
        }
    ]

    result = netex_helper_extract_shape_linestrings(shapes)

    assert isinstance(result, dict)
    assert "SHAPE_1" in result
    
    linestring = result["SHAPE_1"]

    assert isinstance(linestring, LineString)
    assert len(linestring.coords) == 2

    for point in linestring.coords:
        assert isinstance(point, tuple)
        assert len(point) == 2
        assert all(isinstance(coord, float) for coord in point)
    
def test_extract_shape_linestrings_skips_invalid_entities():

    shapes = [
        {
            "id": "INVALID_ID",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                    ]
                }
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsRoute:ROUTE_1",
            "type": "GtfsRoute",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                    ]
                }
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_1",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219],
                        [23.3225],
                    ]
                }
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_2",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977]
                    ]
                }
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_3",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": []
                }
            }
        }
    ]

    result = netex_helper_extract_shape_linestrings(shapes)

    assert result == {}

def test_extract_shape_linestrings_handles_multiple_shapes():
    """
    Test extracting multiple shapes.
    """

    shapes = [
        {
            "id": "GtfsShape:SHAPE_1",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                    ]
                }
            }
        },
        {
            "id": "GtfsShape:SHAPE_2",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                    ]
                }
            }
        }
    ]

    result = netex_helper_extract_shape_linestrings(shapes)

    assert len(result) == 2
    assert "SHAPE_1" in result
    assert "SHAPE_2" in result

def test_extract_shape_linestrings_transforms_coordinates():
    """
    Test that coordinates are transformed and not returned unchanged.
    """

    shapes = [
        {
            "id": "GtfsShape:SHAPE_1",
            "type": "GtfsShape",
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                    ]
                }
            }
        }
    ]

    result = netex_helper_extract_shape_linestrings(shapes)

    original_points = LineString([
        (23.3219, 42.6977),
        (23.3225, 42.6980)
    ])

    assert result["SHAPE_1"].coords != original_points.coords

def test_extract_shape_linestrings_empty_imput():
    
    result = netex_helper_extract_shape_linestrings([])
    assert result == {}