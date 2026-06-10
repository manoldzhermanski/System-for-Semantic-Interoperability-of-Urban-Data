import netex.netex_utils as netex_utils
from unittest.mock import MagicMock


def test_netex_helper_filter_valid_transfers_for_service_journey_interchanges_success():
    """
    Check that only valid transfers are returned.
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Transfer1",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        },
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:urn:ngsi-ld:GtfsTrip:Sofia:Transfer2",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop3"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop4"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip3"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip4"}
        }
    ]

    result = netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers)

    assert result == transfers

def test_netex_helper_filter_valid_transfers_missing_origin():
    """
    Check that transfer is skipped when hasOrigin is missing.
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Transfer1",
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers)

    assert result == []

    netex_utils.logger.error.assert_called_once_with("Transfer cannot be converted to ServiceJourneyInterchange. Missing hasOrigin: %r", transfers[0]["id"])

def test_netex_helper_filter_valid_transfers_missing_destination():
    """
    Check that transfer is skipped when hasDestination is missing.
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Transfer1",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers)

    assert result == []

    netex_utils.logger.error.assert_called_once_with("Transfer cannot be converted to ServiceJourneyInterchange. Missing hasDestination: %r", transfers[0]["id"])

def test_netex_helper_filter_valid_transfers_missing_from_trip():
    """
    Check that transfer is skipped when from_trip_id is missing.
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Transfer1",
            "hasOrigin": { "type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "to_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers)

    assert result == []

    netex_utils.logger.error.assert_called_once_with("Transfer cannot be converted to ServiceJourneyInterchange. Missing from_trip_id: %r", transfers[0]["id"])

def test_netex_helper_filter_valid_transfers_missing_to_trip():
    """
    Check that transfer is skipped when to_trip_id is missing.
    """
    transfers = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:Transfer1",
            "hasOrigin": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop1"},
            "hasDestination": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:Sofia:Stop2"},
            "from_trip_id": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"}
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges(transfers)

    assert result == []

    netex_utils.logger.error.assert_called_once_with("Transfer cannot be converted to ServiceJourneyInterchange. Missing to_trip_id: %r", transfers[0]["id"])

def test_netex_helper_filter_valid_transfers_empty_input():
    """
    Check that empty input returns empty list.
    """
    result = netex_utils.netex_helper_filter_valid_transfers_for_service_journey_interchanges([])

    assert result == []