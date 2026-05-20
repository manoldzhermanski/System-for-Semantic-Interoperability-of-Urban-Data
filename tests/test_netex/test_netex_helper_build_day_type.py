import pytest
import logging
from lxml import etree
from netex.netex_utils import netex_helper_build_day_type

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

def test_netex_helper_build_day_type_with_gtfs_calendar_rule():
    """
    Tests a single GtfsCalendarRule entity which results in building a <DayType> entity
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsCalendarRule:TEST:WeekdayId",
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
   
    result_xml = netex_helper_build_day_type(entity)
   
    expected_xml = """
    <DayType version="1" id="TEST:DayType:WeekdayId">
        <properties>
          <PropertyOfDay>
            <DaysOfWeek>Weekdays</DaysOfWeek>
          </PropertyOfDay>
        </properties>
    </DayType>
    """

    assert_xml_equal(result_xml, expected_xml)

def test_netex_helper_build_day_type_with_gtfs_calendar_date_rule():
    """
    Tests a single GtfsCalendarDateRule entity which results in building a <DayType> entity
    """

    entity = {
        "id": "urn:ngsi-ld:GtfsCalendarDateRule:TEST:WeekdayId:20260414",
        "type": "GtfsCalendarDateRule",
        "hasService": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsService:TEST:WeekdayId"}, 
        "appliesOn": {"type": "Property", "value": "20260414"},
        "exceptionType": {"type": "Property", "value": 1}
        }
   
    result_xml = netex_helper_build_day_type(entity)
   
    expected_xml = """
    <DayType version="1" id="TEST:DayType:WeekdayId"/>
    """
    assert_xml_equal(result_xml, expected_xml)

def test_netex_helper_build_day_type_returns_none_when_id_is_missing():
    """
    Test if entity is missing and `id` field, None is returned
    """
    entity = {
        "type": "GtfsCalendarDateRule",
        "hasService": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsService:TestCity:WeekdayId"
            },
           
            "appliesOn": {
                "type": "Property",
                "value": "20260414"
            },
            
            "exceptionType": {
                "type": "Property",
                "value": 1
            }
        }
    
    result_xml = netex_helper_build_day_type(entity)

    assert result_xml is None

def test_netex_helper_build_day_type_returns_none_when_type_is_missing():
    """
    Test if entity is missing and `type` field, None is returned
    """
    entity = {
        "id": f"urn:ngsi-ld:GtfsCalendarRule:TestCity:WeekdayId",
           
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
    }
    
    result_xml = netex_helper_build_day_type(entity)

    assert result_xml is None
    

def test_netex_helper_build_day_type_returns_none_when_encountering_an_unsupported_type(caplog):
    """
    Test that when encountering an unsupported GTFS type, None is returned
    """
    entity = {"id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1", "type": "GtfsStop"}

    result_xml = netex_helper_build_day_type(entity)

    assert result_xml is None
    assert "Unsupported entity type" in caplog.text


def test_netex_helper_build_day_type_returns_none_if_id_format_is_not_correct(caplog):
    """
    Test that if the `id` field is not in the correct format, None is returned
    """
    entity = {
        "id": "broken_id",
        "type": "GtfsCalendarDateRule",
        "hasService": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsService:TestCity:WeekdayId"
            },
           
            "appliesOn": {
                "type": "Property",
                "value": "20260414"
            },
            
            "exceptionType": {
                "type": "Property",
                "value": 1
            }
        }
    
    result_xml = netex_helper_build_day_type(entity)

    assert result_xml is None
    assert "Invalid ID" in caplog.text


