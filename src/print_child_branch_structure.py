import argparse
import os
import sys

try:
    # noinspection PyUnresolvedReferences
    from typing import (
        Iterable,
        Tuple,
        TypeVar,
    )
except ImportError:
    pass

from git_helpers import get_branch_tracker, get_current_branch, BranchTracker


def output_supports_color():
    # type: () -> bool
    """
    Returns True if the running system's terminal supports color, and False
    otherwise. Taken from django.core.management.color.supports_color
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or
                                                  'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


def make_green(message):
    # type: (str) -> str
    if output_supports_color():
        before = "\033[0;32m"
        after = "\033[0m"
    else:
        before = after = ""
    return before + message + after


def get_branch_structure_string(show_all):
    # type: (bool) -> str
    current_branch = get_current_branch()
    structure_parts = []  # type: List[str]
    with get_branch_tracker() as tracker:
        roots = []
        for parent in tracker.get_all_parents():
            if not tracker.has_parent(parent):
                roots.append(parent)

        skipped_archived = _get_branch_structure_parts_internal(
            tracker, current_branch, roots, structure_parts, show_all)

        if skipped_archived:
            structure_parts.append("(not displaying archived branches, run with --all to see them)")

    return "\n".join(structure_parts)


def _get_branch_structure_parts_internal(tracker, current_branch, roots, structure_parts, show_all):
    # type: (BranchTracker, str, List[str], List[str], bool) -> bool
    first = True
    skipped_archived = False
    for root in roots:
        if not first:
            structure_parts.append("")
        first = False
        structure_parts.append(format_node(current_branch, root))
        child_skipped_archived = _add_tree_parts(tracker, current_branch, root, structure_parts, "", show_all)
        # NOTE: Don't inline this 'or' because it will cause the recursive call not to happen due to short circuiting.
        skipped_archived = skipped_archived or child_skipped_archived
    return skipped_archived


def format_node(current_branch, node):
    # type: (str, str) -> str
    if node == current_branch:
        return make_green(node)
    else:
        return node

T = TypeVar('T')


def sorted_look_ahead(iterable):
    # type: (Iterable[T]) -> Iterable[Tuple[T, bool]]
    it = iter(sorted(iterable))
    last = it.next()
    for val in it:
        yield last, False
        last = val
    yield last, True


def _add_tree_parts(tracker, current_branch, node, parts, indent_characters, show_all):
    # type: (BranchTracker, str, str, List[str], str, bool) -> bool
    # Then print the children
    skipped_archived = False
    children = []
    for child in tracker.children_for_parent(node):
        # We want to either show only the archived or only the non-archived, depending on desired_archived_status
        if not tracker.is_archived(child) or show_all:
            children.append(child)
        else:
            skipped_archived = True

    for child, is_last in sorted_look_ahead(children):
        parts.append(indent_characters + "|")

        if is_last:
            prefix = "\-- "
            child_indent = "    "
        else:
            prefix = "|-- "
            child_indent = "|   "
        parts.append(indent_characters + prefix + format_node(current_branch, child))

        child_skipped_archived = _add_tree_parts(
            tracker, current_branch, child, parts, indent_characters + child_indent, show_all)
        # NOTE: Don't inline this 'or' because it will cause the recursive call not to happen due to short circuiting.
        skipped_archived = skipped_archived or child_skipped_archived

    return skipped_archived

# Example branch structure
"""
master
|
\-- first_branch
    |
    |-- second_branch
    |   |
    |   \-- third_branch
    |
    \-- sibling_branch
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--all", action="store_true",
                        help="Set to show all branches (eg even archived branches)")
    args = parser.parse_args()

    print get_branch_structure_string(args.all)
