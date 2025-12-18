import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_levels_entity

def test_validate_gtfs_levels_entity_all_valid_fields():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "level_id": "L1",
        "level_index": 2.0,
        "level_name": "Second Floor"
    }

    validate_gtfs_levels_entity(entity)

def test_validate_gtfs_levels_entity_missing_required_field():
    """
    Check that if a required field is missing, a ValueError is raised
    """
    entity = {
        "level_index": 2.0,
        "level_name": "Second Floor"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_levels_entity(entity)
    
    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_levels_entity_none_value_as_required_field():
    """
    Check that if a required field has None as a value, ValueError is raised
    """
    entity = {
        "level_id": None,
        "level_index": 2.0,
        "level_name": "Second Floor"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_levels_entity(entity)
    
    assert "Missing required GTFS field:" in str(err.value)