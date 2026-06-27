import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_translations_to_ngsi_ld

def test_gtfs_static_translations_to_ngsi_ld():
    
    # Sample input for GTFS Translation
    sample_raw_data = [
        {
            "table_name": "stops",
            "field_name": "stop_name",
            "language": "en",
            "translation": "TSentralna gara",
            "record_id": "Stop_1",
            "field_value": ""
            },
        {
            "table_name": "stops",
            "field_name": "stop_name",
            "language": "en",
            "translation": "Serdika gara",
            "record_id": "Stop_2",
            "field_value": ""
            }
        ]
    
    # Mock result from parse_gtfs_translations_data
    parsed_data = [
        {
            "table_name": "stops",
            "field_name": "stop_name",
            "language": "en",
            "translation": "TSentralna_gara",
            "record_id": "Stop_1",
            "field_value": None
            },
        {
            "table_name": "stops",
            "field_name": "stop_name",
            "language": "en",
            "translation": "Serdika_gara",
            "record_id": "Stop_2",
            "field_value": ""
         }
        ]
    
    city = "Sofia"
    
    # Mock result from convert_gtfs_transfers_to_ngsi_ld
    converted_data = [
        {
            "id": f"urn:ngsi-ld:GtfsTranslation:{city}:stops:stop_name:en:TSentralna_gara",
            "type": "GtfsTranslation",
            "table_name": {"type": "Property", "value": "stops"},
            "field_name": {"type": "Property", "value": "stop_name"},
            "language": {"type": "Property", "value": "en"},
            "translation": {"type": "Property", "value": "TSentralna_gara"},
            "record_id": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsStop:{city}:Stop_1"},
            "record_sub_id": {"type": "Property", "value": None},
            "field_value": {"type": "Property", "value": None}
            },
        {
            "id": f"urn:ngsi-ld:GtfsTranslation:{city}:stops:stop_name:en:Serdik_gara",
            "type": "GtfsTranslation",
            "table_name": {"type": "Property", "value": "stops"},
            "field_name": {"type": "Property", "value": "stop_name"},
            "language": {"type": "Property", "value": "en"},
            "translation": {"type": "Property", "value": "Serdik_gara"},
            "record_id": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsStop:{city}:Stop_2"},
            "record_sub_id": {"type": "Property", "value": None},
            "field_value": {"type": "Property", "value": None}
            }
        ]
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": f"urn:ngsi-ld:GtfsTranslation:{city}:stops:stop_name:en:TSentralna_gara",
            "type": "GtfsTranslation",
            "table_name": {"type": "Property", "value": "stops"},
            "field_name": {"type": "Property", "value": "stop_name"},
            "language": {"type": "Property", "value": "en"},
            "translation": {"type": "Property", "value": "TSentralna_gara"},
            "record_id": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsStop:{city}:Stop_1"},
            },
        {
            "id": f"urn:ngsi-ld:GtfsTranslation:{city}:stops:stop_name:en:Serdik_gara",
            "type": "GtfsTranslation",
            "table_name": {"type": "Property", "value": "stops"},
            "field_name": {"type": "Property", "value": "stop_name"},
            "language": {"type": "Property", "value": "en"},
            "translation": {"type": "Property", "value": "Serdik_gara"},
            "record_id": {"type": "Relationship", "object": f"urn:ngsi-ld:GtfsStop:{city}:Stop_2"},
            }
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
    
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_translations_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_translations_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_translations_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
             
        # Function call result from gtfs_static_transfers_to_ngsi_ld
        result = gtfs_static_translations_to_ngsi_ld(sample_raw_data, city)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_transfers_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_transfers_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0], city)
    mock_validate.assert_any_call(parsed_data[1], city)

    # Check that convert_gtfs_transfers_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 2
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 2