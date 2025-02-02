from pathlib import Path

import pytest
from pydantic import ValidationError

from src.grpy.tools.path_manager import PathManager


@pytest.fixture
def invalid_path():
    return Path("/invalid/filesystem/path")


@pytest.fixture(scope="session")
def generate_path(tmp_path_factory):
    dir = tmp_path_factory.mktemp("data")
    return dir


@pytest.fixture
def mock_cwd(monkeypatch, generate_path):
    monkeypatch.chdir(generate_path)
    return generate_path


def test_path_manager_init_with_default_cwd(mock_cwd, generate_path):
    pm = PathManager()

    assert isinstance(pm, PathManager)
    assert pm.target == generate_path


def test_path_manager_update_target_after_init(mock_cwd, tmp_path_factory):
    path2 = tmp_path_factory.mktemp("path2")

    path_manager = PathManager()
    path_manager.target = path2

    assert path_manager.target == path2


def test_path_manager_path_unreadable(invalid_path):
    with pytest.raises(ValidationError) as exc_info:
        PathManager(target=invalid_path)
    assert f"Path is not readable: {invalid_path}" in str(exc_info.value)


def test_path_manager_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        PathManager(target=123)

    assert "Input should be an instance of Path" in str(exc_info.value)


def test_path_manager_multiple_updates(mock_cwd, tmp_path_factory):
    path1 = tmp_path_factory.mktemp("path1")
    path2 = tmp_path_factory.mktemp("path2")
    path3 = tmp_path_factory.mktemp("path3")

    pm = PathManager(target=path1)
    assert pm.target == path1

    pm.target = path2
    assert pm.target == path2

    pm.target = path3
    assert pm.target == path3


def test_path_manager_relative_path(mock_cwd):
    relative_path = Path("./test_dir")
    relative_path.mkdir(exist_ok=True)

    with pytest.raises(ValidationError):
        PathManager(target=relative_path)

    relative_path.rmdir()


def test_path_manager_rejects_file(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("test_dir")
    tmp_file = tmp_dir / "test.txt"
    tmp_file.write_text("test content")

    tmp_file.chmod(0o644)

    with pytest.raises(ValueError) as exc_info:
        PathManager(target=tmp_file)

    assert PathManager.ERROR_NOT_DIRECTORY.format(tmp_file) in str(exc_info.value)
