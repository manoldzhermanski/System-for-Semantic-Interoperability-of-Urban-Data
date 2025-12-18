import pytest
from gtfs_static.gtfs_static_utils import validate_required_fields

def test_validate_required_fields_all_required_fields_are_present():
    """
    All required fields are present.
    """

    data = {
        "route_id": "1",
        "route_name": "Main Route",
    }

    required_fields = ["route_id", "route_name"]

    validate_required_fields(data, required_fields)

def test_validate_required_fields_missing_field():
    """
    Check that a missing required field raises a ValueError
    """

    data = {
        "route_name": "Main Route",
    }

    required_fields = ["route_id"]

    with pytest.raises(ValueError) as err:
        validate_required_fields(data, required_fields)

    assert str(err.value) == "Missing required GTFS field: route_id"

def test_validate_required_fields_none_value_raises_value_error():
    """
    Check that a field with a None raises ValueError
    """
    data = {
        "route_id": None,
    }
    required_fields = ["route_id"]

    with pytest.raises(ValueError) as err:
        validate_required_fields(data, required_fields)

    assert str(err.value) == "Missing required GTFS field: route_id"

def test_validate_required_fields_empty_string_raises_value_error():
    """
    Check that an empty string raises ValueError
    """

    data = {
        "route_id": "",
    }

    required_fields = ["route_id"]

    with pytest.raises(ValueError) as err:
        validate_required_fields(data, required_fields)

    assert str(err.value) == "Missing required GTFS field: route_id"
