import pytest
import logging
from lxml import etree
from netex.netex_utils import netex_helper_build_passenger_stop_assignment


@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")


def assert_xml_equal(generated_xml, expected_xml_str):
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)


def test_build_passenger_stop_assignment_success():
    entity = {
        "id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1",
        "type": "GtfsStop",
    }

    result = netex_helper_build_passenger_stop_assignment(entity, 1)

    expected_xml = """
    <PassengerStopAssignment order="1" version="1" id="TEST:PassengerStopAssignment:Stop1">
        <ScheduledStopPointRef ref="TEST:ScheduledStopPoint:Stop1" versionRef="1"/>
        <QuayRef ref="TEST:Quay:Stop1" version="1"/>
    </PassengerStopAssignment>
    """

    assert_xml_equal(result, expected_xml)


def test_build_passenger_stop_assignment_invalid_type(caplog):
    entity = {
        "id": "urn:ngsi-ld:GtfsRoute:TestCity:1",
        "type": "GtfsRoute",
    }

    result = netex_helper_build_passenger_stop_assignment(entity, 1)

    assert result is None
    assert "Unsupported entity type" in caplog.text


def test_build_passenger_stop_assignment_invalid_id(caplog):
    entity = {
        "id": "broken_id",
        "type": "GtfsStop",
    }

    result = netex_helper_build_passenger_stop_assignment(entity, 1)

    assert result is None
    assert "Invalid or missing ID for GtfsStop" in caplog.text