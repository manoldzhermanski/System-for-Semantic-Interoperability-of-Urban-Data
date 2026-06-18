import config
import zipfile
import importlib
import netex.netex_utils as netex_utils


def test_netex_helper_create_otp_zip_contains_all_xml_files(tmp_path, monkeypatch):
    output_dir = tmp_path / "netex" / "output"
    otp_dir = tmp_path / "otp" / "data"

    output_dir.mkdir(parents=True, exist_ok=True)
    otp_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "routes.xml").write_text("<routes/>")
    (output_dir / "stops.xml").write_text("<stops/>")

    monkeypatch.setattr(config, "NETEX_OUTPUT_DIR", output_dir)
    monkeypatch.setattr(config, "OTP_DATA_DIR", otp_dir)

    netex_utils.netex_helper_create_otp_zip()

    zip_path = otp_dir / "netex.zip"

    assert zip_path.exists()

    with zipfile.ZipFile(zip_path) as archive:
        assert set(archive.namelist()) == {"routes.xml", "stops.xml"}

def test_netex_helper_create_otp_zip_ignores_non_xml_files(tmp_path, monkeypatch):
    """
    Test that netex_helper_create_otp_zip function ognores non-XML files
    """
    output_dir = tmp_path / "netex" / "output"
    otp_dir = tmp_path / "otp" / "data"

    output_dir.mkdir(parents=True, exist_ok=True)
    otp_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "NETEX_OUTPUT_DIR", output_dir)
    monkeypatch.setattr(config, "OTP_DATA_DIR", otp_dir)

    (output_dir / "routes.xml").write_text("<routes/>")
    (output_dir / "notes.txt").write_text("test")
    (output_dir / "image.png").write_bytes(b"123")

    monkeypatch.setattr(config, "NETEX_OUTPUT_DIR", output_dir)
    monkeypatch.setattr(config, "OTP_DATA_DIR", otp_dir)

    importlib.reload(netex_utils)
    netex_utils.netex_helper_create_otp_zip()

    with zipfile.ZipFile(otp_dir / "netex.zip") as archive:
        assert archive.namelist() == ["routes.xml"]

def test_netex_helper_create_otp_zip_when_no_xml_files(tmp_path, monkeypatch):
    """
    Test that netex_helper_create_otp_zip returns an empty ZIP file if no XML files are found
    """
    output_dir = tmp_path / "netex" / "output"
    otp_dir = tmp_path / "otp"

    output_dir.mkdir(parents=True, exist_ok=True)
    otp_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "NETEX_OUTPUT_DIR", output_dir)
    monkeypatch.setattr(config, "OTP_DATA_DIR", otp_dir)

    importlib.reload(netex_utils)
    netex_utils.netex_helper_create_otp_zip()

    zip_path = otp_dir / "netex.zip"

    assert zip_path.exists()

    with zipfile.ZipFile(zip_path) as archive:
        assert archive.namelist() == []