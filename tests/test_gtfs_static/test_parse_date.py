import pytest
from gtfs_static.gtfs_static_utils import parse_date

def test_parse_date_valid_date():
    assert parse_date("20240131", "start_date") == "20240131"


def test_parse_date_valid_date_with_spaces():
    assert parse_date(" 20231205 ", "start_date") == "20231205"


def test_parse_date_none_value_as_input():
    assert parse_date(None, "start_date") is None


def test_parse_date_empty_string_raises_value_error():
    assert parse_date("", "start_date") is None


def test_parse_date_invalid_format_raises_value_error():
    with pytest.raises(ValueError) as exc:
        parse_date("2023-01-01", "start_date")

    assert str(exc.value) == "start_date must be a valid date in YYYYMMDD format, got '2023-01-01'"


def test_parse_date_invalid_date_raises_value_error():
    with pytest.raises(ValueError) as exc:
        parse_date("20230231", "start_date")

    assert str(exc.value) == "start_date must be a valid date in YYYYMMDD format, got '20230231'"
