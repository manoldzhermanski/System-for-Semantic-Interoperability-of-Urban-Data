import pytest
from lxml import etree
from netex.netex_utils import netex_convert_calendar_to_operating_period

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

def test_netex_convert_calendar_to_operating_period_single_valid_entity():
    """Tests a standard, valid entity."""
    entities = [{
            "id": f"urn:ngsi-ld:GtfsCalendarRule:TestCity:WeekdayId",
            "type": "GtfsCalendarRule",
           
            "hasService": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsService:TestCity:WeekdayId"
            },
           
            "monday": {
                "type": "Property",
                "value": 1
            },

            "tuesday": {
                "type": "Property",
                "value": 1
            },

            "wednesday": {
                "type": "Property",
                "value": 1
            },

            "thursday": {
                "type": "Property",
                "value": 1
            },

            "friday": {
                "type": "Property",
                "value": 1
            },

            "saturday": {
                "type": "Property",
                "value": 0
            },

            "sunday": {
                "type": "Property",
                "value": 0
            },
           
            "startDate": {
                "type": "Property",
                "value": "20260414"
            },

            "endDate": {
                "type": "Property",
                "value": "20260430"
            }
        }]
    result_xml = netex_convert_calendar_to_operating_period(entities)
    expected_xml = """
    <operatingPeriods>
      <OperatingPeriod version="1" id="TestCity:OperatingPeriod:WeekdayId">
        <FromDate>2026-04-14T00:00:00</FromDate>
        <ToDate>2026-04-30T00:00:00</ToDate>
      </OperatingPeriod>
    </operatingPeriods>
    """
    assert_xml_equal(result_xml, expected_xml)

# NEED TO REFACTOR THIS ONE
def test_netex_convert_calendar_to_operating_period_handles_duplicate_ids_in_validated_input():
    """CRITICAL TEST: Ensures duplicate service_ids produce only one OperatingPeriod."""
    entities = [
        {"id": "urn:city:TestCity:Service1", "startDate": {"value": "20240101"}, "endDate": {"value": "20241231"}},
        {"id": "urn:city:TestCity:Service2", "startDate": {"value": "20250101"}, "endDate": {"value": "20251231"}},
        {"id": "urn:city:TestCity:Service1", "startDate": {"value": "20260101"}, "endDate": {"value": "20261231"}} # Duplicate
    ]
    result_xml = netex_convert_calendar_to_operating_period(entities)
   
    periods = result_xml.findall("OperatingPeriod")

    assert len(periods) == 2

    ids = [p.get("id") for p in periods]

    assert "TestCity:OperatingPeriod:Service1" in ids
    assert "TestCity:OperatingPeriod:Service2" in ids

    service1 = next(p for p in periods if p.get("id") == "TestCity:OperatingPeriod:Service1")
    assert service1.find("FromDate").text == "2024-01-01T00:00:00"

def test_netex_convert_calendar_to_operating_period_with_empty_list():
    """Tests that an empty input list produces an empty container."""
    result_xml = netex_convert_calendar_to_operating_period([])
    expected_xml = "<operatingPeriods/>"
    assert_xml_equal(result_xml, expected_xml)