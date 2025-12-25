import io
import sys
import pytest
import zipfile
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from gtfs_static.gtfs_static_utils import gtfs_static_download_and_extract_zip


def test_download_and_extract_successfully(tmp_path):
    """
    Simulate a GET request to the API endpoint for receiving the GTFS Static ZIP file and 
    Check that it's unzipped in the tmp_path/data directory

    Args:
        tmp_path: Base directory
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
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.url = "http://fake-url.com"

    # Simulate that the GET Request to the API endpoint is sent and status code 200 is received
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)

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
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.url = "http://fake-url.com"

    # Directory that does NOT exist
    mock_base_dir = tmp_path / "new_dir"
    assert not mock_base_dir.exists(), "Mock directory DOES NOT exist"

    # Patch the HTTP request
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=str(mock_base_dir))

    # Directory must now be created
    assert mock_base_dir.exists(), "Mock directory EXISTS"

    # Check the extracted file location
    extracted_file = mock_base_dir / "data" / "routes.txt"
    assert extracted_file.exists(), "'routes.txt' should exist in newly created directory"
   
def test_extract_in_directory_without_data_folder(tmp_path):
    """
    Check that if in the base directory a 'data' folder doesn't exist,
    it's created and the GTFS Static files are unzipped in it

    Args:
        tmp_path: Base directory
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
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.url = "http://fake-url.com"
    
    # Create a file in the base directory    
    old_file = tmp_path / "routes.txt"
    old_file.write_text("NON-EMPTY FILE")
    
    assert any(tmp_path.iterdir()), "Base directory is not empty"
    
    # Patch the HTTP request
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=str(tmp_path))

    # Check the extracted file location
    overwritten_file = tmp_path/ "data" / "routes.txt"
    assert overwritten_file.exists(), "'data' folder was created and files are extracted in it"

def test_extract_in_directory_with_data_folder(tmp_path):
    """
    Check if in the base directory there is a 'data' folder,
    the files are extracted in the 'data' folder

    Args:
        tmp_path: Base directory
    """
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
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.url = "http://fake-url.com"
    
    # Ensure that the target directory exists and is not empty
    mock_base_dir = tmp_path / "data"
    mock_base_dir.mkdir(exist_ok=True)
    
    # Create a mock GTFS Static file which is supposed to be overwritten    
    old_file = mock_base_dir / "routes.txt"
    old_file.write_text("OLD FILE")
    
    assert mock_base_dir.exists(), "'data' folder exists in the base directory"
    assert any(mock_base_dir.iterdir()) and old_file.read_text() == "OLD FILE", "Base directory is not empty and contains the old file"
    
    # Patch the HTTP request
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=str(tmp_path))

    # Check the extracted file location and that the old file is overwritten
    overwritten_file = tmp_path/ "data" / "routes.txt"
    assert overwritten_file.exists() and overwritten_file.read_text() == "NEW FILE", "'data' folder was created and 'routes.txt' has been overwritten"
    
def test_empty_api_endpoint_raises_value_error(tmp_path):
    """
    Check if api_endpoint.value is an empty string, the function raises a ValueError
    """
    # Mock Enum value for API endpoints to be set to an empty string
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = ""
    mock_api_endpoint.name = "TEST_ENDPOINT"

    # Trigger ValueError
    with pytest.raises(ValueError) as err:
        gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)

    # Check if ValueError has been raised
    assert "API endpoint for TEST_ENDPOINT is not set." in str(err.value)
    
def test_none_api_endpoint_raises_value_error(tmp_path):
    """
    Check if api_endpoint.value is None, the function raises a ValueError
    """
    # Mock Enum value for API endpoints to be set to an empty string
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = None
    mock_api_endpoint.name = "TEST_ENDPOINT"

    # Trigger ValueError
    with pytest.raises(ValueError) as err:
        gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)

    # Check if ValueError has been raised
    assert "API endpoint for TEST_ENDPOINT is not set." in str(err.value)
    
def test_requests_404_not_found(tmp_path):
    """
    Check that if the GET request to the API endpoint returns a 404 status code,
    a HTTPError exception is raised
    Args:
        tmp_path: Base directory
    """
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "http://fake-url.com"
    mock_api_endpoint.name = "GTFS_STATIC_ZIP_URL"

     #  Mock GET Response with 404 status code
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error: Not Found")

    # Trigger HTTPError exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.RequestException) as err:
            gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)

    # Check that HTTPError exception is raised
    assert f"Error when fetching GTFS data from {mock_api_endpoint.name}" in str(err.value)

def test_requests_500_internal_server_error(tmp_path):
    """
    Check that if the GET request to the API endpoint returns a 500 status code,
    a HTTPError exception is raised
    Args:
        tmp_path: Base directory
    """
    #  Mock API endpoint with GET Response with 500 status code
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "http://fake-url.com"
    mock_api_endpoint.name = "GTFS_STATIC_ZIP_URL"
    mock_api_endpoint.status_code = 500
    mock_api_endpoint.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error: Internal Server Error")

    # Trigger HTTPError exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_api_endpoint):
        with pytest.raises(requests.exceptions.RequestException) as err:
            gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)

    # Check that HTTPError exception is raised
    assert f"Error when fetching GTFS data from {mock_api_endpoint.name}" in str(err.value)
    
def test_requests_timeout(tmp_path):
    """
    Check that if the GET request to the API endpoint times out,
    a Timeout exception is raised
    Args:
        tmp_path: Base directory
    """
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "http://fake-url.com"
    mock_api_endpoint.name = "GTFS_STATIC_ZIP_URL"
    mock_api_endpoint.side_effect = requests.exceptions.Timeout("The request timed out")

    # Trigger Timeout exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", mock_api_endpoint):
        with pytest.raises(requests.exceptions.RequestException) as err:
            gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)
            
    # Check that Timeout exception is raised
    assert f"Error when fetching GTFS data from {mock_api_endpoint.name}" in str(err.value)
    
def test_empty_zip_response(tmp_path):
    """
    Check that if the API endpoint's response is an empty Zip file,
    a BadZipFile exception is raised
    Args:
        tmp_path: Base directory
    """
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "http://fake-url.com"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b""  # Empty Body

    # Trigger Bad Zip File exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        with pytest.raises(zipfile.BadZipFile) as err:
            gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)
        
    # Check that Bad Zip File expection is raised
    assert "File is not a zip file" in str(err.value)
    
def test_corrupted_zip_file(tmp_path):
    """
    Check that if the API endpoint's response is a corrupted Zip file,
    a BadZipFile exception is raised
    Args:
        tmp_path: Base directory
    """
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "http://fake-url.com"

    # Response contains invalid/non-zip content
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"Corrupted zip file"

    # Trigger Bad Zip File exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", return_value=mock_response):
        with pytest.raises(zipfile.BadZipFile) as err:
            gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)
    
    # Check that Bad Zip File expection is raised
    assert "File is not a zip file" in str(err.value)

def test_api_endpoint_missing_value_raises_error(tmp_path):
    """
    Check that if the GTFS API Endpoints Enum has a missing value, that an AttributeError is thrown
    Args:
        tmp_path: Base directory
    """
    invalid_endpoint = MagicMock()
    del invalid_endpoint.value  # Delete attribute .value

    # Check that AttributeError exception is raised
    with pytest.raises(AttributeError):
        gtfs_static_download_and_extract_zip(api_endpoint=invalid_endpoint, base_dir=tmp_path)

def test_invalid_url_raises_request_exception(tmp_path):
    """
    Check if an invalid URL is given thant a InvalidURL error is thrown
    Args:
        tmp_path: Base directory
    """
    # Prepare mock URL and expected exception
    mock_api_endpoint = MagicMock()
    mock_api_endpoint.value = "  http://b@d url .com  "
    mock_api_endpoint.name = "GTFS_STATIC_ZIP_URL"
    mock_api_endpoint.side_effect = requests.exceptions.InvalidURL("Bad URL")
    

    # Trigger InvalidURL exception
    with patch("gtfs_static.gtfs_static_utils.requests.get", mock_api_endpoint):
        with pytest.raises(requests.exceptions.RequestException) as err:
            gtfs_static_download_and_extract_zip(api_endpoint=mock_api_endpoint, base_dir=tmp_path)
            
    # Check that InvalidURL exception is raised
    assert f"Error when fetching GTFS data from {mock_api_endpoint.name}" in str(err.value)