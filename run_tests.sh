#!/usr/bin/env bash
set -euo pipefail
cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -e ./venv/bin/python ]]; then
    echo "Please create a virtualenv at `venv` and install the `requirements-dev.txt` packages." &>2
    exit 1
fi

exec ./venv/bin/python ./src/tests.py