import pytest
from unittest.mock import patch
from gtfs_static.gtfs_static_utils import gtfs_static_calendar_dates_to_ngsi_ld

# Mock function behavior
@patch("gtfs_static.gtfs_static_utils.remove_none_values")
@patch("gtfs_static.gtfs_static_utils.convert_gtfs_calendar_dates_to_ngsi_ld")
@patch("gtfs_static.gtfs_static_utils.validate_gtfs_calendar_dates_entity")
@patch("gtfs_static.gtfs_static_utils.parse_gtfs_calendar_dates_data")
def test_gtfs_calendar_dates_to_ngsi_ld(mock_parse, mock_validate, mock_convert, mock_remove_none):
    """
    Unit test for gtfs_static_calendar_dates_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Calendar Date
    sample_raw_data = [
        {
            "service_id": "S1",
            "date": "20240101",
            "exception_type": "1",
            },
        {
            "service_id": "S2",
            "date": "20240102",
            "exception_type": "1",
            },
        ]

    # Mock result from parse_gtfs_calendar_dates_data
    parsed_data = [
        {
            "service_id": "S1",
            "date": "20240101",
            "exception_type": 1,
            },
        {
            "service_id": "S2",
            "date": "20240102",
            "exception_type": 1,
            },
        ]
    
    mock_parse.side_effect = parsed_data
    
    # Mock result from convert_gtfs_calendar_dates_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:S1:20240101",
            "type": "GtfsCalendarDateRule",
            "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S1",},
            "appliesOn": {"type": "Property", "value": "20240101",},
            "exceptionType": {"type": "Property", "value": 1,},
            },
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:S2:20240102",
            "type": "GtfsCalendarDateRule",
            "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S2",},
            "appliesOn": {"type": "Property", "value": "20240102",},
            "exceptionType": {"type": "Property", "value": 1,},
            },
        ]
    
    mock_convert.side_effect = converted_data
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:S1:20240101",
            "type": "GtfsCalendarDateRule",
            "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S1",},
            "appliesOn": {"type": "Property", "value": "20240101",},
            "exceptionType": {"type": "Property", "value": 1,},
            },
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:S2:20240102",
            "type": "GtfsCalendarDateRule",
            "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S2",},
            "appliesOn": {"type": "Property", "value": "20240102",},
            "exceptionType": {"type": "Property", "value": 1,},
            },
        ]
    
    mock_remove_none.side_effect = cleaned_data
    
    # Function call result from gtfs_static_calendar_dates_to_ngsi_ld
    result = gtfs_static_calendar_dates_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_calendar_dates_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_calendar_dates_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_calendar_dates_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2