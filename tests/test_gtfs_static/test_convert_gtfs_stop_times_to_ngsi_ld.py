from gtfs_static.gtfs_static_utils import convert_gtfs_stop_times_to_ngsi_ld


def test_convert_gtfs_stop_times_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for stop_times.txt
    """
    city = "Helsinki"
    
    entity = {
        "trip_id": "1040_20260216_Ti_2_1806",
        "arrival_time": "18:32:00",
        "departure_time": "18:32:00",
        "stop_id": f"urn:ngsi-ld:GtfsStop:{city}:1180206",
        "location_group_id": None,
        "location_id": None,
        "stop_sequence": 19,
        "stop_headsign": "Elielinaukio",
        "start_pickup_drop_off_window": None,
        "end_pickup_drop_off_window": None,
        "pickup_type": 0,
        "drop_off_type": 0,
        "continuous_pickup": None,
        "continuous_drop_off": None,
        "shape_dist_traveled": 7.868,
        "timepoint": 0,
        "pickup_booking_rule_id": None,
        "drop_off_booking_rule_id": None,
    }

    result = convert_gtfs_stop_times_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsStopTime:{city}:1040_20260216_Ti_2_1806:19",
        "type": "GtfsStopTime",
        "hasTrip": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsTrip:{city}:1040_20260216_Ti_2_1806",
        },
        "arrivalTime": {
            "type": "Property",
            "value": "18:32:00",
        },
        "departureTime": {
            "type": "Property",
            "value": "18:32:00",
        },
        "hasStop": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:1180206",
        },
        "location_group_id": {
            "type": "Relationship",
            "object": None,
        },
        "location_id": {
            "type": "Relationship",
            "object": None,
        },
        "stopSequence": {
            "type": "Property",
            "value": 19,
        },
        "stopHeadsign": {
            "type": "Property",
            "value": "Elielinaukio",
        },
        "start_pickup_drop_off_window": {
            "type": "Property",
            "value": None,
        },
        "end_pickup_drop_off_window": {
            "type": "Property",
            "value": None,
        },
        "pickupType": {
            "type": "Property",
            "value": 0,
        },
        "dropOffType": {
            "type": "Property",
            "value": 0,
        },
        "continuousPickup": {
            "type": "Property",
            "value": None,
        },
        "continuousDropOff": {
            "type": "Property",
            "value": None,
        },
        "shapeDistTraveled": {
            "type": "Property",
            "value": 7.868,
        },
        "timepoint": {
            "type": "Property",
            "value": 0,
        },
        "pickup_booking_rule_id": {
            "type": "Relationship",
            "object": None,
        },
        "drop_off_booking_rule_id": {
            "type": "Relationship",
            "object": None,
        },
    }

def test_convert_gtfs_stop_times_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for stop_times.txt when optional fileds are missing
    """
    city = "Sofia"
    
    entity = {
        "trip_id": "T1",
        "arrival_time": "08:15:00",
        "departure_time": "08:17:00",
        "stop_id": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        "location_group_id": f"urn:ngsi-ld:GtfsLocationGroup:{city}:LG1",
        "location_id": f"urn:ngsi-ld:GtfsLocation:{city}:L1",
        "stop_sequence": 5,
        "start_pickup_drop_off_window": "07:00:00",
        "end_pickup_drop_off_window": "22:00:00",
        "pickup_type": 0,
        "drop_off_type": 1,
        "continuous_pickup": 0,
        "continuous_drop_off": 1
    }

    result = convert_gtfs_stop_times_to_ngsi_ld(entity, city)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsStopTime:{city}:T1:5",
        "type": "GtfsStopTime",
        "hasTrip": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsTrip:{city}:T1",
        },
        "arrivalTime": {
            "type": "Property",
            "value": "08:15:00",
        },
        "departureTime": {
            "type": "Property",
            "value": "08:17:00",
        },
        "hasStop": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsStop:{city}:S1",
        },
        "location_group_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsLocationGroup:{city}:LG1",
        },
        "location_id": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsLocation:{city}:L1",
        },
        "stopSequence": {
            "type": "Property",
            "value": 5,
        },
        "stopHeadsign": {
            "type": "Property",
            "value": None,
        },
        "start_pickup_drop_off_window": {
            "type": "Property",
            "value": "07:00:00",
        },
        "end_pickup_drop_off_window": {
            "type": "Property",
            "value": "22:00:00",
        },
        "pickupType": {
            "type": "Property",
            "value": 0,
        },
        "dropOffType": {
            "type": "Property",
            "value": 1,
        },
        "continuousPickup": {
            "type": "Property",
            "value": 0,
        },
        "continuousDropOff": {
            "type": "Property",
            "value": 1,
        },
        "shapeDistTraveled": {
            "type": "Property",
            "value": None,
        },
        "timepoint": {
            "type": "Property",
            "value": None,
        },
        "pickup_booking_rule_id": {
            "type": "Relationship",
            "object": None,
        },
        "drop_off_booking_rule_id": {
            "type": "Relationship",
            "object": None,
        },
    }
