import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_transfers_entity
    
def test_validate_gtfs_transfers_entity_all_fields_valid():
    """
    Check that all fields are provided and valid, the validation passes
    """
    entity = {
        "transfer_type": 1,
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": 120
    }

    validate_gtfs_transfers_entity(entity)

def test_validate_gtfs_transfers_entity_missing_required_field():
    """
    Check that a missing required field raises ValueError
    """
    entity = {
        "transfer_type": None,
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": 120
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_transfers_entity(entity)
        
    assert "Missing required GTFS field" in str(err.value)

def test_validate_gtfs_transfers_entity_type_1_missing_from_stop_id():
    """
    Check that if 'transfer_type' is 1 and 'from_stop_id' is None, ValueError is raised
    """
    entity = {
        "transfer_type": 1,
        "from_stop_id": None,
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": 120
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_transfers_entity(entity)
        
    assert "is required when transfer_type is 1, 2 or 3" in str(err.value)
    
def test_validate_gtfs_transfers_entity_type_1_missing_to_stop_id():
    """
    Check that if 'transfer_type' is 1 and 'to_stop_id' is None, ValueError is raised
    """
    entity = {
        "transfer_type": 1,
        "from_stop_id": "S1",
        "to_stop_id": None,
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": 120
    }
    
    with pytest.raises(ValueError) as err:
        validate_gtfs_transfers_entity(entity)
        
    assert "is required when transfer_type is 1, 2 or 3" in str(err.value)

def test_validate_gtfs_transfers_entity_type_4_missing_from_trip_id():
    """
    Check that if 'transfer_type' is 4 and 'from_trip_id' is None, ValueError is raised
    """
    entity = {
        "transfer_type": 4,
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": None,
        "to_trip_id": "T2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": 120
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_transfers_entity(entity)
        
    assert "is required when transfer_type is 4 or 5" in str(err.value)

def test_validate_gtfs_transfers_entity_type_4_missing_to_trip_id():
    """
    Check that if 'transfer_type' is 4 and 'to_trip_id' is None, ValueError is raised
    """
    entity = {
        "transfer_type": 4,
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": None,
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": 120
    }
    
    with pytest.raises(ValueError) as err:
        validate_gtfs_transfers_entity(entity)
        
    assert "is required when transfer_type is 4 or 5" in str(err.value)

def test_validate_gtfs_transfers_entity_negative_min_transfer_time():
    """
    Check that if 'min_transfer_time' is not a non-negative integer, ValueError is raised
    """
    entity = {
        "transfer_type": 1,
        "from_stop_id": "S1",
        "to_stop_id": "S2",
        "from_trip_id": "T1",
        "to_trip_id": "T2",
        "from_route_id": "R1",
        "to_route_id": "R2",
        "min_transfer_time": -1
    }
    
    with pytest.raises(ValueError) as err:
        validate_gtfs_transfers_entity(entity)

    assert "must be a non-negative integer, got" in str(err.value)