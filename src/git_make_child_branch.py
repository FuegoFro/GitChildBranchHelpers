import argparse

from git_helpers import get_current_branch, git, get_branch_tracker, hash_for


def make_child_branch(new_branch_name):
    current_branch = get_current_branch()
    current_rev = hash_for(current_branch)
    with get_branch_tracker() as tracker:
        # Add the child using the current branch as the parent.
        tracker.add_child_for_parent(current_branch, new_branch_name, current_rev)
        # Make the new branch, also where the current branch is
        git("checkout -b %s" % new_branch_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("new_branch_name")
    args = parser.parse_args()
    make_child_branch(args.new_branch_name)
