import pytest
import config
from unittest.mock import Mock
import netex.netex_utils as netex_utils
from netex.netex_utils import netex_get_all_gtfs_trips_of_a_route

def test_netex_get_all_gtfs_trips_of_a_route():

    config.NETEX_OPERATING_CITY = "Sofia"

    route_id = "urn:ngsi-ld:GtfsRoute:Sofia:72"

    mock_trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:72_111",
            "type": "GtfsTrip",
            "route": {"type": "Relationship", "object": "urn:ngsi-ld:GtfsRoute:Sofia:72"}
        }
    ]

    netex_utils.orion_ld_define_header = Mock(return_value={"test": "header"})

    netex_utils.orion_ld_get_entities_by_query_expression = Mock(return_value=mock_trips)

    result = netex_utils.netex_get_all_gtfs_trips_of_a_route(route_id)

    assert result == mock_trips

    netex_utils.orion_ld_define_header.assert_called_once_with("gtfs_static")

    netex_utils.orion_ld_get_entities_by_query_expression.assert_called_once_with("GtfsTrip",
                                                                                  {"test": "header"},
                                                                                  f'route=="{route_id}"',
                                                                                  "Sofia"
                                                                                  )
    

def test_netex_get_all_gtfs_trips_of_a_route_without_operating_city():

    config.NETEX_OPERATING_CITY = None

    with pytest.raises(ValueError) as err:
        netex_get_all_gtfs_trips_of_a_route("urn:ngsi-ld:GtfsRoute:Sofia:72")
        
    assert "Parameter config.NETEX_OPERATING_CITY is not set" in str(err.value)