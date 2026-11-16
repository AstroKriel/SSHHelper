## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
from collections.abc import Iterator
from pathlib import Path

## third-party
import pytest

## personal
from huginn import manage_log

## local
from ssh_helper import ssh_keys

##
## === FIXTURES
##


@pytest.fixture(autouse=True)
def _log_nothing() -> Iterator[None]:
    manage_log.set_log_file_path(log_file_path=None)
    yield


@pytest.fixture
def some_ssh_dir(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Path:
    """Point SSH_DIR at an empty folder, so no test touches the real ~/.ssh."""
    some_ssh_dir = tmp_path / ".ssh"
    monkeypatch.setattr(ssh_keys, "SSH_DIR", some_ssh_dir)
    return some_ssh_dir


## } U-TEST
