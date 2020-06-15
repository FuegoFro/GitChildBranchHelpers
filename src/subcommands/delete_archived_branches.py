from __future__ import print_function, unicode_literals

import os
import sys
from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch, git, does_branch_exist, hash_for
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

class DeleteArchivedBranches(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return 'delete-archived'

    def get_short_description(self):
        # type: () -> Text
        return 'deletes all archived branches'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        pass

    def run_command(self, args):
        # type: (Namespace) -> None
        delete_archived_branches()


def delete_archived_branches():
    # type: () -> None
    with get_branch_tracker() as tracker:
        for branch in tracker.list_of_branches():
            if tracker.is_branch_tracked(branch) and tracker.is_archived(branch):
                if tracker.children_for_parent(branch):
                    print("Skipping deletion of archived branch {} because it has children".format(branch))
                else:
                    print("Deleting {}".format(branch))
                    tracker.remove_child_leaf(branch)
