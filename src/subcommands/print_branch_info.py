import sys
from argparse import ArgumentParser, Namespace
from typing import Optional

from git_helpers import get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand


class PrintBranchInfo(BaseCommand):
    def get_name(self) -> str:
        return "print-branch-info"

    def get_short_description(self) -> str:
        return "prints parent name and base revision of a single branch"

    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-z",
            action="store_true",
            help=(
                "use null byte delimiters between fields and skip field names. "
                "Output becomes '<parent_branch_name>\\0<base_revision>\\n'"
            ),
        )
        parser.add_argument(
            "branch", nargs="?", help="which branch to print information for; defaults to current branch"
        )

    def run_command(self, args: Namespace) -> None:
        print(get_branch_info(args.branch, args.z))


def get_branch_info(branch: Optional[str], use_null_delimiter: bool) -> str:
    if branch is None:
        branch = get_current_branch()

    with get_branch_tracker() as tracker:
        if not tracker.has_parent(branch):
            sys.exit("Branch does not have a parent: {}".format(branch))
        parent = tracker.parent_for_child(branch)
        base = tracker.base_for_branch(branch)

    if use_null_delimiter:
        return "{}\0{}".format(parent, base)
    else:
        return "Parent branch: {}; Base revision: {}".format(parent, base)
