import pytest
from unittest.mock import MagicMock, patch
from json_ld.json_ld_utils import json_ld_transform_coordinates_to_wgs84_coordinates

@pytest.fixture
def mock_transformer():
    transformer = MagicMock()
    transformer.transform.side_effect = lambda x, y: (x + 100, y + 200)
    return transformer

def test_skip_entity_without_location():
    """
    Check that non-geometry objects are ignored
    """
    data = [{"id": "E1"}]

    mock_transformer = MagicMock()
    mock_transformer.transform.return_value = (101, 202)

    with patch("json_ld.json_ld_utils.Transformer.from_crs", return_value = mock_transformer):
        json_ld_transform_coordinates_to_wgs84_coordinates(data)

    assert data == [{"id": "E1"}]

def test_point_geometry_transformed():
    """
    Check that Point geometry are transformed
    """

    data = [
        {
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": [1, 2]
                }
            }
        }
    ]

    mock_transformer = MagicMock()
    mock_transformer.transform.return_value = (101, 202)

    with patch("json_ld.json_ld_utils.Transformer.from_crs", return_value = mock_transformer):
        json_ld_transform_coordinates_to_wgs84_coordinates(data)

    assert data[0]["location"]["value"]["coordinates"] == [101, 202]

def test_multipoint_geometry_transformed():
    """
    Check that MultiPoint geometry is transformed
    """

    data = [
        {
            "location": {
                "value": {
                    "type": "MultiPoint",
                    "coordinates": [
                        [10, 20],
                        [30, 40]
                    ]
                }
            }
        }
    ]

    mock_transformer = MagicMock()
    mock_transformer.transform.return_value = (110, 220)

    with patch("json_ld.json_ld_utils.Transformer.from_crs", return_value = mock_transformer):
        json_ld_transform_coordinates_to_wgs84_coordinates(data)

    location = data[0]["location"]["value"]

    assert location["type"] == "Point"
    assert location["coordinates"] == [110, 220]

def test_point_with_invalid_coordinates():
    """
    Check that if a Point has invalid coordinates, it's ignored
    """
    data = [
        {
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": "invalid"
                }
            }
        }
    ]

    mock_transformer = MagicMock()
    mock_transformer.transform.return_value = (101, 202)

    original = data[0]["location"]["value"].copy()
    with patch("json_ld.json_ld_utils.Transformer.from_crs", return_value = mock_transformer):
        json_ld_transform_coordinates_to_wgs84_coordinates(data)

    assert data[0]["location"]["value"] == original

def test_unsupported_geometry_type():
    """
    Check that if geometry type is not Point or MultiPoint, it's ignored
    """
    data = [
        {
            "location": {
                "value": {
                    "type": "LineString",
                    "coordinates": [1, 2]
                }
            }
        }
    ]

    mock_transformer = MagicMock()
    mock_transformer.transform.return_value = (101, 202)

    original = data[0]["location"]["value"].copy()
    with patch("json_ld.json_ld_utils.Transformer.from_crs", return_value = mock_transformer):
        json_ld_transform_coordinates_to_wgs84_coordinates(data)

    assert data[0]["location"]["value"] == original
