import pytest
from gtfs_static.gtfs_static_utils import parse_gtfs_agency_data

def test_parse_gtfs_agency_data_all_fields_present():
    """
    Check that if all fields are provided with data, they are parsed correctly
    """
    entity = {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "bg",
        "agency_phone": "+359123456",
        "agency_fare_url": "https://example.com/fare",
        "agency_email": "info@example.com",
        "cemv_support": "1",
    }

    result = parse_gtfs_agency_data(entity)

    assert result == {
        "agency_id": "AG1",
        "agency_name": "Test Agency",
        "agency_url": "https://example.com",
        "agency_timezone": "Europe/Sofia",
        "agency_lang": "bg",
        "agency_phone": "+359123456",
        "agency_fare_url": "https://example.com/fare",
        "agency_email": "info@example.com",
        "cemv_support": 1,
    }


def test_parse_gtfs_agency_data_missing_optional_fields():
    """
    Check that if a field is missing, None value is assigned
    """

    entity = {}

    result = parse_gtfs_agency_data(entity)

    assert result == {
        "agency_id": None,
        "agency_name": None,
        "agency_url": None,
        "agency_timezone": None,
        "agency_lang": None,
        "agency_phone": None,
        "agency_fare_url": None,
        "agency_email": None,
        "cemv_support": None,
    }


def test_parse_gtfs_agency_data_whitespace_cleanup():
    """
    Check that white spaces are trimmed
    """
    entity = {
        "agency_id": "  AG1  ",
        "agency_name": "  Test Agency ",
        "cemv_support": " 0 ",
    }

    result = parse_gtfs_agency_data(entity)

    assert result["agency_id"] == "AG1"
    assert result["agency_name"] == "Test Agency"
    assert result["cemv_support"] == 0


def test_parse_gtfs_agency_data_invalid_cemv_support_raises_error():
    """Check that if 'cemv_support' cannot be parsed to int, ValueError is raised"""
    entity = {
        "agency_name": "Test Agency",
        "cemv_support": "abc",
    }

    with pytest.raises(ValueError) as err:
        parse_gtfs_agency_data(entity)

    assert str(err.value) == "cemv_support must be integer, got 'abc'"
