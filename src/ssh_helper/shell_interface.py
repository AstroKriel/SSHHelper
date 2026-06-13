## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import subprocess
import sys
from enum import Enum
from dataclasses import dataclass
from typing import final

## third-party
from rich.console import Console

##
## === LOGGING
##

_CONSOLE = Console(
    highlight=False,
    stderr=True,
)
_CONSOLE_OUT = Console(
    highlight=False,
    stderr=False,
)


class _Colors(str, Enum):
    WHITE = "#FFFFFF"
    GREEN = "#32CD32"
    BLUE = "#2A71F6"
    ORANGE = "#E48500"
    RED = "#FF4500"
    GRAY = "#818181"


class _Markers(str, Enum):
    CIRCLE_OPEN = "○"   # ○
    CIRCLE_CLOSED = "●" # ●
    ARROW = "→"         # →


@dataclass(frozen=True)
class _Theme:
    color: _Colors
    marker: _Markers


@final
class _Themes:
    STEP = _Theme(color=_Colors.WHITE, marker=_Markers.CIRCLE_OPEN)
    SUCCESS = _Theme(color=_Colors.GREEN, marker=_Markers.CIRCLE_CLOSED)
    ACTION = _Theme(color=_Colors.BLUE, marker=_Markers.ARROW)
    ERROR = _Theme(color=_Colors.RED, marker=_Markers.CIRCLE_CLOSED)
    CONTEXT = _Theme(color=_Colors.GRAY, marker=_Markers.ARROW)


def log_step(
    msg: str,
) -> None:
    theme = _Themes.STEP
    _CONSOLE.print(f"[{theme.color.value}]{theme.marker.value}[/] {msg}")


def log_outcome(
    msg: str,
) -> None:
    theme = _Themes.SUCCESS
    _CONSOLE.print(f"[{theme.color.value}]{theme.marker.value} {msg}[/]")


def bind_var(
    var_name: str,
    var_value: str,
) -> None:
    theme = _Themes.CONTEXT
    _CONSOLE.print(f"[{theme.color.value}]{theme.marker.value} {var_name} = {var_value}[/]")


def log_result(
    msg: str,
) -> None:
    theme = _Themes.SUCCESS
    _CONSOLE_OUT.print(f"[{theme.color.value}]{theme.marker.value} {msg}[/]")


def kill(
    msg: str,
) -> None:
    theme = _Themes.ERROR
    _CONSOLE.print(f"[{theme.color.value}]{theme.marker.value}[/] error: {msg}")
    sys.exit(1)


##
## === EXECUTION
##


def run_cmd(
    cmd: list[str],
) -> None:
    theme = _Themes.ACTION
    cmd_string = " ".join(cmd)
    _CONSOLE.print(f"[{theme.color.value}]{theme.marker.value} {cmd_string}[/]")
    subprocess.run(
        cmd,
        check=True,
    )


## } MODULE
