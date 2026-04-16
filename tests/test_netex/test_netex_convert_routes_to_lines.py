import pytest
from lxml import etree
from netex.netex_utils import netex_convert_routes_to_lines

def assert_xml_equal(generated_xml, expected_xml_str):
    """Compares two XML elements for equivalence."""
    parser = etree.XMLParser(remove_blank_text=True)

    expected = etree.fromstring(expected_xml_str, parser)
    generated = etree.fromstring(etree.tostring(generated_xml), parser)

    assert etree.tostring(generated) == etree.tostring(expected)

def test_with_full_route_data():
    entity = {
            "id": f"urn:ngsi-ld:GtfsRoute:TestCity:T1",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsAgency:TestCity:A1"
            },
            
            "shortName": {
                "type": "Property", 
                "value": "Short Name"
            },
            
            "name": {
                "type": "Property", 
                "value": "Name"
            },
            
            "description": {
                "type": "Property", 
                "value": "Description"
            },
            
            "routeType": {
                "type": "Property", 
                "value": 100
            },
            
            "route_url": {
                "type": "Property", 
                "value": "https://test.com"
            },
            
            "routeColor": {
                "type": "Property", 
                "value": "FFFFFF"
            },
            
            "routeTextColor": {
                "type": "Property", 
                "value": "FFFFFF"
            },
            
            "routeSortOrder": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_pickup": {
                "type": "Property", 
                "value": 0
            },
            
            "continuous_drop_off": {
                "type": "Property", 
                "value": 0
            },
            
            "network_id": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsNetwork:TestCity:N1"
            },
            
            "cemv_support": {
                "type": "Property", 
                "value": 0
            }
        }

    result = netex_convert_routes_to_lines(entity)

    expected_xml = """
    <Line version="1" id="TestCity:Line:T1">
        <Name>Name</Name>
        <Description>Description</Description>
        <TransportMode>rail</TransportMode>
        <TransportSubmode>
            <RailSubmode>unknown</RailSubmode>
        </TransportSubmode>
        <Url>https://test.com</Url>
        <PublicCode>Short Name</PublicCode>
        <OperatorRef ref="A1:Operator:A1"/>
        <RepresentedByGroupRef ref="A1:Authority:A1Nett"/>
        <Presentation>
            <Colour>FFFFFF</Colour>
            <TextColour>FFFFFF</TextColour>
        </Presentation>
    </Line>
    """

    assert_xml_equal(result, expected_xml)


def test_minimal_route():
    entity = {
            "id": f"urn:ngsi-ld:GtfsRoute:TestCity:T1",
            "type": "GtfsRoute",
            
            "operatedBy": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsAgency:TestCity:A1"
            },
            
            "shortName": {
                "type": "Property", 
                "value": "Short Name"
            },
            
            "name": {
                "type": "Property", 
                "value": "Name"
            },
            
            "routeType": {
                "type": "Property", 
                "value": 100
            }    
        }

    result = netex_convert_routes_to_lines(entity)

    expected_xml = """
    <Line version="1" id="TestCity:Line:T1">
        <Name>Name</Name>
        <TransportMode>rail</TransportMode>
        <TransportSubmode>
            <RailSubmode>unknown</RailSubmode>
        </TransportSubmode>
        <PublicCode>Short Name</PublicCode>
        <OperatorRef ref="A1:Operator:A1"/>
        <RepresentedByGroupRef ref="A1:Authority:A1Nett"/>
    </Line>
    """

    assert_xml_equal(result, expected_xml)


@pytest.mark.parametrize(
    "route_type, expected_mode, expected_submode_tag",
    [
        (100, "rail", "RailSubmode"),
        (401, "metro", "MetroSubmode"),
        (700, "bus", "BusSubmode"),
        (900, "tram", "TramSubmode"),
        (1000, "water", "WaterSubmode"),
    ]
)
def test_transport_modes(route_type, expected_mode, expected_submode_tag):
    entity = {
        "id": "urn:ngsi-ld:Route:Sofia:10",
        "routeType": {"value": route_type}
    }

    result = netex_convert_routes_to_lines(entity)

    assert result.find("TransportMode").text == expected_mode
    assert result.find(f"TransportSubmode/{expected_submode_tag}") is not None


def test_operator_refs():
    entity = {
        "id": "urn:ngsi-ld:Route:Sofia:10",
        "routeType": {"value": 700},
        "operatedBy": {"object": "urn:ngsi-ld:Agency:Sofia:TA"}
    }

    result = netex_convert_routes_to_lines(entity)

    assert result.find("OperatorRef") is not None
    assert result.find("RepresentedByGroupRef") is not None


def test_presentation_only_colour():
    entity = {
        "id": "urn:ngsi-ld:Route:Sofia:10",
        "routeType": {"value": 700},
        "routeColor": {"value": "FFFFFF"}
    }

    result = netex_convert_routes_to_lines(entity)

    assert result.find("Presentation/Colour").text == "FFFFFF"


def test_presentation_only_text_colour():
    entity = {
        "id": "urn:ngsi-ld:Route:Sofia:10",
        "routeType": {"value": 700},
        "routeTextColor": {"value": "000000"}
    }

    result = netex_convert_routes_to_lines(entity)

    expected_xml = """
    <Line version="1" id="TestCity:Line:T1">
        <Name>Name</Name>
        <Description>Description</Description>
        <TransportMode>rail</TransportMode>
        <TransportSubmode>
            <RailSubmode>unknown</RailSubmode>
        </TransportSubmode>
        <Url>https://test.com</Url>
        <PublicCode>Short Name</PublicCode>
        <OperatorRef ref="TestCity:Operator:A1"/>
        <RepresentedByGroupRef ref="TestCity:Authority:A1Nett"/>
        <Presentation>
            <Colour>FFFFFF</Colour>
            <TextColour>FFFFFF</TextColour>
        </Presentation>
    </Line>
    """

    assert result.find("Presentation/TextColour").text == "000000"


def test_missing_route_type():
    entity = {
        "id": "urn:ngsi-ld:Route:Sofia:10"
    }

    with pytest.raises(ValueError):
        netex_convert_routes_to_lines(entity)