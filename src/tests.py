# coding=utf-8
from __future__ import print_function, unicode_literals

import argparse
import contextlib
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from git_helpers import get_branch_tracker, get_current_branch, git, hash_for
from subcommands.base_command import BaseCommand
from subcommands.clean_branches import clean_invalid_branches
from subcommands.delete_archived_branches import delete_archived_branches
from subcommands.git_make_child_branch import make_child_branch
from subcommands.git_rebase_children import rebase_children
from subcommands.git_remove_leaf_child import GitRemoveLeafBranch
from subcommands.git_rename_branch import rename_current_branch
from subcommands.print_branch_info import get_branch_info
from subcommands.print_child_branch_structure import get_branch_structure_string, make_green
from subcommands.set_branch_archived import set_archived
from type_utils import MYPY

if MYPY:
    from typing import Callable, Iterator, Optional, Sequence, Text, Type

SRC_DIR = os.path.realpath(os.path.dirname(__file__))

UNARCHIVED_PRINT_STRUCTURE = """
master
│
└── first_branch
    │
    ├── second_branch
    │   │
    │   └── third_branch
    │
    └── sibling_branch
""".strip()

ARCHIVED_PRINT_STRUCTURE = """
master
│
└── first_branch
    │
    └── sibling_branch
(not displaying archived branches, run with --all to see them)
""".strip()


@contextlib.contextmanager
def _run_test(path):
    # type: (Text) -> Iterator[None]
    path = os.path.expanduser(path)
    target_container = os.path.dirname(path)
    assert not os.path.exists(path)
    assert os.path.isdir(target_container)

    os.mkdir(path)
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)
        shutil.rmtree(path)


def _assert_fails(function):
    # type: (Callable[[], None]) -> None
    succeeded = False
    try:
        function()
        succeeded = True
    except SystemExit:
        pass
    assert not succeeded


def _mypy_check():
    # type: () -> None
    python_files = glob.glob(os.path.join(SRC_DIR, "*.py"))
    retcode = subprocess.call([sys.executable, "-m", "mypy", "--strict"] + python_files)
    if retcode != 0:
        print("\nMypy failed!!!\n")
        exit(1)


def _initialize_repo():
    # type: () -> None
    """
        Initialize a repo and add a first commit so we can tell what branch we're on.
    """
    print("Initializing repo")
    git("init")
    open("hello.txt", "w").close()
    git("add .")
    git("commit -am initial_commit")

    assert get_current_branch() == "master"


def _command_with_args(command_class, command_args=()):
    # type: (Type[BaseCommand], Sequence[Text]) -> None
    command = command_class()
    command_parser = argparse.ArgumentParser()
    command.inflate_subcommand_parser(command_parser)
    parsed_args = command_parser.parse_args(command_args)
    print(command_parser)
    print(parsed_args)
    command.run_command(parsed_args)


def _integration_test(target_directory):
    # type: (Text) -> None
    with _run_test(target_directory):
        _initialize_repo()
        original_commit = hash_for("HEAD")

        # Create all the branches
        make_child_branch("first_branch")
        assert get_current_branch() == "first_branch"

        make_child_branch("second_branch")
        assert get_current_branch() == "second_branch"

        make_child_branch("third_branch")
        assert get_current_branch() == "third_branch"

        # Rename a branch
        rename_current_branch("third_branch_renamed", force=False)
        assert get_current_branch() == "third_branch_renamed"

        # Rename it back
        rename_current_branch("third_branch", force=False)
        assert get_current_branch() == "third_branch"

        # This should be sibling to second_branch, on top of first_branch
        git("checkout first_branch")
        make_child_branch("sibling_branch")
        assert get_current_branch() == "sibling_branch"

        # Make the first "real" commit, in master
        print("First commit")
        git("checkout master")
        with open(os.path.join(target_directory, "hello.txt"), "wb") as f:
            f.write(b"Hello!")
        # Avoiding spaces because of how we break up args in the `git` function
        git("commit -am first_commit_message")
        first_commit = hash_for("HEAD")
        assert original_commit != first_commit

        # Do the recursive rebase
        print("Rebase first_branch and its children on top of master.")
        git("checkout first_branch")
        rebase_children(True)
        assert first_commit == hash_for("first_branch")
        assert first_commit == hash_for("second_branch")
        assert first_commit == hash_for("third_branch")
        assert first_commit == hash_for("sibling_branch")

        # Make a second commit, this time in first_branch
        print("Make a second commit in first_branch")
        git("checkout first_branch")
        with open(os.path.join(target_directory, "hello.txt"), "wb") as f:
            f.write(b"Hello there!")
        git("commit -am second_commit_message")
        second_commit = hash_for("HEAD")
        assert original_commit != second_commit and first_commit != second_commit

        # Rebase just second_branch. This should update third_branch but shouldn't touch
        # sibling_branch.
        print("Doing second rebase")
        git("checkout second_branch")
        rebase_children(True)
        assert second_commit == hash_for("first_branch")
        assert second_commit == hash_for("second_branch")
        assert second_commit == hash_for("third_branch")
        assert first_commit == hash_for("sibling_branch")

        print("Make a merge conflict in sibling_branch")
        # Add a new commit to the sibling branch, delete the branch, and re-create it at the
        # revision it was at.
        git("checkout sibling_branch")
        # Make a conflicting change on sibling so that we can test rebasing it later.
        with open(os.path.join(target_directory, "hello.txt"), "wb") as f:
            f.write(b"Hello conflict")
        git("commit -am conflicting_change_message")
        sibling_conflicting_commit = hash_for("HEAD")

        print("Test deleting branch")
        # See that removing fails since it's not merged
        _assert_fails(lambda: _command_with_args(GitRemoveLeafBranch, []))
        assert get_current_branch() == "sibling_branch"
        assert sibling_conflicting_commit == hash_for("HEAD")
        _command_with_args(GitRemoveLeafBranch, ["--force"])
        assert get_current_branch() == "first_branch"
        assert second_commit == hash_for("HEAD")

        print("Test creating branch at specific revision")
        make_child_branch("sibling_branch", sibling_conflicting_commit)
        assert get_current_branch() == "sibling_branch"
        assert sibling_conflicting_commit == hash_for("HEAD")

        # This should throw since the rebase has conflicts
        print("Testing merge conflicts")
        _assert_fails(lambda: rebase_children(True))

        # Abort the rebase and try again
        git("rebase --abort")
        # It should fail for the same reason
        print("Testing merge conflicts again")
        _assert_fails(lambda: rebase_children(True))

        print("Resolving the merge conflict")
        with open(os.path.join(target_directory, "hello.txt"), "wb") as f:
            f.write(b"Hello merge")
        git("add hello.txt")
        git("rebase --continue")

        # This should effectively no-op
        print("Doing no-op rebase")
        current_commit = hash_for("HEAD")
        rebase_children(True)
        assert current_commit == hash_for("HEAD")

        unarchived_print_structure_sibling_branch = UNARCHIVED_PRINT_STRUCTURE.replace(
            "sibling_branch", make_green("sibling_branch")
        )
        archived_print_structure_sibling_branch = ARCHIVED_PRINT_STRUCTURE.replace(
            "sibling_branch", make_green("sibling_branch")
        )
        assert get_branch_structure_string(False) == unarchived_print_structure_sibling_branch

        set_archived(True, "second_branch")
        assert get_branch_structure_string(False) == archived_print_structure_sibling_branch
        assert get_branch_structure_string(True) == unarchived_print_structure_sibling_branch

        git("checkout second_branch")
        set_archived(False)
        assert get_branch_structure_string(False) == UNARCHIVED_PRINT_STRUCTURE.replace(
            "second_branch", make_green("second_branch")
        )

        current_commit = hash_for("HEAD")
        assert get_branch_info(
            branch=None, use_null_delimiter=False
        ) == "Parent branch: first_branch; Base revision: {}".format(current_commit)
        assert get_branch_info(branch=None, use_null_delimiter=True) == "first_branch\0{}".format(current_commit)
        try:
            get_branch_info(branch="master", use_null_delimiter=False)
            assert False, "Should not get here"
        except SystemExit as e:
            assert str(e) == "Branch does not have a parent: master"


def _test_clean_branches(target_directory):
    # type: (Text) -> None
    with _run_test(target_directory):
        _initialize_repo()

        # Create all the branches
        make_child_branch("valid_branch")
        assert get_current_branch() == "valid_branch"

        git("checkout master")

        make_child_branch("ghost_branch_childless")
        assert get_current_branch() == "ghost_branch_childless"

        git("checkout master")

        make_child_branch("ghost_branch_with_children")
        assert get_current_branch() == "ghost_branch_with_children"

        make_child_branch("child_of_ghost_branch")
        assert get_current_branch() == "child_of_ghost_branch"

        git("checkout master")

        print("Deleting branches from git")
        git("branch -D ghost_branch_childless")
        git("branch -D ghost_branch_with_children")

        print("Test cleaning by archiving")
        clean_invalid_branches(dry_run=False, archive=True, upstream=False)

        with get_branch_tracker() as tracker:
            assert not tracker.is_archived("valid_branch")
            assert tracker.is_archived("ghost_branch_childless")
            assert tracker.is_archived("ghost_branch_with_children")

            print("Clear archived flags for next test")
            tracker.set_is_archived("ghost_branch_childless", False)
            tracker.set_is_archived("ghost_branch_with_children", False)

        print("Test cleaning by deleting")
        clean_invalid_branches(dry_run=False, archive=False, upstream=False)

        with get_branch_tracker() as tracker:
            assert tracker.is_branch_tracked("valid_branch")
            assert not tracker.is_branch_tracked("ghost_branch_childless")
            assert tracker.is_branch_tracked("ghost_branch_with_children")


def _test_delete_archived_branches(target_directory):
    # type: (Text) -> None
    with _run_test(target_directory):
        _initialize_repo()

        # Create all the branches
        make_child_branch("first_branch")
        assert get_current_branch() == "first_branch"

        git("checkout master")

        make_child_branch("second_branch")
        assert get_current_branch() == "second_branch"

        make_child_branch("second_branch_child_one")
        assert get_current_branch() == "second_branch_child_one"

        make_child_branch("second_branch_child_two")
        assert get_current_branch() == "second_branch_child_two"

        git("checkout master")

        with get_branch_tracker() as tracker:
            tracker.set_is_archived("first_branch", True)
            tracker.set_is_archived("second_branch_child_two", True)

        # Test
        delete_archived_branches()

        with get_branch_tracker() as tracker:
            assert not tracker.is_branch_tracked("first_branch")
            assert tracker.is_branch_tracked("second_branch")
            assert tracker.is_branch_tracked("second_branch_child_one")
            assert not tracker.is_branch_tracked("second_branch_child_two")


def run_tests(target_directory):
    # type: (Optional[Text]) -> None
    _mypy_check()
    if target_directory is None:
        target_directory = tempfile.mkdtemp()
        assert target_directory is not None
        os.rmdir(target_directory)
    _integration_test(target_directory)
    _test_clean_branches(target_directory)
    _test_delete_archived_branches(target_directory)
    print("")
    print("Tests finished successfully!")


def main():
    # type: () -> None
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_target_dir", default=None)
    args = parser.parse_args()
    run_tests(args.test_target_dir)


if __name__ == "__main__":
    main()
