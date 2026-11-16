## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
from pathlib import Path

## third-party
import pytest

## local
from ssh_helper import ssh_keys

##
## === TEST SUITE
##


class TestSSHKey_Paths:

    def test_paths_follow_the_key_name(
        self,
        some_ssh_dir: Path,
    ) -> None:
        ssh_key = ssh_keys.SSHKey(key_name="github")
        assert ssh_key.private_key_path == some_ssh_dir / "id_ed25519_github"
        assert ssh_key.public_key_path == some_ssh_dir / "id_ed25519_github.pub"
        assert ssh_key.records_dir == some_ssh_dir / "records"


class TestCreateKey:

    def test_key_comment_and_record_are_written(
        self,
        some_ssh_dir: Path,
    ) -> None:
        ssh_key = ssh_keys.SSHKey(key_name="some-key")
        ssh_keys.create_key(
            ssh_key=ssh_key,
            purpose="some purpose",
            device="some-device",
            no_passphrase=True,
        )
        public_key = ssh_keys.read_public_key(ssh_key=ssh_key)
        record_paths = list(ssh_key.records_dir.glob("some-key-*.txt"))
        assert ssh_key.private_key_path.is_file()
        assert public_key.startswith("ssh-ed25519 ")
        assert "for some purpose from some-device created on " in public_key
        assert len(record_paths) == 1
        assert public_key in record_paths[0].read_text()
        assert (some_ssh_dir.stat().st_mode & 0o777) == 0o700

    @pytest.mark.usefixtures("some_ssh_dir")
    def test_existing_key_is_refused(
        self,
    ) -> None:
        ssh_key = ssh_keys.SSHKey(key_name="some-key")
        ssh_keys.create_key(
            ssh_key=ssh_key,
            purpose="some purpose",
            device="some-device",
            no_passphrase=True,
        )
        with pytest.raises(FileExistsError):
            ssh_keys.create_key(
                ssh_key=ssh_key,
                purpose="some purpose",
                device="some-device",
                no_passphrase=True,
            )

    @pytest.mark.usefixtures("some_ssh_dir")
    def test_invalid_key_name_is_refused(
        self,
    ) -> None:
        with pytest.raises(ValueError, match="letters, digits"):
            ssh_keys.create_key(
                ssh_key=ssh_keys.SSHKey(key_name="some key"),
                purpose="some purpose",
                device="some-device",
                no_passphrase=True,
            )


class TestEnsureKeyExists:

    @pytest.mark.usefixtures("some_ssh_dir")
    def test_existing_key_is_kept(
        self,
    ) -> None:
        ssh_key = ssh_keys.SSHKey(key_name="some-key")
        ssh_keys.ensure_key_exists(
            ssh_key=ssh_key,
            purpose="some purpose",
            device="some-device",
            no_passphrase=True,
        )
        first_public_key = ssh_keys.read_public_key(ssh_key=ssh_key)
        ssh_keys.ensure_key_exists(
            ssh_key=ssh_key,
            purpose="some purpose",
            device="some-device",
            no_passphrase=True,
        )
        assert ssh_keys.read_public_key(ssh_key=ssh_key) == first_public_key


## } U-TEST
