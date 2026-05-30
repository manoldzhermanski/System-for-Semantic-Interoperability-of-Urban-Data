import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_index_trips_by_route_success():
    """
    Check that proper structure is created
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1",
            "route": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsRoute:Sofia:Route1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2",
            "route": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsRoute:Sofia:Route1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip3",
            "route": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsRoute:Sofia:Route2"
            }
        }
    ]

    result = netex_utils.netex_index_trips_by_route(trips)

    assert result == {
        "urn:ngsi-ld:GtfsRoute:Sofia:Route1": [
            trips[0],
            trips[1]
        ],
        "urn:ngsi-ld:GtfsRoute:Sofia:Route2": [
            trips[2]
        ]
    }

def test_netex_index_trips_by_route_missing_route_relationship():
    """
    Check that error is logged when `route` is missing
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"}
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_trips_by_route(trips)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Trip missing route: %r", trips[0]["id"])

def test_netex_index_trips_by_route_invalid_route_relationship_structure():
    """
    Check that error is logged when route object is missing
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1",
            "route": {"type": "Relationship"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_trips_by_route(trips)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid route structure: %r", trips[0]["id"])

def test_netex_index_trips_by_route_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_trips_by_route([])

    assert result == {}