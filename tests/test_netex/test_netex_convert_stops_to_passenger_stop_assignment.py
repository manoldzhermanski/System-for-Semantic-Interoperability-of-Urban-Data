import pytest
from lxml import etree  # type: ignore
from netex.netex_utils import netex_convert_stops_to_passenger_stop_assignment

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)
    
def test_netex_convert_stops_to_passenger_stop_assignment_with_multiple_entities():
    
    entities = [
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"},
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop2", "type": "GtfsStop"}
    ]
    
    generated_xml = netex_convert_stops_to_passenger_stop_assignment(entities)
    
    expected_xml = """
    <stopAssignments>
        <PassengerStopAssignment order="1" version="1" id="TEST:PassengerStopAssignment:Stop1">
            <ScheduledStopPointRef ref="TEST:ScheduledStopPoint:Stop1" versionRef="1"/>
            <QuayRef ref="TEST:Quay:Stop1" version="1"/>
        </PassengerStopAssignment>
        <PassengerStopAssignment order="2" version="1" id="TEST:PassengerStopAssignment:Stop2">
            <ScheduledStopPointRef ref="TEST:ScheduledStopPoint:Stop2" versionRef="1"/>
            <QuayRef ref="TEST:Quay:Stop2" version="1"/>
        </PassengerStopAssignment>
    </stopAssignments>
    """
    
    assert_xml_equal(generated_xml, expected_xml)
    
def test_netex_convert_stops_to_passenger_stop_assignment_with_empty_list():
    
    entities = []
    
    generated_xml = netex_convert_stops_to_passenger_stop_assignment(entities)
    
    expected_xml = """
    <stopAssignments></stopAssignments>
    """
    
    assert_xml_equal(generated_xml, expected_xml)
    
    