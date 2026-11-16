## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import base64
import hashlib
from pathlib import Path

## personal
from huginn import manage_log, manage_shell

## local
from ssh_helper import ssh_keys

##
## === HOST KEYS
## a host is trusted by adding its public key to ~/.ssh/known_hosts, once its fingerprint matches one the caller
## already knows from a source other than the connection itself, such as the documentation of the host.
##

HOST_KEY_TYPE = "ed25519"


def get_known_hosts_path() -> Path:
    return ssh_keys.SSH_DIR / "known_hosts"


def compute_fingerprint(
    *,
    public_key_text: str,
) -> str:
    """The SHA256 fingerprint of an OpenSSH public key line, as `ssh-keygen -l` prints it."""
    key_fields = public_key_text.split()
    key_blob_text = key_fields[1]
    key_blob = base64.b64decode(key_blob_text)
    key_digest = hashlib.sha256(key_blob).digest()
    key_digest_text = base64.b64encode(key_digest).decode()
    return "SHA256:" + key_digest_text.rstrip("=")


def _get_host_key_line(
    *,
    host: str,
) -> str:
    cmd_scan_host = [
        "ssh-keyscan",
        "-t",
        HOST_KEY_TYPE,
        host,
    ]
    scan_output = manage_shell.query_cmd_and_capture_output(cmd_parts=cmd_scan_host)
    key_lines = [
        _line for _line in scan_output.splitlines() if (_line.strip() != "") and (not _line.startswith("#"))
    ]
    if len(key_lines) == 0:
        raise ValueError(f"`{host}` offered no {HOST_KEY_TYPE} host key")
    return key_lines[0]


def _get_known_host_lines(
    *,
    host: str,
) -> list[str]:
    known_hosts_path = get_known_hosts_path()
    if not known_hosts_path.is_file():
        return []
    cmd_find_host = [
        "ssh-keygen",
        "-F",
        host,
        "-f",
        str(known_hosts_path),
    ]
    find_output = manage_shell.query_cmd_and_capture_output(
        cmd_parts=cmd_find_host,
        raise_error=False,
    )
    return [
        _line for _line in find_output.splitlines() if (_line.strip() != "") and (not _line.startswith("#"))
    ]


def _append_known_host_line(
    *,
    host_key_line: str,
) -> None:
    known_hosts_path = get_known_hosts_path()
    known_hosts_path.parent.mkdir(
        mode=0o700,
        exist_ok=True,
    )
    with known_hosts_path.open("a") as known_hosts_file:
        known_hosts_file.write(host_key_line + "\n")


def ensure_host_trusted(
    *,
    host: str,
    expected_fingerprint: str,
) -> None:
    """Add the host key to known_hosts if its fingerprint matches `expected_fingerprint`; safe to repeat."""
    host_key_line = _get_host_key_line(host=host)
    host_key_fields = host_key_line.split()
    host_public_key_text = " ".join(host_key_fields[1:3])
    host_fingerprint = compute_fingerprint(public_key_text=host_public_key_text)
    if host_fingerprint != expected_fingerprint:
        raise ValueError(
            f"the {HOST_KEY_TYPE} host key of `{host}` has fingerprint {host_fingerprint}, not the expected "
            f"{expected_fingerprint}; it is not trusted",
        )
    known_host_lines = _get_known_host_lines(host=host)
    host_key_blob_text = host_key_fields[2]
    host_is_known = any((host_key_blob_text in _known_host_line) for _known_host_line in known_host_lines)
    if host_is_known:
        manage_log.log_note(f"`{host}` is already trusted, with fingerprint {host_fingerprint}")
        return
    manage_shell.run_fn(
        description=f"add the host key of `{host}` to {get_known_hosts_path()}",
        fn=lambda: _append_known_host_line(host_key_line=host_key_line),
    )
    manage_log.log_outcome(
        f"trusted `{host}`",
        status=manage_log.OutcomeStatus.SUCCESS,
        items={"fingerprint": host_fingerprint},
    )


## } MODULE
