from gtfs_realtime.gtfs_realtime_utils import unix_to_iso8601

def test_unix_to_iso8601_valid_timestamp():
    assert unix_to_iso8601(0) == "1970-01-01T00:00:00Z"
    assert unix_to_iso8601("0") == "1970-01-01T00:00:00Z"

    
def test_unix_to_iso8601_bool_rejected():
    assert unix_to_iso8601(False) == None
        
def test_unix_to_iso8601_none_value_timestamp():
    assert unix_to_iso8601(None) is None
    
def test_unix_to_iso8601_negative_timestamp():
    assert unix_to_iso8601(-1) == "1969-12-31T23:59:59Z"

    