import requests
import config
from gtfs_realtime_pb2 import FeedMessage
from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict



def get_gtfs_realtime_feed(api_endpoint: str) -> bytes:
    """
    Based on the API endpoint, sends a GET request to fetch the GTFS-Realtime feed.
    """
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint}: {e}")
    
def parse_gtfs_realtime_feed(feed_data: bytes, api_endpoint: str = None) -> FeedMessage:
    """
    Parses the GTFS-Realtime feed data into a FeedMessage object.
    Provide an optional api_endpoint for debugging purposes.
    """
    feed = FeedMessage()
    try:
        feed.ParseFromString(feed_data)
    except DecodeError as e:
        endpoint_info = f" from {api_endpoint}" if api_endpoint else ""
        raise ValueError(f"Error parsing GTFS-Realtime feed data from {endpoint_info}: {e}")
    return feed

def gtfs_realtime_feed(feed_data: FeedMessage) -> MessageToDict:
    """
    Converts a FeedMessage object to a dictionary using MessageToDict.
    """
    feed_dict = MessageToDict(feed_data)
    return feed_dict


if __name__ == "__main__":
    api_response = get_gtfs_realtime_feed(config.GTFS_REALTIME_VEHICLE_POSITION_URL)
    feed_data = parse_gtfs_realtime_feed(api_response, config.GTFS_REALTIME_VEHICLE_POSITION_URL)
    feed_dict = gtfs_realtime_feed(feed_data)
    print(feed_dict)