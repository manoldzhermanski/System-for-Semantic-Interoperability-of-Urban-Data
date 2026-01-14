from backend_api.main import ngsi_ld_entity_to_geojson_feature

def test_full_entity_conversion():
    """
    Check happy path
    """
    entity = {
        "id": "urn:ngsi-ld:Place:1",
        "type": "Place",
        "location": {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": [42.0, 23.0]
            }
        },
        "name": {
            "type": "Property",
            "value": "Central Park"
        },
        "managedBy": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Org:1"
        }
    }

    feature = ngsi_ld_entity_to_geojson_feature(entity)

    assert feature["type"] == "Feature"
    assert feature["id"] == entity["id"]
    assert feature["geometry"] == entity["location"]["value"]
    assert feature["properties"]["name"] == "Central Park"
    assert feature["properties"]["managedBy"] == "urn:ngsi-ld:Org:1"
    assert feature["properties"]["entityType"] == "Place"

def test_non_dict_attributes_are_skipped():
    """
    Check that non-dict attributes are skipped
    """
    entity = {
        "id": "1",
        "type": "Test",
        "count": 5,
        "active": True
    }

    feature = ngsi_ld_entity_to_geojson_feature(entity)

    assert feature["geometry"] is None
    assert feature["properties"] == {"entityType": "Test"}

def test_property_without_value_results_in_none():
    """
    Check that empty property fields are ignored
    """
    entity = {
        "id": "1",
        "type": "Test",
        "name": {
            "type": "Property"
        }
    }

    feature = ngsi_ld_entity_to_geojson_feature(entity)

    assert "name" in feature["properties"]
    assert feature["properties"]["name"] is None

def test_relationship_without_object_results_in_none():
    """
    Check that empty relationships fields are ignored
    """
    entity = {
        "id": "1",
        "type": "Test",
        "relatedTo": {
            "type": "Relationship"
        }
    }

    feature = ngsi_ld_entity_to_geojson_feature(entity)

    assert "relatedTo" in feature["properties"]
    assert feature["properties"]["relatedTo"] is None

def test_unsupported_attribute_type_is_ignored():
    """
    If in the dict fiels, if type is not Property or Relationship, the field is ignored
    """
    entity = {
        "id": "1",
        "type": "Test",
        "something": {
            "type": "UnknownType",
            "value": "test"
        }
    }

    feature = ngsi_ld_entity_to_geojson_feature(entity)

    assert feature["geometry"] is None
    assert feature["properties"] == {"entityType": "Test"}
