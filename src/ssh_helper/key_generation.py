## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import datetime
import re
from dataclasses import dataclass, field
from pathlib import Path

## local
from ssh_helper import shell_interface

##
## === CONSTANTS
##

SSH_DIR = Path.home() / ".ssh"
SSH_RECORDS_DIR = SSH_DIR / "records"

##
## === DATA MODELS
##


@dataclass
class SSHKeyConfig:
    name: str
    purpose: str
    device: str
    today: str = field(init=False)
    comment: str = field(init=False)
    private_file: Path = field(init=False)
    public_file: Path = field(init=False)
    record_file: Path = field(init=False)

    def __post_init__(
        self,
    ) -> None:
        self.today = datetime.date.today().strftime("%Y-%m-%d")
        self.comment = f"for {self.purpose} from {self.device} created on {self.today}"
        self.private_file = SSH_DIR / f"id_ed25519_{self.name}"
        self.public_file = self.private_file.with_suffix(".pub")
        self.record_file = SSH_RECORDS_DIR / f"{self.name}-{self.today}.txt"


##
## === PIPELINE STEPS
##


def ensure_name_is_valid(
    *,
    name: str,
) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        shell_interface.kill("`--name` must be alphanumeric, dash, or underscore.")


def ensure_key_does_not_exist(
    *,
    private_file: Path,
) -> None:
    if private_file.exists():
        shell_interface.kill(f"SSH key already exists at {private_file}.")


def ensure_ssh_dir() -> None:
    SSH_DIR.mkdir(mode=0o700, exist_ok=True)
    SSH_DIR.chmod(0o700)
    shell_interface.log_outcome(f"{SSH_DIR} ok")


def generate_key(
    *,
    config: SSHKeyConfig,
) -> None:
    shell_interface.run_cmd([
        "ssh-keygen",
        "-t", "ed25519",
        "-a", "100",
        "-f", str(config.private_file),
        "-C", config.comment,
    ])
    config.private_file.chmod(0o600)


def write_key_record(
    *,
    config: SSHKeyConfig,
) -> None:
    SSH_RECORDS_DIR.mkdir(mode=0o700, exist_ok=True)
    SSH_RECORDS_DIR.chmod(0o700)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    public_key = config.public_file.read_text().rstrip("\n")
    config.record_file.write_text(
        f"# {config.name}\n"
        f"# Created: {timestamp}\n"
        f"\n"
        f"## Command ran\n"
        f'ssh-keygen -t ed25519 -a 100 -f "{config.private_file}" -C "{config.comment}"\n'
        f"\n"
        f"## Files produced\n"
        f"{config.private_file}  (private; never share its contents)\n"
        f"{config.public_file}  (public; share with the host granting access)\n"
        f"\n"
        f"## Public key\n"
        f"{public_key}\n"
        f"\n"
        f"## SSH config block\n"
        f"Host <ALIAS>\n"
        f"\tHostName <REMOTE_HOST>\n"
        f"\tUser <REMOTE_USER>\n"
        f"\tIdentityFile {config.private_file}\n"
        f"\tIdentitiesOnly yes\n"
        f"\n"
        f"## Deploy the key\n"
        f"ssh-copy-id -i {config.public_file} <REMOTE_USER>@<REMOTE_HOST>\n"
        f"\n"
        f"## Test the connection\n"
        f"ssh <ALIAS>\n",
    )
    config.record_file.chmod(0o600)
    shell_interface.log_outcome(f"Record saved to {config.record_file}")


def print_next_steps(
    *,
    config: SSHKeyConfig,
) -> None:
    shell_interface.log_step("Next steps:")
    shell_interface.log_step(f"1. Add the following block to ~/.ssh/config (replace the placeholders):")
    print(
        f"\n"
        f"\tHost <ALIAS>\n"
        f"\t\tHostName <REMOTE_HOST>\n"
        f"\t\tUser <REMOTE_USER>\n"
        f"\t\tIdentityFile {config.private_file}\n"
        f"\t\tIdentitiesOnly yes\n"
    )
    shell_interface.log_step("2. Deploy the key to the remote host:")
    print(f"\n\tssh-copy-id -i {config.public_file} <REMOTE_USER>@<REMOTE_HOST>\n")
    shell_interface.log_step("3. Test the connection:")
    print(f"\n\tssh <ALIAS>\n")
    shell_interface.log_outcome(f"Full record saved to {config.record_file}")


## } MODULE
