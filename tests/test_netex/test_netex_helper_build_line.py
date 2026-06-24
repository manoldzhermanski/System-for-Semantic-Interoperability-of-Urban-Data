import pytest
import lxml.etree as etree
import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")

def assert_xml_equal(generated_xml, expected_xml_str):
    """
    Compares two XML elements by parsing the expected string and comparing string dumps.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

def test_netex_helper_build_line_returns_expected_xml():
    entity = {
        "id": "urn:ngsi-ld:GtfsRoute:TEST:Line_A_94",
        "type": "GtfsRoute",
        "operatedBy": {"type": "Relationship", "object": "A"},
        "shortName": {"type": "Property",  "value": "94"},
        "name": {"type": "Property", "value": "Line 94"}, 
        "description": {"type": "Property", "value": "Line Description"},
        "routeType": {"type": "Property", "value": 3},
        "route_url": {"type": "Property", "value": "https://www.route_a_94.com"},
        "routeColor": {"type": "Property", "value": "000000"},
        "routeTextColor": {"type": "Property", "value": "FFFFFF"},
    }
    
    result_xml = netex_utils.netex_helper_build_line(entity)

    expected_xml = """
        <Line version="1" id="TEST:Line:Line_A_94">
            <Name>Line 94</Name>
            <Description>Line Description</Description>
            <TransportMode>bus</TransportMode>
            <TransportSubmode>
                <BusSubmode>unknown</BusSubmode>
            </TransportSubmode>
            <Url>https://www.route_a_94.com</Url>
            <PublicCode>94</PublicCode>
            <OperatorRef ref="TEST:Operator:A"></OperatorRef>
            <RepresentedByGroupRef ref="TEST:Network:ANett"></RepresentedByGroupRef>
            <Presentation>
                <Colour>000000</Colour>
                <TextColour>FFFFFF</TextColour>
            </Presentation>
        </Line>
    """
    assert_xml_equal(result_xml, expected_xml)
    

def test_netex_helper_build_line_returns_none_when_encountering_an_unsupported_type():
    """
    Test that when encountering an unsupported GTFS type, None is returned
    """
    entity = {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"}

    netex_utils.logger.error = MagicMock()
    
    result_xml = netex_utils.netex_helper_build_line(entity)

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Unsupported entity type for Line conversion: %s", "GtfsStop")

def test_netex_helper_build_line_returns_none_if_id_format_is_not_correct():
    """
    Test that if the `id` field is not in the correct format, None is returned
    """
    entity = {
        "id": "broken_id",
        "type": "GtfsRoute",
        "operatedBy": {"type": "Relationship", "object": "A"},
        "shortName": {"type": "Property",  "value": "94"},
        "name": {"type": "Property", "value": "Line 94"}, 
        "description": {"type": "Property", "value": "Line Description"},
        "routeType": {"type": "Property", "value": 3},
        "route_url": {"type": "Property", "value": "https://www.route_a_94.com"},
        "routeColor": {"type": "Property", "value": "000000"},
        "routeTextColor": {"type": "Property", "value": "FFFFFF"},
    }
    
    netex_utils.logger.error = MagicMock()

    result_xml = netex_utils.netex_helper_build_line(entity)

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsRoute: %r", "broken_id")
    

def test_netex_helper_build_line_invalid_transport_mode():
    """
    Test that ValueError is raised when invalid `routeType` value is given as input
    """
    route = {
        "id": f"urn:ngsi-ld:GtfsRoute:TEST:Line_A_94",
        "type": "GtfsRoute",
        "operatedBy": {"type": "Relationship", "object": "A"},
        "shortName": {"type": "Property",  "value": "94"},
        "name": {"type": "Property", "value": "Line 94"}, 
        "description": {"type": "Property", "value": "Line Description"},
        "routeType": {"type": "Property", "value": 999},
        "route_url": {"type": "Property", "value": "https://www.route_a_94.com"},
        "routeColor": {"type": "Property", "value": "000000"},
        "routeTextColor": {"type": "Property", "value": "FFFFFF"},
    }

    with pytest.raises(ValueError) as err:
        netex_utils.netex_helper_build_line(route)
        
    assert "Unknown Transport Mode" in str(err.value)