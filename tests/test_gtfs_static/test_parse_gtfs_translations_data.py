import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_translations_data

def test_parse_gtfs_translations_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "table_name": "route",
        "field_name": "long_name",
        "language": "en",
        "translation": "Route 1",
        "record_id": "R1",
        "record_sub_id": "",
        "field_value": "Route 1"
    }
    
    result = parse_gtfs_translations_data(entity)
    
    assert result == {
        "table_name": "route",
        "field_name": "long_name",
        "language": "en",
        "translation": "Route_1",
        "record_id": "R1",
        "record_sub_id": None,
        "field_value": "Route_1"
    }
    
def test_parse_gtfs_translations_data_missing_fields():
    """
    Check that if a field is missing, None value is assigned
    """
    entity = {}
    
    result = parse_gtfs_translations_data(entity)
    
    assert result == {
        "table_name": None,
        "field_name": None,
        "language": None,
        "translation": None,
        "record_id": None,
        "record_sub_id": None,
        "field_value": None
    }
    
def test_parse_gtfs_translations_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "table_name": "  route",
        "field_name": "long_name  ",
        "language": "  en  ",
        "translation": "  Route 1",
        "record_id": "R1 ",
        "record_sub_id": " ",
        "field_value": "Route 1  "
    }
    
    result = parse_gtfs_translations_data(entity)
    
    assert result == {
        "table_name": "route",
        "field_name": "long_name",
        "language": "en",
        "translation": "Route_1",
        "record_id": "R1",
        "record_sub_id": None,
        "field_value": "Route_1"
    }