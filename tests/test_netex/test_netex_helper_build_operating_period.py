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

def test_netex_helper_build_operating_period_with_gtfs_calendar_rule():
    """
    Tests a single GtfsCalendarRule entity which results in building a <DayType> entity
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsCalendarRule:TestCity:WeekdayId",
        "type": "GtfsCalendarRule",  
        "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:TestCity:WeekdayId"},
        "monday": {"type": "Property", "value": 1},
        "tuesday": {"type": "Property", "value": 1},
        "wednesday": {"type": "Property", "value": 1},
        "thursday": {"type": "Property","value": 1},
        "friday": {"type": "Property", "value": 1},
        "saturday": {"type": "Property", "value": 0},
        "sunday": {"type": "Property", "value": 0},
        "startDate": {"type": "Property","value": "20260414"},
        "endDate": {"type": "Property", "value": "20260430"}
    }
   
    result_xml = netex_utils.netex_helper_build_operating_period(entity)
   
    expected_xml = """
    <OperatingPeriod version="1" id="TEST:OperatingPeriod:WeekdayId">
        <FromDate>2026-04-14T00:00:00</FromDate>
        <ToDate>2026-04-30T00:00:00</ToDate>
    </OperatingPeriod>
    """

    assert_xml_equal(result_xml, expected_xml)

def test_netex_helper_build_operating_period_returns_none_when_encountering_an_unsupported_type(caplog):
    """
    Test that when encountering an unsupported GTFS type, None is returned
    """
    entity = {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"}

    netex_utils.logger.error = MagicMock()
    
    result_xml = netex_utils.netex_helper_build_operating_period(entity)

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Unsupported entity type for OperatingPeriod: %s", "GtfsStop")

def test_netex_helper_build_operating_period_returns_none_if_id_format_is_not_correct():
    """
    Test that if the `id` field is not in the correct format, None is returned
    """
    entity = {
        "id": "broken_id",
        "type": "GtfsCalendarRule",  
        "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:TestCity:WeekdayId"},
        "monday": {"type": "Property", "value": 1},
        "tuesday": {"type": "Property", "value": 1},
        "wednesday": {"type": "Property", "value": 1},
        "thursday": {"type": "Property","value": 1},
        "friday": {"type": "Property", "value": 1},
        "saturday": {"type": "Property", "value": 0},
        "sunday": {"type": "Property", "value": 0},
        "startDate": {"type": "Property","value": "20260414"},
        "endDate": {"type": "Property", "value": "20260430"}
    }
    
    netex_utils.logger.error = MagicMock()
    
    result_xml = netex_utils.netex_helper_build_operating_period(entity)

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Invalid ID for GtfsCalendarRule: %r", "broken_id")