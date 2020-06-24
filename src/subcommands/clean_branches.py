from __future__ import print_function, unicode_literals

from argparse import ArgumentParser, Namespace

from git_helpers import BranchTracker, does_branch_exist, get_branch_tracker, git, is_branch_upstream_deleted
from subcommands.base_command import BaseCommand
from subcommands.git_remove_leaf_child import remove_branch
from type_utils import MYPY

if MYPY:
    from typing import Text


class CleanBranches(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return "clean-branches"

    def get_short_description(self):
        # type: () -> Text
        return "deletes branches that are no longer known to git"

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument("-n", "--dry-run", action="store_true", help="only print what would be done")
        parser.add_argument(
            "-a", "--archive", action="store_true", help="set to archive instead of delete invalid branches"
        )
        parser.add_argument(
            "-u",
            "--upstream",
            action="store_true",
            help="set to `git fetch` and treat branches with set-but-deleted upstreams as invalid",
        )
        parser.add_argument(
            "--no-upstream",
            action="store_false",
            dest='upstream',
            help="turn off the -u/--upstream flag",
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        clean_invalid_branches(args.dry_run, args.archive, args.upstream)


def clean_invalid_branches(dry_run, archive, upstream):
    # type: (bool, bool, bool) -> None
    if upstream:
        # Make sure we have latest remote info
        git("fetch")

    with get_branch_tracker() as tracker:
        for branch in tracker.linearized_branches():
            if _is_branch_invalid(tracker, branch, upstream):
                if archive:
                    _archive_invalid_branch(dry_run, tracker, branch)
                else:
                    _delete_invalid_branch_if_possible(dry_run, tracker, branch, upstream)


def _is_branch_invalid(tracker, branch_name, upstream):
    # type: (BranchTracker, Text, bool) -> bool
    if upstream:
        return is_branch_upstream_deleted(branch_name)

    return not does_branch_exist(branch_name) and not tracker.is_archived(branch_name)


def _archive_invalid_branch(dry_run, tracker, branch_name):
    # type: (bool, BranchTracker, Text) -> None
    print("Archiving invalid branch '{}'".format(branch_name))
    if not dry_run:
        tracker.set_is_archived(branch_name, True)


def _delete_invalid_branch_if_possible(dry_run, tracker, branch_name, upstream):
    # type: (bool, BranchTracker, Text, bool) -> None
    children = tracker.children_for_parent(branch_name)
    if tracker.children_for_parent(branch_name):
        error_message = (
            "Cannot delete invalid branch '{}' because it has children ({})."
            " Change each child's parent to a different branch first."
        )
        print(error_message.format(branch_name, ", ".join("'{}'".format(child for child in children))))
    else:
        print("Deleting invalid branch '{}'".format(branch_name))
        if not dry_run:
            if upstream:
                remove_branch(tracker, branch_name, force_remove=True)
            else:
                tracker.remove_child_leaf(branch_name)
