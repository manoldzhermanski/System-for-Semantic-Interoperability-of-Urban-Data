import pytest
import lxml.etree as etree
import netex.netex_utils as netex_utils
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import UUID


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
    
@patch("netex.netex_utils.uuid.uuid4")
def test_netex_helper_build_stop_place_returns_expected_xml(mock_uuid):
    """
    Test happy path
    """
    mock_uuid.side_effect = [
        UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    ]
    
    entity = {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop",    
            "code": {"type": "Property", "value": "2545"},
            "name": {"type": "Property", "value": "Stop1"},
            "tts_stop_name":{"type": "Property","value": "Stop1"},
            "description": {"type": "Property", "value": "Stop 1"},
            "location": {
                "type": "GeoProperty",
                "value": {"type": "Point","coordinates": [42.0, 23.0]}},
            "hasParentStation": {"type": "Relationship","object": "urn:ngsi-ld:GtfsStop:TEST:Stop0"},
            "wheelchair_boarding": {"type": "Property", "value": 1},
        }
    
    result_xml = netex_utils.netex_helper_build_stop_place(entity, {"urn:ngsi-ld:GtfsStop:TEST:Stop1": {('bus', 'unknown')}})
    
    expected_xml = """
        <StopPlace version="1" id="TEST:StopPlace:Stop1">
            <Name>Stop1</Name>
            <Description>Stop 1</Description>
            <PublicCode>2545</PublicCode>
            <AccessibilityAssessment version="1" id="TEST:AccessibilityAssessment:aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa">
                <MobilityImpairedAccess>partial</MobilityImpairedAccess>
                <limitations>
                    <AccessibilityLimitation version="1" id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb">
                        <WheelchairAccess>true</WheelchairAccess>
                        <StepFreeAccess>unknown</StepFreeAccess>
                        <EscalatorFreeAccess>unknown</EscalatorFreeAccess>
                        <LiftFreeAccess>unknown</LiftFreeAccess>
                        <AudibleSignalsAvailable>true</AudibleSignalsAvailable>
                        <VisualSignsAvailable>unknown</VisualSignsAvailable>
                    </AccessibilityLimitation>
                </limitations>
            </AccessibilityAssessment>
            <ParentSiteRef ref="TEST:StopPlace:Stop0" version="1"></ParentSiteRef>
            <TransportMode>bus</TransportMode>
            <BusSubmode>unknown</BusSubmode>
            <StopPlaceType>onstreetBus</StopPlaceType>
            <quays>
                <Quay version="1" id="TEST:Quay:Stop1">
                    <PublicCode>2545</PublicCode>
                    <Centroid>
                        <Location>
                            <Longitude>42.0</Longitude>
                            <Latitude>23.0</Latitude>
                        </Location>
                    </Centroid>
                </Quay>
            </quays>
        </StopPlace>
    """
    assert_xml_equal(result_xml, expected_xml)
    
def test_netex_helper_build_stop_place_returns_none_when_encountering_an_unsupported_type():
    """
    Test that when encountering an unsupported GTFS type, None is returned
    """
    entity = {"id": "urn:ngsi-ld:GtfsShape:TestCity:Stop1", "type": "GtfsShape"}

    netex_utils.logger.error = MagicMock()
    
    result_xml = netex_utils.netex_helper_build_stop_place(entity, {"urn:ngsi_ld:GtfsStop:TEST:Stop1": {('bus', 'unknown')}})

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Unsupported entity type for StopPlace conversion: %s", "GtfsShape")
    
def test_netex_helper_build_stop_place_returns_none_if_id_format_is_not_correct():
    """
    Test that if the `id` field is not in the correct format, None is returned
    """
    entity = {
        "id": "broken_id",
        "type": "GtfsStop",    
        "code": {"type": "Property", "value": "2545"},
        "name": {"type": "Property", "value": "Stop1"},
        "tts_stop_name":{"type": "Property","value": "Stop1"},
        "description": {"type": "Property", "value": "Stop 1"},
        "location": {
            "type": "GeoProperty",
            "value": {"type": "Point","coordinates": [42.0, 23.0]}},
        "hasParentStation": {"type": "Relationship","object": "urn:ngsi-ld:GtfsStop:TEST:Stop0"},
        "wheelchair_boarding": {"type": "Property", "value": 1},
    }
    
    netex_utils.logger.error = MagicMock()

    result_xml = netex_utils.netex_helper_build_stop_place(entity, {"urn:ngsi_ld:GtfsStop:TEST:Stop1": {('bus', 'unknown')}})

    assert result_xml is None
    netex_utils.logger.error.assert_called_once_with("Invalid or missing ID for GtfsStop: %r", "broken_id")