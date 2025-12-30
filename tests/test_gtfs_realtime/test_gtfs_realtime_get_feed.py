import pytest
import requests
from unittest.mock import MagicMock, patch
from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_get_feed

def test_get_gtfs_realtime_feed_success():
    """
    Check that if a GET request is send to a valid API endpoint, we get protobuf bytes as a response
    """
    
    # Mock API endpoint
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.name = "GTFS_REALTIME"
    mock_api_endpoint.value = "http://fake-url.com/feed"

    # Mock API response after sending a GET request
    mock_response = MagicMock()
    mock_response.content = b"protobuf-bytes"
    mock_response.raise_for_status.return_value = None

    # Simulate sending the GET request and getting a response
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response) as mock_get:
        result = gtfs_realtime_get_feed(mock_api_endpoint)

    # Check that protobuf bytes are received from the GET response
    assert result == b"protobuf-bytes"

def test_get_gtfs_realtime_feed_missing_url():
    """
    Check that if an API endpoint URL is missing, a ValueError is raised
    """
    # Mock missing URL as API endpoint
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.name = "GTFS_REALTIME"
    mock_api_endpoint.value = None

    # Simulate sending a GET request and raising a ValueError
    with pytest.raises(ValueError) as err:
        gtfs_realtime_get_feed(mock_api_endpoint)

    assert "has no URL configured" in str(err.value)

def test_get_gtfs_realtime_feed_404_not_found():
    """
    Check that if the GET request to the API endpoint returns a 404 status code,
    a HTTPError exception is raised
    """
    # Mock API endpoint and HTTPError
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.name = "GTFS_REALTIME"
    mock_api_endpoint.value = "http://fake-url.com/feed"

    # Mock response with raise_for_status that raises HTTPError
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

    # Trigger HTTPError exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.RequestException) as err:
            gtfs_realtime_get_feed(mock_api_endpoint)

    # Check that HTTPError exception is raised
    assert f"Error when fetching GTFS data from {mock_api_endpoint.name}" in str(err.value)

def test_get_gtfs_realtime_feed_timeout_error():
    """
    Check that if the GET request to the API endpoint times out,
    a Timeout exception is raised
    """
    # Mock API endpoint and Timeout
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.name = "GTFS_REALTIME"
    mock_api_endpoint.value = "http://fake-url.com/feed"

    # Mock requests.get to raise Timeout
    with patch("gtfs_static.gtfs_static_utils.requests.get", side_effect=requests.exceptions.Timeout("The request timed out")):
        with pytest.raises(requests.exceptions.RequestException) as err:
            gtfs_realtime_get_feed(mock_api_endpoint)

    # Check that Timeout exception is raised
    assert f"Error when fetching GTFS data from {mock_api_endpoint.name}" in str(err.value)

