import pytest
import config
from gtfs_realtime.gtfs_realtime_utils import to_ngsi_ld_urn


def test_to_ngsi_ld_urn_valid_urn():
    config.set_operating_city("Sofia")
    assert to_ngsi_ld_urn("123", "Device") == f"urn:ngsi-ld:Device:{config.get_operating_city()}:123"

def test_to_ngsi_ld_urn_valid_urn_with_alphanumeric_value():
    config.set_operating_city("Sofia")
    assert to_ngsi_ld_urn("Device_01", "Sensor") == f"urn:ngsi-ld:Sensor:{config.get_operating_city()}:Device_01"

def test_to_ngsi_ld_urn_none_value_returns_none():
    assert to_ngsi_ld_urn(None, "Device") is None
    
def test_to_ngsi_ld_urn_empty_string_as_value_raises_value_error():
    with pytest.raises(ValueError):
        to_ngsi_ld_urn("", "Device")
        
def test_to_ngsi_ld_urn_empty_string_as_entity_type_raises_value_error():
    with pytest.raises(ValueError):
        to_ngsi_ld_urn("123", "")

def test_to_ngsi_ld_urn_whitespace_string_as_entity_type_raises_value_error():
    with pytest.raises(ValueError):
        to_ngsi_ld_urn("123", "   ")

