import config
from gtfs_static.gtfs_static_utils import convert_gtfs_fare_attributes_to_ngsi_ld

def test_convert_gtfs_fare_attributes_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for fare_attributes.txt
    """
    config.set_operating_city("Sofia")

    entity = {
        "fare_id": "F1",
        "price": 1.60,
        "currency_type": "BGN",
        "payment_method": 0,
        "transfers": 1,
        "agency_id": f"urn:ngsi-ld:GtfsAgency:{config.get_operating_city()}:A1",
        "transfer_duration": 3600,
    }

    result = convert_gtfs_fare_attributes_to_ngsi_ld(entity)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsFareAttributes:{config.get_operating_city()}:F1",
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
            "object": f"urn:ngsi-ld:GtfsAgency:{config.get_operating_city()}:A1",
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
    config.set_operating_city("Sofia")

    entity = {
        "fare_id": "F1",
        "price": 1.60,
        "currency_type": "BGN",
        "payment_method": 0,
        "transfers": 1,
        "agency_id": f"urn:ngsi-ld:GtfsAgency:{config.get_operating_city()}:A1",
    }

    result = convert_gtfs_fare_attributes_to_ngsi_ld(entity)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsFareAttributes:{config.get_operating_city()}:F1",
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
            "object": f"urn:ngsi-ld:GtfsAgency:{config.get_operating_city()}:A1",
        },
        "transfer_duration": {
            "type": "Property",
            "value": None,
        },
    }
