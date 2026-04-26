import pytest
from lxml import etree # type: ignore
from netex.netex_utils import netex_convert_agency_to_authority

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

def test_single_agency_full_details():
    """
    Tests the happy path with a single agency having all contact details.
    """
    input_agencies = [
        {
            "id": "urn:ngsi-ld:GtfsAgency:TESTCITY:ID1",
            "agency_name": {"value": "City Transit"},
            "agency_phone": {"value": "555-0100"},
            "agency_fare_url": {"value": "http://city-transit.com/fares"},
            "agency_email": {"value": "contact@city-transit.com"},
        }
    ]

    result_list = netex_convert_agency_to_authority(input_agencies)

    expected_xml = """
    <Authority version="1" id="TEST:Authority:ID1_ID">
        <CompanyNumber>1</CompanyNumber>
        <Name>City Transit</Name>
        <LegalName>City Transit</LegalName>
        <ContactDetails>
            <Email>contact@city-transit.com</Email>
            <Phone>555-0100</Phone>
            <Url>http://city-transit.com/fares</Url>
        </ContactDetails>
        <OrganisationType>authority</OrganisationType>
    </Authority>
    """
    assert_xml_equal(result_list[0], expected_xml)


def test_single_agency_minimal_details():
    """
    Tests an agency with no optional contact details.
    Note: This also tests the behavior of creating an empty <Url/> tag.
    """
    input_agencies = [
        {
            "id": "urn:ngsi-ld:GtfsAgency:TESTCITY:ID1",
            "agency_name": {"value": "City Transit"},
            "agency_fare_url": {"value": "http://city-transit.com/fares"}
        }
    ]

    result_list = netex_convert_agency_to_authority(input_agencies)

    expected_xml = """
    <Authority version="1" id="TEST:Authority:ID1_ID">
        <CompanyNumber>1</CompanyNumber>
        <Name>City Transit</Name>
        <LegalName>City Transit</LegalName>
        <ContactDetails>
            <Url>http://city-transit.com/fares</Url>
        </ContactDetails>
        <OrganisationType>authority</OrganisationType>
    </Authority>
    """
    assert_xml_equal(result_list[0], expected_xml)


def test_with_two_agencies():

    input_agencies = [
        {
            "id": "urn:ngsi-ld:GtfsAgency:TESTCITY:ID1",
            "agency_name": {"value": "City Transit"},
            "agency_fare_url": {"value": "http://city-transit.com/fares"},
        },
        {
            "id": "urn:ngsi-ld:GtfsAgency:TESTCITY:ID2",
            "agency_name": {"value": "City Transit 2"},
            "agency_fare_url": {"value": "http://city-transit.com/fares2"},
        }
    ]

    organisations = etree.Element("organisations")
    result_list = netex_convert_agency_to_authority(input_agencies)
    for result in result_list:
        organisations.append(result)

    expected_xml = """
    <organisations>
        <Authority version="1" id="TEST:Authority:ID1_ID">
            <CompanyNumber>1</CompanyNumber>
            <Name>City Transit</Name>
            <LegalName>City Transit</LegalName>
            <ContactDetails>
                <Url>http://city-transit.com/fares</Url>
            </ContactDetails>
            <OrganisationType>authority</OrganisationType>
        </Authority>
        <Authority version="1" id="TEST:Authority:ID2_ID">
            <CompanyNumber>2</CompanyNumber>
            <Name>City Transit 2</Name>
            <LegalName>City Transit 2</LegalName>
            <ContactDetails>
                <Url>http://city-transit.com/fares2</Url>
            </ContactDetails>
            <OrganisationType>authority</OrganisationType>
        </Authority>
    </organisations>
    """

    assert_xml_equal(organisations, expected_xml)