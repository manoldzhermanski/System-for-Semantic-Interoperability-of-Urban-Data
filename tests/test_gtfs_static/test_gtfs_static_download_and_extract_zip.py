import io
import os
import sys
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import gtfs_static_download_and_extract_zip


def test_download_and_extract_successfully(tmp_path):
    """
    Simulate a GET request to the API endpoint for receiving the GTFS Static ZIP file and 
    Check that it's unzipped in the gtfs_static/data directory

    Args:
        tmp_path: Mock directory
    """
    # Create a mock ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as z:
        z.writestr("routes.txt", "")
        
    zip_buffer.seek(0)

    # Mock GET Request to the GTFS Static Endpoint
    mock_response = MagicMock()
    mock_response.content = zip_buffer.read()
    mock_response.status_code = 200

    # Mock API endpoint
    mock_config = MagicMock()
    mock_config.url = "http://fake-url.com"

    # Simulate that the GET Request to the API endpoint is sent and status code 200 is received
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(api_endpoint=mock_config, base_dir=tmp_path)

    # Create a mock of the file location and check if it exists
    extracted_file = tmp_path / "data" / "routes.txt"
    assert extracted_file.exists(), "The file 'routes.txt' exists"

def test_extract_creates_directory(tmp_path):
    """
    Check that if a base directory is assigned, the function will create a 'data' directory 
     and unzips the GTFS Static files in it

    Args:
        tmp_path: Mock directory
    """
    # Create a mock ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as z:
        z.writestr("routes.txt", "")

    zip_buffer.seek(0)

    # Mock GET Response
    mock_response = MagicMock()
    mock_response.content = zip_buffer.read()
    mock_response.status_code = 200

    # Mock API endpoint
    mock_config = MagicMock()
    mock_config.url = "http://fake-url.com"

    # Directory that does NOT exist
    mock_base_dir = tmp_path / "new_dir"
    assert not mock_base_dir.exists(), "Mock directory DOES NOT exist"

    # Patch the HTTP request
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(
            api_endpoint=mock_config,
            base_dir=str(mock_base_dir)
        )

    # Directory must now be created
    assert mock_base_dir.exists(), "Mock directory EXISTS"

    # Check the extracted file location
    extracted_file = mock_base_dir / "data" / "routes.txt"
    assert extracted_file.exists(), "'routes.txt' should exist in newly created directory"
   
def test_extract_in_directory_without_data_folder(tmp_path):
    
    # Create a mock ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as z:
        z.writestr("routes.txt", "")

    zip_buffer.seek(0)

    # Mock GET Response
    mock_response = MagicMock()
    mock_response.content = zip_buffer.read()
    mock_response.status_code = 200

    # Mock API endpoint
    mock_config = MagicMock()
    mock_config.url = "http://fake-url.com"
    
    # Create a file in the base directory    
    old_file = tmp_path / "routes.txt"
    old_file.write_text("NON-EMPTY FILE")
    
    assert any(tmp_path.iterdir()), "Base directory is not empty"
    
    # Patch the HTTP request
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(
            api_endpoint=mock_config,
            base_dir=str(tmp_path)
        )

    # Check the extracted file location
    overwritten_file = tmp_path/ "data" / "routes.txt"
    assert overwritten_file.exists(), "'data' folder was created and files are extracted in it"

def test_extract_in_directory_with_data_folder(tmp_path):
    # Create a mock ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as z:
        z.writestr("routes.txt", "NEW FILE")

    zip_buffer.seek(0)

    # Mock GET Response
    mock_response = MagicMock()
    mock_response.content = zip_buffer.read()
    mock_response.status_code = 200

    # Mock API endpoint
    mock_config = MagicMock()
    mock_config.url = "http://fake-url.com"
    
    # Ensure that the target directory exists and is empty
    mock_base_dir = tmp_path / "data"
    mock_base_dir.mkdir(exist_ok=True)
        
    old_file = mock_base_dir / "routes.txt"
    old_file.write_text("OLD FILE")
    
    assert mock_base_dir.exists(), "'data' folder exists in the base directory"
    assert any(mock_base_dir.iterdir()) and old_file.read_text() == "OLD FILE", "Base directory is not empty and contains the old file"
    
    # Patch the HTTP request
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(
            api_endpoint=mock_config,
            base_dir=str(tmp_path)
        )

    # Check the extracted file location
    overwritten_file = tmp_path/ "data" / "routes.txt"
    assert overwritten_file.exists() and overwritten_file.read_text() == "NEW FILE", "'data' folder was created and 'routes.txt' is inside it"