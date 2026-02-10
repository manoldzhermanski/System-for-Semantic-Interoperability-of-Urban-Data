from gtfs_static.gtfs_static_utils import convert_gtfs_levels_to_ngsi_ld

def test_convert_gtfs_levels_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for levels.txt
    """
    entity = {
        "level_id": "L1",
        "level_name": "Platform Level",
        "level_index": 1.0,
    }

    city = "Berlin"

    result = convert_gtfs_levels_to_ngsi_ld(entity, city)

    assert result == {
        "id": "urn:ngsi-ld:GtfsLevel:Berlin:L1",
        "type": "GtfsLevel",
        "name": {
            "type": "Property",
            "value": "Platform Level",
        },
        "level_index": {
            "type": "Property",
            "value": 1.0,
        },
    }
    

def test_convert_gtfs_levels_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for levels.txt when optional fileds are missing
    """
    entity = {
        "level_id": "L1",
        "level_index": 1.0,
    }

    city = "Berlin"

    result = convert_gtfs_levels_to_ngsi_ld(entity, city)

    assert result == {
        "id": "urn:ngsi-ld:GtfsLevel:Berlin:L1",
        "type": "GtfsLevel",
        "name": {
            "type": "Property",
            "value": None,
        },
        "level_index": {
            "type": "Property",
            "value": 1.0,
        },
    }