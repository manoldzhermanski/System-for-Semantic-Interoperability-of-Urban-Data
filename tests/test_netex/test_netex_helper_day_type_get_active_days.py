import pytest
from netex.netex_utils import netex_helper_day_type_get_active_days

@pytest.mark.parametrize("entity_input, expected_output", [
    # Everyday
    (
        {"monday": {"value": 1}, "tuesday": {"value": 1}, "wednesday": {"value": 1},
         "thursday": {"value": 1}, "friday": {"value": 1}, "saturday": {"value": 1},
         "sunday": {"value": 1}},
        "Everyday"
    ),
    # Weekdays
    (
        {"monday": {"value": 1}, "tuesday": {"value": 1}, "wednesday": {"value": 1},
         "thursday": {"value": 1}, "friday": {"value": 1}, "saturday": {"value": 0},
         "sunday": {"value": 0}},
        "Weekdays"
    ),
    # Weekdays (with different order and missing keys)
    (
        {"friday": {"value": 1}, "tuesday": {"value": 1}, "monday": {"value": 1},
         "wednesday": {"value": 1}, "thursday": {"value": 1}},
        "Weekdays"
    ),
    # Weekend
    (
        {"saturday": {"value": 1}, "sunday": {"value": 1}, "monday": {"value": 0}},
        "Weekend"
    ),
    # Specific single day
    (
        {"wednesday": {"value": 1}},
        "Wednesday"
    ),
    # Specific multiple days (e.g., Tuesday and Thursday)
    (
        {"tuesday": {"value": 1}, "thursday": {"value": 1}, "monday": {"value": 0}},
        "Tuesday Thursday" # Order depends on days_map in the function
    ),
    # No active days (all zeros)
    (
        {"monday": {"value": 0}, "tuesday": {"value": 0}, "wednesday": {"value": 0},
         "thursday": {"value": 0}, "friday": {"value": 0}, "saturday": {"value": 0},
         "sunday": {"value": 0}},
        ""
    ),
    # Empty input dictionary
    (
        {},
        ""
    ),
    # Malformed entity (missing 'value' key)
    (
        {"monday": {}},
        ""
    ),
    # Malformed entity (value is not 1)
    (
        {"tuesday": {"value": "true"}, "wednesday": {"value": 1}},
        "Wednesday"
    ),
    # Mixed active and inactive
    (
        {"monday": {"value": 1}, "saturday": {"value": 1}},
        "Monday Saturday"
    )
])
def test_netex_helper_day_type_get_active_days_different_use_cases(entity_input, expected_output):
    """
    Tests the netex_helper_day_type_get_active_days function with various inputs.
    """
    assert netex_helper_day_type_get_active_days(entity_input) == expected_output
