from gtfs_static.gtfs_static_utils import convert_gtfs_calendar_to_ngsi_ld

def test_convert_gtfs_calendar_dates_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for calendar_dates.txt
    """
    entity = {
        "service_id": "S1",
        "monday": 1,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 1,
        "sunday": 1,
        "start_date": "20260408",
        "end_date": "20260430"
    }
    
    city = "Berlin"

    result = convert_gtfs_calendar_to_ngsi_ld(entity, city)

    assert result == {
            "id": f"urn:ngsi-ld:GtfsCalendarRule:Berlin:S1",
            "type": "GtfsCalendarRule",
            
            "hasService": {
                "type": "Relationship",
                "object": f"urn:ngsi-ld:GtfsService:Berlin:S1"
            },
            
            "monday": {
                "type": "Property",
                "value": 1
            },

            "tuesday": {
                "type": "Property",
                "value": 1
            },

            "wednesday": {
                "type": "Property",
                "value": 1
            },

            "thursday": {
                "type": "Property",
                "value": 1
            },

            "friday": {
                "type": "Property",
                "value": 1
            },

            "saturday": {
                "type": "Property",
                "value": 1
            },

            "sunday": {
                "type": "Property",
                "value": 1
            },
            
            "startDate": {
                "type": "Property",
                "value": "20260408"
            },

            "endDate": {
                "type": "Property",
                "value": "20260430"
            }
        }