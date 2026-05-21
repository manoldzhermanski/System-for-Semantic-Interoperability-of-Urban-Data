import pytest
import logging
from lxml import etree
from netex.netex_utils import netex_helper_build_route_point

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

    result_xml = netex_helper_build_route_point(entity)

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


def test_build_route_point_returns_none_for_invalid_type(caplog):
    """
    Test unsupported entity type returns None and logs error.
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsRoute:TEST:1",
        "type": "GtfsRoute"
    }

    with caplog.at_level(logging.ERROR):

        result = netex_helper_build_route_point(entity)

    assert result is None

    assert "Unsupported entity type" in caplog.text


def test_build_route_point_returns_none_for_invalid_id(caplog):
    """
    Test invalid stop ID returns None and logs error.
    """

    entity = {
        "id": "broken_id",
        "type": "GtfsStop"
    }

    with caplog.at_level(logging.ERROR):

        result = netex_helper_build_route_point(entity)

    assert result is None

    assert "Invalid or missing ID for GtfsStop" in caplog.text