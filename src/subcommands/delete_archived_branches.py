# coding=utf-8
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
        roots = []
        for parent in tracker.get_all_parents():
            if not tracker.has_parent(parent):
                roots.append(parent)

        roots = sorted(roots)

        for root in roots:
            delete_archived_branches_internal(tracker, root)

def delete_archived_branches_internal(tracker, branch_name):
    # type: (BranchTracker, Text) -> None
    for child in tracker.children_for_parent(branch_name):
        delete_archived_branches_internal(tracker, child)
    
    if tracker.is_branch_tracked(branch_name) and tracker.is_archived(branch_name):
        if tracker.children_for_parent(branch_name):
            print("Skipping deletion of archived branch {} because it has children".format(branch_name))
        else:
            print("Deleting {}".format(branch_name))
            tracker.remove_child_leaf(branch_name)
