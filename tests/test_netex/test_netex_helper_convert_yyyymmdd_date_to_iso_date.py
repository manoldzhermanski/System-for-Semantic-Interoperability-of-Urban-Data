import pytest
from netex.netex_utils import netex_helper_convert_yyyymmdd_date_to_iso_date

def test_valid_date_conversion():
    """Tests the conversion of a standard, valid date string."""
    assert netex_helper_convert_yyyymmdd_date_to_iso_date("20260414") == "2026-04-14T00:00:00"

def test_leap_year_date():
    """Tests the conversion of a valid leap year date."""
    assert netex_helper_convert_yyyymmdd_date_to_iso_date("20240229") == "2024-02-29T00:00:00"

def test_invalid_date_non_leap_year():
    """Tests that an invalid date (Feb 29 on a non-leap year) raises a ValueError."""
    with pytest.raises(ValueError):
        netex_helper_convert_yyyymmdd_date_to_iso_date("20230229")

def test_invalid_date_impossible_day():
    """Tests that an impossible date (e.g., day 32) raises a ValueError."""
    with pytest.raises(ValueError):
        netex_helper_convert_yyyymmdd_date_to_iso_date("20230132")
       
def test_invalid_format_with_separators():
    """Tests that a string containing non-digit characters raises a ValueError."""
    with pytest.raises(ValueError):
        netex_helper_convert_yyyymmdd_date_to_iso_date("2023-01-01")

@pytest.mark.parametrize("invalid_input", [None, 123, 3.14, True, 20230101, [], {}, (),])
def test_invalid_input_type(invalid_input):
    """Tests that non-string inputs raise the specific ValueError."""
    with pytest.raises(ValueError, match="Input must be a string in YYYYMMDD format."):
        netex_helper_convert_yyyymmdd_date_to_iso_date(invalid_input)

@pytest.mark.parametrize("invalid_length_str", ["2023", "2023010100"])
def test_invalid_length(invalid_length_str):
    """Tests that strings with incorrect length raise a ValueError."""
    with pytest.raises(ValueError, match="Input must be a string in YYYYMMDD format."):
        netex_helper_convert_yyyymmdd_date_to_iso_date(invalid_length_str)

