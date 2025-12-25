import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_trips_to_ngsi_ld
    
def test_gtfs_static_trips_to_ngsi_ld():
    """
    Unit test for gtfs_static_trips_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Trip
    sample_raw_data = [
        {"trip_id": "T1",
         "route_id": "R1",
         "service_id": "S1",
         "direction_id": "0"
         },
        {"trip_id": "T2",
         "route_id": "R2",
         "service_id": "S2",
         "direction_id": "1"
         }
        ]

    # Mock result from parse_gtfs_trips_data
    parsed_data = [
        {"trip_id": "T1",
         "route_id": "R1",
         "service_id": "S1",
         "direction_id": 0
         },
        {"trip_id": "T2",
         "route_id": "R2",
         "service_id": "S2",
         "direction_id": 1
         }
        ]
        
    # Mock result from convert_gtfs_trips_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:T1",
            "type": "GtfsTrip",
            "tripId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:T1"},
            "routeId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:R1"},
            "serviceId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S1"},
            "direction_id": {"type": "Property", "value": 0}
            },
        {
            "id": "urn:ngsi-ld:GtfsTrip:T2",
            "type": "GtfsTrip",
            "tripId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:T2"},
            "routeId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:R2"},
            "serviceId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S2"},
            "direction_id": {"type": "Property", "value": 1}
            }
        ]
        
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:T1",
            "type": "GtfsTrip",
            "tripId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:T1"},
            "routeId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:R1"},
            "serviceId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S1"},
            "direction_id": {"type": "Property", "value": 0}
            },
        {
            "id": "urn:ngsi-ld:GtfsTrip:T2",
            "type": "GtfsTrip",
            "tripId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:T2"},
            "routeId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:R2"},
            "serviceId": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:S2"},
            "direction_id": {"type": "Property", "value": 1}
            }
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
        
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_trips_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_trips_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_trips_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
            
            # Function call result from gtfs_static_trips_to_ngsi_ld
            result = gtfs_static_trips_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_trips_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_trips_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_trips_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2
