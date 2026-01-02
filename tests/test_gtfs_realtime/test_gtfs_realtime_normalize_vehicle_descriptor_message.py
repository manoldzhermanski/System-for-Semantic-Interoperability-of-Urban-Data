from gtfs_realtime.gtfs_realtime_utils import gtfs_realtime_normalize_vehicle_descriptor_message

def test_normalize_vehicle_descriptor_full_payload():
    """
    Check that if all fields in a VehicleDescriptor message are present,
    the result of the function call should be have all fields and all id's should be GTFS URNs
    """
    vehicle = {
        "id": "V1",
        "label": "Bus 42",
        "license_plate": "CA1234AB",
        "wheelchair_accessible": 1,
    }

    result = gtfs_realtime_normalize_vehicle_descriptor_message(vehicle)

    assert result == {
        "id": "urn:ngsi-ld:GtfsVehicle:V1",
        "label": "Bus 42",
        "license_plate": "CA1234AB",
        "wheelchair_accessible": 1,
    }

def test_normalize_vehicle_descriptor_with_missing_fields():
    """
    Check that if fields are missing from a VehicleDescriptor message,
    the normalized dictionary structure has replaced those fields with None values
    """
    vehicle = {
        "id": "V1",
    }

    result = gtfs_realtime_normalize_vehicle_descriptor_message(vehicle)

    assert result == {
        "id": "urn:ngsi-ld:GtfsVehicle:V1",
        "label": None,
        "license_plate": None,
        "wheelchair_accessible": None,
    }

def test_normalize_empty_vehicle():
    """
    Check that if the VehicleDescriptor message is empty,
    all fields of the VehicleDescriptor are None values
    """
    result = gtfs_realtime_normalize_vehicle_descriptor_message({})

    assert result == {
        "id": None,
        "label": None,
        "license_plate": None,
        "wheelchair_accessible": None,
    }


