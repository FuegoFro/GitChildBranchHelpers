import argparse
from git_helpers import get_current_branch, arc
from git_rebase_children import get_branch_mappings


def main():
    current_branch = get_current_branch()
    parent_to_children, child_to_parent = get_branch_mappings()
    if current_branch in child_to_parent:
        arc("diff %s" % child_to_parent[current_branch])
    else:
        # No parent, diff against master
        arc("diff")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main()
