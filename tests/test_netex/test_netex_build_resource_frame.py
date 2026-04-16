import pytest
from lxml import etree
from netex.netex_utils import netex_build_resource_frame


def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)
def test_build_resource_frame_structure_and_content():
    """
    Tests that the ResourceFrame is built correctly, with all organisations.
    """

    city_name = "MyCity"
    input_agencies = [
        {
            "id": "urn:ngsi-ld:Agency:ID1",
            "agency_name": {"value": "City Transit"},
            "agency_fare_url": {"value": "http://city-transit.com/fares"}
        }
    ]

    result_frame = netex_build_resource_frame(input_agencies, city_name)

    expected_xml = """
    <ResourceFrame version="1" id="MyCity:ResourceFrame:1">
      <organisations>
        <Authority version="1" id="ID1:Authority:ID1_ID">
            <CompanyNumber>1</CompanyNumber>
            <Name>City Transit</Name>
            <LegalName>City Transit</LegalName>
            <ContactDetails>
                <Url>http://city-transit.com/fares</Url>
            </ContactDetails>
            <OrganisationType>authority</OrganisationType>
        </Authority>
        <Operator version="1" id="ID1:Operator:ID1">
            <CompanyNumber>1</CompanyNumber>
            <Name>City Transit</Name>
            <LegalName>City Transit</LegalName>
            <ContactDetails>
                <Url>http://city-transit.com/fares</Url>
            </ContactDetails>
            <OrganisationType>operator</OrganisationType>
        </Operator>
      </organisations>
    </ResourceFrame>
    """
    assert_xml_equal(result_frame, expected_xml)