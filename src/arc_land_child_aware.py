import argparse
from git_helpers import get_current_branch, get_branch_mappings, arc, base_branch_name, git


def main():
    current_branch = get_current_branch()
    parent_to_children, child_to_parent = get_branch_mappings()

    parent = child_to_parent.get(current_branch)
    if parent is not None:
        should_land = raw_input("Are you sure you want to land onto non-master branch '%s'? [y/N] " % parent)
        should_land = should_land.lower()
        if should_land not in ("y", "yes"):
            print "Aborting land"
            exit()

        arc("land --onto %s" % parent)
    else:
        # No parent, land onto master
        arc("land")

    # Successfully landed, remove our base branch if we had one.
    if parent is not None:
        base_branch = base_branch_name(parent, current_branch)
        git("branch -D %s" % base_branch)

    # Rename/remove our children's base branches as necessary.
    for child in parent_to_children[current_branch]:
        old_base_branch = base_branch_name(current_branch, child)
        git("branch -D %s" % old_base_branch)
        if parent is not None:
            new_base_branch = base_branch_name(parent, child)
            git("branch %s %s" % (new_base_branch, parent))
        # No need for an else case. Our parent was master (no base branch),
        # so our children will now be off of master (we already deleted the
        # base branch).

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
