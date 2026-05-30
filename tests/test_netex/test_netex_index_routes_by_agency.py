import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_index_routes_by_agency_success():
    """
    Check that proper structure is created
    """
    routes = [
        {
            "id": "urn:ngsi-ld:GtfsRoute:Sofia:Route1",
            "operatedBy": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsAgency:Sofia:Agency1"}
        },
        {
            "id": "urn:ngsi-ld:GtfsRoute:Sofia:Route2",
            "operatedBy": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsAgency:Sofia:Agency1"}
        },
        {
            "id": "urn:ngsi-ld:GtfsRoute:Sofia:Route3",
            "operatedBy": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsAgency:Sofia:Agency2"}
        }
    ]

    result = netex_utils.netex_index_routes_by_agency(routes)

    assert result == {
        "urn:ngsi-ld:GtfsAgency:Sofia:Agency1": [
            routes[0],
            routes[1]
        ],
        "urn:ngsi-ld:GtfsAgency:Sofia:Agency2": [
            routes[2]
        ]
    }

def test_netex_index_routes_by_agency_missing_operated_by():
    """
    Check that error is logged when `operatedBy` is missing
    """
    routes = [
        {
            "id": "urn:ngsi-ld:GtfsRoute:Sofia:Route1"
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_routes_by_agency(routes)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Route missing operatedBy: %r", routes[0]["id"])

def test_netex_index_routes_by_agency_invalid_operated_by_structure():
    """
    Check that error is logged when operatedBy object is missing
    """
    routes = [
        {
            "id": "urn:ngsi-ld:GtfsRoute:Sofia:Route1",
            "operatedBy": {
                "type": "Relationship"
            }
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_routes_by_agency(routes)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid operatedBy structure: %r", routes[0]["id"])

def test_netex_index_routes_by_agency_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_routes_by_agency([])

    assert result == {}