import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_trips_entity

def test_validate_gtfs_trips_entity_all_fields_valid():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "route_id": "R1",
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 1,
        "block_id": "B1",
        "shape_id": "SH1",
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0
    }

    validate_gtfs_trips_entity(entity)

def test_validate_gtfs_trips_entity_missing_required_field():
    """
    Check that if a required field is missing, ValueError is raised
    """
    entity = {
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 1,
        "block_id": "B1",
        "shape_id": "SH1",
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_trips_entity(entity)

    assert "Missing required GTFS field" in str(err.value)

def test_validate_gtfs_trips_entity_none_value_as_required_field():
    """
    Check that if a required field has a None value, ValueError is raised
    """
    entity = {
        "route_id": None,
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 1,
        "block_id": "B1",
        "shape_id": "SH1",
        "wheelchair_accessible": 1,
        "bikes_allowed": 2,
        "cars_allowed": 0
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_trips_entity(entity)

    assert "Missing required GTFS field" in str(err.value)

def test_validate_gtfs_trips_entity_optional_fields_none():
    """
    Check that if optinal fields have None as a value, the validation passes
    """
    entity = {
        "route_id": "R1",
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": None,
        "block_id": None,
        "shape_id": None,
        "wheelchair_accessible": None,
        "bikes_allowed": None,
        "cars_allowed": None
    }

    validate_gtfs_trips_entity(entity)

def test_validate_gtfs_trips_entity_invalid_direction_id():
    """
    Check that invalid value for 'direction_id' raises ValueError
    """
    entity = {
        "route_id": "R1",
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 2,
        "wheelchair_accessible": 0,
        "bikes_allowed": 0,
        "cars_allowed": 0
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_trips_entity(entity)

    assert "'direction_id' must be" in str(err.value)

def test_validate_gtfs_trips_entity_invalid_wheelchair_accessible():
    """
    Check that invalid value for 'wheelchair_accessible' raises ValueError
    """
    entity = {
        "route_id": "R1",
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 1,
        "wheelchair_accessible": 3,
        "bikes_allowed": 0,
        "cars_allowed": 0
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_trips_entity(entity)

    assert "'wheelchair_accessible' must be" in str(err.value)

def test_validate_gtfs_trips_entity_invalid_bikes_allowed():
    """
    Check that invalid value for 'bikes_allowed' raises ValueError
    """

    entity = {
        "route_id": "R1",
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 1,
        "wheelchair_accessible": 0,
        "bikes_allowed": 3,
        "cars_allowed": 0
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_trips_entity(entity)

    assert "'bikes_allowed' must be" in str(err.value)

def test_validate_gtfs_trips_entity_invalid_cars_allowed():
    """
    Check that invalid value for 'cars_allowed' raises ValueError
    """
    entity = {
        "route_id": "R1",
        "service_id": "S1",
        "trip_id": "T1",
        "direction_id": 1,
        "wheelchair_accessible": 0,
        "bikes_allowed": 0,
        "cars_allowed": 3
    }
    with pytest.raises(ValueError) as err:
        validate_gtfs_trips_entity(entity)

    assert "'cars_allowed' must be" in str(err.value)

