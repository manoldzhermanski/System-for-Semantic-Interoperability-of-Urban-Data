from orion_ld.orion_ld_crud_operations import orion_ld_get_count_of_entities_by_type
import pytest
from unittest.mock import patch, MagicMock
import requests

def test_get_count_of_entities_success():
    
    headers = {"Content-Type": "application/ld+json"}

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {"NGSILD-Results-Count": "42"}

    with patch("orion_ld.orion_ld_crud_operations.requests.get", return_value=mock_response):
        result = orion_ld_get_count_of_entities_by_type("Test", headers)

    assert result == 42

def test_get_count_of_entities_missing_header():
    headers = {"Content-Type": "application/ld+json"}

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.headers = {}

    with patch("orion_ld.orion_ld_crud_operations.requests.get", return_value=mock_response):
        result = orion_ld_get_count_of_entities_by_type("Test", headers)

    assert result == 0

def test_get_count_of_entities_http_error():
    headers = {"Content-Type": "application/ld+json"}

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

    with patch("orion_ld.orion_ld_crud_operations.requests.get", return_value=mock_response):
        result = orion_ld_get_count_of_entities_by_type("Test", headers)

    assert result == 0

def test_get_count_of_entities_request_exception():
    headers = {"Content-Type": "application/ld+json"}

    with patch("orion_ld.orion_ld_crud_operations.requests.get", side_effect=requests.exceptions.Timeout("timeout")):
        result = orion_ld_get_count_of_entities_by_type("Test", headers)

    assert result == 0
