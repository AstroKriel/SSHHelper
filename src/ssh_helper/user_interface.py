## { MODULE

##
## === DEPENDENCIES
##

## stdlib
from typing import ClassVar

## personal
from huginn import (
    cmd_args,
    manage_cli,
    manage_log,
)

## local
from ssh_helper import (
    host_keys,
    ssh_keys,
)

##
## === INPUT VALUE TYPES
##


class InputValueTypes(cmd_args.InputValueTypes):
    HOST: ClassVar[cmd_args.InputValueType] = cmd_args.InputValueType(
        placeholder_name="host",
        convert_fn=str,
    )
    FINGERPRINT: ClassVar[cmd_args.InputValueType] = cmd_args.InputValueType(
        placeholder_name="fingerprint",
        convert_fn=str,
    )


##
## === COMMANDS
##


def generate_key(
    *,
    name: str,
    purpose: str,
    device: str,
    no_passphrase: bool,
) -> None:
    """Create ~/.ssh/id_ed25519_<name> with a standard comment and a record; refuse if it exists."""
    ssh_key = ssh_keys.SSHKey(key_name=name)
    try:
        ssh_keys.create_key(
            ssh_key=ssh_key,
            purpose=purpose,
            device=device,
            no_passphrase=no_passphrase,
        )
    except (ValueError, FileExistsError) as error:
        manage_log.exit_with_error(str(error))
    public_key = ssh_keys.read_public_key(ssh_key=ssh_key)
    manage_log.log_note(
        "share the public key with the host granting access",
        items={"public key": public_key},
    )


def trust_host(
    *,
    host: str,
    fingerprint: str,
) -> None:
    """Add the host key of `host` to ~/.ssh/known_hosts once its fingerprint matches `fingerprint`."""
    try:
        host_keys.ensure_host_trusted(
            host=host,
            expected_fingerprint=fingerprint,
        )
    except ValueError as error:
        manage_log.exit_with_error(str(error))


##
## === COMMAND TABLE
##

COMMAND_LINE_TOOL = manage_cli.CommandLineTool(
    name="ssh_helper",
    description="SSH key setup with standard names, comments, and records",
    cmd_groups=[
        manage_cli.CommandGroup(
            title="Keys",
            cmds=[
                manage_cli.Command(
                    name="generate-key",
                    description=
                    "create ~/.ssh/id_ed25519_<name> with a standard comment and a record of how it was made",
                    fn=generate_key,
                    args=[
                        cmd_args.NamedArgument(
                            long_arg_name="name",
                            description="suffix for ~/.ssh/id_ed25519_<name>",
                            input_value_type=InputValueTypes.TEXT,
                            is_required=True,
                        ),
                        cmd_args.NamedArgument(
                            long_arg_name="purpose",
                            description="short description of what the key is for",
                            input_value_type=InputValueTypes.TEXT,
                            is_required=True,
                        ),
                        cmd_args.NamedArgument(
                            long_arg_name="device",
                            description="device the key is generated from",
                            input_value_type=InputValueTypes.TEXT,
                            is_required=True,
                        ),
                        cmd_args.FlagArgument(
                            long_arg_name="no-passphrase",
                            description="create the key without a passphrase, for unattended use such as cron",
                        ),
                    ],
                ),
            ],
        ),
        manage_cli.CommandGroup(
            title="Hosts",
            cmds=[
                manage_cli.Command(
                    name="trust-host",
                    description=
                    "add a host key to ~/.ssh/known_hosts once its fingerprint matches the one given",
                    fn=trust_host,
                    args=[
                        cmd_args.NamedArgument(
                            long_arg_name="host",
                            description="host name, e.g. github.com",
                            input_value_type=InputValueTypes.HOST,
                            is_required=True,
                        ),
                        cmd_args.NamedArgument(
                            long_arg_name="fingerprint",
                            description=
                            "expected SHA256 fingerprint of its ed25519 host key, from a trusted source",
                            input_value_type=InputValueTypes.FINGERPRINT,
                            is_required=True,
                        ),
                    ],
                ),
            ],
        ),
    ],
)

##
## === ENTRY POINT
##


def main() -> None:
    log_file_path = manage_log.get_home_log_file_path(tool_name=COMMAND_LINE_TOOL.name)
    manage_log.set_log_file_path(log_file_path=log_file_path)
    manage_cli.run_cli(command_line_tool=COMMAND_LINE_TOOL)


## } MODULE
