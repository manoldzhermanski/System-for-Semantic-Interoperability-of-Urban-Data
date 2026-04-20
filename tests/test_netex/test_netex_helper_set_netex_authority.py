import pytest
import config
from netex.netex_utils import netex_helper_set_netex_authority


@pytest.fixture(autouse=True)
def reset_config():
    config.NETEX_AUTHORITY = None


def test_set_netex_authority_success():
    entity = {
        "type": "GtfsAgency",
        "id": "urn:ngsi-ld:GtfsAgency:Sofia:BG-SOF"
    }

    netex_helper_set_netex_authority(entity)

    assert config.NETEX_AUTHORITY == "BG-SOF"


def test_set_netex_authority_invalid_type():
    entity = {
        "type": "GtfsStop",
        "id": "urn:ngsi-ld:GtfsStop:Sofia:BG-SOF"
    }

    with pytest.raises(ValueError) as err:
        netex_helper_set_netex_authority(entity)
    
    assert "GtfsAgency" in str(err.value)


def test_set_netex_authority_missing_id():
    entity = {
        "type": "GtfsAgency"
    }

    with pytest.raises(ValueError) as err:
        netex_helper_set_netex_authority(entity)
        
    assert "ID" in str(err.value)
        