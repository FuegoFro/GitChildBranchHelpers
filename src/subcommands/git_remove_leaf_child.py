from __future__ import print_function

from argparse import ArgumentParser, Namespace

from git_helpers import get_branch_tracker, get_current_branch, git, hash_for
from subcommands.base_command import BaseCommand

if False:
    from typing import Text


class GitRemoveLeafBranch(BaseCommand):
    def get_name(self):
        # type: () -> Text
        return 'remove-branch'

    def get_short_description(self):
        # type: () -> Text
        return 'deletes the current branch, if it is merged into its parent'

    def inflate_subcommand_parser(self, parser):
        # type: (ArgumentParser) -> None
        parser.add_argument(
            "-f", "--force",
            action="store_true",
            help='forces the current branch to be removed even if it has not been merged into its '
                 'parent',
        )

    def run_command(self, args):
        # type: (Namespace) -> None
        remove_branch(args.force)


def remove_branch(force_remove):
    # type: (bool) -> None
    current_branch = get_current_branch()
    current_commit = hash_for(current_branch)
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        children = tracker.children_for_parent(current_branch)
        assert not children, \
            "Child branch should not have any children, found {} child(ren)".format(len(children))

        merged_into_parent = [
            line[2:] for line in git("branch --merged {}".format(parent)).split('\n') if line
        ]
        if current_branch in merged_into_parent:
            print("Removing merged branch {!r} (was at commit {})".format(
                current_branch, current_commit))
        elif force_remove:
            print("Force removing unmerged branch {!r} (was at commit {})".format(
                current_branch, current_commit, ))
        else:
            print("")
            print("!!!!!!!!")
            print("!!! Trying to remove branch {!r} not merged into its parent. Re-run with" \
                  "".format(current_branch))
            print("!!! '--force' if you want to force the deletion of this branch.")
            print("!!!")
            print("!!! WARNING: Running with '--force' may cause data loss")
            print("!!!!!!!!")
            print("")
            exit(1)

        git("checkout {}".format(parent))
        # This will fail if we're not forcing the remove and the branch isn't merged in.
        delete_flag = "-D" if force_remove else "-d"
        git("branch {} {}".format(delete_flag, current_branch))

        tracker.remove_child_leaf(current_branch)
