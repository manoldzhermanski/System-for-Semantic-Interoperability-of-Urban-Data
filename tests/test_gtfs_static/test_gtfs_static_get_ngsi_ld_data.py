import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_get_ngsi_ld_data

def test_gtfs_static_get_ngsi_ld_data_valid_file_type():
    city = "Test"
    raw_data = [{"raw": "data"}]
    ngsi_ld_data = [{"id": f"urn:ngsi-ld:{city}:1"}]

    with patch("gtfs_static.gtfs_static_utils.gtfs_static_read_file", return_value=raw_data) as mock_read, \
    patch("gtfs_static.gtfs_static_utils.gtfs_static_agency_to_ngsi_ld", return_value=ngsi_ld_data) as mock_transformer:

        result = gtfs_static_get_ngsi_ld_data(file_type="agency",base_dir="custom_base", city=city)

        # Returned value
        assert result == ngsi_ld_data

        # Correct file path
        mock_read.assert_called_once_with("custom_base/data/agency.txt")

        # Transformer called with raw data
        mock_transformer.assert_called_once_with(raw_data, city)
        
def test_gtfs_static_get_ngsi_ld_data_valid_file_type_magicmock():
    city = "Berlin"
    raw_data = [{"agency_id": "A1"}]
    ngsi_ld_data = [{f"id": f"urn:ngsi-ld:Agency:{city}:A1"}]
    
    
    mock_read = MagicMock()
    mock_read.return_value = raw_data
    
    mock_transformer = MagicMock()
    mock_transformer.return_value = ngsi_ld_data


    with patch("gtfs_static.gtfs_static_utils.gtfs_static_read_file", mock_read), \
         patch("gtfs_static.gtfs_static_utils.gtfs_static_agency_to_ngsi_ld", mock_transformer):

        result = gtfs_static_get_ngsi_ld_data(file_type="agency", base_dir="custom_base", city=city)

    assert result == ngsi_ld_data
    mock_read.assert_called_once_with("custom_base/data/agency.txt")
    mock_transformer.assert_called_once_with(raw_data, city)


def test_gtfs_static_get_ngsi_ld_data_invalid_file_type():
    """
    Check that if file_type is invalid, a FileNotFoundError is raised.
    """
    city = "Sofia"

    with pytest.raises(FileNotFoundError) as err:
        gtfs_static_get_ngsi_ld_data("invalid_type", city)

    assert "Unsupported GTFS static file type" in str(err.value)

def test_gtfs_static_get_ngsi_ld_data_file_not_found():
    """
    Check that if a file is missing when attepmpting to read it,
    a FileNotFoundError is raised.
    """
    city = "Sofia"

    mock_read = MagicMock()
    mock_read.side_effect = FileNotFoundError("Missing file")
    with patch("gtfs_static.gtfs_static_utils.gtfs_static_read_file", side_effect=mock_read):
        with pytest.raises(FileNotFoundError):
            gtfs_static_get_ngsi_ld_data("agency", city)
