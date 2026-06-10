import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_index_shape_by_trip_success():
    """
    Check that trips are properly grouped by shape ID
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1",
            "hasShape": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsShape:Sofia:Shape1"}
        },
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2",
            "hasShape": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsShape:Sofia:Shape2"}
        }
    ]

    result = netex_utils.netex_index_shape_by_trip(trips)

    assert result == {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": "urn:ngsi-ld:GtfsShape:Sofia:Shape1",
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip2": "urn:ngsi-ld:GtfsShape:Sofia:Shape2"
    }

def test_netex_index_shape_by_trip_missing_has_shape():
    """
    Check that error is logged when hasShape is missing
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_shape_by_trip(trips)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Trip missing hasShape: %r", trips[0]["id"])

def test_netex_index_shape_by_trip_invalid_has_shape_structure():
    """
    Check that error is logged when shape object is missing
    """
    trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1",
            "hasShape": {
                "type": "Relationship"
            }
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_shape_by_trip(trips)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Invalid hasShape structure: %r", trips[0]["id"])

def test_netex_index_shape_by_trip_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_shape_by_trip([])

    assert result == {}