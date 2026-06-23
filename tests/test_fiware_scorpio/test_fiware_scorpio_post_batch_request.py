import logging
import requests
import pytest
from unittest.mock import patch, MagicMock
from fiware_scorpio.fiware_scorpio_crud_operations import fiware_scorpio_post_batch_request

def test_batch_create_success_logs_info(caplog):
    """
    Check if successful POST request is logged
    """
    sample_entities = [
        {"id": "urn:ngsi-ld:Test:1", "type": "Test"},
        {"id": "urn:ngsi-ld:Test:2", "type": "Test"},
    ]

    headers = {"Content-Type": "application/ld+json"}

    mock_response = MagicMock()
    mock_response.status_code = 201

    caplog.set_level(logging.INFO)

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", return_value=mock_response):
        fiware_scorpio_post_batch_request(sample_entities, headers)

    assert "Batch OK (2 entities)" in caplog.text

def test_batch_create_http_error_logs_error():
    """
    Check that if status code != 201 is being captured
    """
    headers = {"Content-Type": "application/ld+json"}

    sample_entities = [
        {"id": "urn:ngsi-ld:Test:1", "type": "Test"},
        {"id": "urn:ngsi-ld:Test:2", "type": "Test"},
    ]

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError) as err:
            fiware_scorpio_post_batch_request(sample_entities, headers)

    assert "Batch failed (400)" in str(err.value)
    assert "Bad Request" in str(err.value)


def test_batch_create_request_exception_logs_exception():
    """
    Check that RequestExceptions are captured
    """
    sample_entities = [
        {"id": "urn:ngsi-ld:Test:1", "type": "Test"},
        {"id": "urn:ngsi-ld:Test:2", "type": "Test"},
    ]
    headers = {"Content-Type": "application/ld+json"}

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post",side_effect=requests.exceptions.Timeout("timeout")):
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            fiware_scorpio_post_batch_request(sample_entities, headers)

    assert "timeout" in str(exc_info.value)