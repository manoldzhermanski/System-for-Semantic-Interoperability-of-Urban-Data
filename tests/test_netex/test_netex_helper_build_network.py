import pytest
import logging
from lxml import etree
from netex.netex_utils import netex_helper_build_network

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

def test_netex_helper_build_network_retuns_the_expected_result():
    """
    Tests that the netex_helper_build_network function returns the expected XML structure.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsAgency:TEST:AGENCY1",
        "type": "GtfsAgency",
        "agency_name": {"type": "Property","value": "Mainline Transit"},
    }

    result_xml = netex_helper_build_network(entity)

    expected_xml = """
    <Network version="1" id="TEST:Network:AGENCY1Nett">
        <Name>Mainline Transit</Name>
        <AuthorityRef ref="TEST:Authority:AGENCY1_ID" version="1"></AuthorityRef>
    </Network>
    """
    assert_xml_equal(result_xml, expected_xml)

def test_netex_helper_build_network_returns_none_when_encountering_an_unsupported_type(caplog):
    """
    Test that when encountering an unsupported GTFS type, None is returned
    """
    entity = {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"}

    result_xml = netex_helper_build_network(entity)

    assert result_xml is None
    assert "Unsupported entity type" in caplog.text

def test_netex_helper_build_network_returns_none_if_id_format_is_not_correct(caplog):
    """
    Test that if the `id` field is not in the correct format, None is returned
    """
    entity = {
        "id": "broken_id",
        "type": "GtfsAgency",
        "agency_name": {"type": "Property","value": "Mainline Transit"},
    }

    result_xml = netex_helper_build_network(entity)

    assert result_xml is None
    assert "Invalid or missing ID" in caplog.text

def test_netex_helper_build_network_non_proper_split_elements_returns_none(caplog):
    """
    Test that if the `id` field does not have enough slit elements, None is returned
    """
    entity = {
        "id": "urn:ngsi-ld:GtfsAgency:AGENCY1",
        "type": "GtfsAgency",
        "agency_name": {"type": "Property","value": "Mainline Transit"},
    }

    result_xml = netex_helper_build_network(entity)

    assert result_xml is None
    assert "Invalid ID" in caplog.text