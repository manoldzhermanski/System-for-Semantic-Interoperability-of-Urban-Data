from unittest.mock import MagicMock
import netex.netex_utils as netex_utils


def test_netex_helper_stream_operators_writes_all_authorities():
    """
    Tests that all valid Authority elements are written to the XML file.
    """

    xml_file = MagicMock()

    agencies = [
        {
            "id": "urn:ngsi-ld:GtfsAgency:TEST:A1",
            "type": "GtfsAgency",
            "agency_name":{"type": "Property", "value": "A1"},
            "agency_phone": {"type": "Property", "value": "0895555555"},    
            "agency_fare_url": {"type": "Property", "value": "https://www.a1_transport.bg"},
            "agency_email": {"type": "Property", "value": "a1_transport@gmail.com"}
        },
        {
            "id": "urn:ngsi-ld:GtfsAgency:TEST:A2",
            "type": "GtfsAgency",
            "agency_name":{"type": "Property", "value": "A2"},
            "agency_phone": {"type": "Property", "value": "0895555556"},    
            "agency_fare_url": {"type": "Property", "value": "https://www.a2_transport.bg"},
            "agency_email": {"type": "Property", "value": "a2_transport@gmail.com"}
        },
    ]

    netex_utils.netex_helper_stream_operators(xml_file, agencies)

    assert xml_file.write.call_count == 2
    
def test_netex_helper_stream_operators_skips_invalid_entities():
    """
    Tests that invalid entities are skipped.
    """

    xml_file = MagicMock()

    agencies = [
        {
            "id": "urn:ngsi-ld:GtfsAgency:TEST:A1",
            "type": "GtfsAgency",
            "agency_name":{"type": "Property", "value": "A1"},
            "agency_phone": {"type": "Property", "value": "0895555555"},    
            "agency_fare_url": {"type": "Property", "value": "https://www.a1_transport.bg"},
            "agency_email": {"type": "Property", "value": "a1_transport@gmail.com"}
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:STOP1",
            "type": "GtfsStop",
        },
    ]

    netex_utils.netex_helper_stream_operators(xml_file, agencies)

    assert xml_file.write.call_count == 1
    
def test_netex_helper_stream_operators_skips_duplicate_authorities():
    """
    Tests that duplicate Authority IDs are written only once.
    """

    xml_file = MagicMock()

    entities =[
        {
            "id": "urn:ngsi-ld:GtfsAgency:TEST:A1",
            "type": "GtfsAgency",
            "agency_name":{"type": "Property", "value": "A1"},
            "agency_phone": {"type": "Property", "value": "0895555555"},    
            "agency_fare_url": {"type": "Property", "value": "https://www.a1_transport.bg"},
            "agency_email": {"type": "Property", "value": "a1_transport@gmail.com"}
        },
        {
            "id": "urn:ngsi-ld:GtfsAgency:TEST:A1",
            "type": "GtfsAgency",
            "agency_name":{"type": "Property", "value": "A1"},
            "agency_phone": {"type": "Property", "value": "0895555555"},    
            "agency_fare_url": {"type": "Property", "value": "https://www.a1_transport.bg"},
            "agency_email": {"type": "Property", "value": "a1_transport@gmail.com"}
        }
    ]
    netex_utils.netex_helper_stream_operators(xml_file, entities)

    assert xml_file.write.call_count == 1
    
def test_netex_helper_stream_operators_with_empty_input():
    """
    Tests that no Authority elements are written when the input list is empty.
    """

    xml_file = MagicMock()

    netex_utils.netex_helper_stream_operators(xml_file, [])

    xml_file.write.assert_not_called()