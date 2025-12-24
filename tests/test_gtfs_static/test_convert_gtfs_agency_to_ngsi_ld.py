from gtfs_static.gtfs_static_utils import convert_gtfs_agency_to_ngsi_ld

def test_convert_gtfs_agency_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for agency.txt
    """
    entity = {
        "agency_id": "agency_1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "bg",
        "agency_phone": "+359123456",
        "agency_fare_url": "https://example.com/fares",
        "agency_email": "info@example.com",
        "cemv_support": 1,
    }

    result = convert_gtfs_agency_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsAgency:agency_1",
        "type": "GtfsAgency",
        "agency_name": {
            "type": "Property",
            "value": "Test Agency",
        },
        "agency_url": {
            "type": "Property",
            "value": "https://example.com",
        },
        "agency_timezone": {
            "type": "Property",
            "value": "Europe/Sofia",
        },
        "agency_lang": {
            "type": "Property",
            "value": "bg",
        },
        "agency_phone": {
            "type": "Property",
            "value": "+359123456",
        },
        "agency_fare_url": {
            "type": "Property",
            "value": "https://example.com/fares",
        },
        "agency_email": {
            "type": "Property",
            "value": "info@example.com",
        },
        "cemv_support": {
            "type": "Property",
            "value": 1,
        },
    }

def test_convert_gtfs_agency_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for agency.txt when optional fileds are missing
    """
    entity = {
        "agency_id": "agency_1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
    }

    result = convert_gtfs_agency_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsAgency:agency_1",
        "type": "GtfsAgency",
        "agency_name": {
            "type": "Property",
            "value": "Test Agency",
        },
        "agency_url": {
            "type": "Property",
            "value": "https://example.com",
        },
        "agency_timezone": {
            "type": "Property",
            "value": "Europe/Sofia",
        },
        "agency_lang": {
            "type": "Property",
            "value": None,
        },
        "agency_phone": {
            "type": "Property",
            "value": None,
        },
        "agency_fare_url": {
            "type": "Property",
            "value": None,
        },
        "agency_email": {
            "type": "Property",
            "value": None,
        },
        "cemv_support": {
            "type": "Property",
            "value": None,
        },
    }
