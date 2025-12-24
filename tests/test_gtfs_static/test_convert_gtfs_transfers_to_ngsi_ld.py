from gtfs_static.gtfs_static_utils import convert_gtfs_transfers_to_ngsi_ld

def test_convert_gtfs_transfers_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for transfers.txt
    """
    entity = {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": "urn:ngsi-ld:GtfsRoute:R1",
        "to_route_id": "urn:ngsi-ld:GtfsRoute:R2",
        "transfer_type": 2,
        "min_transfer_time": 300,
    }

    result = convert_gtfs_transfers_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsTransferRule:Transfer:fromStop:S1:toStop:S2:fromTrip:T1:toTrip:T2",
        "type": "GtfsTransferRule",
        "hasOrigin": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:S1",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:S2",
        },
        "from_route_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsRoute:R1",
        },
        "to_route_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsRoute:R2",
        },
        "from_trip_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:T1",
        },
        "to_trip_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:T2",
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

    result = convert_gtfs_transfers_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsTransferRule:Transfer:fromStop:S1:toStop:S2:fromTrip:T1:toTrip:T2",
        "type": "GtfsTransferRule",
        "hasOrigin": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:S1",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:S2",
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
            "object": "urn:ngsi-ld:GtfsTrip:T1",
        },
        "to_trip_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:T2",
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
