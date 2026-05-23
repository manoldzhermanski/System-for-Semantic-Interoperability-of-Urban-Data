import pytest
import config
from netex.netex_utils import netex_helper_set_operating_city


def test_set_operating_city_valid():
    netex_helper_set_operating_city("Sofia")

    assert config.NETEX_OPERATING_CITY == "Sofia"


def test_set_operating_city_strips_whitespace():
    netex_helper_set_operating_city("  Sofia  ")

    assert config.NETEX_OPERATING_CITY == "Sofia"


def test_set_operating_city_title_case():
    netex_helper_set_operating_city("sofia")

    assert config.NETEX_OPERATING_CITY == "Sofia"


def test_set_operating_city_non_string():
    with pytest.raises(TypeError):
        netex_helper_set_operating_city(123)


def test_set_operating_city_empty_string():
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("")


def test_set_operating_city_whitespace_only():
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("    ")


def test_set_operating_city_invalid_characters():
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("Sofia:West")


def test_set_operating_city_invalid_numbers():
    with pytest.raises(ValueError):
        netex_helper_set_operating_city("Sofia2025")