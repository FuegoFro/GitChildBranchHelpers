from __future__ import unicode_literals

from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand
from typing import Optional, Text


class SetBranchArchived(BaseCommand):
    def get_name(self) -> Text:
        return "set-archived"

    def get_short_description(self) -> Text:
        return "sets whether or not a branch is 'archived'"

    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-u", "--unarchive", action="store_true", help="if set, un-archive the given branch; otherwise, archive it"
        )
        parser.add_argument(
            "branch_to_set_archive_property",
            nargs="?",
            help="which branch to operate on. If not supplied, operates on the current branch.",
        )

    def run_command(self, args: Namespace) -> None:
        set_archived(not args.unarchive, args.branch_to_set_archive_property)


def set_archived(archived: bool, branch_name: Optional[Text] = None) -> None:
    if branch_name is None:
        branch_name = get_current_branch()
    with get_branch_tracker() as tracker:
        tracker.set_is_archived(branch_name, archived)
