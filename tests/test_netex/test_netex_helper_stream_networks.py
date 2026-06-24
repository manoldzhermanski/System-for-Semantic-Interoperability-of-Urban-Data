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

        netex_utils.netex_helper_stream_networks(xf, agency)

    root = parse_streamed_xml(output)

    assert root.tag == "Network"

    assert root.get("id") == "TEST:Network:Agency1Nett"

    assert root.findtext("Name") == "Test Transport"

    authority_ref = root.find("AuthorityRef")

    assert authority_ref.get("ref") == "TEST:Authority:Agency1_ID"

def test_stream_network_returns_empty_and_logs_error():

    agency = {
        "id": "broken_id",
        "type": "GtfsAgency",
        "agency_name": {
            "type": "Property",
            "value": "Test Transport"
        }
    }

    xml_file = MagicMock()

    netex_utils.logger.error = MagicMock()

    netex_utils.netex_helper_stream_networks(xml_file, agency)

    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsAgency: %r", "broken_id")

    xml_file.write.assert_not_called()