import pytest
from lxml import etree

from netex.netex_utils import netex_convert_stops_to_stop_place

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")
    
def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TestCity:TestStop",
            "name": {"type": "Property","value": "Central Station"},
            "code": {"type": "Property","value": "100"},
            "description": {"type": "Property","value": "Main hub"},
            "location": {"type": "GeoProperty", "value": {"type": "Point", "coordinates": [23.0, 42.0]}},
            "locationType": {"type": "Property", "value": 0},
            "wheelchair_boarding": {"type": "Property", "value": 1},
            "hasParentStation": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsStop:TestCity:ParentStop"},
        }
    ]

    result_xml = netex_convert_stops_to_stop_place(entities, {})

    expected_xml = """<StopPlace version="1" id="TEST:StopPlace:TestStop">
                            <Name>Central Station</Name>
                            <Description>Main hub</Description>
                            <PublicCode>100</PublicCode>
                            <Centroid>
                            <Location>
                                <Longitude>23.0</Longitude>
                                <Latitude>42.0</Latitude>
                            </Location>
                            </Centroid>
                            <AccessibilityAssessment version="1" id="TEST:AccessibilityAssessment:1">
                                <MobilityImpairedAccess>partial</MobilityImpairedAccess>
                                <limitations>
                                    <AccessibilityLimitation  version="1" id="1">
                                        <WheelchairAccess>true</WheelchairAccess>
                                        <StepFreeAccess>unknown</StepFreeAccess>
                                        <EscalatorFreeAccess>unknown</EscalatorFreeAccess>
                                        <LiftFreeAccess>unknown</LiftFreeAccess>
                                        <AudibleSignalsAvailable>unknown</AudibleSignalsAvailable>
                                        <VisualSignsAvailable>unknown</VisualSignsAvailable>
                                    </AccessibilityLimitation>
                                </limitations>
                            </AccessibilityAssessment>
                            <ParentSiteRef ref="TEST:StopPlace:ParentStop" version="1"/>
                            <TransportMode>bus</TransportMode>
                            <StopPlaceType>busStation</StopPlaceType>
                            <quays>
                                <Quay version="1" id="TEST:Quay:TestStop">
                                    <PublicCode>100</PublicCode>
                                    <Centroid>
                                        <Location>
                                            <Longitude>23.0</Longitude>
                                            <Latitude>42.0</Latitude>
                                        </Location>
                                    </Centroid>
                                </Quay>
                            </quays>
                        </StopPlace>
                    """
    
    assert_xml_equal(result_xml, expected_xml)