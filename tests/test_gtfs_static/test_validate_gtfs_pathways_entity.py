import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_pathways_entity


def test_validate_gtfs_pathways_entity_all_valid_fields():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    validate_gtfs_pathways_entity(entity, city)

def test_validate_gtfs_pathways_entity_missing_required_field():
    """
    Check that if a required field is missing, ValueError is raised
    """
    entity = {
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "Missing required GTFS field:" in str(err.value)

def test_validate_gtfs_pathways_entity_optional_fields_none():
    """
    Check that if optinal fields have None as a value, the validation passes
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": None,
        "traversal_time": None,
        "stair_count": None,
        "max_slope": None,
        "min_width": None
    }
    
    city = "Sofia"

    validate_gtfs_pathways_entity(entity, city)

def test_validate_gtfs_pathways_entity_invalid_pathway_mode():
    """
    Check that invalid value for 'pathway_mode' raises ValueError
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 8,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'pathway_mode' has to be" in str(err.value)

def test_validate_gtfs_pathways_entity_invalid_is_bidirectional():
    """
    Check that invalid value for 'is_bidirectional' raises ValueError
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 2,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'is_bidirectional' has to be 0 or 1" in str(err.value)

def test_validate_gtfs_pathways_entity_pathway_mode_7_does_not_allow_is_bidirectional_1():
    """
    Check that if 'pathway_mode' is 7, 'is_bidirectional' cannot be 1
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 7,
        "is_bidirectional": 1,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "cannot be 1 when 'pathway_mode' is 7" in str(err.value)

def test_validate_gtfs_pathways_entity_negative_length():
    """
    Check that if 'length' < 0.0, ValueError is raised
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": -1.0,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'length' must be a non-negative float" in str(err.value)

def test_validate_gtfs_pathways_entity_zero_traversal_time():
    """
    Check that if 'traversal_time' <= 0, ValueError is raised
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 0,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'traversal_time' must be a positive integer" in str(err.value)

def test_validate_gtfs_pathways_entity_zero_stair_count():
    """
    Check that if 'stair_count' is 0, ValueError is raised
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 0,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'stair_count' must be a non-zero integer" in str(err.value)

def test_validate_gtfs_pathways_entity_max_slope_invalid_pathway_mode():
    """
    Check that if 'pathway_mode' isn't  or 3, 'max_slope' shouldn't be defined
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 2,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 1.2
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'max_slope' can only be defined" in str(err.value)

def test_validate_gtfs_pathways_entity_zero_min_width():
    """
    Check that if 'min_width' <= 0.0, ValueError is raised
    """
    entity = {
        "pathway_id": "P1",
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "pathway_mode": 1,
        "is_bidirectional": 0,
        "length": 10.5,
        "traversal_time": 30,
        "stair_count": 5,
        "max_slope": 0.1,
        "min_width": 0.0
    }
    
    city = "Sofia"

    with pytest.raises(ValueError) as err:
        validate_gtfs_pathways_entity(entity, city)

    assert "'min_width' must be a positive float" in str(err.value)


