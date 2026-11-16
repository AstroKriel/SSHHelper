## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import datetime
import re
from dataclasses import dataclass
from pathlib import Path

## personal
from huginn import manage_log, manage_shell

##
## === SSH KEYS
## every key is an ed25519 key named ~/.ssh/id_ed25519_<key-name>, with the comment
## `for <purpose> from <device> created on <date>`, and a record of how it was made under ~/.ssh/records/.
##

SSH_DIR = Path.home() / ".ssh"
_KEY_NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]+")


@dataclass(frozen=True)
class SSHKey:
    key_name: str

    @property
    def private_key_path(
        self,
    ) -> Path:
        return SSH_DIR / f"id_ed25519_{self.key_name}"

    @property
    def public_key_path(
        self,
    ) -> Path:
        return self.private_key_path.with_suffix(".pub")

    @property
    def records_dir(
        self,
    ) -> Path:
        return SSH_DIR / "records"


def ensure_valid_key_name(
    *,
    key_name: str,
) -> None:
    if _KEY_NAME_PATTERN.fullmatch(key_name) is None:
        raise ValueError(f"a key name holds only letters, digits, `-`, and `_`; got `{key_name}`")


def read_public_key(
    *,
    ssh_key: SSHKey,
) -> str:
    public_key_text = ssh_key.public_key_path.read_text()
    return public_key_text.strip()


def _write_key_record(
    *,
    ssh_key: SSHKey,
    record_path: Path,
    keygen_cmd: list[str],
) -> None:
    ssh_key.records_dir.mkdir(
        mode=0o700,
        exist_ok=True,
    )
    created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    public_key = read_public_key(ssh_key=ssh_key)
    keygen_cmd_text = " ".join(keygen_cmd)
    record_text = (
        f"# {ssh_key.key_name}\n"
        f"# Created: {created_time}\n"
        f"\n"
        f"## Command ran\n"
        f"{keygen_cmd_text}\n"
        f"\n"
        f"## Files produced\n"
        f"{ssh_key.private_key_path}  (private; never share its contents)\n"
        f"{ssh_key.public_key_path}  (public; share with the host granting access)\n"
        f"\n"
        f"## Public key\n"
        f"{public_key}\n"
    )
    record_path.write_text(record_text)
    record_path.chmod(0o600)


def create_key(
    *,
    ssh_key: SSHKey,
    purpose: str,
    device: str,
    no_passphrase: bool,
) -> None:
    """Create the key and its record; refuse if a key of that name exists. `no_passphrase` is for unattended use."""
    ensure_valid_key_name(key_name=ssh_key.key_name)
    if ssh_key.private_key_path.exists():
        raise FileExistsError(f"an SSH key already exists at {ssh_key.private_key_path}")
    today_text = datetime.date.today().isoformat()
    key_comment = f"for {purpose} from {device} created on {today_text}"
    keygen_cmd = [
        "ssh-keygen",
        "-t",
        "ed25519",
        "-a",
        "100",
        "-f",
        str(ssh_key.private_key_path),
        "-C",
        key_comment,
    ]
    if no_passphrase:
        keygen_cmd.extend(["-N", ""])
    record_path = ssh_key.records_dir / f"{ssh_key.key_name}-{today_text}.txt"
    manage_shell.run_fn(
        description=f"create {SSH_DIR} with access for its owner only",
        fn=lambda: SSH_DIR.mkdir(
            mode=0o700,
            exist_ok=True,
        ),
    )
    manage_shell.run_cmd_and_show_output(cmd_parts=keygen_cmd)
    manage_shell.run_fn(
        description=f"write the record {record_path}",
        fn=lambda: _write_key_record(
            ssh_key=ssh_key,
            record_path=record_path,
            keygen_cmd=keygen_cmd,
        ),
    )
    manage_log.log_outcome(
        f"created {ssh_key.private_key_path}",
        status=manage_log.OutcomeStatus.SUCCESS,
        items={"record": record_path},
    )


def ensure_key_exists(
    *,
    ssh_key: SSHKey,
    purpose: str,
    device: str,
    no_passphrase: bool,
) -> None:
    """Create the key and its record unless a key of that name exists; safe to repeat."""
    if ssh_key.private_key_path.exists():
        manage_log.log_note(f"{ssh_key.private_key_path} exists, so no key is created")
        return
    create_key(
        ssh_key=ssh_key,
        purpose=purpose,
        device=device,
        no_passphrase=no_passphrase,
    )


## } MODULE
