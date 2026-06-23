import pytest
from netex.netex_utils import netex_helper_collect_entities_by_service

def test_netex_helper_collect_entities_by_service_collects_entities():
    """
    Test happy path
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1", "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:Sofia:Service1"}},
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip2", "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:Sofia:Service2"}},
    ]

    index = {
        "urn:ngsi-ld:GtfsService:Sofia:Service1": [{"id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar1"}],
        "urn:ngsi-ld:GtfsService:Sofia:Service2": [{"id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar2"}],
    }

    result = netex_helper_collect_entities_by_service(trips, index, "calendar")

    assert result == [
        {"id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar1"},
        {"id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar2"},
    ]
    
def test_netex_helper_collect_entities_by_service_skips_invalid_service(caplog):
    """
    Test that  warning is logged if an entity doesn't have a service attribute
    """
    trips = [
        {"id": "urn:ngsi-ld:GtfsTrip:Sofia:Trip1"},
    ]

    result = netex_helper_collect_entities_by_service(trips, {}, "calendar")

    assert result == []
    assert "Invalid or missing service id" in caplog.text
        
def test_netex_helper_collect_entities_by_service_empty_input():
    """
    Test that empty list is returned when empty input is given
    """
    result = netex_helper_collect_entities_by_service([], {}, "calendar")

    assert result == []