import pytest
import lxml.etree as etree
import netex.netex_utils as netex_utils
from io import BytesIO
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr(
        "netex.netex_utils.config.NETEX_AUTHORITY",
        "TEST"
    )

def parse_streamed_xml(output: BytesIO) -> etree._Element:
    """
    Parses streamed XML output into an lxml root element.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    return etree.fromstring(output.getvalue(), parser=parser)

def test_netex_helper_stream_line_writes_valid_line():
    """
    Test that a valid <Line> element is streamed.
    """

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

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_utils.netex_helper_stream_line(xf, entity)

    root = parse_streamed_xml(output)

    assert root.tag == "lines"

    stop_assignments = root.findall("Line")
    
    assert stop_assignments[0].get("id") == "TEST:Line:Line_A_94"

def test_netex_helper_stream_line_returns_empty_and_logs_error_invalid_id():
    """
    Test that function is not called when invalid ID is given as input
    """
    agency = {
        "id": "broken_id",
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

    xml_file = MagicMock()

    netex_utils.logger.error = MagicMock()

    netex_utils.netex_helper_stream_line(xml_file, agency)

    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsRoute: %r", "broken_id")

    xml_file.write.assert_not_called()
    
def test_netex_helper_stream_line_returns_empty_and_logs_error_invalid_type():
    """
    Test that function is not called when invalid type is given as input
    """
    line = {
        "id": "urn:ngsi-ld:GtfsRoute:TEST:Line_A_94",
        "type": "GtfsStop",
        "operatedBy": {"type": "Relationship", "object": "A"},
        "shortName": {"type": "Property",  "value": "94"},
        "name": {"type": "Property", "value": "Line 94"}, 
        "description": {"type": "Property", "value": "Line Description"},
        "routeType": {"type": "Property", "value": 999},
        "route_url": {"type": "Property", "value": "https://www.route_a_94.com"},
        "routeColor": {"type": "Property", "value": "000000"},
        "routeTextColor": {"type": "Property", "value": "FFFFFF"},
    }

    xml_file = MagicMock()

    netex_utils.logger.error = MagicMock()

    netex_utils.netex_helper_stream_line(xml_file, line)

    netex_utils.logger.error.assert_called_once_with("Unsupported entity type for Line conversion: %s", line["type"])

    xml_file.write.assert_not_called()