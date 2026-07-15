import pytest
import logging
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

def test_build_scheduled_stop_point_success():
    """
    Test successful ScheduledStopPoint creation.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1",
        "type": "GtfsStop",
        "name": {"type": "Property", "value": "Central Station"}
    }

    result_xml = netex_utils.netex_helper_build_scheduled_stop_point(entity)

    expected_xml = """
    <ScheduledStopPoint
        version="1"
        id="TEST:ScheduledStopPoint:Stop1">
        <Name>Central Station</Name>
    </ScheduledStopPoint>
    """

    assert_xml_equal(result_xml, expected_xml)


def test_build_scheduled_stop_point_without_name():
    """
    Test ScheduledStopPoint is created without Name when stop_name is missing.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1",
        "type": "GtfsStop"
    }

    result_xml = netex_utils.netex_helper_build_scheduled_stop_point(entity)

    expected_xml = """
    <ScheduledStopPoint version="1" id="TEST:ScheduledStopPoint:Stop1"/>
    """

    assert_xml_equal(result_xml, expected_xml)


def test_build_scheduled_stop_point_returns_none_for_invalid_type():
    """
    Test unsupported entity type returns None and logs error.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsRoute:TestCity:1",
        "type": "GtfsRoute"
    }

    netex_utils.logger.error = MagicMock()
    
    result_xml = netex_utils.netex_helper_build_scheduled_stop_point(entity)

    assert result_xml is None

    netex_utils.logger.error.assert_called_once_with("Unsupported entity type: %s", "GtfsRoute")


def test_build_scheduled_stop_point_returns_none_for_invalid_id():
    """
    Test invalid stop ID returns None and logs error.
    """

    entity = {
        "id": "broken_id",
        "type": "GtfsStop"
    }
    
    netex_utils.logger.error = MagicMock()

    result_xml = netex_utils.netex_helper_build_scheduled_stop_point(entity)

    assert result_xml is None

    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsStop: %r", "broken_id")