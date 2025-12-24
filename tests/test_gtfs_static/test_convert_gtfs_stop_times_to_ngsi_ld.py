from gtfs_static.gtfs_static_utils import convert_gtfs_stop_times_to_ngsi_ld


def test_convert_gtfs_stop_times_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for stop_times.txt
    """
    entity = {
        "trip_id": "urn:ngsi-ld:GtfsTrip:trip_1",
        "arrival_time": "08:15:00",
        "departure_time": "08:17:00",
        "stop_id": "urn:ngsi-ld:GtfsStop:stop_10",
        "location_group_id": "urn:ngsi-ld:GtfsLocationGroup:lg_1",
        "location_id": "urn:ngsi-ld:GtfsLocation:loc_1",
        "stop_sequence": 5,
        "stop_headsign": "City Center",
        "start_pickup_drop_off_window": "07:00:00",
        "end_pickup_drop_off_window": "22:00:00",
        "pickup_type": 0,
        "drop_off_type": 1,
        "continuous_pickup": 0,
        "continuous_drop_off": 1,
        "shape_dist_traveled": 1234.5,
        "timepoint": 1,
        "pickup_booking_rule_id": "urn:ngsi-ld:GtfsBookingRule:pickup_1",
        "drop_off_booking_rule_id": "urn:ngsi-ld:GtfsBookingRule:dropoff_1",
    }

    result = convert_gtfs_stop_times_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsStopTime:urn:ngsi-ld:GtfsTrip:trip_1:5",
        "type": "GtfsStopTime",
        "hasTrip": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:trip_1",
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
            "object": "urn:ngsi-ld:GtfsStop:stop_10",
        },
        "location_group_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsLocationGroup:lg_1",
        },
        "location_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsLocation:loc_1",
        },
        "stopSequence": {
            "type": "Property",
            "value": 5,
        },
        "stopHeadsign": {
            "type": "Property",
            "value": "City Center",
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
            "value": 1234.5,
        },
        "timepoint": {
            "type": "Property",
            "value": 1,
        },
        "pickup_booking_rule_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsBookingRule:pickup_1",
        },
        "drop_off_booking_rule_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsBookingRule:dropoff_1",
        },
    }

def test_convert_gtfs_stop_times_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for stop_times.txt when optional fileds are missing
    """
    entity = {
        "trip_id": "urn:ngsi-ld:GtfsTrip:trip_1",
        "arrival_time": "08:15:00",
        "departure_time": "08:17:00",
        "stop_id": "urn:ngsi-ld:GtfsStop:stop_10",
        "location_group_id": "urn:ngsi-ld:GtfsLocationGroup:lg_1",
        "location_id": "urn:ngsi-ld:GtfsLocation:loc_1",
        "stop_sequence": 5,
        "start_pickup_drop_off_window": "07:00:00",
        "end_pickup_drop_off_window": "22:00:00",
        "pickup_type": 0,
        "drop_off_type": 1,
        "continuous_pickup": 0,
        "continuous_drop_off": 1
    }

    result = convert_gtfs_stop_times_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsStopTime:urn:ngsi-ld:GtfsTrip:trip_1:5",
        "type": "GtfsStopTime",
        "hasTrip": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsTrip:trip_1",
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
            "object": "urn:ngsi-ld:GtfsStop:stop_10",
        },
        "location_group_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsLocationGroup:lg_1",
        },
        "location_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsLocation:loc_1",
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
