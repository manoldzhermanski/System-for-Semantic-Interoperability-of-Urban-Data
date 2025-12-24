import pytest
from unittest.mock import patch
from gtfs_static.gtfs_static_utils import gtfs_static_levels_to_ngsi_ld

# Mock function behavior
@patch("gtfs_static.gtfs_static_utils.remove_none_values")
@patch("gtfs_static.gtfs_static_utils.convert_gtfs_levels_to_ngsi_ld")
@patch("gtfs_static.gtfs_static_utils.validate_gtfs_levels_entity")
@patch("gtfs_static.gtfs_static_utils.parse_gtfs_levels_data")
def test_gtfs_levels_to_ngsi_ld(mock_parse, mock_validate, mock_convert, mock_remove_none):
    """
    Unit test for gtfs_static_levels_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Level
    sample_raw_data = [
        {
            "level_id": "L1",
            "level_name": "Platform Level",
            "level_index": "1.0",
            },
        {
            "level_id": "L2",
            "level_name": "Platform Level",
            "level_index": "-1.0",
            },
        ]

    # Mock result from parse_gtfs_levels_data
    parsed_data = [
        {
            "level_id": "L1",
            "level_name": "Platform Level",
            "level_index": 1.0,
            },
        {
            "level_id": "L2",
            "level_name": "Platform Level",
            "level_index": -1.0,
            },
        ]
    
    mock_parse.side_effect = parsed_data
    
    # Mock result from convert_gtfs_levels_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsLevel:L1",
            "type": "GtfsLevel",
            "name": {"type": "Property", "value": "Platform Level",},
            "level_index": {"type": "Property", "value": 1.0,},
            },
        {
            "id": "urn:ngsi-ld:GtfsLevel:L2",
            "type": "GtfsLevel",
            "name": {"type": "Property", "value": "Platform Level",},
            "level_index": {"type": "Property", "value": -1.0,},
            },
        ]
    
    mock_convert.side_effect = converted_data
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsLevel:L1",
            "type": "GtfsLevel",
            "name": {"type": "Property", "value": "Platform Level",},
            "level_index": {"type": "Property", "value": 1.0,},
            },
        {
            "id": "urn:ngsi-ld:GtfsLevel:L2",
            "type": "GtfsLevel",
            "name": {"type": "Property", "value": "Platform Level",},
            "level_index": {"type": "Property", "value": -1.0,},
            },
        ]
    
    mock_remove_none.side_effect = cleaned_data
    
    # Function call result from gtfs_static_levels_to_ngsi_ld
    result = gtfs_static_levels_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_levels_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_levels_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_levels_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2