## { MODULE

##
## === DEPENDENCIES
##

## stdlib
import argparse
import subprocess
import sys

## local
from ssh_helper import key_generation
from ssh_helper import shell_interface

##
## === COMMANDS
##


def cmd_generate_key(
    args: argparse.Namespace,
) -> None:
    config = key_generation.SSHKeyConfig(
        name=args.name,
        purpose=args.purpose,
        device=args.device,
    )
    key_generation.ensure_name_is_valid(name=config.name)
    key_generation.ensure_key_does_not_exist(private_file=config.private_file)
    key_generation.ensure_ssh_dir()
    key_generation.generate_key(config=config)
    key_generation.write_key_record(config=config)
    key_generation.print_next_steps(config=config)


##
## === ENTRY POINT
##


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ssh_helper",
        description="A CLI tool for SSH key setup.",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="<command>",
    )

    generate_key_parser = subparsers.add_parser(
        "generate-key",
        help="generate a new ed25519 SSH key with a standardised name and write a key record",
    )
    generate_key_parser.add_argument(
        "--name",
        required=True,
        help="suffix for ~/.ssh/id_ed25519_<NAME>",
    )
    generate_key_parser.add_argument(
        "--purpose",
        required=True,
        help="short description of what the key is for",
    )
    generate_key_parser.add_argument(
        "--device",
        required=True,
        help="device the key is generated from",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "generate-key":
            cmd_generate_key(args)
    except subprocess.CalledProcessError as exc:
        shell_interface.kill(f"command failed: {' '.join(exc.cmd)}")
    except KeyboardInterrupt:
        shell_interface.kill("interrupted")


## } MODULE
