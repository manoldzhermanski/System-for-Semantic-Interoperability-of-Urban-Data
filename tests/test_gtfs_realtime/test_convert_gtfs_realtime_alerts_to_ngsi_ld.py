from gtfs_realtime.gtfs_realtime_utils import convert_gtfs_realtime_alerts_to_ngsi_ld

def test_convert_gtfs_realtime_alerts_to_ngsi_ld_partial_payload():
    """
    Check that the normalized entity is converted to a NGSI-LD representation
    """
    entity = {
        "id": "urn:ngsi-ld:GtfsRealtimeAlert:A1",
        "active_period": [
            {
                "start": "1970-01-01T00:00:00Z",
                "end": "1970-01-01T00:00:00Z"
                }
            ],
        "informed_entity": [],
        "cause": "UNKNOWN_CAUSE",
        "cause_detail": {
            "translation": [
                {
                    "text": "",
                    "language": "bg"
                    }
                ]
            },
        "effect": None,
        "effect_detail": {
            "translation": []
            },
        "url":{
            "translation": []
            },
        "header_text": {
            "translation": []
            },
        "description_text": {
            "translation": []
            },
        "tts_header_text": {
            "translation": []
            },
        "tts_description_text":{
            "translation": []
            },
        "severity_level": None,
        "image": {
            "localized_image": []
            },
        "image_alternative_text":{
            "translation": []
            }
        }
    
    expected = {
        "id": "urn:ngsi-ld:GtfsRealtimeAlert:A1",
        "type": "GtfsRealtimeAlert",
        "active_period": {
            "type": "Property",
            "value": [
                {
                    "start": "1970-01-01T00:00:00Z",
                    "end": "1970-01-01T00:00:00Z"
                    }
                ],
            },
        "informed_entity": {
            "type": "Property",
            "value": []
            },
        "cause": {
            "type": "Property",
            "value": "UNKNOWN_CAUSE",
            },
        "cause_detail": {
            "type": "Property",
            "value": {
            "translation": [
                {
                    "text": "",
                    "language": "bg"
                    }
                ]
            }
            },
        "effect": {
            "type": "Property",
            "value": None
            },
        "effect_detail": {
            "type": "Property",
            "value": { 
                'translation': [],
                }
            },
        "url":{
            "type": "Property",
            "value": { 
                'translation': [],
                }
            },
        "header_text": {
            "type": "Property",
            "value": { 
                'translation': [],
                }
            },
        "description_text": {
            "type": "Property",
            "value": { 
                'translation': [],
                }
            },
        "tts_header_text": {
            "type": "Property",
            "value": { 
                'translation': [],
                }
            },
        "tts_description_text":{
            "type": "Property",
            "value": { 
                'translation': [],
                }
            },
        "severity_level": {
            "type": "Property",
            "value": None,
            },
        "image": {
            "type": "Property",
            "value": {
                "localized_image": [],
                }
            },
        "image_alternative_text":{
            "type": "Property",
            "value": { 
                'translation': [],
                }
            }
        }
    
    result = convert_gtfs_realtime_alerts_to_ngsi_ld(entity)
    
    assert result == expected
    
def test_convert_gtfs_realtime_alerts_to_ngsi_ld_empty_payload():
    pass