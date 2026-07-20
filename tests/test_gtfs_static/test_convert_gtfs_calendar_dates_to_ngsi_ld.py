import config
from gtfs_static.gtfs_static_utils import convert_gtfs_calendar_dates_to_ngsi_ld

def test_convert_gtfs_calendar_dates_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for calendar_dates.txt
    """
    config.set_operating_city("Sofia")

    entity = {
        "service_id": "S1",
        "date": "20240101",
        "exception_type": 1,
    }
    
    result = convert_gtfs_calendar_dates_to_ngsi_ld(entity)

    assert result == {
        "id": f"urn:ngsi-ld:GtfsCalendarDateRule:{config.get_operating_city()}:S1:20240101",
        "type": "GtfsCalendarDateRule",
        "hasService": {
            "type": "Relationship",
            "object": f"urn:ngsi-ld:GtfsService:{config.get_operating_city()}:S1",
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