from gtfs_static.gtfs_static_utils import convert_gtfs_shapes_to_ngsi_ld

def test_convert_gtfs_shapes_with_distance_travelled():
    """
    Check for proper conversion from GTFS to NGSI-LD for shapes.txt
    """
    shape_id = "S1"
    points = [
        {"seq": 2, "coords": [23.32, 42.70], "dist": 100.0},
        {"seq": 1, "coords": [23.31, 42.69], "dist": 0.0},
        {"seq": 3, "coords": [23.33, 42.71], "dist": 150.0},
    ]

    result = convert_gtfs_shapes_to_ngsi_ld(shape_id, points)

    assert result == {
        "id": "urn:ngsi-ld:GtfsShape:S1",
        "type": "GtfsShape",
        "name": {
            "type": "Property",
            "value": "S1",
        },
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "LineString",
                "coordinates": [
                    [23.31, 42.69],
                    [23.32, 42.70],
                    [23.33, 42.71],
                ],
            },
        },
        "distanceTravelled": {
            "type": "Property",
            "value": [0.0, 100.0, 150.0],
        },
    }

def test_convert_gtfs_shapes_without_distance_travelled():
    """
    Check that if 'shape_dist_traveled' is None for the individual shape points,
    the aggreagation would also be None
    """
    shape_id = "S2"
    points = [
        {"seq": 2, "coords": [23.32, 42.70], "dist": None},
        {"seq": 1, "coords": [23.31, 42.69], "dist": None},
    ]

    result = convert_gtfs_shapes_to_ngsi_ld(shape_id, points)

    assert result == {
        "id": "urn:ngsi-ld:GtfsShape:S2",
        "type": "GtfsShape",
        "name": {
            "type": "Property",
            "value": "S2",
        },
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "LineString",
                "coordinates": [
                    [23.31, 42.69],
                    [23.32, 42.70],
                ],
            },
        },
        "distanceTravelled": {
            "type": "Property",
            "value": None,
        },
    }
