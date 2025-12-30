from unittest.mock import patch
from typing import Any
from google.transit.gtfs_realtime_pb2 import FeedMessage # type: ignore
from google.protobuf.json_format import MessageToDict
from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_feed_to_dict


def test_feed_to_dict_returns_dict():
    """
    Check that the result of the function call is a dict
    """
    feed = FeedMessage()
    result = gtfs_realtime_feed_to_dict(feed)
    assert isinstance(result, dict)


def test_feed_to_dict_calls_message_to_dict():
    """
    Verify that gtfs_realtime_feed_to_dict delegates the conversion
    to MessageToDict and returns its result.

    The MessageToDict function is mocked so that the test does not
    depend on the actual protobuf implementation.
    """
    # Create a mock FeedMessage 
    feed = FeedMessage()
    
    # Create a mock expected result
    expected_result: dict[str, Any] = {"key": "value"}
    
    # Patch MessageToDict to return the mock expected result
    with \
        patch("gtfs_realtime.gtfs_realtime_utils.MessageToDict", return_value= expected_result) \
        as mock_message_to_dict:
            
            # Simulate function call
            result = gtfs_realtime_feed_to_dict(feed)

    # Check that the function call was done with the mock FeedMessage and the result is as expected
    mock_message_to_dict.assert_called_once_with(feed)
    assert result == expected_result
