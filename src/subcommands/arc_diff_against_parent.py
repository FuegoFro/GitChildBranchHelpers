import argparse
from argparse import ArgumentParser, Namespace

from git_helpers import arc, fail_if_not_rebased, get_current_branch
from subcommands.git_rebase_children import get_branch_tracker
from subcommands.base_command import BaseCommand


class ArcDiffAgainstParent(BaseCommand):
    def get_name(self):
        # type: () -> str
        return 'arc-diff'

    def get_short_description(self):
        # type: () -> str
        return '`arc diff` this branch against its parent branch'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument(
            'arc_diff_args',
            nargs=argparse.REMAINDER,
            help="arguments to pass through to `arc diff`. You may need to add '--' before "
                 "them if the the first arg to pass through starts with '-'.",
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        extra_arc_diff_options = args.arc_diff_args
        if extra_arc_diff_options:
            # If the first extra arg starts with "-", "--" must also have been passed, and
            # argparse doesn't remove it for us
            if "--" in extra_arc_diff_options:
                extra_arc_diff_options.remove("--")
            extra_args = " " + " ".join(extra_arc_diff_options)
        else:
            extra_args = ""

        current_branch = get_current_branch()
        with get_branch_tracker() as tracker:
            parent = tracker.parent_for_child(current_branch)
            fail_if_not_rebased(current_branch, parent, tracker)
            arc("diff {}{}".format(parent, extra_args))
