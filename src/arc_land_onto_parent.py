import sys

from git_helpers import arc, fail_if_not_rebased, get_branch_tracker, get_current_branch

try:
    # noinspection PyUnresolvedReferences
    from typing import List
except ImportError:
    pass


def main(extra_arc_land_options):
    # type: (List[str]) -> None
    if extra_arc_land_options:
        extra_args = " " + " ".join(extra_arc_land_options)
    else:
        extra_args = ""

    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        fail_if_not_rebased(current_branch, parent, tracker)

        if parent != "master":
            should_land = raw_input("Are you sure you want to land onto non-master branch "
                                    "'%s'? [y/N] " % parent)
            should_land = should_land.lower()
            if should_land not in ("y", "yes"):
                print "Aborting land"
                exit()

        arc("land --onto %s%s" % (parent, extra_args))

        # Successfully landed, replace ourselves with our parent
        tracker.collapse_and_remove_parent(current_branch)

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
