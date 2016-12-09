if [ -n "$BASH_VERSION" ]; then
    GIT_CHILD_BRANCH_HELPERS_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/src
elif [ -n "$ZSH_VERSION" ]; then
    GIT_CHILD_BRANCH_HELPERS_LOCATION="${0:a:h}"/src
else
    echo "Unknown shell, not setting up git child branch helpers! (not bash or zsh)" >&2
fi

if [ -d "$GIT_CHILD_BRANCH_HELPERS_LOCATION" ]; then
    # Commands are prefixed with "c" for "child"

    # Rebase
    alias crb='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/git_rebase_children.py'
    # Make branch
    alias cmk='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/git_make_child_branch.py'
    # Arc diff
    alias cad='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/arc_diff_against_parent.py'
    # Arc land
    alias cal='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/arc_land_onto_parent.py'
    # Print structure
    alias cps='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/print_child_branch_structure.py'
    # Rename
    alias crn='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/git_rename_branch.py'
    # Remove leaf child
    alias crm='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/git_remove_leaf_child.py'
    # Change parent
    alias ccp='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/git_change_parent.py'
    # Set archived
    alias csa='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION"/set_branch_archived.py'
fi
