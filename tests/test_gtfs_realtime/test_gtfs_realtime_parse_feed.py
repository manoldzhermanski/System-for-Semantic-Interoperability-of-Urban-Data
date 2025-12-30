import pytest
from unittest.mock import patch, MagicMock
from google.protobuf.message import DecodeError

from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_parse_feed
from google.transit.gtfs_realtime_pb2 import FeedMessage # type: ignore

def test_parse_feed_success():
    feed_bytes = b"dummy_data"

    with patch.object(FeedMessage, "ParseFromString"):
        feed = gtfs_realtime_parse_feed(feed_bytes)

    assert isinstance(feed, FeedMessage)


def test_parse_feed_decode_error_with_endpoint():
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "http://fake-url.com"
    mock_api_endpoint.name = "GTFS_REALTIME_URL"
    
    mock_api_response = MagicMock()
    mock_api_response.content = b"invalid_data"

    with patch.object(FeedMessage,"ParseFromString",side_effect=DecodeError("parse failed")):
        with pytest.raises(DecodeError) as err:
            gtfs_realtime_parse_feed(mock_api_response, mock_api_endpoint)

    assert f"Error parsing GTFS-Realtime feed data from {mock_api_endpoint.name}" in str(err.value)


def test_parse_feed_decode_error_without_endpoint():
    mock_api_response = MagicMock()
    mock_api_response.content = b"invalid_data"

    with patch.object(FeedMessage, "ParseFromString",side_effect=DecodeError("parse failed")):
        with pytest.raises(DecodeError) as err:
            gtfs_realtime_parse_feed(mock_api_response, None)

    assert "Error parsing GTFS-Realtime feed data" in str(err.value)
