import argparse

from git_helpers import get_branch_tracker, get_current_branch, git, hash_for


def remove_branch(force_remove):
    # type: (bool) -> None
    current_branch = get_current_branch()
    current_commit = hash_for(current_branch)
    with get_branch_tracker() as tracker:
        parent = tracker.parent_for_child(current_branch)
        children = tracker.children_for_parent(current_branch)
        assert not children, \
            "Child branch should not have any children, found %s child(ren)" % len(children)

        merged_into_parent = [
            line[2:] for line in git("branch --merged %s" % parent).split('\n') if line
        ]
        if current_branch in merged_into_parent:
            print "Removing merged branch %r (was at commit %s)" % (current_branch, current_commit)
        elif force_remove:
            print "Force removing unmerged branch %r (was at commit %s)" % (
                current_branch,
                current_commit,
            )
        else:
            print ""
            print "!!!!!!!!"
            print "!!! Trying to remove branch %r not merged into its parent. Re-run with" \
                  "" % current_branch
            print "!!! '--force' if you want to force the deletion of this branch."
            print "!!!"
            print "!!! WARNING: Running with '--force' may cause data loss"
            print "!!!!!!!!"
            print ""
            exit(1)

        git("checkout %s" % parent)
        # This will fail if we're not forcing the remove and the branch isn't merged in.
        delete_flag = "-D" if force_remove else "-d"
        git("branch %s %s" % (delete_flag, current_branch))

        tracker.remove_child_leaf(current_branch)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true")
    args = parser.parse_args()
    remove_branch(args.force)
