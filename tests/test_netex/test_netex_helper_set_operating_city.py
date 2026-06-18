import pytest
import config
from netex.netex_utils import netex_helper_set_operating_city


def test_netex_helper_set_operating_city_happy_path():
    """
    Test that the operating city candidate fits the defined set of rules
    """
    netex_helper_set_operating_city("Sofia")

    assert config.NETEX_OPERATING_CITY == "Sofia"

def test_netex_helper_set_operating_city_2_word_city():
    """
    Test that if the operating city candidate is named with 2 or more words, they are conneted with underscore
    """
    netex_helper_set_operating_city("Veliko Turnovo")

    assert config.NETEX_OPERATING_CITY == "Veliko_Turnovo"

def test_netex_helper_set_operating_city_dash_connect():
    """
    Test that the operating city candidate is named with 2 or more words,
    connected with dashes, the are replaced with underscores
    """
    netex_helper_set_operating_city("Veliko-Turnovo")

    assert config.NETEX_OPERATING_CITY == "Veliko_Turnovo"

def test_netex_helper_set_operating_city_dash_connect():
    """
    Test that the operating city candidate is named with 2 or more words, connected with a underscore, it's accepted
    """
    netex_helper_set_operating_city("Veliko_Turnovo")

    assert config.NETEX_OPERATING_CITY == "Veliko_Turnovo"

def test_netex_helper_set_operating_city_strips_whitespace():
    """
    Test that surrounding white spaces are remvoed
    """
    netex_helper_set_operating_city("  Sofia  ")

    assert config.NETEX_OPERATING_CITY == "Sofia"


def test_netex_helper_set_operating_city_title_case():
    """
    Test that if operating city is with lower case letters, they are turned to title case
    """
    netex_helper_set_operating_city("sofia")

    assert config.NETEX_OPERATING_CITY == "Sofia"


def test_netex_helper_set_operating_city_non_string():
    """
    Test that numeric input is not accepted
    """
    with pytest.raises(TypeError):
        netex_helper_set_operating_city(123)


def test_netex_helper_set_operating_city_empty_string():
    """
    Test that empty string is not accepted
    """
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("")


def test_netex_helper_set_operating_city_whitespace_only():
    """
    Test that white spaces only are not accepted
    """
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("    ")


def test_netex_helper_set_operating_city_invalid_characters():
    """
    Test that only the underscore and dash are accepted for connecting words that form a city name
    """
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("Sofia:West")


def test_set_operating_city_invalid_numbers():
    """
    Test that a name containing numbers is not accepted
    """
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("Sofia2025")