import pytest
from lxml import etree
from netex.netex_utils import netex_build_networks

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

def test_single_network_creation():
    """
    Tests the successful creation of a single <Network> element.
    """

    input_agencies = [
        {
            "id": "urn:ngsi-ld:Agency:AGENCY1",
            "agency_name": {"value": "Mainline Transit"},
        }
    ]

    result_list = netex_build_networks(input_agencies)

    expected_xml = """
    <Network version="1" id="AGENCY1:Network:AGENCY1Nett">
        <Name>Mainline Transit</Name>
        <AuthorityRef ref="AGENCY1:Authority:AGENCY1_ID" version="1"/>
    </Network>
    """
    assert_xml_equal(result_list[0], expected_xml)


def test_multiple_networks_creation():
    """
    Tests that the function correctly processes a list with multiple agencies.
    """
    input_agencies = [
        {"id": "urn:ngsi-ld:Agency:A1", "agency_name": {"value": "Agency One"}},
        {"id": "urn:ngsi-ld:Agency:A2", "agency_name": {"value": "Agency Two"}},
    ]

    result_list = netex_build_networks(input_agencies)

    assert len(result_list) == 2
    # Check the second element to ensure its data is correct
    expected_xml_for_second = """
    <Network version="1" id="A2:Network:A2Nett">
        <Name>Agency Two</Name>
        <AuthorityRef ref="A2:Authority:A2_ID" version="1"/>
    </Network>
    """
    assert_xml_equal(result_list[1], expected_xml_for_second)