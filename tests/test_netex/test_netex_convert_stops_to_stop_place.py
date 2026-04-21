import pytest
from lxml import etree

from netex.netex_utils import netex_convert_stops_to_stop_place

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")
    
def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TestCity:TestStop",
            "name": {"type": "Property","value": "Central Station"},
            "code": {"type": "Property","value": "100"},
            "description": {"type": "Property","value": "Main hub"},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [23.0, 42.0]}},
            "locationType": {"type": "Property", "value": 0},
        }
    ]

    result = netex_convert_stops_to_stop_place(entities, {})

    xml = etree.tostring(result)
    root = etree.fromstring(xml)

    stop_place = root.find("StopPlace")

    assert stop_place is not None
    assert stop_place.attrib["id"] == "TEST:StopPlace:TestStop"

    assert stop_place.findtext("Name") == "Central Station"
    assert stop_place.findtext("PublicCode") == "100"
    assert stop_place.findtext("Description") == "Main hub"

    coords = stop_place.find(".//Centroid/Location")
    assert coords.findtext("Longitude") == "23.0"
    assert coords.findtext("Latitude") == "42.0"