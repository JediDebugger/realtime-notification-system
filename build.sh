#!/usr/bin/env bash
# Build: check the Python version, create .venv, install the package and its
# test dependency, and byte-compile the sources so syntax errors fail the build.
# Override the interpreter with PYTHON=/path/to/python3.11 ./build.sh
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "error: '$PYTHON' not found. Install Python 3.11 or newer, or set PYTHON=/path/to/python3.11." >&2
    exit 1
fi

if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    version="$("$PYTHON" -c 'import platform; print(platform.python_version())')"
    echo "error: Python 3.11 or newer is required, but '$PYTHON' is $version." >&2
    echo "Set PYTHON=/path/to/python3.11 (or newer) and re-run ./build.sh." >&2
    exit 1
fi

if [ ! -d .venv ]; then
    "$PYTHON" -m venv .venv
fi

.venv/bin/python -m pip install --quiet --disable-pip-version-check -e ".[dev]"
.venv/bin/python -m compileall -q src

echo "Build OK. Run ./run.sh for the demo or ./test.sh for the tests."
