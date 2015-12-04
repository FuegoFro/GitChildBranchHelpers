# Usage

Source the `bash_git_helper_aliases.sh` file in your `.bashrc`, then use the the various commands
to work with your branches. Make sure to always use these commands when possible, rather than using
the raw git alternatives, so that this can keep track of all the branches properly.

In particular:
- Always create branches with the `git_make_child_branch` script (default alias `cmk`), even if the
  branch is off of master.
- Always rebase branches with `git_rebase_children` (default alias `crb`)
- Always land branches with `arc_land_child_aware` (default alias `cad`)
