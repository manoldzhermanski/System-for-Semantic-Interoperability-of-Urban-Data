import pytest
from unittest.mock import patch
from json_ld.json_ld_utils import json_ld_get_ngsi_ld_data

def test_json_ld_get_ngsi_ld_data_valid_keyword_happy_path():
    """
    Check happy path
    """
    mock_data = [{"id": "E1"}]

    with patch("json_ld.json_ld_utils.json_ld_read_file", return_value=mock_data) as mock_read, \
        patch("json_ld.json_ld_utils.json_ld_transform_coordinates_to_wgs84_coordinates") as mock_transform:

        result = json_ld_get_ngsi_ld_data(keyword="culture", base_dir="/fake/base")

        mock_read.assert_called_once_with("/fake/base/data/pois_culture_ngsi.jsonld")

        mock_transform.assert_called_once_with(mock_data)
        assert result == mock_data

def test_json_ld_get_ngsi_ld_data_invalid_keyword_raises_value_error():
    """
    Check that unsupported PoIs categories are handled
    """
    with pytest.raises(ValueError) as err:
        json_ld_get_ngsi_ld_data("invalid_category")

    assert "Unsupported PoIs category" in str(err.value)

def test_json_ld_get_ngsi_ld_data_file_not_found_raises_error():
    """
    Check that if file is not present use-case is handled
    """
    with patch("json_ld.json_ld_utils.json_ld_read_file", side_effect=FileNotFoundError("missing file")):
        with pytest.raises(FileNotFoundError):
            json_ld_get_ngsi_ld_data(keyword="health", base_dir="/fake/base")

def test_json_ld_get_ngsi_ld_data_invalid_json_structure_raises_error():
    """
    Check that errors with reading the file are handled
    """
    with patch("json_ld.json_ld_utils.json_ld_read_file", side_effect=ValueError("Invalid NGSI-LD file structure")):
        with pytest.raises(ValueError):
            json_ld_get_ngsi_ld_data(keyword="kids", base_dir="/fake/base")