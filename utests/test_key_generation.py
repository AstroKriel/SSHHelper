## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
import tempfile
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, patch

## local
from ssh_helper import key_generation

##
## === TEST SUITE
##


class TestSSHKeyConfig_Paths(unittest.TestCase):

    def test_private_key_path_uses_name(
        self,
    ) -> None:
        config = key_generation.SSHKeyConfig(
            name="github",
            purpose="github access",
            device="desktop",
        )
        self.assertEqual(
            config.private_file,
            Path.home() / ".ssh" / "id_ed25519_github",
        )

    def test_public_key_path_is_private_with_pub_suffix(
        self,
    ) -> None:
        config = key_generation.SSHKeyConfig(
            name="github",
            purpose="github access",
            device="desktop",
        )
        self.assertEqual(
            config.public_file,
            config.private_file.with_suffix(".pub"),
        )

    def test_record_file_path_includes_name(
        self,
    ) -> None:
        config = key_generation.SSHKeyConfig(
            name="github",
            purpose="github access",
            device="desktop",
        )
        self.assertIn(
            "github",
            config.record_file.name,
        )

    def test_comment_includes_purpose_and_device(
        self,
    ) -> None:
        config = key_generation.SSHKeyConfig(
            name="github",
            purpose="github access",
            device="desktop",
        )
        self.assertIn(
            "github access",
            config.comment,
        )
        self.assertIn(
            "desktop",
            config.comment,
        )


class TestEnsureNameIsValid_ValidNames(unittest.TestCase):

    def test_accepts_lowercase(
        self,
    ) -> None:
        key_generation.ensure_name_is_valid(name="github")

    def test_accepts_uppercase(
        self,
    ) -> None:
        key_generation.ensure_name_is_valid(name="GITHUB")

    def test_accepts_digits(
        self,
    ) -> None:
        key_generation.ensure_name_is_valid(name="github2")

    def test_accepts_dash(
        self,
    ) -> None:
        key_generation.ensure_name_is_valid(name="my-key")

    def test_accepts_underscore(
        self,
    ) -> None:
        key_generation.ensure_name_is_valid(name="my_key")


class TestEnsureNameIsValid_InvalidNames(unittest.TestCase):

    def test_rejects_space(
        self,
    ) -> None:
        with self.assertRaises(
            SystemExit,
        ):
            key_generation.ensure_name_is_valid(name="my key")

    def test_rejects_dot(
        self,
    ) -> None:
        with self.assertRaises(
            SystemExit,
        ):
            key_generation.ensure_name_is_valid(name="my.key")

    def test_rejects_slash(
        self,
    ) -> None:
        with self.assertRaises(
            SystemExit,
        ):
            key_generation.ensure_name_is_valid(name="my/key")

    def test_rejects_at_symbol(
        self,
    ) -> None:
        with self.assertRaises(
            SystemExit,
        ):
            key_generation.ensure_name_is_valid(name="user@host")


class TestEnsureKeyDoesNotExist_Behaviour(unittest.TestCase):

    def test_exits_if_private_key_exists(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            private_file = Path(tmp_dir) / "id_ed25519_github"
            private_file.touch()
            with self.assertRaises(
                SystemExit,
            ):
                key_generation.ensure_key_does_not_exist(private_file=private_file)

    def test_passes_if_private_key_absent(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            private_file = Path(tmp_dir) / "id_ed25519_github"
            key_generation.ensure_key_does_not_exist(private_file=private_file)


class TestGenerateKey_Behaviour(unittest.TestCase):

    def test_calls_ssh_keygen(
        self,
    ) -> None:
        config = key_generation.SSHKeyConfig(
            name="github",
            purpose="github access",
            device="desktop",
        )
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("pathlib.Path.chmod"):
                key_generation.generate_key(config=config)
            args = cast(list[str], mock_run.call_args[0][0])
            self.assertEqual(
                args[0],
                "ssh-keygen",
            )
            self.assertIn(
                "ed25519",
                args,
            )
            self.assertIn(
                str(config.private_file),
                args,
            )
            self.assertIn(
                config.comment,
                args,
            )

    def test_sets_private_key_permissions(
        self,
    ) -> None:
        config = key_generation.SSHKeyConfig(
            name="github",
            purpose="github access",
            device="desktop",
        )
        with patch("subprocess.run"):
            with patch("pathlib.Path.chmod") as mock_chmod:
                key_generation.generate_key(config=config)
            mock_chmod.assert_called_once_with(
                0o600,
            )


##
## === ENTRY POINT
##

if __name__ == "__main__":
    _ = unittest.main()

## } U-TEST
