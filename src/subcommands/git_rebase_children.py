from argparse import ArgumentParser, Namespace

from git_helpers import (
    BranchTracker,
    does_branch_contain_commit,
    get_branch_tracker,
    get_current_branch,
    git,
    hash_for,
)
from subcommands.base_command import BaseCommand

if False:
    from typing import Text


class GitRebaseOntoParent(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return 'rebase'

    def get_short_description(self):
        # type: () -> Text
        return 'rebase the current branch onto its parent'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument(
            "-r", "--recursive",
            action="store_true",
            help="if set, will recursively rebase all sub-branches onto their parents",
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        rebase_children(args.recursive)


def do_rebase(tracker, parent, child):
    # type: (BranchTracker, Text, Text) -> None
    base = tracker.base_for_branch(child)
    parent_rev = hash_for(parent)
    if base == parent_rev:
        return

    tracker.start_rebase(child, parent_rev)
    git("rebase --onto {} {} {}".format(parent, base, child))
    tracker.finish_rebase(child, parent_rev)


def rebase_children(is_recursive):
    # type: (bool) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        do_rebase(tracker, tracker.parent_for_child(current_branch), current_branch)

        if is_recursive:
            to_rebase_onto = [current_branch]
            while to_rebase_onto:
                parent = to_rebase_onto.pop()
                children = tracker.children_for_parent(parent)
                for child in children:
                    do_rebase(tracker, parent, child)
                    to_rebase_onto.append(child)

        # Go back to where we started.
        git("checkout {}".format(current_branch))
