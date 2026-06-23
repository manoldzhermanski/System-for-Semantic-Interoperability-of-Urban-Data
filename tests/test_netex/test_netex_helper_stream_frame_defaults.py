from unittest.mock import MagicMock
from lxml import etree # type: ignore
import netex.netex_utils as netex_utils

def test_netex_helper_stream_frame_defaults_writes_xml():
    """
    Test happy path
    """
    agency = {
        "type": "GtfsAgency",
        "agency_timezone": {"value": "Europe/Sofia"},
        "agency_lang": {"value": "bg"}
    }

    xml_file = MagicMock()

    netex_utils.netex_helper_stream_frame_defaults(xml_file, agency)

    xml_file.write.assert_called_once()

    element = xml_file.write.call_args.args[0]

    assert element.tag == "FrameDefaults"
    
def test_netex_helper_stream_frame_defaults_does_not_write_invalid_entity():
    """
    Test that netex_helper_stream_frame_defaults does not write if an invalid agency is given as input
    """
    agency = {"type": "GtfsStop"}

    xml_file = MagicMock()

    netex_utils.netex_helper_stream_frame_defaults(xml_file, agency)

    xml_file.write.assert_not_called()