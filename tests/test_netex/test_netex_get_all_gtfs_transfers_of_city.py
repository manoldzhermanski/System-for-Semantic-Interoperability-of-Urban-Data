import pytest
import config
from unittest.mock import Mock
import netex.netex_utils as netex_utils


def test_netex_get_all_gtfs_transfers_of_city_success():
    """
    Test that if config.NETEX_OPERATING_CITY is set, the GET request is sent
    """
    config.NETEX_OPERATING_CITY = "Sofia"

    mock_entities = [{"id": "urn:ngsi-ld:GtfsTransfer:Sofia:A"}]

    netex_utils.orion_ld_get_entities_by_type = Mock(return_value=mock_entities)
    netex_utils.orion_ld_define_header = Mock(return_value={"test": "header"})

    result = netex_utils.netex_get_all_gtfs_transfers_of_city()

    assert result == mock_entities

def test_netex_get_all_gtfs_transfers_of_city_without_city():
    """
    Test that ValueError is raised when config.NETEX_OPERATING_CITY is not set
    """
    config.NETEX_OPERATING_CITY = None

    with pytest.raises(ValueError):
        netex_utils.netex_get_all_gtfs_transfers_of_city()