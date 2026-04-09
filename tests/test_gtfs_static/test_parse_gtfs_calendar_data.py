import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_calendar_data

def test_parse_gtfs_calendar_data_all_fields_present():
    """
    Check if all fields are provided, they are parsed correctly
    """

    entity = {
        "service_id": "S1",
        "monday": "1",
        "tuesday": "1",
        "wednesday": "1",
        "thursday": "1",
        "friday": "1",
        "saturday": "1",
        "sunday": "1",
        "start_date": "20260408",
        "end_date": "20260430"
    }

    result = parse_gtfs_calendar_data(entity)

    assert result == {
        "service_id": "S1",
        "monday": 1,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 1,
        "sunday": 1,
        "start_date": "20260408",
        "end_date": "20260430"
    }

def test_parse_gtfs_calendar_data_missing_fields():
    """
    Check that if a field is missing, None value is assgined
    """

    entity = {}

    result = parse_gtfs_calendar_data(entity)

    assert result == {
        "service_id": None,
        "monday": None,
        "tuesday": None,
        "wednesday": None,
        "thursday": None,
        "friday": None,
        "saturday": None,
        "sunday": None,
        "start_date": None,
        "end_date": None
    }

def test_parse_gtfs_calendar_data_whitespace_cleanup():
    """
    Check that whitespaces are trimmed
    """

    entity = {
        "service_id": " S1 ",
        "monday": " 1 ",
        "tuesday": " 1 ",
        "wednesday": " 1 ",
        "thursday": " 1 ",
        "friday": " 1 ",
        "saturday": " 1 ",
        "sunday": " 1 ",
        "start_date": " 20260408 ",
        "end_date": " 20260430 "
    }

    result = parse_gtfs_calendar_data(entity)

    assert result == {
        "service_id": "S1",
        "monday": 1,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 1,
        "sunday": 1,
        "start_date": "20260408",
        "end_date": "20260430"
    }

def test_parse_gtfs_calendar_data_invalid_date_raises_error():
    """
    Check that invalid date format raises ValueError
    """

    entity = {"start_date": "2024-01-31"}

    with pytest.raises(ValueError) as err:
        parse_gtfs_calendar_data(entity)

    assert str(err.value) == "start_date must be a valid date in YYYYMMDD format, got '2024-01-31'"

def test_parse_gtfs_calendar_data_invalid_exception_type_raises_error():
    """
    Check that if 'exception_type' cannot be parsed to integer, ValueError is raised
    """
    entity = {
        "monday": "abc"
    }

    with pytest.raises(ValueError) as err:
        parse_gtfs_calendar_data(entity)

    assert str(err.value) == "monday must be integer, got 'abc'"
