import pytest
from lxml import etree #type: ignore
from netex.netex_utils import netex_convert_stops_to_scheduled_stop_points

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

def test_netex_convert_stops_to_scheduled_stop_points_with_multiple_entities():
    
    entities = [
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"},
        {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop2", "type": "GtfsStop"}
    ]
    
    generated_xml = netex_convert_stops_to_scheduled_stop_points(entities)
    
    expected_xml = """
    <scheduledStopPoints>
        <ScheduledStopPoint version="1" id="TEST:ScheduledStopPoint:Stop1></ScheduledStopPoint>
        <ScheduledStopPoint version="1" id="TEST:ScheduledStopPoint:Stop2></ScheduledStopPoint>
    </scheduledStopPoints>
    """
    
def test_netex_convert_stops_to_scheduled_stop_points_with_empty_list():
    
    entities = []
    
    generated_xml = netex_convert_stops_to_scheduled_stop_points(entities)
    
    expected_xml = """
    <scheduledStopPoints></scheduledStopPoints>
    """
    