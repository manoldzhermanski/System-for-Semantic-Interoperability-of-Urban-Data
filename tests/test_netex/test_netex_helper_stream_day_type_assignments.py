import pytest
import logging
from lxml import etree
from io import BytesIO
from netex.netex_utils import netex_helper_stream_day_type_assignments


@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")

def parse_streamed_xml(output: BytesIO) -> etree._Element:
    """
    Parses streamed XML output into an lxml root element.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    return etree.fromstring(output.getvalue(), parser=parser)


def test_stream_day_type_assignment_writes_day_type_assignmentss():
    """
    Test that valid DayType XML elements are written.
    """

    entities = [
        {
        "id": "urn:ngsi-ld:GtfsCalendarRule:TestCity:WeekdayId",
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
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:
        netex_helper_stream_day_type_assignments(xf, entities)

    root = parse_streamed_xml(output)

    assert root.tag == "dayTypeAssignments"

    day_types = root.findall("DayTypeAssignment")

    assert len(day_types) == 1

    assert day_types[0].get("id") == "TEST:DayTypeAssignment:WeekdayId_1"


def test_stream_day_type_assignments_skips_invalid_entities():
    """
    Test that invalid entities are skipped.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TestCity:Stop1",
            "type": "GtfsStop"
        }
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:
        netex_helper_stream_day_type_assignments(xf, entities)

    root = parse_streamed_xml(output)

    day_types = root.findall("DayType")

    assert len(day_types) == 0


def test_stream_day_type_assignmentss_empty_input():
    """
    Test that empty input still creates <dayTypeAssignments>.
    """

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:
        netex_helper_stream_day_type_assignments(xf, [])

    root = parse_streamed_xml(output)

    assert root.tag == "dayTypeAssignments"

    assert len(root.findall("DayTypeAssignment")) == 0


def test_stream_day_type_assignments_logs_info(caplog):
    """
    Test that informational logs are emitted.
    """

    entities = [
        {
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
    ]

    output = BytesIO()

    with caplog.at_level(logging.INFO):

        with etree.xmlfile(output, encoding="utf-8") as xf:
            netex_helper_stream_day_type_assignments(xf, entities)

    assert "Streaming DayTypeAssignment" in caplog.text

    assert "Finished streaming 1 DayTypeAssignment" in caplog.text