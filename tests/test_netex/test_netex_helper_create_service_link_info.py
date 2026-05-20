# import pytest
# from netex.netex_utils import netex_helper_create_service_link_info

# Point = tuple[float, float]

# def test_create_service_link_info_single_trip():
#     """
#     Test generating ServiceLink information for a single trip.
#     """

#     stops_per_trip = {"TRIP_1": ["STOP_1", "STOP_2", "STOP_3"]}

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (0.0, 0.0),
#         "STOP_2": (5.0, 0.0),
#         "STOP_3": (10.0, 0.0),
#     }

#     shape_line_strings = {
#         "SHAPE_1": [
#             (0.0, 0.0),
#             (10.0, 0.0),
#         ]
#     }

#     shape_per_trip = {"TRIP_1": "SHAPE_1"}

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     assert result == [
#         {
#             "trip_id": "TRIP_1",
#             "from_stop": "STOP_1",
#             "to_stop": "STOP_2",
#             "distance": pytest.approx(5.0),
#             "geometry": [
#                 (0.0, 0.0),
#                 (5.0, 0.0),
#             ],
#         },
#         {
#             "trip_id": "TRIP_1",
#             "from_stop": "STOP_2",
#             "to_stop": "STOP_3",
#             "distance": pytest.approx(5.0),
#             "geometry": [
#                 (5.0, 0.0),
#                 (10.0, 0.0),
#             ],
#         },
#     ]


# def test_create_service_link_info_multiple_trips():
#     """
#     Test generating ServiceLink information for multiple trips.
#     """

#     stops_per_trip = {
#         "TRIP_1": ["STOP_1", "STOP_2"],
#         "TRIP_2": ["STOP_3", "STOP_4"],
#     }

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (0.0, 0.0),
#         "STOP_2": (10.0, 0.0),
#         "STOP_3": (0.0, 0.0),
#         "STOP_4": (20.0, 0.0),
#     }

#     shape_line_strings = {
#         "SHAPE_1": [
#             (0.0, 0.0),
#             (10.0, 0.0),
#         ],
#         "SHAPE_2": [
#             (0.0, 0.0),
#             (20.0, 0.0),
#         ],
#     }

#     shape_per_trip = {
#         "TRIP_1": "SHAPE_1",
#         "TRIP_2": "SHAPE_2",
#     }

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     assert len(result) == 2

#     assert result[0]["trip_id"] == "TRIP_1"
#     assert result[1]["trip_id"] == "TRIP_2"


# def test_create_service_link_info_skips_trip_without_shape():
#     """
#     Test that trips without shape mappings are skipped.
#     """

#     stops_per_trip = {
#         "TRIP_1": ["STOP_1", "STOP_2"]
#     }

#     stop_coordinates: dict[str, Point] = {
#         "STOP_1": (0.0, 0.0),
#         "STOP_2": (10.0, 0.0),
#     }

#     shape_line_strings = {
#         "SHAPE_1": [
#             (0.0, 0.0),
#             (10.0, 0.0),
#         ]
#     }

#     shape_per_trip = {}

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     assert result == []


# def test_create_service_link_info_skips_missing_shape_geometry():
#     """
#     Test that trips with missing shape geometries are skipped.
#     """

#     stops_per_trip = {"TRIP_1": ["STOP_1", "STOP_2"]}

#     stop_coordinates = {
#         "STOP_1": (0.0, 0.0),
#         "STOP_2": (10.0, 0.0),
#     }

#     shape_line_strings = {}

#     shape_per_trip = {"TRIP_1": "SHAPE_1"}

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     assert result == []


# def test_create_service_link_info_skips_empty_shape_geometry():
#     """
#     Test that empty shape geometries are skipped.
#     """

#     stops_per_trip = {"TRIP_1": ["STOP_1", "STOP_2"]}

#     stop_coordinates = {
#         "STOP_1": (0.0, 0.0),
#         "STOP_2": (10.0, 0.0),
#     }

#     shape_line_strings = {
#         "SHAPE_1": []
#     }

#     shape_per_trip = {"TRIP_1": "SHAPE_1"}

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     assert result == []


# def test_create_service_link_info_skips_missing_stop_distances():
#     """
#     Test that trips with missing stop projections are skipped.
#     """

#     stops_per_trip = {"TRIP_1": ["STOP_1", "STOP_2"]}

#     stop_coordinates = {}

#     shape_line_strings = {
#         "SHAPE_1": [
#             (0.0, 0.0),
#             (10.0, 0.0),
#         ]
#     }

#     shape_per_trip = {"TRIP_1": "SHAPE_1"}

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     assert result == []


# def test_create_service_link_info_handles_empty_input():
#     """
#     Test that empty input returns an empty list.
#     """

#     result = netex_helper_create_service_link_info(
#         stops_per_trip={},
#         stop_coordinates={},
#         shape_line_strings={},
#         shape_per_trip={},
#     )

#     assert result == []


# def test_create_service_link_info_creates_correct_number_of_segments():
#     """
#     Test that the correct number of ServiceLink segments is generated.
#     """

#     stops_per_trip = {"TRIP_1": ["STOP_1", "STOP_2", "STOP_3", "STOP_4"]}

#     stop_coordinates = {
#         "STOP_1": (0.0, 0.0),
#         "STOP_2": (5.0, 0.0),
#         "STOP_3": (10.0, 0.0),
#         "STOP_4": (15.0, 0.0),
#     }

#     shape_line_strings = {
#         "SHAPE_1": [
#             (0.0, 0.0),
#             (15.0, 0.0),
#         ]
#     }

#     shape_per_trip = {"TRIP_1": "SHAPE_1"}

#     result = netex_helper_create_service_link_info(
#         stops_per_trip,
#         stop_coordinates,
#         shape_line_strings,
#         shape_per_trip,
#     )

#     # 4 stops -> 3 consecutive segments
#     assert len(result) == 3