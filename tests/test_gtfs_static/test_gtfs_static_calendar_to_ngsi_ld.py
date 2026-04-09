import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_calendar_to_ngsi_ld

# Mock function behavior

def test_gtfs_calendar_dates_to_ngsi_ld():
    """
    Unit test for gtfs_static_calendar_dates_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """

    city = "Sofia"

    # Sample input for GTFS Calendar Date
    sample_raw_data = [
        {
            "service_id": "S1",
            "monday": "1",
            "tuesday": "1",
            "wednesday": "1",
            "thursday": "1",
            "friday": "1",
            "saturday": "1",
            "sunday": "1",
            "start_date": "20260408",
            "end_date": "20260430"
            },
        {
            "service_id": "S2",
            "monday": "1",
            "tuesday": "1",
            "wednesday": "1",
            "thursday": "1",
            "friday": "1",
            "saturday": "1",
            "sunday": "1",
            "start_date": "20260408",
            "end_date": "20260430"
            },
        ]

    # Mock result from parse_gtfs_calendar_dates_data
    parsed_data = [
        {
            "service_id": "S1",
            "monday": 1,
            "tuesday": 1,
            "wednesday": 1,
            "thursday": 1,
            "friday": 1,
            "saturday": 1,
            "sunday": 1,
            "start_date": "20260408",
            "end_date": "20260430"
            },
        {
            "service_id": "S2",
            "monday": 1,
            "tuesday": 1,
            "wednesday": 1,
            "thursday": 1,
            "friday": 1,
            "saturday": 1,
            "sunday": 1,
            "start_date": "20260408",
            "end_date": "20260430"
            },
        ]
        
    # Mock result from convert_gtfs_calendar_dates_to_ngsi_ld
    converted_data = [
        {
            "id": f"urn:ngsi-ld:GtfsCalendarRule:{city}:S1",
            "type": "GtfsCalendarRule",
            "hasService": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsService:{city}:S1"},
            "monday": {"type": "Property", "value": 1},
            "tuesday": {"type": "Property", "value": 1},
            "wednesday": {"type": "Property", "value": 1},
            "thursday": {"type": "Property","value": 1},
            "friday": {"type": "Property", "value": 1},
            "saturday": {"type": "Property", "value": 1},
            "sunday": {"type": "Property", "value": 1},
            "startDate": {"type": "Property", "value": "20260408"},
            "endDate": {"type": "Property", "value": "20260430"}
            },
        {
            "id": f"urn:ngsi-ld:GtfsCalendarRule:{city}:S2",
            "type": "GtfsCalendarRule",
            "hasService": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsService:{city}:S2"},
            "monday": {"type": "Property", "value": 1},
            "tuesday": {"type": "Property", "value": 1},
            "wednesday": {"type": "Property", "value": 1},
            "thursday": {"type": "Property","value": 1},
            "friday": {"type": "Property", "value": 1},
            "saturday": {"type": "Property", "value": 1},
            "sunday": {"type": "Property", "value": 1},
            "startDate": {"type": "Property", "value": "20260408"},
            "endDate": {"type": "Property", "value": "20260430"}
            },
        ]
        
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": f"urn:ngsi-ld:GtfsCalendarRule:{city}:S1",
            "type": "GtfsCalendarRule",
            "hasService": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsService:{city}:S1"},
            "monday": {"type": "Property", "value": 1},
            "tuesday": {"type": "Property", "value": 1},
            "wednesday": {"type": "Property", "value": 1},
            "thursday": {"type": "Property","value": 1},
            "friday": {"type": "Property", "value": 1},
            "saturday": {"type": "Property", "value": 1},
            "sunday": {"type": "Property", "value": 1},
            "startDate": {"type": "Property", "value": "20260408"},
            "endDate": {"type": "Property", "value": "20260430"}
        },
        {
            "id": f"urn:ngsi-ld:GtfsCalendarRule:{city}:S2",
            "type": "GtfsCalendarRule",
            "hasService": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsService:{city}:S2"},
            "monday": {"type": "Property", "value": 1},
            "tuesday": {"type": "Property", "value": 1},
            "wednesday": {"type": "Property", "value": 1},
            "thursday": {"type": "Property","value": 1},
            "friday": {"type": "Property", "value": 1},
            "saturday": {"type": "Property", "value": 1},
            "sunday": {"type": "Property", "value": 1},
            "startDate": {"type": "Property", "value": "20260408"},
            "endDate": {"type": "Property", "value": "20260430"}
            },
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
    
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_calendar_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_calendar_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_calendar_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
             
            # Function call result from gtfs_static_calendar_dates_to_ngsi_ld
            result = gtfs_static_calendar_to_ngsi_ld(sample_raw_data, city)

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