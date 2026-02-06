import os
import tempfile
import shutil
import pytest

from custom_ai_gateway_policies import get_version

def test_get_version_reads_file(tmp_path, monkeypatch):
    # Create the expected directory structure: tmp_path/../../VERSION
    src_dir = tmp_path / "src" / "custom_ai_gateway_policies"
    src_dir.mkdir(parents=True)
    version_file = tmp_path / "VERSION"
    version_file.write_text("2.3.4")
    # Patch __file__, abspath, and dirname to simulate module location
    import custom_ai_gateway_policies
    fake_init = src_dir / "__init__.py"
    fake_init.touch()
    monkeypatch.setattr(custom_ai_gateway_policies, "__file__", str(fake_init))
    monkeypatch.setattr(os.path, "abspath", lambda x: str(fake_init))
    monkeypatch.setattr(os.path, "dirname", lambda x: str(src_dir))
    # The VERSION file is expected two levels up from src/custom_ai_gateway_policies
    version_path = src_dir.parent.parent / "VERSION"
    version_path.write_text("2.3.4")
    assert get_version() == "2.3.4"

def test_get_version_file_not_found(monkeypatch):
    # Patch __file__ in the target module to a temp dir with no VERSION file
    import custom_ai_gateway_policies
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(custom_ai_gateway_policies, "__file__", os.path.join(tmpdir, "__init__.py"))
        with pytest.raises(FileNotFoundError):
            get_version()
