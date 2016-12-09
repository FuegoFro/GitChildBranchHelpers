# Git helpers for working with child branches
This is a set of utilities to make working on child branches (and grandchild branches and arbitrary trees of branches) easier, without getting messed up due to an incorrect merge-base. I've found this to be particularly helpful when code review support is spotty, since you can just keep working in child branches and can always go back and update your parent and rebase easily if you need to. Working on RC branches is also easier, since there's no more having to remember to land onto the right branch.

## The problem being solved
Let's say we have a set of dependent branches, as described by the commit graph below, where each node (eg `A2`) is a commit and each line represents a branch, with the branch name at the end (eg `<= feature_c`).

```
M1 <= master
|
\--A1--A2 <= feature_a
       |
       |--B1 <= feature_b
       |
       \--C1 <= feature_c
          |
          \--D1 <= feature_d
```

Now let's say we do some more work on our branches and we pull `master`. Our commit graph now looks like this:

```
M1--M2 <= master
|
\--A1--A2--A3 <=feature_a
       |
       |--B1--B2 <=feature_b
       |
       \--C1--C2 <=feature_c
          |
          \--D1 <=feature_d
```

There are two primary operations to support, given a commit graph like the one above. The first is propagating changes to child branches. Let's say commit `A3` contains a crucial fix or breaking change that needs to be taken into account in a few of the other feature branches. What we can do is checkout the `feature_a` branch and propagate our changes. This will recursively cause each child branch to rebase onto the tip of its parent branch. The [`git_rebase_children.py`](./src/git_rebase_children.py) script does this currently (though it will also rebase the current branch on top of its parent, which is not done in this example). The result would be as follows:

```
M1--M2 <= master
|
\--A1--A2--A3 <=feature_a
           |
           |--B1'--B2' <=feature_b
           |
           \--C1'--C2' <=feature_c
                   |
                   \--D1' <=feature_d
```

Let's go back to the situation before we propagated changes from the `feature_a` branch. Another workflow we want to support is getting all of the upstream changes in a branch. Say you're working on `feature_b` and you find a bug preventing you from working, but realize the bug is fixed in `master`. What we want to do here is pull in upstream changes, or effectively super rebase such that we rebasing not just on our parent, but all the way to the upper-most parent. This causes us to be based on the latest code from **each** of our parent branches. There are no scripts in this repo that do this behavior yet. Doing this for `feature_b` would cause the commit graph to look like this:

```
M1--M2 <= master
|   |
|   \--A1'--A2'--A3' <=feature_a
|                |
|                \--B1'--B2' <=feature_b
|
\--A1--A2(--A3)
       |
       \--C1--C2 <=feature_c
          |
          \--D1 <=feature_d
```

Note that at this point, `feature_c` and `feature_d` are no longer actually based on `feature_a`. However, these scripts will correctly handle this when you propagate changes from `feature_a` (or `master`), or when you rebase onto upstream changes from `feature_c` or `feature_d`. Doing so would look like this (with the exception of pulling upstream changes from `feature_c`, which would leave `feature_d` not actually based on the current `feature_a`):

```
M1--M2 <= master
    |
    \--A1'--A2'--A3' <=feature_a
                 |
                 |--B1'--B2' <=feature_b
                 |
                 \--C1'--C2' <=feature_c
                         |
                         \--D1' <=feature_d
```

## Usage
Source the [`bash_zsh_git_helper_aliases.sh`](./bash_zsh_git_helper_aliases.sh) file in your `.bashrc` (or `.zshrc`), then use the the various commands to work with your branches.
Make sure to always use these commands when possible, rather than using the raw git alternatives, so that this can keep
track of all the branches properly.

In particular:

- Always create branches with the [`git_make_child_branch`](./src/git_make_child_branch.py) script (default alias `cmk`), even if the
  branch is off of master.
- Always rebase branches with [`git_rebase_children`](./src/git_rebase_children.py) (default alias `crb`)
- Always diff branches with [`arc_diff_against_parent`](./src/arc_diff_against_parent.py) (default alias `cad`)
- Always land branches with [`arc_land_onto_parent`](./src/arc_land_onto_parent.py) (default alias `cal`)

For a list of all available commands, look in the [`bash_zsh_git_helper_aliases.sh`](./bash_zsh_git_helper_aliases.sh) file.

Unfortunately, right now there's no good way to tell it about your existing branches, but they should continue to work fine
alongside this so you can try this out with new branches you make.

## Implementation details
This solution involves a series of scripts that call through to `git` while maintaining extra information about the branches you create. Specifically, for each branch it records:

- The branch name
- The parent branch's name
- The commit that the branch is based off of
- Optionally, the commit that the branch is rebasing to

This is stored in the repo's `.git` folder, at `child_branch_helper/branches.csv`. By keeping track of the base revision separately from the parent branch name, we're able to allow the parent branch to change and be rebased independently of the child. However, in order to iniitally obtain this information and keep it up to date, you must use these scripts for certain operations. In particular, these scripts should always be used to:

- Make new branches - so that we have the correct parent branch name and initial base revision
- Rebase a branch - so that we can update the base revision
- Arc diff a branch - so we can ensure you're only diffing against your parent and diff's don't contain your parent's commits.
- Arc land a branch - so we can ensure you're only landing your code, and none of your parent branch's

## Future work
I'd like to make it so you don't have to remember to use special commands, but rather it just works seamlessly. Whether this is patching or wrapping `git`, or something else, it'd be nice to come up with a more seamless integration. Similarly for `arc`, which might just involve changing the merge-base strategy.
