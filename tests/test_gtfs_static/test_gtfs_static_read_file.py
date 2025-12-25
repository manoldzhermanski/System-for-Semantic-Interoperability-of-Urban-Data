
import pytest

from gtfs_static.gtfs_static_utils import gtfs_static_read_file

def test_read_valid_gtfs_file(tmp_path):
    """
    Check that if a valid GTFS Static file (CSV format) is read and a list of dictionaries is returned
    where the keys are the header names and the values are from the respective rows
    Args:
        tmp_path: Base directory
    """
    # Create a valid GTFS Static file
    file = tmp_path / "routes.txt"
    file.write_text("route_id,route_short_name\n1,10\n2,20\n")

    # Read file
    result = gtfs_static_read_file(file)

    # Expect that the result is a list of dictionaries
    # where the keys are the header names and the values are from the respective rows
    assert result == [
        {"route_id": "1", "route_short_name": "10"},
        {"route_id": "2", "route_short_name": "20"},
    ]

def test_read_empty_file(tmp_path):
    """
    Check that if the file is empty, an empty list is returned
    Args:
        tmp_path: Base directory
    """
    # Create an empty file
    file = tmp_path / "empty.txt"
    file.write_text("")

    # Expect the function to return an empty list
    assert gtfs_static_read_file(file) == []

def test_read_header_only(tmp_path):
    """
    Check that if only the header is present (data is missing), an empty list is returned
    Args:
        tmp_path: Base directory
    """
    # Create a file without data (only headers)
    file = tmp_path / "header_only.txt"
    file.write_text("route_id,route_short_name\n")

    # Expect the function to return an empty list
    assert gtfs_static_read_file(file) == []
    
def test_missing_header_raises_error(tmp_path):
    """
    Check that if the header is missing a ValueError is raised
    Args:
        tmp_path: Base directory
    """
    # Create a file where one of the headers is a number
    file = tmp_path / "no_header.txt"
    file.write_text("ok,5\n1,10\n2,20\n")

    # Attempt to read the file and expect a ValueError
    with pytest.raises(ValueError) as exc:
        gtfs_static_read_file(file)

    # Check that ValueError is raised
    assert "Missing or invalid header row" in str(exc.value)
    
def test_empty_header_columns_raises_error(tmp_path):
    """
    Check that empty header columns raise a ValueError.
    Args:
        tmp_path (_type_): Base directory
    """
    # Create a file without header columns
    file = tmp_path / "empty_header.txt"
    file.write_text(",,\n1,2,3\n")

    # Attempt to read the file and expect a ValueError
    with pytest.raises(ValueError) as exc:
        gtfs_static_read_file(file)

    # Check that ValueError is raised
    assert "Missing or invalid header row" in str(exc.value)

def test_read_wrong_delimiter(tmp_path):
    """
    Check that using a wrong delimiter raises a ValueError.
    Args:
        tmp_path: Base directory
    """
    # Create a test file with semicolon delimiter
    file = tmp_path / "semicolon.txt"
    file.write_text("route_id;route_short_name\n1;10\n", encoding="utf-8")

    # Attempt to read the file and expect a ValueError
    with pytest.raises(ValueError) as err:
        gtfs_static_read_file(str(file))

    # Check that ValueError is raised
    assert "Invalid delimiter" in str(err.value)

def test_file_not_found(tmp_path):
    """
    Check that attempting to read a non-existent file raises a FileNotFoundError.
    Args:
        tmp_path: Base directory
    """
    # Define a path to a non-existent file
    missing = tmp_path / "missing.txt"

    # Attempt to read the missing file and expect a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        gtfs_static_read_file(missing)
