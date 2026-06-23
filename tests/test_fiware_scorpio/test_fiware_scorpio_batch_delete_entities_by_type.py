import pytest
import requests
from unittest.mock import patch, MagicMock
from fiware_scorpio.fiware_scorpio_crud_operations import fiware_scorpio_batch_delete_entities_by_type

headers = {"Content-Type": "application/ld+json"}

def test_batch_delete_entities_success():
    entities = [
        {"id": "urn:ngsi-ld:Test:1"},
        {"id": "urn:ngsi-ld:Test:2"},
    ]

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_get_count_of_entities_by_type", side_effect=[2, 0]), \
        patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_get_entities_by_type", return_value=entities), \
        patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post") as mock_post:

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        fiware_scorpio_batch_delete_entities_by_type("Test", headers)

        mock_post.assert_called_once()

def test_batch_delete_entities_http_error():
    
    entities = [{"id": "urn:ngsi-ld:Test:1"}]

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_get_count_of_entities_by_type", return_value=1), \
        patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_get_entities_by_type", return_value=entities), \
        patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", side_effect=requests.exceptions.HTTPError("Delete failed")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            fiware_scorpio_batch_delete_entities_by_type("Test", headers)

        assert "Delete failed" in str(err.value)

def test_batch_delete_entities_timeout():
    
    entities = [{"id": "urn:ngsi-ld:Test:1"}]

    with patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_get_count_of_entities_by_type", return_value=1), \
        patch("fiware_scorpio.fiware_scorpio_crud_operations.fiware_scorpio_get_entities_by_type", return_value=entities), \
        patch("fiware_scorpio.fiware_scorpio_crud_operations.requests.post", side_effect=requests.exceptions.Timeout("timeout")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            fiware_scorpio_batch_delete_entities_by_type("Test", headers)

        assert "timeout" in str(err.value)
