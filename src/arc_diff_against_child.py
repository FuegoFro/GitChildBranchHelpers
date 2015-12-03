import sys

from git_helpers import get_current_branch, arc
from git_rebase_children import get_branch_tracker


def main(extra_arc_diff_options):
    if extra_arc_diff_options:
        extra_args = " " + " ".join(extra_arc_diff_options)
    else:
        extra_args = ""

    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        arc("diff %s%s" % (parent, extra_args))

if __name__ == '__main__':
    extra_arc_diff_options = sys.argv[1:]
    main(extra_arc_diff_options)
