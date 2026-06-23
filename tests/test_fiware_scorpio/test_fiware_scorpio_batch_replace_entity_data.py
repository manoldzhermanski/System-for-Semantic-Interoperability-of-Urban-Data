import pytest
import requests
from unittest.mock import patch, MagicMock
from fiware_scorpio.fiware_scorpio_crud_operations import fiware_scorpio_batch_replace_entity_data

headers = {"Content-Type": "application/ld+json"}

sample_entities = [
    {
        "id": "urn:ngsi-ld:Test:1",
        "type": "Test",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
    },
    {
        "id": "urn:ngsi-ld:Test:2",
        "type": "Test",
        "@context": ["https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"]
    }
]

def test_batch_replace_success_201():
    mock_response = MagicMock()
    mock_response.status_code = 201

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", return_value=mock_response):
        fiware_scorpio_batch_replace_entity_data(sample_entities, headers)

def test_batch_replace_partial_success_207():
    mock_response = MagicMock()
    mock_response.status_code = 207

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", return_value=mock_response):
        fiware_scorpio_batch_replace_entity_data(sample_entities, headers)

def test_batch_replace_http_error_status():

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", side_effect=requests.exceptions.HTTPError("Bad Request")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            fiware_scorpio_batch_replace_entity_data(sample_entities, headers)

    assert "Bad Request" in str(err.value)

def test_batch_replace_request_exception_timeout():
    
    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", side_effect=requests.exceptions.Timeout("timeout")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            fiware_scorpio_batch_replace_entity_data(sample_entities, headers)

    assert "timeout" in str(err.value)
