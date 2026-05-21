import pytest
from netex.netex_utils import netex_helper_extract_stop_coordinates

Point = tuple[float, float]

def test_netex_helper_extract_stop_coordinates_skips_invalid_entries():
    
    entities = [
        {"id": "INVALID_ID_1", "type": "GtfsStop", 
         "location": {"type": "GeoProperty","value": {"type": "Point", "coordinates": [23.3219, 42.6977]}}},
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop_2", "type": "GtfsTrip", 
         "location": {"type": "GeoProperty","value": {"type": "Point", "coordinates": [23.3219, 42.6977]}}},
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop_3", "type": "GtfsTrip", 
         "location": {"type": "GeoProperty","value": {"type": "Point", "coordinates": [23.3219]}}},
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop_4", "type": "GtfsStop"},
        {"id": None, "type": None, "location": None},
    ]
    
    result = netex_helper_extract_stop_coordinates(entities)
    
    assert result == {}

def test_extract_stop_coordinates_handles_multiple_stops():
    """
    Test extracting multiple valid stops.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TestCity:Stop_1",
            "type": "GtfsStop",
            "location": {
                "value": {
                    "coordinates": [23.3219, 42.6977]
                }
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TestCity:Stop_2",
            "type": "GtfsStop",
            "location": {
                "value": {
                    "coordinates": [24.7453, 42.1354]
                }
            }
        }
    ]

    result = netex_helper_extract_stop_coordinates(entities)

    assert isinstance(result, dict)
    assert len(result) == 2
    assert "Stop_1" in result
    assert "Stop_2" in result
    assert isinstance(result["Stop_1"], tuple)
    assert isinstance(result["Stop_2"], tuple)
    assert len(result["Stop_1"]) == 2
    assert len(result["Stop_2"]) == 2
    assert all(isinstance(coord, float) for coord in result["Stop_1"])
    assert all(isinstance(coord, float) for coord in result["Stop_2"])
    
def test_that_empty_list_of_entities_returns_empty_result():
    result = netex_helper_extract_stop_coordinates([])
    assert result == {}