from argparse import ArgumentParser, Namespace

from git_helpers import BranchTracker, get_branch_tracker, get_current_branch, git, hash_for
from subcommands.base_command import BaseCommand


class GitRemoveLeafBranch(BaseCommand):
    def get_name(self) -> str:
        return "remove-branch"

    def get_short_description(self) -> str:
        return "deletes the current branch, if it is merged into its parent"

    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="forces the current branch to be removed even if it has not been merged into its parent",
        )
        parser.add_argument(
            "branch_name", nargs="?", help="the branch to remove; if not provided removes the current branch"
        )

    def run_command(self, args: Namespace) -> None:
        with get_branch_tracker() as tracker:
            remove_branch(tracker, branch_name=args.branch_name or get_current_branch(), force_remove=args.force)


def remove_branch(tracker: BranchTracker, branch_name: str, force_remove: bool) -> None:
    branch_commit = hash_for(branch_name)
    parent = tracker.parent_for_child(branch_name)
    children = tracker.children_for_parent(branch_name)
    assert not children, "Child branch should not have any children, found {} child(ren)".format(len(children))

    merged_into_parent = [line[2:] for line in git("branch --merged {}".format(parent)).split("\n") if line]
    if branch_name in merged_into_parent:
        print("Removing merged branch {!r} (was at commit {})".format(branch_name, branch_commit))
    elif force_remove:
        print("Force removing unmerged branch {!r} (was at commit {})".format(branch_name, branch_commit))
    else:
        print("")
        print("!!!!!!!!")
        print("!!! Trying to remove branch {!r} not merged into its parent. Re-run with".format(branch_name))
        print("!!! '--force' if you want to force the deletion of this branch.")
        print("!!!")
        print("!!! WARNING: Running with '--force' may cause data loss")
        print("!!!!!!!!")
        print("")
        exit(1)

    if branch_name == get_current_branch():
        git("checkout {}".format(parent))
    # This will fail if we're not forcing the remove and the branch isn't merged in.
    delete_flag = "-D" if force_remove else "-d"
    git("branch {} {}".format(delete_flag, branch_name))

    tracker.remove_child_leaf(branch_name)
