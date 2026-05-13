import pytest

from netex.netex_utils import netex_helper_create_line_string_segments_between_stop_pairs

Point = tuple[float, float]

def test_create_linestring_segment_between_stops_returns_list():
    """
    Test that the function returns a list.
    """

    stop_pair = ("STOP_1", "STOP_2")

    stop_distances_along_shape = {"STOP_1": 2.0, "STOP_2": 8.0}

    gtfs_shape: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0)
    ]

    result = netex_helper_create_line_string_segments_between_stop_pairs(stop_pair, stop_distances_along_shape, gtfs_shape)

    assert isinstance(result, list)
    assert result == [
        (2.0, 0.0),
        (8.0, 0.0)
    ]


def test_create_linestring_segment_between_stops_handles_multisegment_shape():
    """
    Test creating a segment from a multi-segment LineString.
    """

    stop_pair = ("STOP_1", "STOP_2")

    stop_distances_along_shape = {"STOP_1": 5.0, "STOP_2": 15.0}

    gtfs_shape: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0),
        (10.0, 10.0),
    ]

    result = netex_helper_create_line_string_segments_between_stop_pairs(stop_pair, stop_distances_along_shape, gtfs_shape)

    assert result == [
        (5.0, 0.0),
        (10.0, 0.0),
        (10.0, 5.0),
    ]


def test_create_linestring_segment_between_stops_returns_empty_for_equal_distances():
    """
    Test that equal stop distances return an empty LineString.
    """

    stop_pair = ("STOP_1", "STOP_2")

    stop_distances_along_shape = {
        "STOP_1": 5.0,
        "STOP_2": 5.0,
    }

    gtfs_shape: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0),
    ]

    result = netex_helper_create_line_string_segments_between_stop_pairs(
        stop_pair,
        stop_distances_along_shape,
        gtfs_shape,
    )

    assert result == []


def test_create_linestring_segment_between_stops_returns_empty_for_reverse_distances():
    """
    Test that reversed stop distances return an empty LineString.
    """

    stop_pair = ("STOP_1", "STOP_2")

    stop_distances_along_shape = {"STOP_1": 8.0, "STOP_2": 2.0}

    gtfs_shape: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0)
    ]

    result = netex_helper_create_line_string_segments_between_stop_pairs(stop_pair, stop_distances_along_shape, gtfs_shape)

    assert result == []


def test_create_linestring_segment_between_stops_raises_keyerror_for_missing_from_stop():
    """
    Test that missing from-stop distances raise KeyError.
    """

    stop_pair = ("STOP_1", "STOP_2")

    stop_distances_along_shape = {
        "STOP_2": 8.0,
    }

    gtfs_shape: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0),
    ]

    with pytest.raises(KeyError):
        netex_helper_create_line_string_segments_between_stop_pairs(stop_pair, stop_distances_along_shape, gtfs_shape)


def test_create_linestring_segment_between_stops_raises_keyerror_for_missing_to_stop():
    """
    Test that missing to-stop distances raise KeyError.
    """

    stop_pair = ("STOP_1", "STOP_2")

    stop_distances_along_shape = {
        "STOP_1": 2.0,
    }

    gtfs_shape: list[Point] = [
        (0.0, 0.0),
        (10.0, 0.0),
    ]

    with pytest.raises(KeyError):
        netex_helper_create_line_string_segments_between_stop_pairs(stop_pair, stop_distances_along_shape, gtfs_shape)