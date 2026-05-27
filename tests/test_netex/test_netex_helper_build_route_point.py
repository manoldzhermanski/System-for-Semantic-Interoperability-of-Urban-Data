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

def test_build_route_point_success():
    """
    Test successful RoutePoint creation from a valid GtfsStop entity.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
        "type": "GtfsStop"
    }

    result_xml = netex_utils.netex_helper_build_route_point(entity)

    expected_xml = """
    <RoutePoint version="1" id="TEST:RoutePoint:Stop1">
        <projections>
            <PointProjection version="1" id="TEST:PointProjection:Stop1">
                <ProjectToPointRef ref="TEST:ScheduledStopPoint:Stop1"/>
            </PointProjection>
        </projections>
    </RoutePoint>
    """

    assert_xml_equal(result_xml, expected_xml)


def test_build_route_point_returns_none_for_invalid_type():
    """
    Test unsupported entity type returns None and logs error.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsRoute:TEST:1",
        "type": "GtfsRoute"
    }

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_helper_build_route_point(entity)

    assert result is None

    netex_utils.logger.error.assert_called_once_with("Unsupported entity type: %s", "GtfsRoute")


def test_build_route_point_returns_none_for_invalid_id():
    """
    Test invalid stop ID returns None and logs error.
    """

    entity = {
        "id": "broken_id",
        "type": "GtfsStop"
    }

    netex_utils.logger.error = MagicMock()
    
    result = netex_utils.netex_helper_build_route_point(entity)

    assert result is None

    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsStop: %r", "broken_id")