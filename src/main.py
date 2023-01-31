import argparse

from subcommands import get_commands
from subcommands.base_command import BaseCommand


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title="actions", description="valid actions", help="run <action> -h for more details"
    )

    for command in get_commands():
        command_parser = subparsers.add_parser(command.get_name(), help=command.get_short_description())
        command.inflate_subcommand_parser(command_parser)
        command_parser.set_defaults(command_obj=command)

    args = parser.parse_args()
    command_obj: BaseCommand = args.command_obj
    del args.command_obj
    command_obj.run_command(args)


if __name__ == "__main__":
    main()
