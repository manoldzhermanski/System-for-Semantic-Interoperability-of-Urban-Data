import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_index_trip_by_shape_success():
    """
    Check that proper structure is created
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1",
            "hasShape": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsShape:Sofia:Shape1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2",
            "hasShape": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsShape:Sofia:Shape1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip3",
            "hasShape": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsShape:Sofia:Shape2"
            }
        }
    ]

    result = netex_utils.netex_index_trip_by_shape(trips)

    assert result == {
        "urn:ngsi-ld:GtfsShape:Sofia:Shape1": [
            trips[0],
            trips[1]
        ],
        "urn:ngsi-ld:GtfsShape:Sofia:Shape2": [
            trips[2]
        ]
    }

def test_netex_index_trip_by_shape_missing_has_shape_relationship():
    """
    Check that error is logged when `hasShape` is missing
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"}
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_trip_by_shape(trips)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Trip missing hasShape: %r", trips[0]["id"])

def test_netex_index_trip_by_shape_invalid_has_shape_relationship_structure():
    """
    Check that error is logged when hasShape object is missing
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1",
            "hasShape": {"type": "Relationship"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_trip_by_shape(trips)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid hasShape structure: %r", trips[0]["id"])

def test_netex_index_trip_by_shape_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_trip_by_shape([])

    assert result == {}