from git_helpers import get_branch_tracker


def print_branch_structure():
    with get_branch_tracker() as tracker:
        roots = []
        for parent in tracker.get_all_parents():
            if not tracker.has_parent(parent):
                roots.append(parent)

    for root in roots:
        print root
        print_tree(tracker, root, "")


def look_ahead(iterable):
    it = iter(iterable)
    last = it.next()
    for val in it:
        yield last, False
        last = val
    yield last, True


def print_tree(tracker, node, indent_characters):
    # Then print the children
    for child, is_last in look_ahead(tracker.children_for_parent(node)):
        print indent_characters + "|"
        if is_last:
            print indent_characters + "\-- " + child
            new_indent = indent_characters + "    "
        else:
            print indent_characters + "|-- " + child
            new_indent = indent_characters + "|   "
        print_tree(tracker, child, new_indent)

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
