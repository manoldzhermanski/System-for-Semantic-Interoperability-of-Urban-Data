import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_calendar_dates_entity

def test_validate_gtfs_calendar_dates_entity_all_valid_fields():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "service_id": "S1",
        "date": "20260101",
        "exception_type": 1
    }

    validate_gtfs_calendar_dates_entity(entity)

def test_validate_gtfs_calendar_dates_entity_missing_required_field():
    """
    Check that if a required field is missing, a ValueError is raised
    """
    entity = {
        "date": "20260101",
        "exception_type": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_calendar_dates_entity(entity)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_calendar_dates_entity_invalid_date_value():
    """
    Check that invalid 'date' value raises ValueError
    """
    entity = {
        "service_id": "S1",
        "date": "2026-13-40",
        "exception_type": 1
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_calendar_dates_entity(entity)

    assert "date must be a valid date in YYYYMMDD" in str(err.value)

def test_validate_gtfs_calendar_dates_entity_invalid_exception_type():
    """
    Check that invalid 'exception_type' value raises ValueError
    """
    entity = {
        "service_id": "S1",
        "date": "20260101",
        "exception_type": 3
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_calendar_dates_entity(entity)

    assert "exception_type must be 1 or 2" in str(err.value)