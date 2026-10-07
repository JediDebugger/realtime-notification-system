#!/usr/bin/env bash
# Build: find Python 3.11+, create .venv, install the package and its test
# dependency, and byte-compile the sources so syntax errors fail the build.
#
# Without PYTHON set, uses python3 if it is 3.11 or newer (the machine's
# default, so the most likely to have venv and pip working); otherwise the
# newest python3.N on PATH that is (a stock Mac's python3 is 3.9) (DEC-16).
# Override with PYTHON=/path/to/python3.11 ./build.sh
set -euo pipefail
cd "$(dirname "$0")"

# Prints the interpreter's version, e.g. 3.12.1. Fails if it can't run.
python_version() {
    "$1" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null
}

is_supported() {
    local major minor
    IFS=. read -r major minor _ <<<"$1"
    [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; }
}

if [ -n "${PYTHON:-}" ]; then
    if ! command -v "$PYTHON" >/dev/null 2>&1; then
        echo "error: '$PYTHON' not found. Install Python 3.11 or newer, or set PYTHON=/path/to/python3.11." >&2
        exit 1
    fi
    version="$(python_version "$PYTHON")" || version="unknown"
    if ! is_supported "$version"; then
        echo "error: Python 3.11 or newer is required, but '$PYTHON' is $version." >&2
        echo "Set PYTHON=/path/to/python3.11 (or newer) and re-run ./build.sh." >&2
        exit 1
    fi
else
    found=""
    if command -v python3 >/dev/null 2>&1 && v="$(python_version python3)"; then
        if is_supported "$v"; then
            PYTHON=python3
            version="$v"
        else
            found="python3 $v"
        fi
    fi
    if [ -z "${PYTHON:-}" ]; then
        # Every python3.N on PATH (not python3.N-config etc.), newest qualifying wins.
        best_minor=0
        seen=" "
        while IFS= read -r name; do
            case "${name#python3.}" in ''|*[!0-9]*) continue ;; esac
            case "$seen" in *" $name "*) continue ;; esac
            seen="$seen$name "
            v="$(python_version "$name")" || continue
            if is_supported "$v"; then
                IFS=. read -r _ minor _ <<<"$v"
                if [ "$minor" -gt "$best_minor" ]; then
                    PYTHON="$name"
                    version="$v"
                    best_minor="$minor"
                fi
            else
                found="${found:+$found, }$name $v"
            fi
        done < <(compgen -c python3.)
    fi
    if [ -z "${PYTHON:-}" ]; then
        echo "error: Python 3.11 or newer is required, but none was found on PATH." >&2
        echo "Looked for python3 and python3.N; found: ${found:-none}." >&2
        echo "Install Python 3.11+, or set PYTHON=/path/to/python3.11 (or newer) and re-run ./build.sh." >&2
        exit 1
    fi
fi

if [ ! -d .venv ]; then
    echo "Creating .venv with $PYTHON ($version)"
    "$PYTHON" -m venv .venv
fi

.venv/bin/python -m pip install --quiet --disable-pip-version-check -e ".[dev]"
.venv/bin/python -m compileall -q src

echo "Build OK. Run ./run.sh for the demo or ./test.sh for the tests."
