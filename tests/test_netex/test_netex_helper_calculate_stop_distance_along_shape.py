# import pytest
# from netex.netex_utils import netex_helper_calculate_stop_distance_along_shape

# Point = tuple[float, float]

# def test_calculate_stop_distance_along_shape_returns_float():
#     """
#     Test that the function returns a float.
#     """

#     stop_coordinates: Point = (5.0, 0.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert isinstance(result, float)


# def test_calculate_stop_distance_along_shape_on_straight_line():
#     """
#     Test calculating distance along a straight LineString.
#     """

#     stop_coordinates: Point = (5.0, 0.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == pytest.approx(5.0)


# def test_calculate_stop_distance_along_shape_at_line_start():
#     """
#     Test calculating distance for a point at the start of the LineString.
#     """

#     stop_coordinates: Point = (0.0, 0.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == pytest.approx(0.0)


# def test_calculate_stop_distance_along_shape_at_line_end():
#     """
#     Test calculating distance for a point at the end of the LineString.
#     """

#     stop_coordinates: Point = (10.0, 0.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == pytest.approx(10.0)


# def test_calculate_stop_distance_along_shape_multisegment_linestring():
#     """
#     Test calculating distance along a multi-segment LineString.
#     """

#     stop_coordinates: Point = (10.0, 5.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#         (10.0, 10.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == pytest.approx(15.0)


# def test_calculate_stop_distance_along_shape_projects_point_onto_line():
#     """
#     Test projecting a point that is not exactly on the LineString.
#     """

#     stop_coordinates: Point = (5.0, 3.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     # The point projects orthogonally onto (5, 0)
#     assert result == pytest.approx(5.0)


# def test_calculate_stop_distance_along_shape_handles_point_before_start():
#     """
#     Test projecting a point before the start of the LineString.
#     """

#     stop_coordinates: Point = (-5.0, 0.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == pytest.approx(0.0)


# def test_calculate_stop_distance_along_shape_handles_point_after_end():
#     """
#     Test projecting a point after the end of the LineString.
#     """

#     stop_coordinates: Point = (20.0, 0.0)

#     gtfs_shape: list[Point] = [
#         (0.0, 0.0),
#         (10.0, 0.0),
#     ]

#     result = netex_helper_calculate_stop_distance_along_shape(
#         stop_coordinates,
#         gtfs_shape,
#     )

#     assert result == pytest.approx(10.0)