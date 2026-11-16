# SSH Helper

`ssh_helper` sets up SSH keys the same way every time. Keys get a standard name (`~/.ssh/id_ed25519_<name>`), a comment saying what they are for, where they were made and when, and a record in `~/.ssh/records/`. Host keys are only trusted once their fingerprint matches one you got from a trusted source.

It works as a command line tool and as a library for other tools.

---

## Getting setup

Before you start, you will need [uv](https://docs.astral.sh/uv/).

Clone this repo and install `ssh_helper` as a globally accessible tool:

```bash
git clone git@github.com:AstroKriel/SSHHelper.git
cd SSHHelper
uv tool install .
```

Verify everything is working:

```bash
ssh_helper --help
```

If `ssh_helper` is not found, add `~/.local/bin` to your `PATH`.

---

## Available commands

```bash
ssh_helper generate-key --name <name> --purpose <purpose> --device <device> [--no-passphrase]
ssh_helper trust-host --host <host> --fingerprint <fingerprint>
```

`generate-key` refuses to overwrite an existing key. Use `--no-passphrase` only for keys that must work unattended, such as from cron.

`trust-host` scans the host, compares its ed25519 fingerprint with the one given, and adds it to `~/.ssh/known_hosts` only if they match. Running it again does nothing. For GitHub, the fingerprints are listed [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints).

Every command accepts `--dry-run` to show the changes without making them.

---

## Use as a library

Add it as a dependency, pinned by commit:

```toml
[project]
dependencies = ["ssh_helper"]

[tool.uv.sources]
ssh_helper = { git = "https://github.com/AstroKriel/SSHHelper.git", rev = "<commit>" }
```

Then:

```python
from ssh_helper import host_keys, ssh_keys

ssh_key = ssh_keys.SSHKey(key_name="<name>")
ssh_keys.ensure_key_exists(
    ssh_key=ssh_key,
    purpose="<purpose>",
    device="<device>",
    no_passphrase=True,
)
host_keys.ensure_host_trusted(
    host="github.com",
    expected_fingerprint="SHA256:<fingerprint>",
)
```

Both functions can be called repeatedly; they only change something the first time.

---

## File structure

```
SSHHelper/
├── src/ssh_helper/
│   ├── ssh_keys.py        # create keys with a standard name, comment, and record
│   ├── host_keys.py       # trust a host key once its fingerprint matches
│   └── user_interface.py  # command line tool
└── utests/
```
