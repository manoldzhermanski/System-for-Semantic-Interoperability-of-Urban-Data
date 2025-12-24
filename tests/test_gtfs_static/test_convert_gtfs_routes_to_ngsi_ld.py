from gtfs_static.gtfs_static_utils import convert_gtfs_routes_to_ngsi_ld

def test_convert_gtfs_routes_to_ngsi_ld():
    """
    Check for proper conversion from GTFS to NGSI-LD for routes.txt
    """
    entity = {
        "route_id": "R42",
        "agency_id": "urn:ngsi-ld:GtfsAgency:sofia",
        "route_short_name": "42",
        "route_long_name": "Central Station – Airport",
        "route_desc": "Express bus route",
        "route_type": 3,
        "route_url": "https://example.com/routes/42",
        "route_color": "FF0000",
        "route_text_color": "FFFFFF",
        "route_sort_order": 10,
        "continuous_pickup": 0,
        "continuous_drop_off": 1,
        "network_id": "urn:ngsi-ld:GtfsNetwork:city",
        "cemv_support": 0,
    }

    result = convert_gtfs_routes_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R42",
        "type": "GtfsRoute",
        "operatedBy": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsAgency:sofia",
        },
        "shortName": {
            "type": "Property",
            "value": "42",
        },
        "name": {
            "type": "Property",
            "value": "Central Station – Airport",
        },
        "description": {
            "type": "Property",
            "value": "Express bus route",
        },
        "routeType": {
            "type": "Property",
            "value": 3,
        },
        "route_url": {
            "type": "Property",
            "value": "https://example.com/routes/42",
        },
        "routeColor": {
            "type": "Property",
            "value": "FF0000",
        },
        "routeTextColor": {
            "type": "Property",
            "value": "FFFFFF",
        },
        "routeSortOrder": {
            "type": "Property",
            "value": 10,
        },
        "continuous_pickup": {
            "type": "Property",
            "value": 0,
        },
        "continuous_drop_off": {
            "type": "Property",
            "value": 1,
        },
        "network_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsNetwork:city",
        },
        "cemv_support": {
            "type": "Property",
            "value": 0,
        },
    }
    
def test_convert_gtfs_routes_to_ngsi_ld_missing_optional_fields():
    """
    Check for proper conversion from GTFS to NGSI-LD for routes.txt when optional fileds are missing
    """
    entity = {
        "route_id": "R42",
        "agency_id": "urn:ngsi-ld:GtfsAgency:sofia",
        "route_short_name": "42",
        "route_long_name": "Central Station – Airport",
        "route_type": 3,
        "continuous_pickup": 0,
        "continuous_drop_off": 1,
        "network_id": "urn:ngsi-ld:GtfsNetwork:city"
    }

    result = convert_gtfs_routes_to_ngsi_ld(entity)

    assert result == {
        "id": "urn:ngsi-ld:GtfsRoute:Bulgaria:Sofia:R42",
        "type": "GtfsRoute",
        "operatedBy": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsAgency:sofia",
        },
        "shortName": {
            "type": "Property",
            "value": "42",
        },
        "name": {
            "type": "Property",
            "value": "Central Station – Airport",
        },
        "description": {
            "type": "Property",
            "value": None,
        },
        "routeType": {
            "type": "Property",
            "value": 3,
        },
        "route_url": {
            "type": "Property",
            "value": None,
        },
        "routeColor": {
            "type": "Property",
            "value": None,
        },
        "routeTextColor": {
            "type": "Property",
            "value": None,
        },
        "routeSortOrder": {
            "type": "Property",
            "value": None,
        },
        "continuous_pickup": {
            "type": "Property",
            "value": 0,
        },
        "continuous_drop_off": {
            "type": "Property",
            "value": 1,
        },
        "network_id": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:GtfsNetwork:city",
        },
        "cemv_support": {
            "type": "Property",
            "value": None,
        },
    }