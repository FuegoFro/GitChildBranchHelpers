if [ -n "$BASH_VERSION" ]; then
    GIT_CHILD_BRANCH_HELPERS_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/bin/child
elif [ -n "$ZSH_VERSION" ]; then
    GIT_CHILD_BRANCH_HELPERS_LOCATION="${0:a:h}"/bin/child
else
    echo "Unknown shell, not setting up git child branch helpers! (not bash or zsh)" >&2
fi

if [ -e "$GIT_CHILD_BRANCH_HELPERS_LOCATION" ]; then
    # Commands are prefixed with "c" for "child"

    # Rebase
    alias crb='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" rebase'
    # Make branch
    alias cmk='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" make-branch'
    # Arc diff
    alias cad='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" arc-diff'
    # Arc land
    alias cal='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" arc-land'
    # Print structure
    alias cps='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" print-structure'
    # Rename
    alias crn='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" rename'
    # Remove leaf child
    alias crm='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" remove-branch'
    # Change parent
    alias ccp='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" change-parent'
    # Set archived
    alias csa='python "$GIT_CHILD_BRANCH_HELPERS_LOCATION" set-archived'
fi
