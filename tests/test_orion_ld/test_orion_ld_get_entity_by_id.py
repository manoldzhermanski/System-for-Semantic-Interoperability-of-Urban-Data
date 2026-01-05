import pytest
import requests
from unittest.mock import patch, MagicMock
from orion_ld.orion_ld_crud_operations import orion_ld_get_entity_by_id


def test_get_entity_success_with_unicode():
    """
    Test successful retrieval and unicode decoding of NGSI-LD entity.
    """
    headers = {"Content-Type": "application/ld+json"}

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.encoding = "utf-8"
    mock_response.json.return_value = {
        "id": "urn:ngsi-ld:Test:1",
        "type": "Test",
        "name": {
            "type": "Property",
            "value": "\\u041b\\u0438\\u043d\\u0438\\u044f 94"
        },
        "operatedBy": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Line:94"
        }
    }

    with patch("orion_ld.orion_ld_crud_operations.requests.get", return_value=mock_response):
        result = orion_ld_get_entity_by_id("urn:ngsi-ld:Test:1",headers)

    assert result["name"]["value"] == "Линия 94"
    assert result["operatedBy"]["object"] == "urn:ngsi-ld:Line:94"


def test_get_entity_http_error():
    """
    Test behavior when Orion-LD returns an HTTP error.
    """
    headers = {"Content-Type": "application/ld+json"}
    
    with patch("orion_ld.orion_ld_crud_operations.requests.get", side_effect=requests.exceptions.HTTPError("404 Not Found")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            orion_ld_get_entity_by_id("urn:ngsi-ld:NonExisting:1",headers)

    assert "404 Not Found" in str(err.value)


def test_get_entity_without_unicode():
    """
    Test entity retrieval when no unicode decoding is needed.
    """
    headers = {"Content-Type": "application/ld+json"}
    
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.encoding = "utf-8"
    mock_response.json.return_value = {
        "id": "urn:ngsi-ld:Test:1",
        "type": "Test",
        "count": {
            "type": "Property",
            "value": 1
        }
    }

    with patch("orion_ld.orion_ld_crud_operations.requests.get", return_value=mock_response):
        result = orion_ld_get_entity_by_id("urn:ngsi-ld:Simple:1", headers)

    assert result["count"]["value"] == 1
