#!/usr/bin/env bash
# Build: create .venv with Python 3.11+, install the package and its test
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

# 3.11 is the minimum (DEC-16). Anything that isn't a version, e.g. "unknown", fails quietly.
is_supported() {
    local major minor
    IFS=. read -r major minor _ <<<"$1"
    case "$major" in ''|*[!0-9]*) return 1 ;; esac
    case "$minor" in ''|*[!0-9]*) return 1 ;; esac
    [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 11 ]; }
}

# Sets PYTHON and version, or exits with an error saying what was found.
find_python() {
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
        return
    fi

    local found="" name v minor best_minor=0 seen=" "
    if command -v python3 >/dev/null 2>&1 && v="$(python_version python3)"; then
        if is_supported "$v"; then
            PYTHON=python3
            version="$v"
            return
        fi
        found="python3 $v"
    fi
    # Every python3.N on PATH (not python3.N-config etc.); the newest qualifying wins.
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

    if [ -z "${PYTHON:-}" ]; then
        echo "error: Python 3.11 or newer is required, but none was found on PATH." >&2
        echo "Looked for python3 and python3.N; found: ${found:-none}." >&2
        echo "To install one:" >&2
        echo "  macOS: brew install python@3.12, or the installer from https://www.python.org/downloads/" >&2
        echo "  Debian/Ubuntu: sudo apt install python3 python3-venv (if your release's python3 is 3.11+)" >&2
        echo "Or set PYTHON=/path/to/python3.11 (or newer) and re-run ./build.sh." >&2
        exit 1
    fi
}

# A .venv whose pip can't run (e.g. left half-made by a failed venv) would
# fail every later build, so start it again.
if [ -d .venv ] && ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
    echo ".venv is broken (its pip doesn't run); removing it so it can be recreated"
    rm -rf .venv
fi

if [ ! -d .venv ]; then
    find_python
    echo "Creating .venv with $PYTHON ($version)"
    if ! "$PYTHON" -m venv .venv; then
        rm -rf .venv
        echo "error: '$PYTHON -m venv .venv' failed, so the partial .venv was removed." >&2
        echo "On Debian/Ubuntu this usually means the venv package is missing: sudo apt install python${version%.*}-venv" >&2
        exit 1
    fi
fi

.venv/bin/python -m pip install --quiet --disable-pip-version-check -e ".[dev]"
.venv/bin/python -m compileall -q src

echo "Build OK. Run ./run.sh for the demo or ./test.sh for the tests."
