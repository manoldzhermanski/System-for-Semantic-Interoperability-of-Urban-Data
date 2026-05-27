import pytest
import config
import netex.netex_utils as netex_utils
from unittest.mock import Mock
from netex.netex_utils import netex_get_all_trips_of_an_agency

def test_netex_get_all_trips_of_an_agency_success():

    config.NETEX_OPERATING_CITY = "Sofia"

    agency_id = "urn:ngsi-ld:GtfsAgency:Sofia:A"

    mock_routes = [
        {"id": "urn:ngsi-ld:GtfsRoute:Sofia:72"},
        {"id": "urn:ngsi-ld:GtfsRoute:Sofia:94"}
    ]

    mock_route_72_trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:72_111"
        }
    ]

    mock_route_94_trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:94_222"
        }
    ]

    netex_utils.netex_get_all_gtfs_routes_of_an_agency = Mock(return_value=mock_routes)

    netex_utils.netex_get_all_gtfs_trips_of_a_route = Mock(
        side_effect=[
            mock_route_72_trips,
            mock_route_94_trips
        ]
    )

    result = netex_utils.netex_get_all_trips_of_an_agency(agency_id)

    assert result == (mock_route_72_trips + mock_route_94_trips)

    netex_utils.netex_get_all_gtfs_routes_of_an_agency.assert_called_once_with(agency_id)

    assert netex_utils.netex_get_all_gtfs_trips_of_a_route.call_count == 2

    netex_utils.netex_get_all_gtfs_trips_of_a_route.assert_any_call("urn:ngsi-ld:GtfsRoute:Sofia:72")

    netex_utils.netex_get_all_gtfs_trips_of_a_route.assert_any_call("urn:ngsi-ld:GtfsRoute:Sofia:94")
    
def test_netex_get_all_trips_of_an_agency_skips_routes_without_id():

    config.NETEX_OPERATING_CITY = "Sofia"

    agency_id = "urn:ngsi-ld:GtfsAgency:Sofia:A"

    mock_routes = [
        {},{"id": "urn:ngsi-ld:GtfsRoute:Sofia:72"}
    ]

    mock_trips = [
        {
            "id": "urn:ngsi-ld:GtfsTrip:Sofia:72_111"
        }
    ]

    netex_utils.netex_get_all_gtfs_routes_of_an_agency = Mock(return_value=mock_routes)

    netex_utils.netex_get_all_gtfs_trips_of_a_route = Mock(return_value=mock_trips)

    netex_utils.logger.error = Mock()

    result = netex_utils.netex_get_all_trips_of_an_agency(agency_id)

    assert result == mock_trips

    netex_utils.logger.error.assert_called_once()

    netex_utils.netex_get_all_gtfs_trips_of_a_route.assert_called_once_with("urn:ngsi-ld:GtfsRoute:Sofia:72")

def test_netex_get_all_trips_of_an_agency_without_operating_city():

    config.NETEX_OPERATING_CITY = None

    with pytest.raises(ValueError) as err:
        netex_get_all_trips_of_an_agency("urn:ngsi-ld:GtfsAgency:Sofia:A")

    assert "Parameter config.NETEX_OPERATING_CITY is not set" in str(err.value)
        