import netex.netex_utils as netex_utils
from unittest.mock import MagicMock


def test_netex_index_transfers_by_origin_trip_success():
    """
    Check that valid transfers are grouped by origin trip.
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:Sofia:Transfer1",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        },
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:Sofia:Transfer2",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        },
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:Sofia:Transfer3",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip3"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip4"}
        }
    ]

    netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges = MagicMock(return_value=transfers)

    result = netex_utils.netex_index_transfers_by_origin_trip(transfers)

    assert result == {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": [
            transfers[0],
            transfers[1]
        ],
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip3": [
            transfers[2]
        ]
    }


def test_netex_index_transfers_by_origin_trip_empty_input():
    """
    Check that empty dictionary is returned when no valid transfers exist.
    """
    netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges = MagicMock(return_value=[])

    result = netex_utils.netex_index_transfers_by_origin_trip([])

    assert result == {}

def test_netex_index_transfers_by_origin_trip_filters_transfers():
    """
    Test that the helper function filters the incorrect transfers before indexing
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:Sofia:Transfer1",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        },
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:Sofia:Transfer2",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        },
        {
            "id": "urn:ngsi-ld:GtfsTransferRule:Sofia:Transfer3",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip3"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip4"}
        }
    ]
    
    valid_transfers = [
        transfers[0],
        transfers[2],
    ]

    netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges = MagicMock(
        return_value=valid_transfers
    )

    result = netex_utils.netex_index_transfers_by_origin_trip(transfers)

    assert result == {
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip1": [transfers[0]],
        "urn:ngsi-ld:GtfsTrip:Sofia:Trip3": [transfers[2]],
}