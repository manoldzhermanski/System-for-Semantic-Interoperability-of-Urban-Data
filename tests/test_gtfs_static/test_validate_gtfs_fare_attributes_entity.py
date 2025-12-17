import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_fare_attributes_entity

def test_validate_gtfs_fare_attributes_entity_all_valid_fields():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "fare_id": "FARE1",
        "price": 2.50,
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": 2,
        "transfer_duration": 3600
    }

    validate_gtfs_fare_attributes_entity(entity)

def test_validate_gtfs_fare_attributes_entity_missing_required_field():
    """
    Check that if a required field is missing, a ValueError is raised
    """
    entity = {
        "fare_id": "FARE1",
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": 2,
        "transfer_duration": 3600
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_fare_attributes_entity(entity)
    
    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_fare_attributes_entity_none_value_as_required_field():
    """
    Check that if a required field has None as a value, ValueError is raised
    """
    entity = {
        "fare_id": "FARE1",
        "price": None,
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": 2,
        "transfer_duration": 3600
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_fare_attributes_entity(entity)
    
    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_fare_attributes_entity_invalid_price():
    """
    Check that invalid 'price' value raises ValueError
    """
    entity = {
        "fare_id": "FARE1",
        "price": -1,
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": 2,
        "transfer_duration": 3600
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_fare_attributes_entity(entity)

    assert "'price' is not a valid currency price" in str(err.value)

def test_validate_gtfs_fare_attributes_entity_invalid_currency_type():
    """
    Check that invalid 'currency_type' value raises ValueError
    """
    entity = {
        "fare_id": "FARE1",
        "price": 2.50,
        "currency_type": "EURO",
        "payment_method": 1,
        "transfers": 2,
        "transfer_duration": 3600
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_fare_attributes_entity(entity)

    assert "'currency_type' is not a valid currency code" in str(err.value)

def test_validate_gtfs_fare_attributes_entity_invalid_payment_method():
    """
    Check that invalid 'payment_method' value raises ValueError
    """
    entity = {
        "fare_id": "FARE1",
        "price": 2.50,
        "currency_type": "EUR",
        "payment_method": 2,
        "transfers": 2,
        "transfer_duration": 3600
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_fare_attributes_entity(entity)

    assert "'payment_method' must be 0 or 1" in str(err.value)

def test_validate_gtfs_fare_attributes_entity_invalid_transfers():
    """
    Check that invalid 'transfers' value raises ValueError
    """
    entity = {
        "fare_id": "FARE1",
        "price": 2.50,
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": 3,
        "transfer_duration": 3600
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_fare_attributes_entity(entity)

    assert "'transfers' should be 0, 1 or 2" in str(err.value)
