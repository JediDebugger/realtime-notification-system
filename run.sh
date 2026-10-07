#!/usr/bin/env bash
# Run the example-usage demo.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    echo "run ./build.sh first" >&2
    exit 1
fi

exec .venv/bin/python -m notifications
