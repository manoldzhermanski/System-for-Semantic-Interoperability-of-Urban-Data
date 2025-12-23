import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_shapes_entity

def test_validate_gtfs_shapes_validate_shapes_all_fields_valid():
    entity = {
        "shape_id": "S1",
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": 0,
        "shape_dist_traveled": 12.5,
    }

    validate_gtfs_shapes_entity(entity)

def test_validate_shapes_missing_required_field():
    entity = {
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": 0,
        "shape_dist_traveled": 12.5,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_shapes_entity(entity)
        
    assert "Missing required GTFS field" in str(err.value)

def test_validate_gtfs_shapes_entity_optional_fields_none():
    """
    Check that if optinal fields have None as a value, the validation passes
    """
    entity = {
        "shape_id": "S1",
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": 0,
        "shape_dist_traveled": None,
    }

    validate_gtfs_shapes_entity(entity)

def test_validate_shapes_negative_shape_pt_sequence():
    entity = {
        "shape_id": "S1",
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": -1,
        "shape_dist_traveled": 12.5,
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_shapes_entity(entity)

    assert "'shape_pt_sequence' must be a non-negative integer" in str(err.value)

def test_validate_shapes_negative_dist_traveled():
    entity = {
        "shape_id": "S1",
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": 0,
        "shape_dist_traveled": -1.0,
    }
    with pytest.raises(ValueError) as err:
        validate_gtfs_shapes_entity(entity)

    assert "'shape_dist_traveled' must be a non-negative float" in str(err.value)
