import logging
import requests
from unittest.mock import patch, MagicMock
from orion_ld.orion_ld_crud_operations import orion_ld_post_batch_request

def test_batch_create_success_logs_debug(caplog):
    """
    Check if sucessful POST request is captured
    """
    sample_entities = [
        {"id": "urn:ngsi-ld:Test:1", "type": "Test"},
        {"id": "urn:ngsi-ld:Test:2", "type": "Test"},
    ]
    
    headers = {"Content-Type": "application/ld+json"}
    
    mock_response = MagicMock()
    mock_response.status_code = 201

    caplog.set_level(logging.DEBUG)

    with patch("orion_ld.orion_ld_crud_operations.requests.post", return_value=mock_response):
        orion_ld_post_batch_request(sample_entities, headers)

    assert "Sending batch create request to Orion-LD" in caplog.text

def test_batch_create_http_error_logs_error(caplog):
    """
    Check that failed POST requests are captured
    """
    sample_entities = [
        {"id": "urn:ngsi-ld:Test:1", "type": "Test"},
        {"id": "urn:ngsi-ld:Test:2", "type": "Test"},
    ]
    
    headers = {"Content-Type": "application/ld+json"}
    
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    caplog.set_level(logging.ERROR)

    with patch("orion_ld.orion_ld_crud_operations.requests.post", return_value=mock_response):
        orion_ld_post_batch_request(sample_entities, headers)

    assert "Batch failed" in caplog.text
    assert "400" in caplog.text


def test_batch_create_request_exception_logs_exception(caplog):
    """
    Check that request exceptions are captured
    """
    sample_entities = [
        {"id": "urn:ngsi-ld:Test:1", "type": "Test"},
        {"id": "urn:ngsi-ld:Test:2", "type": "Test"},
    ]
    
    headers = {"Content-Type": "application/ld+json"}
    
    caplog.set_level(logging.ERROR)

    with patch(
        "orion_ld.orion_ld_crud_operations.requests.post",
        side_effect=requests.exceptions.Timeout,
    ):
        orion_ld_post_batch_request(sample_entities, headers)

    assert "Batch POST request to Orion-LD failed" in caplog.text