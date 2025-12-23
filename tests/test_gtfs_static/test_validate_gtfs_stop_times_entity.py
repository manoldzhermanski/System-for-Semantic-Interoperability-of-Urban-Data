import pytest
from gtfs_static.gtfs_static_utils import validate_gtfs_stop_times_entity

def test_validate_gtfs_stop_times_entity_fields_valid_arrival_departure():
    """
    Check that if for a valid entity is given, the validation passes
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }
    
    validate_gtfs_stop_times_entity(entity)
    
def test_validate_gtfs_stop_times_entity_fields_valid_pickup_drop_off_window():
    """
    Check that if for a valid entity is given, the validation passes
    """
    entity = {
        "trip_id": "trip_1",
        "location_group_id": "LG1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "start_pickup_drop_off_window": "08:00:00",
        "end_pickup_drop_off_window": "09:00:00",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 0,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }
    
    validate_gtfs_stop_times_entity(entity)

def test_validate_gtfs_stop_times_missing_required_field():
    """
    Check that if 'trip_id' is missing, ValueError is raised
    """
    entity = {
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }
    
    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert "Missing required GTFS field" in str(err.value)

def test_validate_gtfs_stop_times_entity_optional_fields_none():
    """
    Check that if optinal fields have None as a value, the validation passes
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": None,
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": None,
        "timepoint": None,
        "pickup_booking_rule_id": None,
        "drop_off_booking_rule_id": None
    }
    
    validate_gtfs_stop_times_entity(entity)
    
def test_validate_gtfs_stop_times_invalid_timepoint():
    """
    Check that invalid value for 'timepoint' raises ValueError
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 2,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }
    
    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "'timepoint' should be 0 or 1, got" in str(err.value)
    
def test_validate_gtfs_stop_times_arrival_and_pickup_window_together_forbidden():
    """
    Check that if the 2 time groups ('arrival_time'/'departure_time') and ('start_pickup_drop_off_window'/
    'end_pickup_drop_off_window') are defined, ValueError is raised
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "start_pickup_drop_off_window": "08:00:00",
        "end_pickup_drop_off_window": "09:00:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "cannot be defined at the same time" in str(err.value)
    
def test_validate_gtfs_stop_times_no_time_information_defined():
    """
    Check that if the 2 time groups ('arrival_time'/'departure_time') and ('start_pickup_drop_off_window'/
    'end_pickup_drop_off_window') are missing, ValueError is raised
    """
    entity = {
        "trip_id": "trip_1",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 0,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "must be defined" in str(err.value)
    
def test_validate_gtfs_stop_times_more_than_one_location_identifier():
    """
    Check that if more than 1 location identifiers is defined ('stop_id', 'location_group_id', 'location_id'),
    a ValueError is raised
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "location_id":"L1",
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "Exactly one" in str(err.value)
    
def test_validate_gtfs_stop_times_none_location_identifier():
    """
    Check that if 'stop_id', 'location_group_id' and 'location_id' are missing, ValueError is raised
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "Exactly one" in str(err.value)

def test_validate_gtfs_stop_times_location_id_requires_pickup_window():
    """
    Check that if "location_id" or "location_group_id" is defined and "start_pickup_drop_off_window"
    and "end_pickup_drop_off_window" are missing, a ValueError is raised
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "location_id": "L1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert "are required when using location_id or location_group_id" in str(err.value)

def test_validate_gtfs_stop_times_timepoint_1_requires_times():
    """
    Check that if 'timepoint' is 1 and 'arrival_time' or 'departure_time' is missing, ValueError is raised
    """
    entity = {
    "trip_id": "trip_1",
    "departure_time": "08:05:00",
    "stop_id": "S1",
    "stop_sequence": 1,
    "stop_headsign": "STOP1",
    "pickup_type": 1,
    "drop_off_type": 1,
    "continuous_pickup": 1,
    "continuous_drop_off": 1,
    "shape_dist_traveled": 0.0,
    "timepoint": 1,
    "pickup_booking_rule_id": "PBR1",
    "drop_off_booking_rule_id": "DBR1"
}

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "arrival_time and departure_time are required when timepoint = 1" in str(err.value)
    
def test_validate_gtfs_stop_times_invalid_pickup_type_value():
    """
    Check that invalid value for 'pickup_type' raises ValueError
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 4,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }
    
    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)

    assert "must be 0, 1, 2 or 3, got" in str(err.value)

def test_validate_gtfs_stop_times_pickup_type_forbidden_with_location():
    """
    Check that if location_group_id or location_id is defined and 'pickup_type' has a value
    of 0 or 3, ValueError is raised
    """
    entity = {
        "trip_id": "trip_1",
        "location_id": "L1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "start_pickup_drop_off_window": "08:00:00",
        "end_pickup_drop_off_window": "09:00:00",
        "pickup_type": 3,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 0,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert "cannot be 0 or 3 when using location_group_id or location_id" in str(err.value)

def test_validate_gtfs_stop_times_invalid_drop_off_type_value():
    """
    Check that invalid value for 'continuous_drop_off' raises ValueError
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": -1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert " must be 0, 1, 2 or 3, got" in str(err.value)

def test_validate_gtfs_stop_times_invalid_continuous_pickup():
    """
    Check that invalid value for 'continuous_pickup' raises ValueError
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 4,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 0.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert " must be 0, 1, 2 or 3, got" in str(err.value)

def test_validate_gtfs_stop_times_continuous_pickup_forbidden_with_location():
    """
    Check that if location_group_id or location_id is defined and 'continuous_pickup' has a value
    other than 1, ValueError is raised
    """
    entity = {
    "trip_id": "trip_1",
    "location_group_id": "LG1",
    "stop_sequence": 1,
    "stop_headsign": "STOP1",
    "start_pickup_drop_off_window": "08:00:00",
    "end_pickup_drop_off_window": "08:05:00",
    "pickup_type": 1,
    "drop_off_type": 1,
    "continuous_pickup": 0,
    "continuous_drop_off": 1,
    "shape_dist_traveled": 0.0,
    "timepoint": 0,
    "pickup_booking_rule_id": "PBR1",
    "drop_off_booking_rule_id": "DBR1"
}

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert "cannot be 0, 2 or 3 when using location_group_id or location_id" in str(err.value)

def test_validate_gtfs_stop_times_negative_shape_dist_traveled():
    """
    Check that if shape_dist_traveled is not a non-negative float, a ValueError is raised.
    """
    entity = {
        "trip_id": "trip_1",
        "arrival_time": "08:00:00",
        "departure_time": "08:05:00",
        "stop_id": "S1",
        "stop_sequence": 1,
        "stop_headsign": "STOP1",
        "pickup_type": 1,
        "drop_off_type": 1,
        "continuous_pickup": 1,
        "continuous_drop_off": 1,
        "shape_dist_traveled": -1.0,
        "timepoint": 1,
        "pickup_booking_rule_id": "PBR1",
        "drop_off_booking_rule_id": "DBR1"
    }

    with pytest.raises(ValueError) as err:
        validate_gtfs_stop_times_entity(entity)
        
    assert "should be a non-negative float" in str(err.value)
