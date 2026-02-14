from gtfs_static.gtfs_static_utils import convert_gtfs_pathways_to_ngsi_ld

def test_convert_gtfs_pathways_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for pathways.txt
    """
    city = "Sofia"
    
    entity = {
        "pathway_id": "P1",
        "from_stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        "to_stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S2",
        "pathway_mode": 1,
        "is_bidirectional": 1,
        "length": 120.5,
        "traversal_time": 90,
        "stair_count": 10,
        "max_slope": 5.0,
        "min_width": 1.2,
        "signposted_as": "Exit",
        "reversed_signposted_as": "Entrance",
    }

    result = convert_gtfs_pathways_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsPathway:{city}:P1",
        "type": "GtfsPathway",
        "hasOrigin": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S2",
        },
        "pathway_mode": {
            "type": "Property",
            "value": 1,
        },
        "isBidirectional": {
            "type": "Property",
            "value": 1,
        },
        "length": {
            "type": "Property",
            "value": 120.5,
        },
        "traversal_time": {
            "type": "Property",
            "value": 90,
        },
        "stair_count": {
            "type": "Property",
            "value": 10,
        },
        "max_slope": {
            "type": "Property",
            "value": 5.0,
        },
        "min_width": {
            "type": "Property",
            "value": 1.2,
        },
        "signposted_as": {
            "type": "Property",
            "value": "Exit",
        },
        "reversed_signposted_as": {
            "type": "Property",
            "value": "Entrance",
        },
    }
    
def test_convert_gtfs_pathways_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for pathways.txt when optional fileds are missing
    """
    city = "Sofia"
    
    entity = {
        "pathway_id": "P1",
        "from_stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        "to_stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S2",
        "pathway_mode": 1,
        "is_bidirectional": 1,
    }

    result = convert_gtfs_pathways_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsPathway:{city}:P1",
        "type": "GtfsPathway",
        "hasOrigin": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S2",
        },
        "pathway_mode": {
            "type": "Property",
            "value": 1,
        },
        "isBidirectional": {
            "type": "Property",
            "value": 1,
        },
        "length": {
            "type": "Property",
            "value": None,
        },
        "traversal_time": {
            "type": "Property",
            "value": None,
        },
        "stair_count": {
            "type": "Property",
            "value": None,
        },
        "max_slope": {
            "type": "Property",
            "value": None,
        },
        "min_width": {
            "type": "Property",
            "value": None,
        },
        "signposted_as": {
            "type": "Property",
            "value": None,
        },
        "reversed_signposted_as": {
            "type": "Property",
            "value": None,
        },
    }