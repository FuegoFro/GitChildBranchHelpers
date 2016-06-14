import argparse
from git_helpers import get_current_branch, get_branch_tracker, git


def main(new_branch_name):
    # type: (str) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        git("checkout -b %s" % new_branch_name)
        git("branch -d %s" % current_branch)
        tracker.rename_branch(current_branch, new_branch_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("new_branch_name")
    args = parser.parse_args()
    main(args.new_branch_name)
