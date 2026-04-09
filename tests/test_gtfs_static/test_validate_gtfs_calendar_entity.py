import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_calendar_entity

def test_validate_gtfs_calendar_entity_all_valid_fields():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
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

    validate_gtfs_calendar_entity(entity)

def test_validate_gtfs_calendar_entity_missing_required_field():
    """
    Check that if a required field is missing, a ValueError is raised
    """
    entity = {
        "service_id": "S1",
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 1,
        "sunday": 1,
        "end_date": "20260430"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_calendar_entity(entity)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_calendar_entity_invalid_exception_type():
    """
    Check that invalid 'exception_type' value raises ValueError
    """
    entity = {
        "service_id": "S1",
        "monday": 2,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 1,
        "sunday": 1,
        "start_date": "20260408",
        "end_date": "20260430"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_calendar_entity(entity)

    assert "monday must be 0 or 1" in str(err.value)