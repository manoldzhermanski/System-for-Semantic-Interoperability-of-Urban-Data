import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_fare_attributes_data

def test_parse_gtfs_fare_attributes_data_all_fields_valid():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """

    entity = {
        "fare_id": "F1",
        "price": "2.50",
        "currency_type": "EUR",
        "payment_method": "1",
        "transfers": "0",
        "agency_id": "AG1",
        "transfer_duration": "3600"
    }

    result = parse_gtfs_fare_attributes_data(entity)

    assert result == {
        "fare_id": "F1",
        "price": 2.5,
        "currency_type": "EUR",
        "payment_method": 1,
        "transfers": 0,
        "agency_id": "AG1",
        "transfer_duration": 3600
    }


def test_parse_gtfs_fare_attributes_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}

    result = parse_gtfs_fare_attributes_data(entity)

    assert result == {
        "fare_id": None,
        "price": None,
        "currency_type": None,
        "payment_method": None,
        "transfers": None,
        "agency_id": None,
        "transfer_duration": None
    }


def test_parse_gtfs_fare_attributes_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "fare_id": "  F1 ",
        "price": " 2.5 ",
        "payment_method": " 1 "
    }

    result = parse_gtfs_fare_attributes_data(entity)

    assert result == {
        "fare_id":"F1",
        "price": 2.5,
        "payment_method": 1
    }


def test_parse_gtfs_fare_attributes_data_invalid_price_raises_error():
    """
    Check that invalid price raises ValueError
    """
    entity = {"price": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_fare_attributes_data(entity)

    assert str(err.value) == "price must be float, got 'abc'"


def test_parse_gtfs_fare_attributes_data_invalid_payment_method_raises_error():
    """
    Check that invalid payment_method raises ValueError
    """

    entity = {"payment_method": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_fare_attributes_data(entity)

    assert str(err.value) == "payment_method must be integer, got 'abc'"


def test_parse_gtfs_fare_attributes_data_invalid_transfers_raises_error():
    """
    Check that invalid transfers raises ValueError
    """
    
    entity = {"transfers": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_fare_attributes_data(entity)

    assert str(err.value) == "transfers must be integer, got 'abc'"


def test_parse_gtfs_fare_attributes_data_invalid_transfer_duration_raises_error():
    """
    Check that invalid transfer_duration raises ValueError
    """

    entity = {"transfer_duration": "abc"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_fare_attributes_data(entity)

    assert str(err.value) == "transfer_duration must be integer, got 'abc'"
