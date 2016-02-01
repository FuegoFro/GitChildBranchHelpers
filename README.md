# Git helpers for working with child branches

## Overview

This is a set of utilities to make working on child branches (and grandchild branches and arbitrary trees branches) easier.
When you use these commands to make and rebase your branches, it automatically keeps track of which branch is its parent and
which commit it's based off of so you can rebase your parent and then rebase yourself without getting messed up due to the
incorrect merge-base. There's some other handy utilities in there:

- Recursively rebase a branch and all of its children (and all of that branch's children etc).

- Arc diff and land easily. It'll automatically diff against and land onto your parent branch and won't let you diff if
  you're not actually based off of your parent. Landing does the right thing of collapsing the tree such that all of the landed
  branch's children move to its parent.

- Other tools for managing branch structure, including changing a branch's parent, deleting a leaf branch, and print out the
  tree of branches in beautiful ascii art.

I've found this to be particularly helpful when code review support is spotty, since you can just keep working in child
branches and can always go back and update your parent and rebase easily if you need to. Working on RC branches is also
easier, since there's no more having to remember to land onto the right branch.

Unfortunately, right now there's no good way to tell it about your existing branches, but they should continue to work fine
alongside this so you can try this out with new branches you make.

## Usage

Source the [`bash_git_helper_aliases.sh`](./bash_git_helper_aliases.sh) file in your `.bashrc`, then use the the various commands to work with your branches.
Make sure to always use these commands when possible, rather than using the raw git alternatives, so that this can keep
track of all the branches properly.

In particular:

- Always create branches with the `git_make_child_branch` script (default alias `cmk`), even if the
  branch is off of master.

- Always rebase branches with `git_rebase_children` (default alias `crb`)

- Always diff branches with `arc_diff_against_parent` (default alias `cad`)

- Always land branches with `arc_land_onto_parent` (default alias `cal`)

For a list of all available commands, look in the [`bash_git_helper_aliases.sh`](./bash_git_helper_aliases.sh) file.
