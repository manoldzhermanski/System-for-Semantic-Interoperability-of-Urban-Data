import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_stop_times_to_ngsi_ld


def test_gtfs_static_stop_times_to_ngsi_ld():
    """
    Unit test for gtfs_static_stop_times_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    
    city = "Sofia"
    
    # Sample input for GTFS Stop Time
    sample_raw_data = [
        {
            "trip_id": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
            "arrival_time": "08:15:00",
            "departure_time": "08:17:00",
            "stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S1",
            "stop_sequence": "5",
            },
        {
            "trip_id": f"urn:ngsi-ld:GtfsTrip:{city}:T2",
            "arrival_time": "08:17:00",
            "departure_time": "08:19:00",
            "stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S2",
            "stop_sequence": "6",
            }
        ]

    # Mock result from parse_gtfs_stop_times_data
    parsed_data = [
        {
            "trip_id": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
            "arrival_time": "08:15:00",
            "departure_time": "08:17:00",
            "stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S1",
            "stop_sequence": 5,
            },
        {
            "trip_id": f"urn:ngsi-ld:GtfsTrip:{city}:T2",
            "arrival_time": "08:17:00",
            "departure_time": "08:19:00",
            "stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S2",
            "stop_sequence": 6,
            }
        ]
    
    # Mock result from convert_gtfs_stop_times_to_ngsi_ld
    converted_data = [
        {
            "id": f"urn:ngsi-ld:GtfsStopTime:{city}:T1:5",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsTrip:{city}:T1",},
            "arrivalTime": {"type": "Property", "value": "08:15:00",},
            "departureTime": {"type": "Property","value": "08:17:00",},
            "hasStop": {"type": "Relationship","object": f"urn:ngsi-ld:GtfsStop:{city}:S1",},
            "stopSequence": {"type": "Property", "value": 5},
            },
        {
            "id": f"urn:ngsi-ld:GtfsStopTime{city}:T2:6",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsTrip:{city}:T2",},
            "arrivalTime": {"type": "Property", "value": "08:17:00",},
            "departureTime": {"type": "Property","value": "08:19:00",},
            "hasStop": {"type": "Relationship","object": f"urn:ngsi-ld:GtfsStop:{city}:S2",},
            "stopSequence": {"type": "Property", "value": 6},
            },
        ]
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": f"urn:ngsi-ld:GtfsStopTime:{city}:T1:5",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsTrip:{city}:T1",},
            "arrivalTime": {"type": "Property", "value": "08:15:00",},
            "departureTime": {"type": "Property","value": "08:17:00",},
            "hasStop": {"type": "Relationship","object": f"urn:ngsi-ld:GtfsStop:{city}:S1",},
            "stopSequence": {"type": "Property", "value": 5},
            },
        {
            "id": f"urn:ngsi-ld:GtfsStopTime:{city}:T2:6",
            "type": "GtfsStopTime",
            "hasTrip": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsTrip:{city}:T2",},
            "arrivalTime": {"type": "Property", "value": "08:17:00",},
            "departureTime": {"type": "Property","value": "08:19:00",},
            "hasStop": {"type": "Relationship","object": f"urn:ngsi-ld:GtfsStop:{city}:S2",},
            "stopSequence": {"type": "Property", "value": 6},
            },
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
    
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_stop_times_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_stop_times_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_stop_times_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
            # Function call result from gtfs_static_stop_times_to_ngsi_ld
            result = gtfs_static_stop_times_to_ngsi_ld(sample_raw_data, city)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_stop_times_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_stop_times_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0], city)
    mock_validate.assert_any_call(parsed_data[1], city)

    # Check that convert_gtfs_stop_times_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2