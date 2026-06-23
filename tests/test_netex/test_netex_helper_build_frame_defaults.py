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
    
def test_netex_helper_build_frame_defaults_retuns_the_expected_result():
    """
    Tests that the netex_helper_build_frame_defaults function returns the expected XML structure.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsAgency:TEST:AGENCY1",
        "type": "GtfsAgency",
        "agency_timezone": {"type": "Property", "value": "Europe/Sofia"},   
        "agency_lang": {"type": "Property", "value": "bg"}
    }

    result_xml = netex_utils.netex_helper_build_frame_defaults(entity)

    expected_xml = """
      <FrameDefaults>
        <DefaultLocale>
          <TimeZone>Europe/Sofia</TimeZone>
          <DefaultLanguage>bg</DefaultLanguage>
        </DefaultLocale>
      </FrameDefaults>
    """
    assert_xml_equal(result_xml, expected_xml)

def test_netex_helper_build_frame_defaults_returns_none_when_encountering_an_unsupported_type():
    """
    Test that when encountering an unsupported GTFS type, None is returned
    """
    entity = {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"}

    netex_utils.logger.error = MagicMock()
    
    result_xml = netex_utils.netex_helper_build_frame_defaults(entity)

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Unsupported entity type for FrameDefaults conversion: %s", "GtfsStop")