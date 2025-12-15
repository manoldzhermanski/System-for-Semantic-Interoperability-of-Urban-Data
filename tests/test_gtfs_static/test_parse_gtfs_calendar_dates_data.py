import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_calendar_dates_data

def test_parse_gtfs_calendar_dates_data_all_fields_valid():
    """
    Check if all fields are provided, they are parsed correctly
    """

    entity = {
        "service_id": "S1",
        "date": "20240131",
        "exception_type": "1"
    }

    result = parse_gtfs_calendar_dates_data(entity)

    assert result == {
        "service_id": "S1",
        "date": "20240131",
        "exception_type": 1
    }

def test_parse_gtfs_calendar_dates_data_missing_optional_fields():
    """
    Check that if a field is missing, None value is assgined
    """

    entity = {}

    result = parse_gtfs_calendar_dates_data(entity)

    assert result == {
        "service_id": None,
        "date": None,
        "exception_type": None
    }

def test_parse_gtfs_calendar_dates_data_whitespace_cleanup():
    """
    Check that whitespaces are trimmed
    """

    entity = {
        "service_id": "  S1 ",
        "date": " 20240131 ",
        "exception_type": " 0 "
    }

    result = parse_gtfs_calendar_dates_data(entity)

    assert result["service_id"] == "S1"
    assert result["date"] == "20240131"
    assert result["exception_type"] == 0

def test_parse_gtfs_calendar_dates_data_invalid_date_raises_error():
    """
    Check that invalid date format raises ValueError
    """

    entity = {
        "service_id": "S1",
        "date": "2024-01-31",
        "exception_type": "1"
    }

    with pytest.raises(ValueError) as err:
        parse_gtfs_calendar_dates_data(entity)

    assert str(err.value) == "date must be a valid date in YYYYMMDD format, got '2024-01-31'"

def test_parse_gtfs_calendar_dates_data_invalid_exception_type_raises_error():
    """
    Check that invalid value for 'exception_type' raises ValueError
    """
    entity = {
        "service_id": "S1",
        "date": "20240131",
        "exception_type": "abc"
    }

    with pytest.raises(ValueError) as err:
        parse_gtfs_calendar_dates_data(entity)

    assert str(err.value) == "exception_type must be integer, got 'abc'"
