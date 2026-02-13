import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_agency_to_ngsi_ld


def test_gtfs_agency_to_ngsi_ld():
    """
    Unit test for gtfs_static_agency_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    city = "Sofia"

    # Sample input for GTFS Agency
    sample_raw_data = [
        {
            "agency_id": "A1",
            "agency_name": "Test Agency",
            "agency_url": "https://example.com",
            "agency_timezone": "Europe/Sofia",
            },
        {
            "agency_id": "A2",
            "agency_name": "Test Agency",
            "agency_url": "https://example.com",
            "agency_timezone": "Europe/Sofia",
            },
        ]

    # Mock result from parse_gtfs_agency_data
    parsed_data = [
        {
            "agency_id": "A1",
            "agency_name": "Test Agency",
            "agency_url": "https://example.com",
            "agency_timezone": "Europe/Sofia",
            },
        {
            "agency_id": "A2",
            "agency_name": "Test Agency",
            "agency_url": "https://example.com",
            "agency_timezone": "Europe/Sofia",
            },
        ]
    
    # Mock result from convert_gtfs_agency_to_ngsi_ld
    converted_data = [
        {
            "id": f"urn:ngsi-ld:GtfsAgency:{city}:A1",
            "type": "GtfsAgency",
            "agency_name": {"type": "Property", "value": "Test Agency",},
            "agency_url": {"type": "Property", "value": "https://example.com",},
            "agency_timezone": {"type": "Property","value": "Europe/Sofia",},
        },
        {
            "id": "urn:ngsi-ld:GtfsAgency:A2",
            "type": "GtfsAgency",
            "agency_name": {"type": "Property", "value": "Test Agency",},
            "agency_url": {"type": "Property", "value": "https://example.com",},
            "agency_timezone": {"type": "Property","value": "Europe/Sofia",},
            },
        ]
        
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": f"urn:ngsi-ld:GtfsAgency:{city}:A1",
            "type": "GtfsAgency",
            "agency_name": {"type": "Property", "value": "Test Agency",},
            "agency_url": {"type": "Property", "value": "https://example.com",},
            "agency_timezone": {"type": "Property","value": "Europe/Sofia",},
        },
        {
            "id": "urn:ngsi-ld:GtfsAgency:A2",
            "type": "GtfsAgency",
            "agency_name": {"type": "Property", "value": "Test Agency",},
            "agency_url": {"type": "Property", "value": "https://example.com",},
            "agency_timezone": {"type": "Property","value": "Europe/Sofia",},
            },
        ]
        
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)

    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_agency_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_agency_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_agency_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):

            # Function call result from gtfs_static_agency_to_ngsi_ld
            result = gtfs_static_agency_to_ngsi_ld(sample_raw_data, city)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_agency_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_agency_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_agency_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2