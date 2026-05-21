import pytest
import logging
from lxml import etree
from netex.netex_utils import netex_helper_build_scheduled_stop_point

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
        "stop_name": {"type": "Property", "value": "Central Station"}
    }

    result_xml = netex_helper_build_scheduled_stop_point(entity)

    expected_xml = """
    <ScheduledStopPoint
        version="1"
        id="TEST:ScheduledStopPoint:Stop1">
        <Name>Central Station</Name>
        <LocationRef ref="TEST:StopPlace:Stop1" version="1"/>
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

    result_xml = netex_helper_build_scheduled_stop_point(entity)

    expected_xml = """
    <ScheduledStopPoint
        version="1"
        id="TEST:ScheduledStopPoint:Stop1">
        <LocationRef ref="TEST:StopPlace:Stop1" version="1"/>
    </ScheduledStopPoint>
    """

    assert_xml_equal(result_xml, expected_xml)


def test_build_scheduled_stop_point_returns_none_for_invalid_type(caplog):
    """
    Test unsupported entity type returns None and logs error.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsRoute:TestCity:1",
        "type": "GtfsRoute"
    }


    result_xml = netex_helper_build_scheduled_stop_point(entity)

    assert result_xml is None

    assert "Unsupported entity type" in caplog.text


def test_build_scheduled_stop_point_returns_none_for_invalid_id(caplog):
    """
    Test invalid stop ID returns None and logs error.
    """

    entity = {
        "id": "broken_id",
        "type": "GtfsStop"
    }

    result_xml = netex_helper_build_scheduled_stop_point(entity)

    assert result_xml is None

    assert "Invalid or missing ID for GtfsStop" in caplog.text