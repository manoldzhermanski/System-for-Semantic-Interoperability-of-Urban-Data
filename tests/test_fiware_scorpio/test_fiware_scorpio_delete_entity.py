import pytest
import requests
from unittest.mock import patch, MagicMock

from fiware_scorpio.fiware_scorpio_crud_operations import fiware_scorpio_delete_entity

headers = {"Content-Type": "application/ld+json"}
entity_id = "urn:ngsi-ld:Test:1"

def test_delete_entity_success():
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.delete", return_value=mock_response):
        fiware_scorpio_delete_entity(entity_id, headers)

def test_delete_entity_http_error():

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.delete", side_effect=requests.exceptions.HTTPError("Not Found")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            fiware_scorpio_delete_entity(entity_id, headers)

    assert "Not Found" in str(err.value)

def test_delete_entity_timeout():
    
    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.delete", side_effect=requests.exceptions.Timeout("timeout")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            fiware_scorpio_delete_entity(entity_id, headers)

    assert "timeout" in str(err.value)
