from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch, git
from subcommands.base_command import BaseCommand


class GitRenameBranch(BaseCommand):
    def get_name(self):
        # type: () -> str
        return 'rename'

    def get_short_description(self):
        # type: () -> str
        return 'rename the current branch'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument("new_branch_name", help='the new name for the current branch')

    def run_command(self, args):
        # type: (Namespace) -> None
        rename_current_branch(args.new_branch_name)


def rename_current_branch(new_branch_name):
    # type: (str) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        git("checkout -b %s" % new_branch_name)
        git("branch -d %s" % current_branch)
        tracker.rename_branch(current_branch, new_branch_name)
