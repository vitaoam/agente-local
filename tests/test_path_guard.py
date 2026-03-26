from pathlib import Path

from app.services.path_guard import is_path_allowed, validate_path
from app.config import DESKTOP_PATH, DOCUMENTS_PATH, DOWNLOADS_PATH


def test_desktop_path_allowed():
    assert is_path_allowed(DESKTOP_PATH / "test.txt")


def test_documents_path_allowed():
    assert is_path_allowed(DOCUMENTS_PATH / "test.txt")


def test_downloads_path_allowed():
    assert is_path_allowed(DOWNLOADS_PATH / "test.txt")


def test_desktop_subfolder_allowed():
    assert is_path_allowed(DESKTOP_PATH / "subpasta" / "arquivo.txt")


def test_system_path_blocked():
    assert not is_path_allowed(Path("C:/Windows/System32/test.txt"))


def test_root_path_blocked():
    assert not is_path_allowed(Path("C:/test.txt"))


def test_program_files_blocked():
    assert not is_path_allowed(Path("C:/Program Files/test.txt"))


def test_parent_traversal_blocked():
    traversal = DESKTOP_PATH / ".." / ".." / "Windows"
    assert not is_path_allowed(traversal)


def test_validate_allowed_path():
    allowed, resolved, msg = validate_path(str(DESKTOP_PATH / "test.txt"))
    assert allowed is True
    assert msg == ""


def test_validate_blocked_path():
    allowed, resolved, msg = validate_path("C:/Windows/test.txt")
    assert allowed is False
    assert "fora das pastas permitidas" in msg
