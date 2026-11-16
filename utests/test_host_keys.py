## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
import subprocess

## third-party
import pytest

## local
from ssh_helper import (
    host_keys,
    ssh_keys,
)

##
## === TEST DATA
##


def _make_some_host_key() -> tuple[str, str]:
    """Create a key to stand in for a host key; return its known_hosts line and its fingerprint from ssh-keygen."""
    ssh_key = ssh_keys.SSHKey(key_name="some-host")
    ssh_keys.create_key(
        ssh_key=ssh_key,
        purpose="standing in for a host key",
        device="tests",
        no_passphrase=True,
    )
    public_key = ssh_keys.read_public_key(ssh_key=ssh_key)
    public_key_fields = public_key.split()
    host_key_line = f"some.host {public_key_fields[0]} {public_key_fields[1]}"
    fingerprint_output = subprocess.run(
        ["ssh-keygen", "-lf", str(ssh_key.public_key_path)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    fingerprint = fingerprint_output.split()[1]
    return host_key_line, fingerprint


def _scan_host_offline(
    monkeypatch: pytest.MonkeyPatch,
    host_key_line: str,
) -> None:
    """Replace the ssh-keyscan call, so tests never reach the network."""

    def _get_host_key_line(
        *,
        host: str,
    ) -> str:
        assert host == "some.host"
        return host_key_line

    monkeypatch.setattr(host_keys, "_get_host_key_line", _get_host_key_line)


##
## === TEST SUITE
##


@pytest.mark.usefixtures("some_ssh_dir")
class TestComputeFingerprint:

    def test_matches_ssh_keygen(
        self,
    ) -> None:
        host_key_line, fingerprint = _make_some_host_key()
        host_key_fields = host_key_line.split()
        public_key_text = " ".join(host_key_fields[1:3])
        assert host_keys.compute_fingerprint(public_key_text=public_key_text) == fingerprint


@pytest.mark.usefixtures("some_ssh_dir")
class TestEnsureHostTrusted:

    def test_matching_host_is_added_once(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        host_key_line, fingerprint = _make_some_host_key()
        _scan_host_offline(monkeypatch, host_key_line)
        host_keys.ensure_host_trusted(
            host="some.host",
            expected_fingerprint=fingerprint,
        )
        host_keys.ensure_host_trusted(
            host="some.host",
            expected_fingerprint=fingerprint,
        )
        known_hosts_lines = host_keys.get_known_hosts_path().read_text().splitlines()
        assert known_hosts_lines == [host_key_line]

    def test_mismatching_host_is_refused(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        host_key_line, _fingerprint = _make_some_host_key()
        _scan_host_offline(monkeypatch, host_key_line)
        with pytest.raises(ValueError, match="not trusted"):
            host_keys.ensure_host_trusted(
                host="some.host",
                expected_fingerprint="SHA256:not-the-fingerprint",
            )
        assert not host_keys.get_known_hosts_path().exists()


## } U-TEST
