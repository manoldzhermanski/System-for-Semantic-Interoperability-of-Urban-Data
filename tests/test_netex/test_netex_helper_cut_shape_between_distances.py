# import pytest
# from netex.netex_utils import netex_helper_cut_shape_between_distances

# Point = tuple[float, float]


# def test_cut_shape_between_distances_returns_list():
#     """
#     Test that the function returns a list.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=0.0,
#         end_d=5.0,
#     )

#     assert isinstance(result, list)


# def test_cut_shape_between_distances_returns_empty_when_end_less_than_start():
#     """
#     Test that an empty list is returned when end distance is less than start distance.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=10.0,
#         end_d=5.0,
#     )

#     assert result == []


# def test_cut_shape_between_distances_returns_empty_when_end_equals_start():
#     """
#     Test that an empty list is returned when end distance equals start distance.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=5.0,
#         end_d=5.0,
#     )

#     assert result == []


# def test_cut_shape_between_distances_cuts_correct_segment():
#     """
#     Test cutting a LineString between two distances.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=2.0,
#         end_d=8.0,
#     )

#     assert result == [
#         (2.0, 0.0),
#         (8.0, 0.0),
#     ]


# def test_cut_shape_between_distances_handles_multisegment_linestring():
#     """
#     Test cutting a multi-segment LineString.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#         (10.0, 10.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=5.0,
#         end_d=15.0,
#     )

#     assert result == [
#         (5.0, 0.0),
#         (10.0, 0.0),
#         (10.0, 5.0),
#     ]


# def test_cut_shape_between_distances_returns_full_shape():
#     """
#     Test cutting the entire LineString.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=0.0,
#         end_d=10.0,
#     )

#     assert result == [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]


# def test_cut_shape_between_distances_handles_distances_beyond_shape_length():
#     """
#     Test cutting with an end distance greater than the LineString length.
#     """

#     shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_cut_shape_between_distances(
#         shape,
#         start_d=5.0,
#         end_d=20.0,
#     )

#     assert result == [
#         (5.0, 0.0),
#         (10.0, 0.0),
#     ]


# def test_cut_shape_between_distances_handles_empty_shape():
#     """
#     Test cutting an empty LineString.
#     """

#     result = netex_helper_cut_shape_between_distances(
#         [],
#         start_d=0.0,
#         end_d=10.0,
#     )

#     assert result == []