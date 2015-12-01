import argparse

from git_helpers import get_current_branch, git, base_branch_name


def make_child_branch(new_branch_name):
    current_branch = get_current_branch()

    # Make the base branch where the current branch is.
    # If we're on master, no need for a base branch.
    if current_branch != "master":
        base_branch = base_branch_name(current_branch, new_branch_name)
        git("branch %s %s" % (base_branch, current_branch))

    # Make the new branch, also where the current branch is
    git("checkout -b %s" % new_branch_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("new_branch_name")
    args = parser.parse_args()
    make_child_branch(args.new_branch_name)
