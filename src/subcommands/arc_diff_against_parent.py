from __future__ import unicode_literals

import argparse
from argparse import ArgumentParser, Namespace

from git_helpers import arc, get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand
from typing import Text


class ArcDiffAgainstParent(BaseCommand):
    def get_name(self) -> Text:
        return "arc-diff"

    def get_short_description(self) -> Text:
        return "`arc diff` this branch against its parent branch"

    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "arc_diff_args",
            nargs=argparse.REMAINDER,
            help=(
                "arguments to pass through to `arc diff`. You may need to add '--' before "
                "them if the the first arg to pass through starts with '-'."
            ),
        )

    def run_command(self, args: Namespace) -> None:
        extra_arc_diff_options = args.arc_diff_args
        if extra_arc_diff_options:
            # If the first extra arg starts with "-", "--" must also have been passed, and
            # argparse doesn't remove it for us
            if extra_arc_diff_options[0] == "--":
                del extra_arc_diff_options[0]
            extra_args = " " + " ".join(extra_arc_diff_options)
        else:
            extra_args = ""

        current_branch = get_current_branch()
        with get_branch_tracker() as tracker:
            base = tracker.base_for_branch(current_branch)
            arc("diff {}{}".format(base, extra_args))
