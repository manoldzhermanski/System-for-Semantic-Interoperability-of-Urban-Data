from gtfs_static.gtfs_static_utils import convert_gtfs_transfers_to_ngsi_ld

def test_convert_gtfs_transfers_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for transfers.txt
    """
    
    city = "Sofia"
    
    entity = {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
        "to_route_id": f"urn:ngsi-ld:GtfsRoute:{city}:R2",
        "transfer_type": 2,
        "min_transfer_time": 300,
    }

    result = convert_gtfs_transfers_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsTransferRule:{city}:Transfer:fromStop:S1:toStop:S2:fromTrip:T1:toTrip:T2",
        "type": "GtfsTransferRule",
        "hasOrigin": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S2",
        },
        "from_route_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsRoute:{city}:R1",
        },
        "to_route_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsRoute:{city}:R2",
        },
        "from_trip_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
        },
        "to_trip_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsTrip:{city}:T2",
        },
        "transferType": {
            "type": "Property",
            "value": 2,
        },
        "minimumTransferTime": {
            "type": "Property",
            "value": 300,
        },
    }

def test_convert_gtfs_transfers_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for transfers.txt when optional fileds are missing
    """
    entity = {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "transfer_type": 2,
    }
    
    city = "Sofia"

    result = convert_gtfs_transfers_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsTransferRule:{city}:Transfer:fromStop:S1:toStop:S2:fromTrip:T1:toTrip:T2",
        "type": "GtfsTransferRule",
        "hasOrigin": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S2",
        },
        "from_route_id": {
            "type": "Relationship",
            "object": None,
        },
        "to_route_id": {
            "type": "Relationship",
            "object": None,
        },
        "from_trip_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
        },
        "to_trip_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsTrip:{city}:T2",
        },
        "transferType": {
            "type": "Property",
            "value": 2,
        },
        "minimumTransferTime": {
            "type": "Property",
            "value": None,
        },
    }
