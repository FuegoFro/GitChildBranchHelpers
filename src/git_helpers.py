from collections import defaultdict
import subprocess

BASE_BRANCH_SEPARATOR = "_BASE_"


def git(command):
    return subprocess.check_output(["git"] + command.split(" "))


def get_current_branch():
    return git("rev-parse --abbrev-ref HEAD").strip()


def get_branch_mappings():
    # Set to initial values
    parent_to_children = defaultdict(list)
    child_to_parent = {}

    # Extract the parent/child pairs from all branches
    branches = git("branch").split("\n")
    for branch in branches:
        branch = branch[2:].strip()
        if BASE_BRANCH_SEPARATOR not in branch:
            continue

        branch_split = branch.split(BASE_BRANCH_SEPARATOR)
        if len(branch_split) != 2:
            continue

        child, parent = branch_split
        parent_to_children[parent].append(child)
        assert child not in child_to_parent, "Child is %s, branch is %s, ctp is %s" % (child, branch, repr(child_to_parent))
        child_to_parent[child] = parent

    return parent_to_children, child_to_parent


def base_branch_name(parent, child):
    return child + BASE_BRANCH_SEPARATOR + parent


def arc(command):
        subprocess.check_call(["arc"] + command.split(" "))
