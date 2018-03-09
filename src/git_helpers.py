from __future__ import print_function, unicode_literals

import _csv
import csv
import os
import shutil
import subprocess
import sys
from collections import defaultdict

try:
    # noinspection PyUnresolvedReferences
    from typing import (
        Any,
        BinaryIO,
        Callable,
        Dict,
        Iterable,
        List,
        Optional,
        Tuple,
        TypeVar,
        Union,
        Text,
        TextIO,
        cast,
    )
except ImportError:
    pass


def git(command):
    # type: (Text) -> Text
    ret = run_command_expecting_failure(subprocess.check_output, "git", command).decode()
    if sys.version_info[0] >= 3:
        return cast(Text, ret)
    else:
        return ret


def get_current_branch():
    # type: () -> Text
    return git("rev-parse --abbrev-ref HEAD").strip()


def get_branch_tracker():
    # type: () -> BranchTrackerWrapper
    git_dir = git("rev-parse --git-dir").strip()
    config_dir = os.path.join(git_dir, "child_branch_helper")
    if os.path.exists(config_dir):
        assert os.path.isdir(config_dir)
    else:
        os.mkdir(config_dir)
    config_file = os.path.join(config_dir, "branches.csv")
    # Make sure the config file exists
    if not os.path.exists(config_file):
        open(config_file, "a").close()
    return BranchTrackerWrapper(config_file)


def does_branch_contain_commit(branch, commit):
    # type: (Text, Text) -> bool
    try:
        return git("branch --contains {}".format(commit)).find(" {}\n".format(branch)) >= 0
    except SystemExit:
        return False


def fail_if_not_rebased(current_branch, parent, tracker):
    # type: (Text, Text, BranchTracker) -> None
    bases = tracker.bases_for_branch(current_branch)
    assert len(bases) in (1, 2)
    if len(bases) == 2 or not does_branch_contain_commit(parent, bases[0]):
        print("Please rebase this branch on top of its parent")
        exit()


def arc(command):
    # type: (Text) -> None
    run_command_expecting_failure(subprocess.check_call, "arc", command)


T = TypeVar('T')


def run_command_expecting_failure(command_runner, program, command):
    # type: (Callable[[List[Text]], T], Text, Text) -> T
    try:
        return command_runner([program] + command.split(" "))
    except subprocess.CalledProcessError:
        print("")
        print("!!!!!!!!")
        print("!!! Failed to run/finish {} command:".format(program))
        print("!!! `{} {}`".format(program, command))
        print("!!!!!!!!")
        print("")
        exit(1)
    except KeyboardInterrupt:
        print("")
        print("User aborted command: `{} {}`".format(program, command))
        print("")
        exit(1)


def get_csv_reader(f):
    # type: (BinaryIO) -> _csv._reader
    if sys.version_info[0] >= 3:
        generator = (line.decode() for line in f)
    else:
        generator = (str(line) for line in f)
    return csv.reader(generator)


class BranchTrackerWrapper(object):
    def __init__(self, config_file):
        # type: (Text) -> None
        super(BranchTrackerWrapper, self).__init__()
        self.config_file = config_file

    def __enter__(self):
        # type: () -> BranchTracker
        self.branch_tracker = BranchTracker(self.config_file)
        return self.branch_tracker

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_value, exc_traceback):
        # type: (Any, Any, Any) -> None
        self.branch_tracker.save_to_file()


class BranchTracker(object):
    _VERSION_ROW_ID = "version"

    def __init__(self, config_file):
        # type: (Text) -> None
        super(BranchTracker, self).__init__()
        self._config_file = config_file
        self._child_to_parent = {}  # type: Dict[Text, Text]
        self._parent_to_children = defaultdict(list)  # type: Dict[Text, List[Text]]
        self._branch_to_bases = {}  # type: Dict[Text, Tuple[Text, ...]]
        self._is_branch_archived = {}  # type: Dict[Text, bool]
        # Read config file
        with open(config_file, "rb") as f:
            # Run migrations as necessary. This will re-write the stored file before we read any
            # branch data from it.
            self._version = self._run_migrations(f)
            reader = get_csv_reader(f)
            # We don't need to handle the version row, since that'll be handled by _run_migrations
            for row in reader:
                child, parent, base, rebase_base, is_archived = row
                assert child not in self._child_to_parent
                assert child not in self._branch_to_bases
                self._child_to_parent[child] = parent
                self._parent_to_children[parent].append(child)
                self._is_branch_archived[child] = is_archived == "True"
                assert base
                if rebase_base:
                    self._branch_to_bases[child] = (base, rebase_base)
                else:
                    self._branch_to_bases[child] = (base, )

    def _run_migrations(self, f):
        # type: (BinaryIO) -> int
        """
        Migrates the file if necessary. Once this method finishes, the file will have the latest
        version's format and the passed in file object will be pointing at the first row of data.

        :param f: A file object pointing to the branch data file
        :return: The current version of the file
        """
        # First get the current version from the file
        version = self._get_version_from_file(f)

        # Then get the relevant migrations.
        all_migrations = self._get_migrations()
        target_version = len(all_migrations)
        migrations_to_run = all_migrations[version:]

        # If there are any migrations to run, run them
        if not migrations_to_run:
            assert version == target_version, "No migrations to run, but not at target version"
        else:
            for migration in migrations_to_run:
                migration(self._config_file)

            # Now re-seek the input file to the right place
            f.seek(0)
            assert self._get_version_from_file(f) == target_version, \
                "Migrations did not leave database at target version"

        # Return the new version number
        return target_version

    def _get_version_from_file(self, f):
        # type: (BinaryIO) -> int
        # If there are no rows in the file, assume we're on version 0
        version = 0
        reader = get_csv_reader(f)
        # We only want to look at the first line, but the easiest way to do that is a for loop with
        # a break.
        for version_row in reader:
            if len(version_row) == 2:
                version_row_id, version_str = version_row
                assert version_row_id == self._VERSION_ROW_ID, "Version row ID doesn't match"
                version = int(version_str)
            break

        return version

    @staticmethod
    def _get_migrations():
        # type: () -> Tuple[Callable[[Text], None], ...]
        # Add a notion of an archived field
        def m001_add_archived_field(config_file):
            # type: (Text) -> None
            # Because this migration introduces versions, we have to add the initial version to the
            # file.
            migrated_file_contents = ["version,1\n"]
            # Add the archived field to each entry, defaulting to False.
            with open(config_file, 'r') as f:
                for line in f:
                    migrated_file_contents += [line.rstrip() + ",False\n"]
            with open(config_file, 'wb') as f_out:
                f_out.write("".join(migrated_file_contents).encode())

        return (
            m001_add_archived_field,
        )

    def save_to_file(self):
        # type: () -> None
        tmp_config_file = self._config_file + ".tmp"
        with open(tmp_config_file, "w") as f:
            writer = csv.writer(f)
            writer.writerow([BranchTracker._VERSION_ROW_ID, self._version])
            for child, parent in self._child_to_parent.items():
                bases = self._branch_to_bases[child]
                if len(bases) == 1:
                    base = bases[0]
                    rebase_base = ""
                else:
                    base, rebase_base = bases
                is_archived = self._is_branch_archived[child]
                writer.writerow([child, parent, base, rebase_base, is_archived])
        shutil.move(tmp_config_file, self._config_file)

    def parent_for_child(self, child):
        # type: (Text) -> Text
        return self._child_to_parent[child]

    def children_for_parent(self, parent):
        # type: (Text) -> List[Text]
        return self._parent_to_children[parent]

    def bases_for_branch(self, branch):
        # type: (Text) -> Tuple[Text,...]
        return self._branch_to_bases[branch]

    def get_all_parents(self):
        # type: () -> Iterable[Text]
        return self._parent_to_children.keys()

    def has_parent(self, branch):
        # type: (Text) -> bool
        return branch in self._child_to_parent

    def collapse_and_remove_parent(self, old_parent):
        # type: (Text) -> None
        # Remove the old parent from its parent, use that as the new parent
        new_parent = self._child_to_parent.pop(old_parent)
        self._parent_to_children[new_parent].remove(old_parent)

        # Remove the old parent's base branches
        self._branch_to_bases.pop(old_parent)

        # Update the old parent's children to point to the new parent
        if old_parent in self._parent_to_children:
            children = self._parent_to_children.pop(old_parent)
            self._parent_to_children[new_parent].extend(children)
            for child in children:
                self._child_to_parent[child] = new_parent

    def add_child_for_parent(self, parent, new_child, child_base):
        # type: (Text, Text, Text) -> None
        self._child_to_parent[new_child] = parent
        self._parent_to_children[parent].append(new_child)
        self._branch_to_bases[new_child] = (child_base, )
        self._is_branch_archived[new_child] = False

    def start_rebase(self, branch, new_base):
        # type: (Text, Text) -> None
        bases = self._branch_to_bases[branch]
        assert len(bases) == 1
        self._branch_to_bases[branch] = bases + (new_base, )

    def finish_rebase(self, branch, new_base):
        # type: (Text, Text) -> None
        bases = self._branch_to_bases[branch]
        assert len(bases) == 2
        self._branch_to_bases[branch] = (new_base, )

    def rename_branch(self, old_branch, new_branch):
        # type: (Text, Text) -> None
        self._branch_to_bases[new_branch] = self._branch_to_bases.pop(old_branch)
        self._is_branch_archived[new_branch] = self._is_branch_archived.pop(old_branch)

        if old_branch in self._child_to_parent:
            parent = self._child_to_parent[new_branch] = self._child_to_parent.pop(old_branch)
            self._parent_to_children[parent].remove(old_branch)
            self._parent_to_children[parent].append(new_branch)

        if old_branch in self._parent_to_children:
            children = self._parent_to_children[new_branch] = self._parent_to_children.pop(old_branch)
            for child in children:
                self._child_to_parent[child] = new_branch

    def remove_child_leaf(self, child_leaf):
        # type: (Text) -> None
        children = self._parent_to_children[child_leaf]
        assert not children, "Expected branch to be a leaf node, had {} child(ren).".format(
            len(children))

        if child_leaf in self._child_to_parent:
            parent = self._child_to_parent.pop(child_leaf)
            self._parent_to_children[parent].remove(child_leaf)

    def set_parent(self, child, new_parent):
        # type: (Text, Text) -> None
        if child in self._child_to_parent:
            old_parent = self._child_to_parent[child]
            self._parent_to_children[old_parent].remove(child)

        self._child_to_parent[child] = new_parent
        self._parent_to_children[new_parent].append(child)

    def set_is_archived(self, branch, is_archived):
        # type: (Text, bool) -> None
        self._is_branch_archived[branch] = is_archived

    def is_archived(self, branch):
        # type: (Text) -> bool
        return self._is_branch_archived[branch]


def hash_for(rev):
    # type: (Text) -> Text
    return git("rev-parse --verify {}".format(rev)).strip()
