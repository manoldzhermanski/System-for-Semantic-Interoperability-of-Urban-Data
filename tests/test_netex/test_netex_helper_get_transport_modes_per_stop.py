from unittest.mock import patch
import netex.netex_utils as netex_utils

from unittest.mock import patch

def test_netex_helper_get_transport_modes_per_stop_returns_expected_mapping():
    """
    Test happy path
    """
    authority_dataset = {
        "routes": [
            {
                "id": "urn:ngsi-ld:GtfsRoute:TEST:Route1",
                "routeType": {"type": "Property", "value": 3},
            },
            {
                "id": "urn:ngsi-ld:GtfsRoute:TEST:Route2",
                "routeType": {"type": "Property", "value": 0},
            },
        ],
        "trips": [
            {
                "id": "urn:ngsi-ld:GtfsTrip:TEST:Trip1",
                "route": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:TEST:Route1"},
            },
            {
                "id": "urn:ngsi-ld:GtfsTrip:TEST:Trip2",
                "route": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:TEST:Route2"},
            },
        ],
        "stop_times": [
            {
                "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip1"},
                "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop1"},
            },
            {
                "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip1"},
                "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop2"},
            },
            {
                "hasTrip": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:TEST:Trip2"},
                "hasStop": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TEST:Stop2"},
            },
        ],
    }

    with patch(
        "netex.netex_utils.netex_helper_get_transport_mode_and_submode",
        side_effect=[('bus', 'unknown'), ('tram', 'unknown')],
    ):
        result = netex_utils.netex_helper_get_transport_modes_per_stop(authority_dataset)

    assert result == {
        "urn:ngsi-ld:GtfsStop:TEST:Stop1": {('bus', 'unknown')},
        "urn:ngsi-ld:GtfsStop:TEST:Stop2": {('bus', 'unknown'), ('tram', 'unknown')},
    }
    
def test_netex_helper_get_transport_modes_per_stop_with_no_routes():
    """
    Test that if autority dataset is empty, empty dict is returned
    """
    authority_dataset = {
        "routes": [],
        "trips": [],
        "stop_times": [],
    }

    result = netex_utils.netex_helper_get_transport_modes_per_stop(authority_dataset)

    assert result == {}
    
def test_netex_helper_get_transport_modes_per_stop_calls_helper_once_per_route():
    authority_dataset = {
        "routes": [
            {"id": "urn:ngsi-ld:GtfsRoute:TEST:Route1", "routeType": {"value": 3}},
            {"id": "urn:ngsi-ld:GtfsRoute:TEST:Route2", "routeType": {"value": 0}},
            {"id": "urn:ngsi-ld:GtfsRoute:TEST:Route3", "routeType": {"value": 2}},
        ],
        "trips": [],
        "stop_times": [],
    }

    with patch(
        "netex.netex_utils.netex_helper_get_transport_mode_and_submode",
        side_effect=[('bus', 'unknown'), ('tram', 'unknown'), ('rail', 'unknown')],
    ) as mock_helper:
        netex_utils.netex_helper_get_transport_modes_per_stop(authority_dataset)

    assert mock_helper.call_count == 3