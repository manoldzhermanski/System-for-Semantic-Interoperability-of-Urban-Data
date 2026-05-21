import pytest
import logging
from io import BytesIO
from lxml import etree
from netex.netex_utils import netex_helper_stream_scheduled_stop_points

@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")


def parse_streamed_xml(output: BytesIO) -> etree._Element:
    """
    Parses streamed XML output into an lxml root element.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    return etree.fromstring(output.getvalue(), parser=parser)

def test_stream_scheduled_stop_points_success():
    """
    Test ScheduledStopPoints are streamed correctly.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop"
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop2",
            "type": "GtfsStop"
        }
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_scheduled_stop_points(xf, entities)

    root = parse_streamed_xml(output)

    scheduled_stop_points = root.findall("ScheduledStopPoint")

    assert len(scheduled_stop_points) == 2


def test_stream_scheduled_stop_points_removes_duplicates():
    """
    Test duplicate ScheduledStopPoints are streamed only once.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop"
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop"
        }
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_scheduled_stop_points(xf, entities)

    root = parse_streamed_xml(output)

    scheduled_stop_points = root.findall("ScheduledStopPoint")

    assert len(scheduled_stop_points) == 1


def test_stream_scheduled_stop_points_skips_invalid_entities():
    """
    Test invalid entities are skipped.
    """

    entities = [
        {
            "id": "broken_id",
            "type": "GtfsStop"
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop"
        }
    ]

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_scheduled_stop_points(xf, entities)

    root = parse_streamed_xml(output)

    scheduled_stop_points = root.findall("ScheduledStopPoint")

    assert len(scheduled_stop_points) == 1


def test_stream_scheduled_stop_points_logs_info(caplog):
    """
    Test informational logs are emitted.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop"
        }
    ]

    output = BytesIO()

    with caplog.at_level(logging.INFO):

        with etree.xmlfile(output, encoding="utf-8") as xf:

            netex_helper_stream_scheduled_stop_points(xf, entities)

    assert "Streaming ScheduledStopPoints" in caplog.text

    assert "Finished streaming 1 ScheduledStopPoints" in caplog.text