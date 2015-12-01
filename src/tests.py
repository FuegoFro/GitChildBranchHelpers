import argparse
import contextlib
import os
import shutil
import subprocess

from git_helpers import git, get_current_branch, hash_for
from git_make_child_branch import make_child_branch
from git_rebase_children import rebase_children
from print_child_branch_structure import print_branch_structure


@contextlib.contextmanager
def run_test(path):
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)
        shutil.rmtree(path)


def main(target_directory):
    target_directory = os.path.expanduser(target_directory)
    target_container = os.path.dirname(target_directory)
    assert not os.path.exists(target_directory)
    assert os.path.isdir(target_container)

    os.mkdir(target_directory)
    with run_test(target_directory):
        # Initialize a repo and add a first commit so we can tell what branch we're on.
        print "Initializing repo"
        git("init")
        open("hello.txt", "w").close()
        git("add .")
        git("commit -am initial_commit")

        assert get_current_branch() == "master"
        original_commit = hash_for("HEAD")

        # Create all the branches
        make_child_branch("first_branch")
        assert get_current_branch() == "first_branch"

        make_child_branch("second_branch")
        assert get_current_branch() == "second_branch"

        make_child_branch("third_branch")
        assert get_current_branch() == "third_branch"

        # This should be sibling to second_branch, on top of first_branch
        git("checkout first_branch")
        make_child_branch("sibling_branch")
        assert get_current_branch() == "sibling_branch"

        # Make the first "real" commit, in master
        print "First commit"
        git("checkout master")
        with open(os.path.join(target_directory, "hello.txt"), "w") as f:
            f.write("Hello!")
        # Avoiding spaces because of how we break up args in the `git` function
        git("commit -am first_commit_message")
        first_commit = hash_for("HEAD")
        assert original_commit != first_commit

        # Do the recursive rebase
        print "Rebase first_branch and its children on top of master."
        git("checkout first_branch")
        rebase_children()
        assert first_commit == hash_for("first_branch")
        assert first_commit == hash_for("second_branch")
        assert first_commit == hash_for("third_branch")
        assert first_commit == hash_for("sibling_branch")

        # Make a second commit, this time in first_branch
        print "Make a second commit in first_branch"
        git("checkout first_branch")
        with open(os.path.join(target_directory, "hello.txt"), "w") as f:
            f.write("Hello there!")
        git("commit -am second_commit_message")
        second_commit = hash_for("HEAD")
        assert original_commit != second_commit and first_commit != second_commit

        # Rebase just second_branch. This should update third_branch but shouldn't touch sibling_branch.
        print "Doing second rebase"
        git("checkout second_branch")
        rebase_children()
        assert second_commit == hash_for("first_branch")
        assert second_commit == hash_for("second_branch")
        assert second_commit == hash_for("third_branch")
        assert first_commit == hash_for("sibling_branch")

        print "Make a merge conflict in sibling_branch"
        git("checkout sibling_branch")
        with open(os.path.join(target_directory, "hello.txt"), "w") as f:
            f.write("Hello conflict")
        git("commit -am conflicting_change_message")

        # This should throw since the rebase has conflicts
        print "Testing merge conflicts"
        try:
            rebase_children()
            assert False
        except subprocess.CalledProcessError:
            pass

        # Abort the rebase and try again
        git("rebase --abort")
        # It should fail for the same reason
        print "Testing merge conflicts again"
        try:
            rebase_children()
            assert False
        except subprocess.CalledProcessError:
            pass

        print "Resolving the merge conflict"
        with open(os.path.join(target_directory, "hello.txt"), "w") as f:
            f.write("Hello merge")
        git("add hello.txt")
        git("rebase --continue")

        # This should effectively no-op
        print "Doing no-op rebase"
        current_commit = hash_for("HEAD")
        rebase_children()
        assert current_commit == hash_for("HEAD")

        print_branch_structure()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("test_target_dir")
    args = parser.parse_args()
    main(args.test_target_dir)
