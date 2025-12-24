from gtfs_static.gtfs_static_utils import convert_gtfs_transfers_to_ngsi_ld

def test_convert_gtfs_transfers_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for transfers.txt
    """
    entity = {
        "from_stop_id": "STOP_A",
        "to_stop_id": "STOP_B",
        "from_trip_id": "TRIP_1",
        "to_trip_id": "TRIP_2",
        "from_route_id": "urn:ngsi-ld:GtfsRoute:R1",
        "to_route_id": "urn:ngsi-ld:GtfsRoute:R2",
        "transfer_type": 2,
        "min_transfer_time": 300,
    }

    result = convert_gtfs_transfers_to_ngsi_ld(entity)

    assert result == {
        "id": (
            "urn:ngsi-ld:GtfsTransferRule:"
            "Transfer:"
            "fromStop:STOP_A:"
            "toStop:STOP_B:"
            "fromTrip:TRIP_1:"
            "toTrip:TRIP_2"
        ),
        "type": "GtfsTransferRule",
        "hasOrigin": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:STOP_A",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:STOP_B",
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
            "object": "urn:ngsi-ld:GtfsTrip:TRIP_1",
        },
        "to_trip_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:TRIP_2",
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
        "from_stop_id": "STOP_A",
        "to_stop_id": "STOP_B",
        "from_trip_id": "TRIP_1",
        "to_trip_id": "TRIP_2",
        "transfer_type": 2,
    }

    result = convert_gtfs_transfers_to_ngsi_ld(entity)

    assert result == {
        "id": (
            "urn:ngsi-ld:GtfsTransferRule:"
            "Transfer:"
            "fromStop:STOP_A:"
            "toStop:STOP_B:"
            "fromTrip:TRIP_1:"
            "toTrip:TRIP_2"
        ),
        "type": "GtfsTransferRule",
        "hasOrigin": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:STOP_A",
        },
        "hasDestination": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsStop:STOP_B",
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
            "object": "urn:ngsi-ld:GtfsTrip:TRIP_1",
        },
        "to_trip_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:TRIP_2",
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
