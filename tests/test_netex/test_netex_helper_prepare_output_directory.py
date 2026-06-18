import pytest
import shutil
import config
from netex.netex_utils import netex_helper_prepare_output_directory

def test_netex_helper_prepare_output_directory_creates_directory(tmp_path, monkeypatch):
    """
    Check that netex_helper_prepare_output_directory creates the output directory if it doesn't exist
    """
    output_dir = tmp_path / "netex" / "output"

    monkeypatch.setattr(config, "NETEX_OUTPUT_DIR", output_dir)

    assert not output_dir.exists()

    netex_helper_prepare_output_directory()

    assert output_dir.exists()
    assert output_dir.is_dir()

def test_netex_helper_prepare_output_directory_recreates_existing_directory(tmp_path, monkeypatch):
    """
    Check that if output directory exists, netex_helper_prepare_output_directory deletes it's content
    """
    output_dir = tmp_path / "netex" / "output"

    output_dir.mkdir(parents=True, exist_ok=True)

    test_file = output_dir / "dummy.xml"
    test_file.write_text("test")

    monkeypatch.setattr(config, "NETEX_OUTPUT_DIR", output_dir)

    assert test_file.exists()

    netex_helper_prepare_output_directory()

    assert output_dir.exists()
    assert output_dir.is_dir()
    assert not test_file.exists()
    assert list(output_dir.iterdir()) == []