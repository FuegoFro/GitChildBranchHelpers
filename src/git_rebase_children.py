import argparse

from git_helpers import git, get_current_branch, get_branch_tracker, hash_for, does_branch_contain_commit, BranchTracker


def do_rebase(tracker, parent, child):
    # type: (BranchTracker, str, str) -> None
    bases = tracker.bases_for_branch(child)

    if len(bases) == 2:
        first_base, second_base = bases
        has_first_base = does_branch_contain_commit(child, first_base)
        has_second_base = does_branch_contain_commit(child, second_base)
        # Should have at least one of the two bases
        assert has_first_base or has_second_base
        if has_first_base and has_second_base:
            # Choose the newer one. The older one will be the merge base of the two
            older_base = git("merge-base %s %s" % (first_base, second_base))
            first_is_newer = older_base == second_base
            base = first_base if first_is_newer else second_base
        else:
            # Only has one, choose the one that it does have
            base = bases[0] if has_first_base else bases[1]
        tracker.finish_rebase(child, base)
    else:
        base = bases[0]

    parent_rev = hash_for(parent)

    tracker.start_rebase(child, parent_rev)
    git("rebase --onto %s %s %s" % (parent, base, child))
    tracker.finish_rebase(child, parent_rev)


def rebase_children(is_recursive):
    # type: (bool) -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        do_rebase(tracker, tracker.parent_for_child(current_branch), current_branch)

        if is_recursive:
            to_rebase_onto = [current_branch]
            while to_rebase_onto:
                parent = to_rebase_onto.pop()
                children = tracker.children_for_parent(parent)
                for child in children:
                    do_rebase(tracker, parent, child)
                    to_rebase_onto.append(child)

        # Go back to where we started.
        git("checkout %s" % current_branch)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="If set, will recursively rebase all sub-branches")
    args = parser.parse_args()
    rebase_children(args.recursive)
