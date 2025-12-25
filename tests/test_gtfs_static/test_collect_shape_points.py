import pytest
from gtfs_static.gtfs_static_utils import collect_shape_points

def test_collect_shape_points_creates_new_shape():
    shapes = {}

    entity = {
        "shape_id": "S1",
        "shape_pt_sequence": 1,
        "shape_pt_lon": 23.32,
        "shape_pt_lat": 42.69,
        "shape_dist_traveled": 0.0,
    }

    collect_shape_points(shapes, entity)

    assert "S1" in shapes
    assert len(shapes["S1"]) == 1
    assert shapes["S1"][0] == {"seq": 1, "coords": [23.32, 42.69], "dist": 0.0,}


def test_collect_shape_points_appends_to_existing_shape():
    shapes = {
        "S1": [
            {"seq": 1, "coords": [23.30, 42.60], "dist": 0.0}
        ]
    }

    entity = {
        "shape_id": "S1",
        "shape_pt_sequence": 2,
        "shape_pt_lon": 23.31,
        "shape_pt_lat": 42.61,
        "shape_dist_traveled": 1.2,
    }

    collect_shape_points(shapes, entity)

    assert len(shapes["S1"]) == 2
    assert shapes["S1"][1]["seq"] == 2

def test_collect_shape_points_without_distance():
    shapes = {}

    entity = {
        "shape_id": "S2",
        "shape_pt_sequence": 1,
        "shape_pt_lon": 24.00,
        "shape_pt_lat": 43.00,
    }

    collect_shape_points(shapes, entity)

    assert shapes["S2"][0]["dist"] is None
