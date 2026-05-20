# import pytest
# from netex.netex_utils import netex_helper_map_trips_to_shapes

# def test_map_trips_to_shapes_returns_proper_structure():
#     """
#     Test that the function returns a proper structure.
#     """

#     trips = [
#         {
#             "id": "urn:ngsi-ld:GtfsTrip:TestCity:TRIP_1",
#             "type": "GtfsTrip",
#             "hasShape": {
#                 "type": "Relationship",
#                 "object": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_1"
#             }
#         }
#     ]

#     result = netex_helper_map_trips_to_shapes(trips)

#     assert isinstance(result, dict)
#     assert result == {
#         "TRIP_1": "SHAPE_1"
#     }

# def test_map_trips_to_shapes_handles_multiple_trips():
#     """
#     Test extracting mappings for multiple trips.
#     """

#     trips = [
#         {
#             "id": "urn:ngsi-ld:GtfsTrip:TestCity:TRIP_1",
#             "type": "GtfsTrip",
#             "hasShape": {
#                 "type": "Relationship",
#                 "object": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_1"
#             }
#         },
#         {
#             "id": "urn:ngsi-ld:GtfsTrip:TestCity:TRIP_2",
#             "type": "GtfsTrip",
#             "hasShape": {
#                 "type": "Relationship",
#                 "object": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_2"
#             }
#         }
#     ]

#     result = netex_helper_map_trips_to_shapes(trips)

#     assert result == {
#         "TRIP_1": "SHAPE_1",
#         "TRIP_2": "SHAPE_2",
#     }

# def test_map_trips_to_shapes_skips_invalid_entities():
#     """
#     Test that invalid trip entities are skipped.
#     """

#     trips = [
#         {
#             "id": "INVALID_ID",
#             "type": "GtfsTrip",
#             "hasShape": {
#                 "type": "Relationship",
#                 "object": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_1"
#             }
#         },
#         {
#             "id": "urn:ngsi-ld:GtfsTrip:TestCity:TRIP_1",
#             "type": "GtfsTrip",
#             "hasShape": {
#                 "type": "Relationship",
#                 "object": "INVALID_SHAPE_ID"
#             }
#         },
#         {
#             "id": "urn:ngsi-ld:GtfsTrip:TestCity:TRIP_2",
#             "type": "GtfsTrip",
#             "hasShape": {}
#         },
#         {
#             "id": "urn:ngsi-ld:GtfsTrip:TestCity:TRIP_1",
#             "type": "GtfsRoute",
#             "hasShape": {
#                 "type": "Relationship",
#                 "object": "urn:ngsi-ld:GtfsShape:TestCity:SHAPE_1"
#             }
#         }
#     ]

#     result = netex_helper_map_trips_to_shapes(trips)

#     assert result == {}


# def test_map_trips_to_shapes_empty_input():
#     """
#     Test that an empty input list returns an empty dictionary.
#     """

#     result = netex_helper_map_trips_to_shapes([])

#     assert result == {}