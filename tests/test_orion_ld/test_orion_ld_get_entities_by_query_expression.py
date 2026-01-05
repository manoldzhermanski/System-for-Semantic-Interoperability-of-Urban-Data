import pytest
from unittest.mock import patch, MagicMock
import requests
from orion_ld.orion_ld_crud_operations import orion_ld_get_entities_by_query_expression

def test_get_entities_by_query_single_page():
    headers = {"Content-Type": "application/ld+json"}
    
    sample_entities = [{"id": "1", "type": "Test"}]
    query = 'name=="София"'

    mock_response_1 = MagicMock()
    mock_response_1.status_code = 200
    mock_response_1.json.return_value = sample_entities
    mock_response_1.encoding = "utf-8"

    mock_response_2 = MagicMock()
    mock_response_2.status_code = 200
    mock_response_2.json.return_value = []
    mock_response_2.encoding = "utf-8"

    with patch(
        "orion_ld.orion_ld_crud_operations.requests.get",
        side_effect=[mock_response_1, mock_response_2]
    ) as mock_get:
        result = orion_ld_get_entities_by_query_expression("Test", headers, query)

    assert result == sample_entities

    assert mock_get.call_count == 2

    called_q = mock_get.call_args_list[0][1]["params"]["q"]
    assert "\\u0421\\u043e\\u0444\\u0438\\u044f" in called_q


def test_get_entities_by_query_http_error():
    
    headers = {"Content-Type": "application/ld+json"}
    
    with patch("orion_ld.orion_ld_crud_operations.requests.get", side_effect = requests.exceptions.HTTPError("404 Not Found")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            orion_ld_get_entities_by_query_expression("Test", headers, 'name=="Test"')

    assert "404 Not Found" in str(err.value)