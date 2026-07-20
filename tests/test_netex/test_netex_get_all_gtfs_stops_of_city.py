import pytest
import config
from unittest.mock import Mock
import netex.netex_utils as netex_utils


def test_netex_get_all_gtfs_stops_of_city_success():
    """
    Test that if get_operating_city() is set, the GET request is sent
    """
    config.set_operating_city("Sofia")

    mock_entities = [{"id": "urn:ngsi-ld:GtfsStop:Sofia:A"}]

    netex_utils.fiware_scorpio_get_entities_by_type = Mock(return_value=mock_entities)
    netex_utils.fiware_scorpio_define_header = Mock(return_value={"test": "header"})

    result = netex_utils.netex_get_all_gtfs_stops_of_city()

    assert result == mock_entities

def test_netex_get_all_gtfs_stops_of_city_without_city():
    """
    Test that ValueError is raised when get_operating_city() is not set
    """
    config.OPERATING_CITY = None

    with pytest.raises(RuntimeError):
        netex_utils.netex_get_all_gtfs_stops_of_city()