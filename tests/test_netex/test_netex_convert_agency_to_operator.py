import pytest
from lxml import etree
from netex.netex_utils import netex_convert_agency_to_operator

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)
# --- Pytest Test Functions ---

def test_single_operator_full_details():
    """
    Tests converting a single agency with all details to an Operator.
    """

    input_agencies = [
        {
            "id": "urn:ngsi-ld:Agency:CITY_TRANSIT",
            "agency_name": {"value": "City Transit"},
            "agency_phone": {"value": "555-1111"},
            "agency_fare_url": {"value": "http://city.com"},
            "agency_email": {"value": "contact@city.com"},
        }
    ]

    result_list = netex_convert_agency_to_operator(input_agencies)

    expected_xml = """
    <Operator version="1" id="CITY_TRANSIT:Operator:CITY_TRANSIT">
        <CompanyNumber>1</CompanyNumber>
        <Name>City Transit</Name>
        <LegalName>City Transit</LegalName>
        <ContactDetails>
            <Email>contact@city.com</Email>
            <Phone>555-1111</Phone>
            <Url>http://city.com</Url>
        </ContactDetails>
        <OrganisationType>operator</OrganisationType>
    </Operator>
    """
    assert_xml_equal(result_list[0], expected_xml)


def test_two_operators():
    """
    Tests converting two agencies, ensuring the index in the ID is correct.
    This confirms the `enumerate` bug from previous versions is fixed.
    """

    input_agencies = [
        {
            "id": "urn:ngsi-ld:Agency:ID1",
            "agency_name": {"value": "City Transit"},
            "agency_fare_url": {"value": "http://city.com"},
        },
        {
            "id": "urn:ngsi-ld:Agency:ID2",
            "agency_name": {"value": "City Transit 2"},
            "agency_fare_url": {"value": "http://citytwo.com"},
        }
    ]

    organisations = etree.Element("organisations")
    result_list = netex_convert_agency_to_operator(input_agencies)
    for result in result_list:
        organisations.append(result)

    expected_xml = """
    <organisations>
        <Operator version="1" id="ID1:Operator:ID1">
            <CompanyNumber>1</CompanyNumber>
            <Name>City Transit</Name>
            <LegalName>City Transit</LegalName>
            <ContactDetails>
                <Url>http://city.com</Url>
            </ContactDetails>
            <OrganisationType>operator</OrganisationType>
        </Operator>
        <Operator version="1" id="ID2:Operator:ID2">
            <CompanyNumber>2</CompanyNumber>
            <Name>City Transit 2</Name>
            <LegalName>City Transit 2</LegalName>
            <ContactDetails>
                <Url>http://citytwo.com</Url>
            </ContactDetails>
            <OrganisationType>operator</OrganisationType>
        </Operator>
    </organisations>
    """
    assert_xml_equal(organisations, expected_xml)
