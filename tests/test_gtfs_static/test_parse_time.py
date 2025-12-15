import pytest
from gtfs_static.gtfs_static_utils import parse_time

def test_parse_time_valid_time():
    """
    Check that a valid time is given as input, it's properly parsed
    """
    assert parse_time("12:34:56", "arrival_time") == "12:34:56"


def test_parse_time_single_digit_hour():
    """
    Check if valid hours,minutes and seconds are gived, leading zeros are added
    """
    assert parse_time("2:5:3", "arrival_time") == "02:05:03"


def test_parse_time_hours_over_24():
    """
    Check that hours above 25 are accepted
    """
    assert parse_time("25:35:00", "arrival_time") == "25:35:00"


def test_parse_time_with_whitespace():
    """
    Check that white spaces are trimmed
    """
    assert parse_time(" 01:02:03 ", "arrival_time") == "01:02:03"


def test_parse_time_none_raises_error():
    """
    Check that if None value is given as input, ValueError is raised
    """
    with pytest.raises(ValueError) as exc:
        parse_time(None, "arrival_time")

    assert str(exc.value) == "arrival_time cannot be empty"


def test_parse_time_empty_string_raises_error():
    """Check that an empty string is given as input, ValueError is raised"""
    with pytest.raises(ValueError) as err:
        parse_time("", "arrival_time")

    assert str(err.value) == "arrival_time cannot be empty"


def test_parse_time_invalid_format_raises_error():
    """
    Check that if the time string is not in the HH:MM:SS format, ValueError is raised
    """
    with pytest.raises(ValueError) as err:
        parse_time("12:34", "arrival_time")

    assert str(err.value) == "arrival_time must be in HH:MM:SS format, got '12:34'"


def test_parse_time_invalid_minutes_raises_error():
    """
    Check that if the seconds are >= 60, ValueError is raised
    """
    with pytest.raises(ValueError) as err:
        parse_time("10:60:00", "arrival_time")

    assert str(err.value) == (
        "arrival_time must be a valid time in HH:MM:SS format, got '10:60:00'"
    )


def test_parse_time_invalid_seconds_raises_error():
    """
    Check that if the seconds are >= 60, ValueError is raised
    """

    with pytest.raises(ValueError) as err:
        parse_time("10:00:60", "arrival_time")

    assert str(err.value) == (
        "arrival_time must be a valid time in HH:MM:SS format, got '10:00:60'"
    )


def test_parse_time_negative_hours_raises_error():
    """
    Check that negative hours raise ValueError
    """

    with pytest.raises(ValueError) as err:
        parse_time("-1:00:00", "arrival_time")

    assert str(err.value) == (
        "arrival_time must be a valid time in HH:MM:SS format, got '-1:00:00'"
    )


def test_parse_time_non_numeric_raises_error():
    """
    Check that non-numeric values are given, a ValueError is raised
    """

    with pytest.raises(ValueError) as err:
        parse_time("aa:bb:cc", "arrival_time")

    assert str(err.value) == (
        "arrival_time must be a valid time in HH:MM:SS format, got 'aa:bb:cc'"
    )
