import os
import sys

from typing import TypeVar, Iterable, Tuple

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
    if not supported_platform or not is_a_tty:
        return False
    return True


def make_green(message):
    # type: (str) -> str
    if output_supports_color():
        before = "\033[0;32m"
        after = "\033[0m"
    else:
        before = after = ""
    return before + message + after


def print_branch_structure():
    # type: () -> None
    current_branch = get_current_branch()
    with get_branch_tracker() as tracker:
        roots = []
        for parent in tracker.get_all_parents():
            if not tracker.has_parent(parent):
                roots.append(parent)

    first = True
    for root in roots:
        if not first:
            print ""
        first = False
        print format_node(current_branch, root)
        print_tree(tracker, current_branch, root, "")


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


def print_tree(tracker, current_branch, node, indent_characters):
    # type: (BranchTracker, str, str, str) -> None
    # Then print the children
    for child, is_last in sorted_look_ahead(tracker.children_for_parent(node)):
        print indent_characters + "|"

        if is_last:
            prefix = "\-- "
            child_indent = "    "
        else:
            prefix = "|-- "
            child_indent = "|   "
        print indent_characters + prefix + format_node(current_branch, child)

        print_tree(tracker, current_branch, child, indent_characters + child_indent)

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
    print_branch_structure()
