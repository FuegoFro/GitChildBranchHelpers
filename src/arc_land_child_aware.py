import argparse
from git_helpers import get_current_branch, get_branch_tracker, arc


def main():
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        if parent != "master":
            should_land = raw_input("Are you sure you want to land onto non-master branch '%s'? [y/N] " % parent)
            should_land = should_land.lower()
            if should_land not in ("y", "yes"):
                print "Aborting land"
                exit()

        arc("land --onto %s" % parent)

        # Successfully landed, replace ourselves with our parent
        tracker.collapse_and_remove_parent(current_branch)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
