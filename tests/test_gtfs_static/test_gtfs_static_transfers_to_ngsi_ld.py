import pytest
from unittest.mock import patch
from gtfs_static.gtfs_static_utils import gtfs_static_transfers_to_ngsi_ld

# Mock function behavior
@patch("gtfs_static.gtfs_static_utils.remove_none_values")
@patch("gtfs_static.gtfs_static_utils.convert_gtfs_transfers_to_ngsi_ld")
@patch("gtfs_static.gtfs_static_utils.validate_gtfs_transfers_entity")
@patch("gtfs_static.gtfs_static_utils.parse_gtfs_transfers_data")
def test_gtfs_static_transfers_to_ngsi_ld(mock_parse, mock_validate, mock_convert, mock_remove_none):
    """
    Unit test for gtfs_static_transfers_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Transfer
    sample_raw_data = [
        {
            "transfer_type": "1",
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            },
        {
            "transfer_type": "4",
            "from_trip_id": "T1",
            "to_trip_id": "T2",
         }
        ]

    # Mock result from parse_gtfs_transfers_data
    parsed_data = [
        {
            "transfer_type": 1,
            "from_stop_id": "S1",
            "to_stop_id": "S2",
            },
        {
            "transfer_type": 4,
            "from_trip_id": "T1",
            "to_trip_id": "T2",
         }
        ]
    
    mock_parse.side_effect = parsed_data
    
    # Mock result from convert_gtfs_transfers_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:fromStop:S1:toStop:S2",
            "type": "GtfsTransfer",
            "from_stop_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:S1"},
            "to_stop_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:S2"},
            "transfer_type": {"type": "Property", "value": 1}
            },
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:fromTrip:T1:toTrip:T2",
            "type": "GtfsTransfer",
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:T1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:T1"},
            "transfer_type": {"type": "Property", "value": 4}
            }
        ]
    
    mock_convert.side_effect = converted_data
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:fromStop:S1:toStop:S2",
            "type": "GtfsTransfer",
            "from_stop_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:S1"},
            "to_stop_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:S2"},
            "transfer_type": {"type": "Property", "value": 1}
            },
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:fromTrip:T1:toTrip:T2",
            "type": "GtfsTransfer",
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:T1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:T1"},
            "transfer_type": {"type": "Property", "value": 4}
            }
        ]
    
    mock_remove_none.side_effect = cleaned_data
    
    # Function call result from gtfs_static_transfers_to_ngsi_ld
    result = gtfs_static_transfers_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_transfers_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_transfers_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_transfers_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2
