import pytest
import logging
from io import BytesIO
from lxml import etree  # type: ignore

from netex.netex_utils import netex_helper_stream_stop_places


@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")


def parse_streamed_xml(output: BytesIO) -> etree._Element:
    """
    Parses streamed XML output into an lxml root element.
    """
    parser = etree.XMLParser(remove_blank_text=True)

    return etree.fromstring(output.getvalue(), parser=parser)


def test_stream_stop_places_success():
    """
    Test StopPlaces are streamed correctly.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop",
            "name": {"value": "Stop 1"}
        },
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop2",
            "type": "GtfsStop",
            "name": {"value": "Stop 2"}
        }
    ]

    transport_modes_per_stop = {
        "urn:ngsi-ld:GtfsStop:TEST:Stop1": {("bus", "unknown")},
        "urn:ngsi-ld:GtfsStop:TEST:Stop2": {("tram", "unknown")}
    }

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_stop_places(xf, transport_modes_per_stop, entities)

    root = parse_streamed_xml(output)

    stop_places = root.findall("StopPlace")

    assert len(stop_places) == 2
    
def test_stream_stop_places_skips_invalid_entities():
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

    transport_modes_per_stop = {
        "urn:ngsi-ld:GtfsStop:TEST:Stop1": {("bus", "unknown")}
    }

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_stop_places(xf, transport_modes_per_stop, entities)

    root = parse_streamed_xml(output)

    stop_places = root.findall("StopPlace")

    assert len(stop_places) == 1
    
def test_stream_stop_places_removes_duplicates():
    """
    Test duplicate StopPlaces are streamed only once.
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

    transport_modes_per_stop = {
        "urn:ngsi-ld:GtfsStop:TEST:Stop1": {("bus", "unknown")}
    }

    output = BytesIO()

    with etree.xmlfile(output, encoding="utf-8") as xf:

        netex_helper_stream_stop_places(xf, transport_modes_per_stop, entities)

    root = parse_streamed_xml(output)

    stop_places = root.findall("StopPlace")

    assert len(stop_places) == 1
    
def test_stream_stop_places_logs_info(caplog):
    """
    Test informational logs are emitted.
    """

    entities = [
        {
            "id": "urn:ngsi-ld:GtfsStop:TEST:Stop1",
            "type": "GtfsStop"
        }
    ]

    transport_modes_per_stop = {
        "urn:ngsi-ld:GtfsStop:TEST:Stop1": {("bus", "unknown")}
    }

    output = BytesIO()

    with caplog.at_level(logging.INFO):

        with etree.xmlfile(output, encoding="utf-8") as xf:

            netex_helper_stream_stop_places(xf, transport_modes_per_stop, entities)

    assert "Streaming StopPlaces" in caplog.text
    assert "Finished streaming 1 stopPlaces" in caplog.text