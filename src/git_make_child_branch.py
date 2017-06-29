import argparse

from git_helpers import get_current_branch, git, get_branch_tracker, hash_for

try:
    # noinspection PyUnresolvedReferences
    from typing import Optional
except ImportError:
    pass


def make_child_branch(new_branch_name, revision=None):
    # type: (str, Optional[str]) -> None
    parent = get_current_branch()
    if revision is None:
        # Use the current revision as the base
        base_rev = hash_for("HEAD")
    else:
        # Use the merge-base of the given revision and the parent branch as the base
        base_rev = git("merge-base %s %s" % (parent, revision)).strip()

    with get_branch_tracker() as tracker:
        # Add the child using the current branch as the parent.
        tracker.add_child_for_parent(parent, new_branch_name, base_rev)
        # Make the new branch, either where the current branch is or at the specified revision
        if revision is None:
            command = "checkout -b %s" % new_branch_name
        else:
            command = "checkout -b %s %s" % (new_branch_name, revision)
        git(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("new_branch_name")
    parser.add_argument("--revision", "-r", required=False)
    args = parser.parse_args()
    make_child_branch(args.new_branch_name, args.revision)
