import sys
import requests
import zipfile
import os
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config


def download_and_extract_gtfs_zip(api_endpoint: str, base_dir: str = "gtfs-static") -> list[str]:
    """
    Downloads a GTFS-Static ZIP file from the given API URL and extracts its contents to the specified directory.
    """
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error when fetching GTFS data from {api_endpoint}: {e}") from e

    # Make directory if it does not exist
    extract_to = os.path.join(base_dir, "data")
    os.makedirs(extract_to, exist_ok=True)
    
    # Extract the ZIP file
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall(extract_to)

    


if __name__ == "__main__":
    download_and_extract_gtfs_zip(config.GTFS_STATIC_ZIP_URL)