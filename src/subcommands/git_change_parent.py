from __future__ import print_function

from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand

if False:
    from typing import Text


class GitChangeParent(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return 'change-parent'

    def get_short_description(self):
        # type: () -> Text
        return 'change the parent branch of the currently checked out branch'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument("new_parent", help="the name of the branch to be this branch's parent")

    def run_command(self, args):
        # type: (Namespace) -> None
        new_parent = args.new_parent
        current_branch = get_current_branch()
        with get_branch_tracker() as tracker:
            tracker.set_parent(current_branch, new_parent)
        print("You may want to rebase on top of the new parent to make sure its changes are "
              "visible in this branch.")
