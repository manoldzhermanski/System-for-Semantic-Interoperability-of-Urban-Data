import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_pathways_to_ngsi_ld

def test_gtfs_pathways_to_ngsi_ld():
    """
    Unit test for gtfs_static_pathways_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Pathway
    sample_raw_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "urn:ngsi-ld:GtfsStop:S1",
            "to_stop_id": "urn:ngsi-ld:GtfsStop:S2",
            "pathway_mode": "1",
            "is_bidirectional": "1",
            },
        {
            "pathway_id": "P2",
            "from_stop_id": "urn:ngsi-ld:GtfsStop:S3",
            "to_stop_id": "urn:ngsi-ld:GtfsStop:S4",
            "pathway_mode": "1",
            "is_bidirectional": "1",
            },
        ]

    # Mock result from parse_gtfs_pathways_data
    parsed_data = [
        {
            "pathway_id": "P1",
            "from_stop_id": "urn:ngsi-ld:GtfsStop:S1",
            "to_stop_id": "urn:ngsi-ld:GtfsStop:S2",
            "pathway_mode": 1,
            "is_bidirectional": 1,
            },
        {
            "pathway_id": "P2",
            "from_stop_id": "urn:ngsi-ld:GtfsStop:S3",
            "to_stop_id": "urn:ngsi-ld:GtfsStop:S4",
            "pathway_mode": 1,
            "is_bidirectional": 1,
            },
        ]
    
    # Mock result from convert_gtfs_pathways_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsPathway:P1",
            "type": "GtfsPathway",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S1",},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S2",},
            "pathway_mode": {"type": "Property", "value": 1,},
            "isBidirectional": {"type": "Property", "value": 1,}
            },
        {
            "id": "urn:ngsi-ld:GtfsPathway:P2",
            "type": "GtfsPathway",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S3",},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S4",},
            "pathway_mode": {"type": "Property", "value": 1,},
            "isBidirectional": {"type": "Property", "value": 1,}
            },
        ]
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsPathway:P1",
            "type": "GtfsPathway",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S1",},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S2",},
            "pathway_mode": {"type": "Property", "value": 1,},
            "isBidirectional": {"type": "Property", "value": 1,}
            },
        {
            "id": "urn:ngsi-ld:GtfsPathway:P2",
            "type": "GtfsPathway",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S3",},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:S4",},
            "pathway_mode": {"type": "Property", "value": 1,},
            "isBidirectional": {"type": "Property", "value": 1,}
            },
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
    
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_pathways_data", mock_parse),\
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_pathways_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_pathways_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
            
            # Function call result from gtfs_static_pathways_to_ngsi_ld
            result = gtfs_static_pathways_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_pathways_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_pathways_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_pathways_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2