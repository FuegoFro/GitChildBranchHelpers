import argparse

from git_helpers import git, get_current_branch, base_branch_name, get_branch_mappings


def do_rebase(parent, child):
    if parent is None:
        base_branch = None
        parent = "master"
        rebase_start = "master"
    else:
        base_branch = base_branch_name(parent, child)
        rebase_start = base_branch

    git("rebase --onto %s %s %s" % (parent, rebase_start, child))
    # Move our base branch to be where the parent is now
    if base_branch is not None:
        git("branch -D %s" % base_branch)
        git("branch %s %s" % (base_branch, parent))


def rebase_children():
    current_branch = get_current_branch()
    parent_to_children, child_to_parent = get_branch_mappings()

    do_rebase(child_to_parent.get(current_branch), current_branch)

    to_rebase_onto = [current_branch]
    while to_rebase_onto:
        parent = to_rebase_onto.pop()
        children = parent_to_children[parent]
        for child in children:
            do_rebase(parent, child)
            to_rebase_onto.append(child)

    # Go back to where we started.
    git("checkout %s" % current_branch)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    rebase_children()
