from orion_ld.orion_ld_crud_operations import orion_ld_get_attribute_values_from_etities
from unittest.mock import patch, MagicMock
import requests
import pytest

headers = {"Content-Type": "application/ld+json"}

def test_get_attribute_values_success():
    entity_ids = [
        "urn:ngsi-ld:Test:1",
        "urn:ngsi-ld:Test:2",
    ]
    attributes = ["name", "speed"]

    sample_response = [
        {
            "id": "urn:ngsi-ld:Test:1",
            "type": "Test",
            "name": {"type": "Property", "value": "A"},
            "speed": {"type": "Property", "value": 50},
        },
        {
            "id": "urn:ngsi-ld:Test:2",
            "type": "Test",
            "name": {"type": "Property", "value": "B"},
            "speed": {"type": "Property", "value": 60},
        }
    ]

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_response

    with patch("orion_ld.orion_ld_crud_operations.requests.get",return_value=mock_response):
        result = orion_ld_get_attribute_values_from_etities(entity_ids, attributes, headers)

    assert result == sample_response

def test_get_attribute_values_http_error():

    with patch("orion_ld.orion_ld_crud_operations.requests.get", side_effect=requests.exceptions.HTTPError("Bad Request")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            orion_ld_get_attribute_values_from_etities(["urn:ngsi-ld:Test:1"], ["name"], headers)

    assert "Bad Request" in str(err.value)

def test_get_attribute_values_timeout():
    
    with patch("orion_ld.orion_ld_crud_operations.requests.get", side_effect=requests.exceptions.Timeout("timeout")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            orion_ld_get_attribute_values_from_etities(["urn:ngsi-ld:Test:1"], ["name"], headers)

    assert "timeout" in str(err.value)
