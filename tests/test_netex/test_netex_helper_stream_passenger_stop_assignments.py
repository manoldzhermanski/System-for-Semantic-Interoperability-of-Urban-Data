import logging
from io import BytesIO
from lxml import etree

from netex.netex_utils import netex_helper_stream_passenger_stop_assignments

def parse_streamed_xml(output: BytesIO) -> etree._Element:
    """
    Parses streamed XML output into an lxml root element.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    return etree.fromstring(output.getvalue(), parser=parser)


def test_stream_passenger_stop_assignments_success():
    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop",
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop2",
            "type": "GtfsStop",
        },
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:
        netex_helper_stream_passenger_stop_assignments(xf, entities)

    root = parse_streamed_xml(output)

    assert root.tag == "stopAssignments"

    stop_assignments = root.findall("PassengerStopAssignment")

    assert len(stop_assignments) == 2


def test_stream_passenger_stop_assignments_deduplicates():
    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop",
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop",
        },
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:
        netex_helper_stream_passenger_stop_assignments(xf, entities)

    root = parse_streamed_xml(output)

    passenger_stop_assignments = root.findall("PassengerStopAssignment")

    assert len(passenger_stop_assignments) == 1


def test_stream_passenger_stop_assignments_logs(caplog):
    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop",
        }
    ]

    output = BytesIO()

    with caplog.at_level(logging.INFO):
        with etree.xmlfile(output, encoding="utf-8") as xf:
            netex_helper_stream_passenger_stop_assignments(xf, entities)

    assert "Streaming PassengerStopAssignments" in caplog.text
    assert "Finished streaming 1 PassengerStopAssignments" in caplog.text