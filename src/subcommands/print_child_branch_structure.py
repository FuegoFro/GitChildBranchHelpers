import os
import sys
from argparse import ArgumentParser, Namespace

from git_helpers import BranchTracker, get_branch_tracker, get_current_branch
from subcommands.base_command import BaseCommand
from typing import Iterable, List, Text, Tuple


class PrintChildBranchStructure(BaseCommand):
    def get_name(self) -> str:
        return "print-structure"

    def get_short_description(self) -> str:
        return "prints the dependency structure of the branches"

    def inflate_subcommand_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "-a", "--all", action="store_true", help="set to show all branches, including archived branches"
        )

    def run_command(self, args: Namespace) -> None:
        print(get_branch_structure_string(args.all))


def output_supports_color() -> bool:
    """
    Returns True if the running system's terminal supports color, and False
    otherwise. Taken from django.core.management.color.supports_color
    """
    plat = sys.platform
    supported_platform = plat != "Pocket PC" and (plat != "win32" or "ANSICON" in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty


def make_green(message: str) -> str:
    if output_supports_color():
        before = "\033[0;32m"
        after = "\033[0m"
    else:
        before = after = ""
    return before + message + after


def make_magenta(message: str) -> str:
    if output_supports_color():
        before = "\033[0;35m"
        after = "\033[0m"
    else:
        before = after = ""
    return before + message + after


def get_branch_structure_string(show_all: bool) -> str:
    current_branch = get_current_branch()
    structure_parts: List[str] = []
    with get_branch_tracker() as tracker:
        roots = []
        for parent in tracker.get_all_parents():
            if not tracker.has_parent(parent):
                roots.append(parent)
        roots = sorted(roots)

        skipped_archived = _get_branch_structure_parts_internal(
            tracker, current_branch, roots, structure_parts, show_all
        )

        if skipped_archived:
            structure_parts.append("(not displaying archived branches, run with --all to see them)")

    return "\n".join(structure_parts)


def _get_branch_structure_parts_internal(tracker: BranchTracker, current_branch: str, roots: List[str], structure_parts: List[str], show_all: bool) -> bool:
    first = True
    skipped_archived = False
    for root in roots:
        if not first:
            structure_parts.append("")
        first = False
        structure_parts.append(format_node(current_branch, root, is_archived=False))
        child_skipped_archived = _add_tree_parts(tracker, current_branch, root, structure_parts, "", show_all)
        # NOTE: Don't inline this 'or' because it will cause the recursive call not to happen due
        # to short circuiting.
        skipped_archived = skipped_archived or child_skipped_archived
    return skipped_archived


def format_node(current_branch: str, node: str, is_archived: bool) -> str:
    if node == current_branch:
        node = make_green(node)
    if is_archived:
        node = '{} {}'.format(node, make_magenta('(archived)'))
    return node


def sorted_look_ahead(iterable: Iterable[str]) -> Iterable[Tuple[str, bool]]:
    it = iter(sorted(iterable))

    try:
        last = next(it)
    except StopIteration:
        return

    for val in it:
        yield last, False
        last = val
    yield last, True


def _add_tree_parts(tracker: BranchTracker, current_branch: str, node: str, parts: List[str], indent_characters: str, show_all: bool) -> bool:
    # Then print the children
    skipped_archived = False
    children = []
    for child in tracker.children_for_parent(node):
        # We want to either show only the archived or only the non-archived, depending on
        # desired_archived_status
        if not tracker.is_archived(child) or show_all:
            children.append(child)
        else:
            skipped_archived = True

    for child, is_last in sorted_look_ahead(children):
        parts.append(indent_characters + "│")

        if is_last:
            prefix = "└── "
            child_indent = "    "
        else:
            prefix = "├── "
            child_indent = "│   "
        parts.append(indent_characters + prefix + format_node(current_branch, child, tracker.is_archived(child)))

        child_skipped_archived = _add_tree_parts(
            tracker, current_branch, child, parts, indent_characters + child_indent, show_all
        )
        # NOTE: Don't inline this 'or' because it will cause the recursive call not to happen due
        # to short circuiting.
        skipped_archived = skipped_archived or child_skipped_archived

    return skipped_archived


# Example branch structure
"""
master
│
└── first_branch
    │
    ├── second_branch
    │   │
    │   └── third_branch
    │
    └── sibling_branch
"""
