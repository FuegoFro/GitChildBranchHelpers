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
    alias cmk='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" make-branch'
    # Arc diff
    alias cad='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" arc-diff'
    # Arc land
    alias cal='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" arc-land'
    # Print structure
    alias cps='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" print-structure'
    # Rename
    alias crn='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" rename'
    # Remove leaf child
    alias crm='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" remove-branch'
    # Change parent
    alias ccp='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" change-parent'
    # Set archived
    alias csa='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" set-archived'
    # Print branch info
    alias cbi='"$GIT_CHILD_BRANCH_HELPERS_LOCATION" print-branch-info'
fi
