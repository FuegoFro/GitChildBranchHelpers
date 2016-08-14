import argparse

from git_helpers import get_current_branch, get_branch_tracker
from typing import Optional


def set_archived(archived, branch_name=None):
    # type: (bool, Optional[str]) -> None
    if branch_name is None:
        branch_name = get_current_branch()
    with get_branch_tracker() as tracker:
        tracker.set_is_archived(branch_name, archived)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--unarchive", action="store_true",
                        help="If set, un-archive the given branch, rather than archiving it.")
    parser.add_argument("branch_to_set_archive_property", nargs="?")
    args = parser.parse_args()
    set_archived(not args.unarchive, args.branch_to_set_archive_property)
