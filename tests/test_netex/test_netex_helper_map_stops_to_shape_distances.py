# import pytest

# from netex.netex_utils import netex_helper_map_stops_to_shape_distances


# Point = tuple[float, float]


# def test_map_stops_to_shape_distances_returns_dictionary():
#     """
#     Test that the function returns a dictionary.
#     """

#     stop_ids = ["STOP_1", "STOP_2"]

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (2.0, 0.0),
#         "STOP_2": (8.0, 0.0)
#     }

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_map_stops_to_shape_distances(
#         stop_ids,
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert isinstance(result, dict)
#     assert result == {
#         "STOP_1": pytest.approx(2.0),
#         "STOP_2": pytest.approx(8.0),
#     }



# def test_map_stops_to_shape_distances_handles_multisegment_shape():
#     """
#     Test calculating distances on a multi-segment LineString.
#     """

#     stop_ids = ["STOP_1"]

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (10.0, 5.0),
#     }

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#         (10.0, 10.0),
#     ]

#     result = netex_helper_map_stops_to_shape_distances(
#         stop_ids,
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == {
#         "STOP_1": pytest.approx(15.0),
#     }


# def test_map_stops_to_shape_distances_skips_missing_stop_coordinates():
#     """
#     Test that stops without coordinates are skipped.
#     """

#     stop_ids = ["STOP_1"]

#     stop_coordinates: dict[str, Point] = {}

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_map_stops_to_shape_distances(
#         stop_ids,
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == {}


# def test_map_stops_to_shape_distances_handles_empty_stop_ids():
#     """
#     Test that empty stop IDs return an empty dictionary.
#     """

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (5.0, 0.0),
#     }

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_map_stops_to_shape_distances(
#         [],
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == {}


# def test_map_stops_to_shape_distances_handles_empty_shape():
#     """
#     Test handling an empty shape.
#     """

#     stop_ids = ["STOP_1"]

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (5.0, 0.0),
#     }

#     result = netex_helper_map_stops_to_shape_distances(
#         stop_ids,
#         stop_coordinates,
#         [],
#     )

#     assert result == {}


# def test_map_stops_to_shape_distances_preserves_stop_order():
#     """
#     Test that stop IDs are processed in the provided order.
#     """

#     stop_ids = ["STOP_A", "STOP_B", "STOP_C"]

#     stop_coordinates: dict[str, Point] = {
#         "STOP_A": (1.0, 0.0),
#         "STOP_B": (5.0, 0.0),
#         "STOP_C": (9.0, 0.0),
#     }

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_map_stops_to_shape_distances(
#         stop_ids,
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert list(result.keys()) == stop_ids