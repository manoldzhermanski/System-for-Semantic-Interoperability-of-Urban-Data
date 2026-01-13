import json
import pytest
from json_ld.json_ld_utils import json_ld_read_file

def test_json_ld_read_file_valid_ngsi_ld_file(tmp_path):
    """Check happy path"""
    file = tmp_path / "valid.json"
    file.write_text(json.dumps({
        "entities": [
            {"id": "urn:ngsi-ld:Entity:1", "type": "Test"}
        ]
    }), encoding="utf-8")

    result = json_ld_read_file(str(file))

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "urn:ngsi-ld:Entity:1"

def test_json_ld_read_file_file_not_found():
    """
    Check that FileNotFoundError is handled
    """
    with pytest.raises(FileNotFoundError):
        json_ld_read_file("non_existent_file.json")

def test_json_ld_read_file_invalid_json(tmp_path):
    """Check that invalid JSON file content is handled"""
    file = tmp_path / "invalid.json"
    file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        json_ld_read_file(str(file))

def test_json_ld_read_file_root_is_not_dict(tmp_path):
    """
    Check if the root of the file is not a dict, ValueError is raised
    """
    file = tmp_path / "not_dict.json"
    file.write_text(json.dumps([{"entities": []}]), encoding="utf-8")

    with pytest.raises(ValueError) as err:
        json_ld_read_file(str(file))

    assert "expected a JSON object" in str(err.value)

def test_json_ld_read_file_missing_entities_key(tmp_path):
    """
    Check that if 'entities' key is missing, ValueError is raised
    """
    file = tmp_path / "missing_entities.json"
    file.write_text(json.dumps({"no_entities": [{"id": 1}]}), encoding="utf-8")

    with pytest.raises(ValueError) as err:
        json_ld_read_file(str(file))

    assert "expected 'entities' key with a list value" in str(err.value)

def test_json_ld_read_file_entities_not_a_list(tmp_path):
    """
    Check that if a agains the 'entities' key a non-list structure is observed,
    ValueError is raised.
    """
    file = tmp_path / "entities_not_list.json"
    file.write_text(json.dumps({"entities": {"id": 1}}), encoding="utf-8")

    with pytest.raises(ValueError) as err:
        json_ld_read_file(str(file))

    assert "expected 'entities' key with a list value" in str(err.value)

