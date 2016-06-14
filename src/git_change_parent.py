import argparse
from git_helpers import get_current_branch, get_branch_tracker


def main(new_parent):
    # type: (str) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        tracker.set_parent(current_branch, new_parent)
    print "You may want to rebase on top of the new parent to make sure its changes are visible in this branch."


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("new_parent")
    args = parser.parse_args()
    main(args.new_parent)
