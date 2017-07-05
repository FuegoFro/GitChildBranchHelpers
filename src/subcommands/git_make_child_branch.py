from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch, git, hash_for
from subcommands.base_command import BaseCommand

try:
    # noinspection PyUnresolvedReferences
    from typing import Optional
except ImportError:
    pass


class GitMakeChildBranch(BaseCommand):
    def get_name(self):
        # type: () -> str
        return 'make-branch'

    def get_short_description(self):
        # type: () -> str
        return 'creates a new branch at the current commit with the current branch as its parent'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument("new_branch_name", help='the name of the new child branch to create')
        parser.add_argument(
            "--revision", "-r",
            required=False,
            help='the revision that the new branch will point at. If not supplied, it will point '
                 'at the current commit.',
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        make_child_branch(args.new_branch_name, args.revision)


def make_child_branch(new_branch_name, revision=None):
    # type: (str, Optional[str]) -> None
    parent = get_current_branch()
    if revision is None:
        # Use the current revision as the base
        base_rev = hash_for("HEAD")
    else:
        # Use the merge-base of the given revision and the parent branch as the base
        base_rev = git("merge-base {} {}".format(parent, revision)).strip()

    with get_branch_tracker() as tracker:
        # Add the child using the current branch as the parent.
        tracker.add_child_for_parent(parent, new_branch_name, base_rev)
        # Make the new branch, either where the current branch is or at the specified revision
        if revision is None:
            command = "checkout -b {}".format(new_branch_name)
        else:
            command = "checkout -b {} {}".format(new_branch_name, revision)
        git(command)
