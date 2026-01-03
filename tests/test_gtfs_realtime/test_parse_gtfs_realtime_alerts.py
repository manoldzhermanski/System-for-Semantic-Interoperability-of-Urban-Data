from gtfs_realtime.gtfs_realtime_utils import parse_gtfs_realtime_alerts

def test_parse_gtfs_realtime_alerts_partial_payload():
    """
    Check that the entries with data are parsed correctly and the remaining fields have None values
    """
    entity = {
        "id": "A1",
        "alert": {
            "active_period": [
                {
                    "start": 0,
                    "end": 0
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
        }
        
    
    expected = {
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
    
    
    result = parse_gtfs_realtime_alerts(entity)
   
    assert result == expected

def test_parse_gtfs_realtime_alerts_empty_entity():
    """
    Check that if the Alert entity is empty, all fields have None values
    """
    entity = {}
    
    expected = {
        "id": None,
        "active_period": [],
        "informed_entity": [],
        "cause": None,
        "cause_detail": {
            "translation": []
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
    
    result = parse_gtfs_realtime_alerts(entity)
    
    assert result == expected
