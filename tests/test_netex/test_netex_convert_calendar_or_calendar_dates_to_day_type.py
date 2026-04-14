import pytest
import logging
from lxml import etree
from netex.netex_utils import netex_convert_calendar_or_calendar_dates_to_day_type

def assert_xml_equal(generated_xml, expected_xml_str):
    """
    Compares two XML elements by parsing the expected string and comparing string dumps.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

# --- Pytest Scenarios ---

def test_netex_convert_calendar_or_calendar_dates_to_day_type_with_gtfs_calendar_rule():
    """Tests a single GtfsCalendarRule entity which should have a <properties> block."""
    entities = [
        {
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
        }
    ]
   
    result_xml = netex_convert_calendar_or_calendar_dates_to_day_type(entities)
   
    expected_xml = """
    <dayTypes>
      <DayType version="1" id="TestCity:DayType:WeekdayId">
        <properties>
          <PropertyOfDay>
            <DaysOfWeek>Weekdays</DaysOfWeek>
          </PropertyOfDay>
        </properties>
      </DayType>
    </dayTypes>
    """
    assert_xml_equal(result_xml, expected_xml)

def test_netex_convert_calendar_or_calendar_dates_to_day_type_with_gtfs_calendar_date_rule():
    """Tests a single GtfsCalendarDateRule entity, which should NOT have a <properties> block."""
    entities = [
        {
            "id": "urn:ngsi-ld:TestCity:WeekdayId:20260414",
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
        ]
   
    result_xml = netex_convert_calendar_or_calendar_dates_to_day_type(entities)
   
    expected_xml = """
    <dayTypes>
      <DayType version="1" id="TestCity:DayType:WeekdayId"/>
    </dayTypes>
    """
    assert_xml_equal(result_xml, expected_xml)

def test_netex_convert_calendar_or_calendar_dates_to_day_type_with_mixed_entities():
    """Tests a list containing both types of entities."""
    entities = [
        {
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
        },
        {
            "id": "urn:ngsi-ld:TestCity:SpecialDay:20260414",
            "type": "GtfsCalendarDateRule",
            "hasService": {
                    "type": "Relationship",
                    "object": f"urn:ngsi-ld:GtfsService:TestCity:SpecialDay"
                },
               
                "appliesOn": {
                    "type": "Property",
                    "value": "20260414"
                },
               
                "exceptionType": {
                    "type": "Property",
                    "value": 1
                }
            },
    ]
   
    result_xml = netex_convert_calendar_or_calendar_dates_to_day_type(entities)
   
    expected_xml = """
    <dayTypes>
      <DayType version="1" id="TestCity:DayType:WeekdayId">
        <properties>
          <PropertyOfDay>
            <DaysOfWeek>Weekdays</DaysOfWeek>
          </PropertyOfDay>
        </properties>
      </DayType>
      <DayType version="1" id="TestCity:DayType:SpecialDay"/>
    </dayTypes>
    """
    assert_xml_equal(result_xml, expected_xml)

def test_netex_convert_calendar_or_calendar_dates_to_day_type_with_empty_list():
    """Tests that an empty input list produces an empty <dayTypes> container."""
    result_xml = netex_convert_calendar_or_calendar_dates_to_day_type([])
    expected_xml = "<dayTypes/>"
    assert_xml_equal(result_xml, expected_xml)

def test_netex_convert_calendar_or_calendar_dates_to_day_type_with_invalid_and_malformed_data():
    """Tests that invalid entities are skipped and do not break the function."""
    entities = [
        {
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
        },
        {"type": "GtfsCalendarRule"}, # Missing ID
        {"id": "invalid-id-format", "type": "GtfsCalendarRule"}, # Invalid ID
        {"id": "some:id", "type": "UnsupportedType"}, # Unknown type
    ]
   
    result_xml = netex_convert_calendar_or_calendar_dates_to_day_type(entities)
   
    # Only the first, valid entity should be processed.
    expected_xml = """
    <dayTypes>
      <DayType version="1" id="TestCity:DayType:WeekdayId">
        <properties>
          <PropertyOfDay>
            <DaysOfWeek>Weekdays</DaysOfWeek>
          </PropertyOfDay>
        </properties>
      </DayType>
    </dayTypes>
    """
    assert_xml_equal(result_xml, expected_xml)