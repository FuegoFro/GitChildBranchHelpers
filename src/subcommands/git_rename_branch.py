from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch, git
from subcommands.base_command import BaseCommand
from type_utils import MYPY

if MYPY:
    from typing import Text


class GitRenameBranch(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return 'rename'

    def get_short_description(self):
        # type: () -> Text
        return 'rename the current branch'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument("-f", "--force", action="store_true", help="Force the deletion of the current branch")
        parser.add_argument("new_branch_name", help='the new name for the current branch')

    def run_command(self, args):
        # type: (Namespace) -> None
        rename_current_branch(args.new_branch_name, args.force)


def rename_current_branch(new_branch_name, force):
    # type: (Text, bool) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        git("checkout -b {}".format(new_branch_name))
        flag = "-D" if force else "-d"
        git("branch {} {}".format(flag, current_branch))
        tracker.rename_branch(current_branch, new_branch_name)
