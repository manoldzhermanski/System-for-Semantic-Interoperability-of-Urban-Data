from gtfs_static.gtfs_static_utils import convert_gtfs_calendar_dates_to_ngsi_ld

def test_convert_gtfs_calendar_dates_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for calendar_dates.txt
    """
    entity = {
        "service_id": "weekday_service",
        "date": "20240101",
        "exception_type": 1,
    }

    result = convert_gtfs_calendar_dates_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:weekday_service:20240101",
        "type": "GtfsCalendarDateRule",
        "hasService": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsService:weekday_service",
        },
        "appliesOn": {
            "type": "Property",
            "value": "20240101",
        },
        "exceptionType": {
            "type": "Property",
            "value": 1,
        },
    }