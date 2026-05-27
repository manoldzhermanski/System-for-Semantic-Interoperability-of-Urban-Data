import pytest
import config
import netex.netex_utils as netex_utils
from unittest.mock import Mock
from netex.netex_utils import netex_get_all_gtfs_routes_of_an_agency


def test_netex_get_all_gtfs_routes_of_an_agency():

    config.NETEX_OPERATING_CITY = "Sofia"

    agency_id = "urn:ngsi-ld:GtfsAgency:Sofia:A"

    mock_routes = [
        {
            "id": "urn:ngsi-ld:GtfsRoute:Sofia:72",
            "type": "GtfsRoute"
        }
    ]

    netex_utils.orion_ld_define_header = Mock(return_value={"test": "header"})

    netex_utils.orion_ld_get_entities_by_query_expression = Mock(return_value=mock_routes)

    result = netex_utils.netex_get_all_gtfs_routes_of_an_agency(agency_id)

    assert result == mock_routes

    netex_utils.orion_ld_define_header.assert_called_once_with("gtfs_static")

    netex_utils.orion_ld_get_entities_by_query_expression.assert_called_once_with("GtfsRoute",
                                                                                  {"test": "header"},
                                                                                  f'operatedBy=="{agency_id}"',
                                                                                  "Sofia"
                                                                                  )

def test_netex_get_all_gtfs_routes_of_an_agency_without_operating_city():

    config.NETEX_OPERATING_CITY = None

    with pytest.raises(ValueError) as err:
        netex_get_all_gtfs_routes_of_an_agency("urn:ngsi-ld:GtfsAgency:Sofia:A")
         
    assert "Parameter config.NETEX_OPERATING_CITY is not set" in str(err.value)     

