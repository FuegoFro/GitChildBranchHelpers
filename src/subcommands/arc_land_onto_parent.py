import argparse
from argparse import ArgumentParser, Namespace

from git_helpers import arc, fail_if_not_rebased, get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand


class ArcLandOntoParent(BaseCommand):
    def get_name(self):
        # type: () -> str
        return 'arc-land'

    def get_short_description(self):
        # type: () -> str
        return '`arc land` this branch onto its parent branch'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument(
            'arc_land_args',
            nargs=argparse.REMAINDER,
            help="arguments to pass through to `arc land`. You may need to add '--' before "
                 "them if the the first arg to pass through starts with '-'.",
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        extra_arc_land_options = args.arc_land_args
        if extra_arc_land_options:
            # If the first extra arg starts with "-", "--" must also have been passed, and
            # argparse doesn't remove it for us
            if extra_arc_land_options[0] == "--":
                del extra_arc_land_options[0]
            extra_args = " " + " ".join(extra_arc_land_options)
        else:
            extra_args = ""

        current_branch = get_current_branch()
        with get_branch_tracker() as tracker:
            parent = tracker.parent_for_child(current_branch)
            fail_if_not_rebased(current_branch, parent, tracker)

            if parent != "master":
                should_land = raw_input("Are you sure you want to land onto non-master branch "
                                        "'{}'? [y/N] ".format(parent))
                should_land = should_land.lower()
                if should_land not in ("y", "yes"):
                    print "Aborting land"
                    exit()

            arc("land --onto {}{}".format(parent, extra_args))

            # Successfully landed, replace ourselves with our parent
            tracker.collapse_and_remove_parent(current_branch)
