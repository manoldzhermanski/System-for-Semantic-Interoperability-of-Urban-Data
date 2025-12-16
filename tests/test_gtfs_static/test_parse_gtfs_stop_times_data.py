import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_stop_times_data

def test_parse_gtfs_stop_times_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "trip_id": "T1",
        "arrival_time": "25:30:00",
        "departure_time": "25:35:00",
        "stop_id": "S1",
        "location_group_id": "LG1",
        "location_id": "L1",
        "stop_sequence": "5",
        "stop_headsign": "Center",
        "start_pickup_drop_off_window": "06:00:00",
        "end_pickup_drop_off_window": "22:00:00",
        "pickup_type": "0",
        "drop_off_type": "1",
        "continuous_pickup": "0",
        "continuous_drop_off": "1",
        "shape_dist_traveled": "12.5",
        "timepoint": "1",
        "pickup_booking_rule_id": "PR1",
        "drop_off_booking_rule_id": "DR1"
    }

    result = parse_gtfs_stop_times_data(entity)

    assert result == {
        "trip_id": "T1",
        "arrival_time": "25:30:00",
        "departure_time": "25:35:00",
        "stop_id": "S1",
        "location_group_id": "LG1",
        "location_id": "L1",
        "stop_sequence": 5,
        "stop_headsign": "Center",
        "start_pickup_drop_off_window": "06:00:00",
        "end_pickup_drop_off_window": "22:00:00",
        "pickup_type": 0,
        "drop_off_type": 1,
        "continuous_pickup": 0,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 12.5,
        "timepoint": 1,
        "pickup_booking_rule_id": "PR1",
        "drop_off_booking_rule_id": "DR1"
    }

def test_parse_gtfs_stop_times_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}

    result = parse_gtfs_stop_times_data(entity)

    assert result == {
        "trip_id": None,
        "arrival_time": None,
        "departure_time": None,
        "stop_id": None,
        "location_group_id": None,
        "location_id": None,
        "stop_sequence": None,
        "stop_headsign": None,
        "start_pickup_drop_off_window": None,
        "end_pickup_drop_off_window": None,
        "pickup_type": None,
        "drop_off_type": None,
        "continuous_pickup": None,
        "continuous_drop_off": None,
        "shape_dist_traveled": None,
        "timepoint": None,
        "pickup_booking_rule_id": None,
        "drop_off_booking_rule_id": None
    }

def test_parse_gtfs_stop_times_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "trip_id": " T1 ",
        "arrival_time": " 08:00:00 ",
        "stop_sequence": " 3 ",
        "shape_dist_traveled": " 5.5 "
    }

    result = parse_gtfs_stop_times_data(entity)

    assert result == {
        "trip_id": "T1",
        "arrival_time": "08:00:00",
        "departure_time": None,
        "stop_id": None,
        "location_group_id": None,
        "location_id": None,
        "stop_sequence": 3,
        "stop_headsign": None,
        "start_pickup_drop_off_window": None,
        "end_pickup_drop_off_window": None,
        "pickup_type": None,
        "drop_off_type": None,
        "continuous_pickup": None,
        "continuous_drop_off": None,
        "shape_dist_traveled": 5.5,
        "timepoint": None,
        "pickup_booking_rule_id": None,
        "drop_off_booking_rule_id": None
    }

def test_parse_gtfs_stop_times_data_invalid_arrival_time():
    """
    Check that if 'arrival_time' cannot be parsed to time, ValueError is raised
    """
    entity = {"arrival_time": "25:99:00"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stop_times_data(entity)
    assert "arrival_time must be a valid time" in str(err.value)

def test_parse_gtfs_stop_times_data_invalid_stop_sequence():
    """
    Check that if 'stop_sequence' cannot be parsed to integer, ValueError is raised
    """
    entity = {"stop_sequence": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stop_times_data(entity)
    assert str(err.value) == "stop_sequence must be integer, got 'abc'"

def test_parse_gtfs_stop_times_data_invalid_shape_dist_traveled():
    """
    Check that if 'shape_dist_traveled' cannot be parsed to float, ValueError is raised
    """
    entity = {"shape_dist_traveled": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_stop_times_data(entity)
    assert str(err.value) == "shape_dist_traveled must be float, got 'abc'"
