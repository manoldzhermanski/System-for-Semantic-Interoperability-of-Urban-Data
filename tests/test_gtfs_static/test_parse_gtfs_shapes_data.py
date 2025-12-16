import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_shapes_data

def test_parse_gtfs_shapes_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "shape_id": "S1",
        "shape_pt_lat": "42.6977",
        "shape_pt_lon": "23.3219",
        "shape_pt_sequence": "1",
        "shape_dist_traveled": "12.5"
    }

    result = parse_gtfs_shapes_data(entity)

    assert result == {
        "shape_id": "S1",
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": 1,
        "shape_dist_traveled": 12.5
    }

def test_parse_gtfs_shapes_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}
    result = parse_gtfs_shapes_data(entity)

    assert result == {
        "shape_id": None,
        "shape_pt_lat": None,
        "shape_pt_lon": None,
        "shape_pt_sequence": None,
        "shape_dist_traveled": None
    }

def test_parse_gtfs_shapes_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "shape_id": " S1 ",
        "shape_pt_lat": " 42.6977 ",
        "shape_pt_lon": " 23.3219 ",
        "shape_pt_sequence": " 1 ",
        "shape_dist_traveled": " 12.5 "
    }

    result = parse_gtfs_shapes_data(entity)

    assert result == {
        "shape_id":"S1",
        "shape_pt_lat": 42.6977,
        "shape_pt_lon": 23.3219,
        "shape_pt_sequence": 1,
        "shape_dist_traveled": 12.5
    }

def test_parse_gtfs_shapes_data_invalid_shape_pt_lat_raises_error():
    """
    Check that if 'shape_pt_lat' cannot be parsed to float, ValueError is raised
    """
    entity = {"shape_pt_lat": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_shapes_data(entity)
    assert str(err.value) == "shape_pt_lat must be float, got 'abc'"

def test_parse_gtfs_shapes_data_invalid_shape_pt_lon_raises_error():
    """
    Check that if 'shape_pt_lon' cannot be parsed to float, ValueError is raised
    """
    entity = {"shape_pt_lon": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_shapes_data(entity)
    assert str(err.value) == "shape_pt_lon must be float, got 'abc'"

def test_parse_gtfs_shapes_data_invalid_shape_pt_sequence_raises_error():
    """
    Check that if 'shape_pt_sequence' cannot be parsed to integer, ValueError is raised
    """
    entity = {"shape_pt_sequence": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_shapes_data(entity)
    assert str(err.value) == "shape_pt_sequence must be integer, got 'abc'"

def test_parse_gtfs_shapes_data_invalid_shape_dist_traveled_raises_error():
    """
    Check that if 'shape_dist_traveled' cannot be parsed to float, ValueError is raised
    """
    entity = {"shape_dist_traveled": "abc"}
    with pytest.raises(ValueError) as err:
        parse_gtfs_shapes_data(entity)
    assert str(err.value) == "shape_dist_traveled must be float, got 'abc'"
