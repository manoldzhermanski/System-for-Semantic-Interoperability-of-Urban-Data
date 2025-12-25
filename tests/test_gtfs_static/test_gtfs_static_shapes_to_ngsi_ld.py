import pytest
from unittest.mock import patch, MagicMock
from gtfs_static.gtfs_static_utils import gtfs_static_shapes_to_ngsi_ld
    
def test_gtfs_static_times_to_ngsi_ld():
    """
    Unit test for gtfs_static_shapes_to_ngsi_ld:
    - Check for proper function call order (parse, validate, convert, remove_none)
    - Checks if valid NGSI-LD entities are produced
    """
    # Sample input for GTFS Shape
    sample_raw_data = [
        {
            "shape_id": "S1",
            "shape_pt_lat": "42.6977",
            "shape_pt_lon": "23.3219",
            "shape_pt_sequence": "1",
            "shape_dist_traveled": "0.7"
        },
        {
            "shape_id": "S1",
            "shape_pt_lat": "42.6980",
            "shape_pt_lon": "23.3225",
            "shape_pt_sequence": "2",
            "shape_dist_traveled": "1.5"
        }
    ]

    # Mock result from parse_gtfs_shapes_data
    parsed_data  = [
        {
            "shape_id": "S1",
            "shape_pt_lat": 42.6977,
            "shape_pt_lon": 23.3219,
            "shape_pt_sequence": 1,
            "shape_dist_traveled": 0.7
        },
        {
            "shape_id": "S1",
            "shape_pt_lat": 42.6980,
            "shape_pt_lon": 23.3225,
            "shape_pt_sequence": 2,
            "shape_dist_traveled": 1.5
        }
    ]
    
    # Mock result from convert_gtfs_shapes_to_ngsi_ld
    converted_data = [
        {
            "id": "urn:ngsi-ld:GtfsShape:shape_1",
            "type": "GtfsShape",
            "name": {
                "type": "Property",
                "value": "shape_1",
                },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                        ],
                    },
                },
            "distanceTravelled": {
                "type": "Property",
                "value": [0.7, 1.5],
                },
            }
        ]
    
    # Mock result from remove_none_values
    cleaned_data = [
        {
            "id": "urn:ngsi-ld:GtfsShape:shape_1",
            "type": "GtfsShape",
            "name": {
                "type": "Property",
                "value": "shape_1",
                },
            "location": {
                "type": "GeoProperty",
                "value": {
                    "type": "LineString",
                    "coordinates": [
                        [23.3219, 42.6977],
                        [23.3225, 42.6980],
                        ],
                    },
                },
            "distanceTravelled": {
                "type": "Property",
                "value": [0.7, 1.5],
                },
            }
        ]
    
    mock_parse = MagicMock(side_effect=parsed_data)
    mock_validate = MagicMock()
    mock_convert = MagicMock(side_effect=converted_data)
    mock_remove_none = MagicMock(side_effect=cleaned_data)
        
    # Mock function behavior
    with \
        patch("gtfs_static.gtfs_static_utils.parse_gtfs_shapes_data", mock_parse), \
        patch("gtfs_static.gtfs_static_utils.validate_gtfs_shapes_entity", mock_validate), \
        patch("gtfs_static.gtfs_static_utils.convert_gtfs_shapes_to_ngsi_ld", mock_convert), \
        patch("gtfs_static.gtfs_static_utils.remove_none_values", mock_remove_none):
            
            # Function call result from gtfs_static_shapes_to_ngsi_ld
            result = gtfs_static_shapes_to_ngsi_ld(sample_raw_data)

    # Check that result is as expected
    assert result == cleaned_data
    
    # Check that parse_gtfs_shapes_data is called for every entity
    assert mock_parse.call_count == 2
    mock_parse.assert_any_call(sample_raw_data[0])
    mock_parse.assert_any_call(sample_raw_data[1])

    # Check that validate_gtfs_shapes_entity is called for every entity
    assert mock_validate.call_count == 2
    mock_validate.assert_any_call(parsed_data[0])
    mock_validate.assert_any_call(parsed_data[1])

    # Check that convert_gtfs_shapes_to_ngsi_ld is called for every entity
    assert mock_convert.call_count == 1
    
    # Check that remove_none_values is called for every entity
    assert mock_remove_none.call_count == 1