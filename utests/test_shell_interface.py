## { U-TEST

##
## === DEPENDENCIES
##

## stdlib
from unittest.mock import MagicMock, patch

## third-party
import pytest

## local
from ssh_helper import shell_interface

##
## === LOGGING
##


class TestLogStep_Output:

    def test_writes_to_stderr(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.log_step("doing something")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "doing something" in captured.err

    def test_includes_step_marker(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.log_step("doing something")
        captured = capsys.readouterr()
        assert "○" in captured.err


class TestLogOutcome_Output:

    def test_writes_to_stderr(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.log_outcome("it worked")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "it worked" in captured.err

    def test_includes_outcome_marker(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.log_outcome("it worked")
        captured = capsys.readouterr()
        assert "●" in captured.err


class TestBindVar_Output:

    def test_writes_to_stderr(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.bind_var("key_name", "github")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "key_name" in captured.err
        assert "github" in captured.err

    def test_includes_arrow_marker(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.bind_var("key_name", "github")
        captured = capsys.readouterr()
        assert "→" in captured.err


class TestLogResult_Output:

    def test_writes_to_stdout(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.log_result("all done")
        captured = capsys.readouterr()
        assert captured.err == ""
        assert "all done" in captured.out

    def test_includes_outcome_marker(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        shell_interface.log_result("all done")
        captured = capsys.readouterr()
        assert "●" in captured.out


##
## === EXECUTION
##


class TestKill_Behaviour:

    def test_exits_with_code_1(
        self,
    ) -> None:
        with pytest.raises(
            SystemExit,
        ) as exc_info:
            shell_interface.kill("something went wrong")
        assert exc_info.value.code == 1

    def test_writes_error_to_stderr(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        with pytest.raises(SystemExit):
            shell_interface.kill("something went wrong")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "something went wrong" in captured.err


class TestRunCmd_Behaviour:

    def test_calls_subprocess_run(
        self,
    ) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            shell_interface.run_cmd(["echo", "hello"])
            mock_run.assert_called_once()

    def test_logs_command_to_stderr(
        self,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            shell_interface.run_cmd(["echo", "hello"])
            captured = capsys.readouterr()
            assert "echo hello" in captured.err


## } U-TEST
