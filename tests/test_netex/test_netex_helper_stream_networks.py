import pytest
import logging
from lxml import etree
from io import BytesIO
from unittest.mock import MagicMock
from netex.netex_utils import netex_helper_stream_networks

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

def test_stream_network_writes_valid_network():
    """
    Test that a valid <Network> element is streamed.
    """

    agency = {
        "id": "urn:ngsi-ld:GtfsAgency:TestCity:Agency1",
        "type": "GtfsAgency",
        "agency_name": {"type": "Property", "value": "Test Transport"}
    }

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_networks(xf, agency)

    root = parse_streamed_xml(output)

    assert root.tag == "Network"

    assert root.get("id") == "TEST:Network:Agency1Nett"

    assert root.findtext("Name") == "Test Transport"

    authority_ref = root.find("AuthorityRef")

    assert authority_ref.get("ref") == "TEST:Authority:Agency1_ID"

def test_stream_network_returns_empty_and_logs_error(caplog):

    agency = {
        "id": "broken_id",
        "type": "GtfsAgency",
        "agency_name": {"type": "Property", "value": "Test Transport"}
    }

    xml_file = MagicMock()

    with caplog.at_level("ERROR"):
        netex_helper_stream_networks(xml_file, agency)

    assert "Invalid or missing ID for GtfsAgency" in caplog.text
    xml_file.write.assert_not_called()