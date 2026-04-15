import pytest
from lxml import etree
from typing import Any, Dict
from netex.netex_utils import netex_build_frame_defaults
# --- Custom Assertion Helper ---

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)


def test_with_full_agency_data():
    agency = {
        "id": f"urn:ngsi-ld:GtfsAgency:Sofia:TA",
        "type": "GtfsAgency",
           
        "agency_name":{
            "type": "Property",
            "value": "TestAgency"
        },

        "agency_url": {
            "type": "Property",
            "value": "https://agency.com"
        },
           
        "agency_timezone": {
            "type": "Property",
            "value": "Europe/Sofia"
        },

        "agency_lang": {
            "type": "Property",
            "value": "bg"
        },
    }
   
    result_xml = netex_build_frame_defaults(agency)

   
    expected_xml_str = """
    <FrameDefaults>
        <DefaultLocale>
            <TimeZone>Europe/Sofia</TimeZone>
            <DefaultLanguage>bg</DefaultLanguage>
        </DefaultLocale>
    </FrameDefaults>
    """
   
    assert_xml_equal(result_xml, expected_xml_str)


@pytest.mark.parametrize(
    "agency_data, expected_timezone",
    [
        (
            {
            "id": f"urn:ngsi-ld:GtfsAgency:Sofia:TA",
                "type": "GtfsAgency",
                   
                "agency_name":{
                    "type": "Property",
                    "value": "TestAgency"
                },

                "agency_url": {
                    "type": "Property",
                    "value": "https://agency.com"
                },
                   
                "agency_timezone": {
                    "type": "Property",
                    "value": "Europe/Sofia"
                }
            }
        ),
        (
            {
                "id": f"urn:ngsi-ld:GtfsAgency:Sofia:TA",
                "type": "GtfsAgency",
                   
                "agency_name":{
                    "type": "Property",
                    "value": "TestAgency"
                },

                "agency_url": {
                    "type": "Property",
                    "value": "https://agency.com"
                },
                   
                "agency_timezone": {
                    "type": "Property",
                    "value": "Europe/Sofia"
                },

                "agency_lang": {
                    "type": "Property",
                    "value": None
                }
            }
        )
    ]
)
def test_without_language(agency_data, expected_timezone):
    """
    Tests cases where the language should NOT be included in the output.
    """

    result_xml = netex_build_frame_defaults(agency_data)

    expected_xml_str = f"""
    <FrameDefaults>
        <DefaultLocale>
            <TimeZone>{expected_timezone}</TimeZone>
        </DefaultLocale>
    </FrameDefaults>
    """

    assert_xml_equal(result_xml, expected_xml_str)