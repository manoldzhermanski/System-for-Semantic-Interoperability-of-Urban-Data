import netex.netex_utils as netex_utils
from unittest.mock import MagicMock

def test_netex_index_calendar_or_calendar_dates_by_service_success_calendar():
    """
    Check that proper structure is created for calendar
    """
    calendar_dates = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar1",
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia:Service1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar2",
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia:Service1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar3",
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia:Service2"
            }
        }
    ]

    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service(calendar_dates)

    assert result == {
        "urn:ngsi-ld:GtfsService:Sofia:Service1": [
            calendar_dates[0],
            calendar_dates[1]
        ],
        "urn:ngsi-ld:GtfsService:Sofia:Service2": [
            calendar_dates[2]
        ]
    }
    
def test_netex_index_calendar_or_calendar_dates_by_service_calendar_dates():
    """
    Check that proper structure is created for calendar dates
    """
    calendar_dates = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:CalendarDate1:20260529",
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia:Service1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:CalendarDate2",
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia:Service1"
            }
        },
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:CalendarDate3",
            "hasService": {
                "type": "Relationship",
                "object": "urn:ngsi-ld:GtfsService:Sofia:Service2"
            }
        }
    ]

    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service(calendar_dates)

    assert result == {
        "urn:ngsi-ld:GtfsService:Sofia:Service1": [
            calendar_dates[0],
            calendar_dates[1]
        ],
        "urn:ngsi-ld:GtfsService:Sofia:Service2": [
            calendar_dates[2]
        ]
    }

def test_netex_index_calendar_or_calendar_dates_by_service_missing_service_calendar():
    """
    Check that error is logged when `hasService` is missing
    """
    calendar = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarRule:Sofia:Calendar1"
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service(calendar)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Calendar / Calendar Date has missing or invalid service: %r", calendar[0]["id"])
    
def test_netex_index_calendar_or_calendar_dates_by_service_missing_service_calendar_date():
    """
    Check that error is logged when `hasService` is missing
    """
    calendar_dates = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:CalendarDate1:20260529"
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service(calendar_dates)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Calendar / Calendar Date has missing or invalid service: %r", calendar_dates[0]["id"])

def test_netex_index_calendar_or_calendar_dates_by_service_invalid_service_structure_calendar():
    """
    Check that error is logged when `hasService` object is missing
    """
    calendar = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:Calendar1",
            "hasService": {
                "type": "Relationship"
            }
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service(calendar)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Calendar / Calendar Date has missing or invalid service: %r", calendar[0]["id"])

def test_netex_index_calendar_or_calendar_dates_by_service_invalid_service_structure_calendar_date():
    """
    Check that error is logged when `hasService` object is missing
    """
    calendar_dates = [
        {
            "id": "urn:ngsi-ld:GtfsCalendarDateRule:Sofia:CalendarDate1:20260529",
            "hasService": {
                "type": "Relationship"
            }
        }
    ]

    netex_utils.logger.error = MagicMock()

    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service(calendar_dates)

    assert result == {}

    netex_utils.logger.error.assert_called_once_with("Calendar / Calendar Date has missing or invalid service: %r", calendar_dates[0]["id"])

def test_netex_index_calendar_dates_by_service_empty_input():
    """
    Check that if input is empty list, empty dict is returned
    """
    result = netex_utils.netex_index_calendar_or_calendar_dates_by_service([])

    assert result == {}