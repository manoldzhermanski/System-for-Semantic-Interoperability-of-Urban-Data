import pytest
import requests
from unittest.mock import patch, Mock
from orion_ld.orion_ld_crud_operations import orion_ld_get_entities_by_type

def test_get_entities_by_type_multiple_pages():
    """
    Check for multiple pagination
    """
    headers = {"Content-Type": "application/ld+json"}

    first_page = [{"id": "urn:ngsi-ld:Test:1", "type": "Test"}]
    second_page = [{"id": "urn:ngsi-ld:Test:2", "type": "Test"}]

    # Multiple pagination calls
    mock_response_1 = Mock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = first_page
    mock_response_1.encoding = "utf-8"

    mock_response_2 = Mock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = second_page
    mock_response_2.encoding = "utf-8"

    # Final call returns empty list
    mock_response_3 = Mock()
    mock_response_3.status_code = 200
    mock_response_3.json.return_value = []
    mock_response_3.encoding = "utf-8"

    with patch("orion_ld.orion_ld_crud_operations.requests.get",
               side_effect=[mock_response_1, mock_response_2, mock_response_3]) as mock_get:
        result = orion_ld_get_entities_by_type("Test", headers)

    assert result == first_page + second_page
    assert mock_get.call_count == 3


def test_get_entities_by_type_http_error():
    """
    Check that HTTP exceptions are catched
    """
    headers = {"Content-Type": "application/ld+json"}

    with patch("orion_ld.orion_ld_crud_operations.requests.get", side_effect=requests.exceptions.HTTPError("404 Not Found")):
        with pytest.raises( requests.exceptions.RequestException) as err:
            orion_ld_get_entities_by_type("GtfsRoute", headers)
            
    assert "404 Not Found" in str(err.value)
