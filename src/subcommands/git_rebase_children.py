from __future__ import unicode_literals

import argparse
import subprocess
from argparse import ArgumentParser, Namespace

from git_helpers import (
    BranchTracker,
    get_branch_tracker,
    get_current_branch,
    git,
    hash_for,
    run_command_expecting_failure,
)
from subcommands.base_command import BaseCommand
from type_utils import MYPY

if MYPY:
    from typing import Sequence, Text


class GitRebaseOntoParent(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return "rebase"

    def get_short_description(self):
        # type: () -> Text
        return "rebase the current branch onto its parent"

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="if set, will recursively rebase all sub-branches onto their parents",
        )
        parser.add_argument(
            "-b",
            "--branch",
            help=(
                "the branch to rebase; if not provided removes the current branch"
            ),
        )
        parser.add_argument(
            "git_rebase_args",
            nargs=argparse.REMAINDER,
            help=(
                "arguments to pass through to `git rebase`. You may need to add '--' before "
                "them if the the first arg to pass through starts with '-'."
            ),
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        rebase_children(args.recursive, args.branch, args.git_rebase_args)


def do_rebase(tracker, parent, child, extra_args):
    # type: (BranchTracker, Text, Text, Text) -> None
    base = tracker.base_for_branch(child)
    parent_rev = hash_for(parent)
    if base == parent_rev:
        return

    tracker.start_rebase(child, parent_rev)
    # Can't use the `git` function since we don't want to capture/return output text.
    command = "rebase --onto {} {} {}{}".format(parent, base, child, extra_args)
    run_command_expecting_failure(subprocess.check_call, "git", command)
    tracker.finish_rebase(child, parent_rev)


def rebase_children(is_recursive, branch, extra_git_rebase_args=()):
    # type: (bool, Optional[Text], Sequence[Text]) -> None
    if branch is None:
        branch = get_current_branch()
    if extra_git_rebase_args:
        # If the first extra arg starts with "-", "--" must also have been passed, and
        # argparse doesn't remove it for us
        if extra_git_rebase_args[0] == "--":
            extra_git_rebase_args = extra_git_rebase_args[1:]
        extra_args = " " + " ".join(extra_git_rebase_args)
    else:
        extra_args = ""

    with get_branch_tracker() as tracker:
        do_rebase(tracker, tracker.parent_for_child(branch), branch, extra_args)

        if is_recursive:
            to_rebase_onto = [branch]
            while to_rebase_onto:
                parent = to_rebase_onto.pop()
                children = tracker.children_for_parent(parent)
                for child in children:
                    do_rebase(tracker, parent, child, extra_args)
                    to_rebase_onto.append(child)

        # Go back to where we started.
        git("checkout {}".format(branch))
