from gtfs_realtime.gtfs_realtime_utils import to_snake_case

def test_to_snake_case_pascal_case():
    """
    Check that PascalCase is converted to snake_case
    """
    assert to_snake_case("ActivePeriod") == "active_period"

def test_to_snake_case_camel_case():
    """
    Check that camelCase is converted to snake_case
    """
    assert to_snake_case("activePeriod") == "active_period"

def test_to_snake_case_already_snake_case():
    """
    Check that snake_case stays unmodified
    """
    assert to_snake_case("active_period") == "active_period"

def test_to_snake_case_with_numbers():
    """
    Check that if a digit is present in the text,
    it's part of the first string in the snake_case
    """
    assert to_snake_case("Route2Direction") == "route2_direction"

def test_to_snake_case_empty_string():
    """
    Check that if an empty string is given as input, a empty string is retured
    """
    assert to_snake_case("") == ""
