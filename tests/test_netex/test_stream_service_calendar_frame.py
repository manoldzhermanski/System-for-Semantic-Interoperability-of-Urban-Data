import pytest
import logging
from lxml import etree
from io import BytesIO
from unittest.mock import MagicMock

from netex.netex_utils import netex_stream_service_calendar_frame


@pytest.fixture(autouse=True)
def set_netex_authority(monkeypatch):
    monkeypatch.setattr("netex.netex_utils.config.NETEX_AUTHORITY", "TEST")

def test_service_calendar_frame_structure():

    xml_output = BytesIO()

    calendars = []
    calendar_dates = []

    with etree.xmlfile(xml_output, encoding="utf-8") as xf:
        netex_stream_service_calendar_frame(xf, calendars, calendar_dates)

    xml_str = xml_output.getvalue().decode()

    assert "<ServiceCalendarFrame" in xml_str
    assert 'version="1"' in xml_str
    assert "TEST:ServiceCalendarFrame:1" in xml_str

def test_stream_calls_day_types(monkeypatch):
    """
    Ensure day types streamer is called.
    """

    xml_file = MagicMock()
    xml_file.element.return_value.__enter__.return_value = None
    xml_file.element.return_value.__exit__.return_value = None

    mock_day_types = MagicMock()
    mock_operating = MagicMock()
    mock_assignments = MagicMock()

    monkeypatch.setattr("netex.netex_utils.netex_helper_stream_day_types", mock_day_types)
    monkeypatch.setattr("netex.netex_utils.netex_helper_stream_operating_periods", mock_operating)
    monkeypatch.setattr("netex.netex_utils.netex_helper_stream_day_type_assignments", mock_assignments)

    calendars = [{"type": "GtfsCalendarRule"}]
    calendar_dates = [{"type": "GtfsCalendarDateRule"}]

    netex_stream_service_calendar_frame(xml_file, calendars, calendar_dates)

    all_entities = calendars + calendar_dates

    mock_day_types.assert_called_once_with(xml_file, all_entities)

    mock_operating.assert_called_once_with(xml_file, calendars)

    mock_assignments.assert_called_once_with(xml_file, all_entities)