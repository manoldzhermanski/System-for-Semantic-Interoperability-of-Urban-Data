from gtfs_static.gtfs_static_utils import convert_gtfs_fare_attributes_to_ngsi_ld

def test_convert_gtfs_fare_attributes_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for fare_attributes.txt
    """
    entity = {
        "fare_id": "F1",
        "price": 1.60,
        "currency_type": "BGN",
        "payment_method": 0,
        "transfers": 1,
        "agency_id": "urn:ngsi-ld:GtfsAgency:A1",
        "transfer_duration": 3600,
    }

    result = convert_gtfs_fare_attributes_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsFareAttributes:F1",
        "type": "GtfsFareAttributes",
        "price": {
            "type": "Property",
            "value": 1.60,
        },
        "currency_type": {
            "type": "Property",
            "value": "BGN",
        },
        "payment_method": {
            "type": "Property",
            "value": 0,
        },
        "transfers": {
            "type": "Property",
            "value": 1,
        },
        "agency": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsAgency:A1",
        },
        "transfer_duration": {
            "type": "Property",
            "value": 3600,
        },
    }

def test_convert_gtfs_fare_attributes_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for fare_attributes.txt when optional fileds are missing
    """
    entity = {
        "fare_id": "F1",
        "price": 1.60,
        "currency_type": "BGN",
        "payment_method": 0,
        "transfers": 1,
        "agency_id": "urn:ngsi-ld:GtfsAgency:A1",
    }

    result = convert_gtfs_fare_attributes_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsFareAttributes:F1",
        "type": "GtfsFareAttributes",
        "price": {
            "type": "Property",
            "value": 1.60,
        },
        "currency_type": {
            "type": "Property",
            "value": "BGN",
        },
        "payment_method": {
            "type": "Property",
            "value": 0,
        },
        "transfers": {
            "type": "Property",
            "value": 1,
        },
        "agency": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsAgency:A1",
        },
        "transfer_duration": {
            "type": "Property",
            "value": None,
        },
    }
