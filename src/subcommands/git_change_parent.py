from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand


class GitChangeParent(BaseCommand):
    def get_name(self) -> str:
        return "change-parent"

    def get_short_description(self) -> str:
        return "change the parent branch of the currently checked out branch"

    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument("new_parent", help="the name of the branch to be this branch's parent")
        parser.add_argument(
            "--branch",
            "-b",
            required=False,
            help=(
                "the branch to change the parent of. If not supplied, it changes the parent of " "the current branch."
            ),
        )

    def run_command(self, args: Namespace) -> None:
        new_parent = args.new_parent
        branch = args.branch or get_current_branch()
        with get_branch_tracker() as tracker:
            tracker.set_parent(branch, new_parent)
        print("You may want to rebase on top of the new parent to make sure its changes are " "visible in this branch.")
