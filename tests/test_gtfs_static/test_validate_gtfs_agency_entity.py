import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_agency_entity

def test_validate_gtfs_agency_entity_all_valid_fields():
    """
    Check that all fields are provided and valid, the validation passes and 'agency_id' is written as a NGSI URN
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }

    validate_gtfs_agency_entity(entity)

    assert entity["agency_id"] == "urn:ngsi-ld:GtfsAgency:AG1"

def test_validate_gtfs_agency_entity_missing_required_field():
    """
    Check that if a required field is missing, a ValueError is raised
    """
    entity = {
        "agency_id": "AG1",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_url():
    """
    Check that invalid 'agency_url' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "www.fakeurl.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "agency_url must be a valid URL" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_fare_url():
    """
    Check that invalid 'agency_fare_url' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "www.fakeurl.com",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "agency_fare_url must be a valid URL" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_timezone():
    """
    Check that invalid 'agency_timezone' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Asia/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "agency_timezone must be a valid timezone" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_language():
    """
    Check that invalid 'agency_lang' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "bulgarian",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }
    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "agency_lang must be a valid language code" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_phone():
    """
    Check that invalid 'agency_phone' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "123456789!",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "agency_phone must be a valid phone number" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_email():
    """
    Check that invalid 'agency_email' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "fake_mail.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "agency_email must be a valid email address" in str(err.value)

def test_validate_gtfs_agency_entity_invalid_cemv_support():
    """
    Check that invalid 'cemv_support' value raises ValueError
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "en",
        "agency_phone": "+359888123456",
        "agency_email": "info@example.com",
        "agency_fare_url": "https://example.com/fare",
        "cemv_support": 5
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_agency_entity(entity)

    assert "cemv_support must be 0, 1 or 2" in str(err.value)
