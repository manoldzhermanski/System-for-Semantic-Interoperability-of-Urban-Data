
import pytest

from gtfs_static.gtfs_static_utils import gtfs_static_validate_csv

def test_read_valid_gtfs_file(tmp_path):
    """
    Check that a valid GTFS CSV file returns a valid CSV reader.
    """
    file = tmp_path / "routes.txt"
    file.write_text("route_id,route_short_name\n1,10\n2,20\n")

    with open(file, encoding="utf-8-sig", newline="") as f:
        reader = gtfs_static_validate_csv(f)
        result = list(reader)

    assert result == [
        {"route_id": "1", "route_short_name": "10"},
        {"route_id": "2", "route_short_name": "20"},
    ]

def test_read_empty_file(tmp_path):
    """
    Check that an empty file returns None.
    """
    file = tmp_path / "empty.txt"
    file.write_text("")

    with open(file, encoding="utf-8-sig", newline="") as f:
        result = gtfs_static_validate_csv(f)

    assert result is None

def test_read_header_only(tmp_path):
    """
    Check that a file containing only a header returns an empty reader.
    """
    file = tmp_path / "header_only.txt"
    file.write_text("route_id,route_short_name\n")

    with open(file, encoding="utf-8-sig", newline="") as f:
        reader = gtfs_static_validate_csv(f)
        result = list(reader)

    assert result == []
    
def test_missing_header_raises_error(tmp_path):
    """
    Check that an invalid header raises ValueError.
    """
    file = tmp_path / "no_header.txt"
    file.write_text("ok,5\n1,10\n2,20\n")

    with open(file, encoding="utf-8-sig", newline="") as f:
        with pytest.raises(ValueError) as exc:
            gtfs_static_validate_csv(f)

    assert "Missing or invalid header row" in str(exc.value)
    
def test_empty_header_columns_raises_error(tmp_path):
    """
    Check that empty header columns raise ValueError.
    """
    file = tmp_path / "empty_header.txt"
    file.write_text(",,\n1,2,3\n")

    with open(file, encoding="utf-8-sig", newline="") as f:
        with pytest.raises(ValueError) as exc:
            gtfs_static_validate_csv(f)

    assert "Missing or invalid header row" in str(exc.value)

def test_read_wrong_delimiter(tmp_path):
    """
    Check that using a wrong delimiter raises ValueError.
    """
    file = tmp_path / "semicolon.txt"
    file.write_text("route_id;route_short_name\n1;10\n")

    with open(file, encoding="utf-8-sig", newline="") as f:
        with pytest.raises(ValueError) as exc:
            gtfs_static_validate_csv(f)

    assert "Invalid delimiter" in str(exc.value)