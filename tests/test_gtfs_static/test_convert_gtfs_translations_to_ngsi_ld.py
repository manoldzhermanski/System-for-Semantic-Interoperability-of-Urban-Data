import pytest
from gtfs_static.gtfs_static_utils import convert_gtfs_translations_to_ngsi_ld

def test_convert_gtfs_translations_to_ngsi_ld_record_id_defined():
    """
    Test conversion when 'record_id' is defined
    """
    city = "Sofia"
    
    entity = {
        "table_name": "stops",
        "field_name": "stop_name",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": f"urn:ngsi-ld:GtfsStop:{city}:Stop_1",
        "field_value": None,
    }
    
    result = convert_gtfs_translations_to_ngsi_ld(entity, city)
    
    assert result == {
        "id": f"urn:ngsi-ld:GtfsTranslation:{city}:stops:stop_name:en:TSentralna gara",
        "type": "GtfsTranslation",
        
        "table_name": {
            "type": "Property",
            "value": "stops"
        },
        
        "field_name": {
            "type": "Property",
            "value": "stop_name"
        },
        
        "language": {
            "type": "Property",
            "value": "en"
        },
        
        "translation": {
            "type": "Property",
            "value": "TSentralna gara"
        },
        
        "record_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:Stop_1"
        },
        
        "record_sub_id": {
            "type": "Property",
            "value": None
        },
        
        "field_value": {
            "type": "Property",
            "value": None
        }
    } 
    
def test_convert_gtfs_translations_to_ngsi_ld_field_value_defined():
    """
    Test conversion when 'field_value' is defined
    """
    entity = {
        "table_name": "stops",
        "field_name": "stop_name",
        "language": "en",
        "translation": "TSentralna gara",
        "record_id": None,
        "field_value": "ЦЕНТРАЛНА ГАРА",
    }
    
    city = "Sofia"
    
    result = convert_gtfs_translations_to_ngsi_ld(entity, city)
    
    assert result == {
        "id": f"urn:ngsi-ld:GtfsTranslation:{city}:stops:stop_name:en:TSentralna gara",
        "type": "GtfsTranslation",
        
        "table_name": {
            "type": "Property",
            "value": "stops"
        },
        
        "field_name": {
            "type": "Property",
            "value": "stop_name"
        },
        
        "language": {
            "type": "Property",
            "value": "en"
        },
        
        "translation": {
            "type": "Property",
            "value": "TSentralna gara"
        },
        
        "record_id": {
            "type": "Relationship",
            "object": None
        },
        
        "record_sub_id": {
            "type": "Property",
            "value": None
        },
        
        "field_value": {
            "type": "Property",
            "value": "ЦЕНТРАЛНА ГАРА"
        }
    } 