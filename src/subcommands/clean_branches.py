from __future__ import print_function, unicode_literals

import os
import sys
from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch, git, does_branch_exist, BranchTracker
from subcommands.base_command import BaseCommand

try:
    # noinspection PyUnresolvedReferences
    from typing import (
        Iterable,
        List,
        Tuple,
        TypeVar,
        Text,
    )

    T = TypeVar('T')
except ImportError:
    pass

from git_helpers import get_branch_tracker, get_current_branch, BranchTracker

class CleanBranches(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return 'clean-branches'

    def get_short_description(self):
        # type: () -> Text
        return 'deletes branches that are no longer known to git'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument("-a", "--archive", action="store_true",
                            help="set to archive instead of delete invalid branches")

    def run_command(self, args):
        # type: (Namespace) -> None
        clean_invalid_branches(args.archive)


def clean_invalid_branches(archive):
    # type: (bool) -> None
    with get_branch_tracker() as tracker:
        for branch in tracker.list_of_branches():
            if _is_branch_invalid(tracker, branch):
                if archive:
                    _archive_invalid_branch(tracker, branch)
                else:
                    _delete_invalid_branch_if_possible(tracker, branch)


def _is_branch_invalid(tracker, branch_name):
    # type: (BranchTracker, Text) -> bool
    return not does_branch_exist(branch_name) and not tracker.is_archived(branch_name)


def _archive_invalid_branch(tracker, branch_name):
    # type: (BranchTracker, Text) -> None
    print("Archiving invalid branch {}".format(branch_name))
    tracker.set_is_archived(branch_name, True)


def _delete_invalid_branch_if_possible(tracker, branch_name):
    # type: (BranchTracker, Text) -> None
    children = tracker.children_for_parent(branch_name)
    if tracker.children_for_parent(branch_name):
        error_message = "Cannot delete invalid branch {} because it has children ({}). Try rebasing its children on a valid branch first."
        print(error_message.format(branch_name, children))
    else:
        print("Deleting invalid branch {}".format(branch_name))
        tracker.remove_child_leaf(branch_name)
