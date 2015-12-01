import argparse
from git_helpers import get_current_branch, arc
from git_rebase_children import get_branch_tracker


def main():
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        arc("diff %s" % parent)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
