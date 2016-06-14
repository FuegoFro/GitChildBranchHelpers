import argparse
from git_helpers import get_current_branch, get_branch_tracker, git


def main(force_remove):
    # type: (bool) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        children = tracker.children_for_parent(current_branch)
        assert not children, "Child branch should not have any children, found %s child(ren)" % len(children)

        git("checkout %s" % parent)
        # This will fail if we're not forcing the remove and the branch isn't merged in.
        delete_flag = "-D" if force_remove else "-d"
        git("branch %s %s" % (delete_flag, current_branch))

        tracker.remove_child_leaf(current_branch)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true")
    args = parser.parse_args()
    main(args.force)
