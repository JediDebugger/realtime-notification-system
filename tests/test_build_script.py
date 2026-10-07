"""build.sh finds a Python 3.11+ interpreter (DEC-16).

Each test runs a copy of build.sh with PATH limited to fake interpreters.
A fake prints its version for any `-c` command and refuses everything else,
so the build stops right after choosing an interpreter: no venv, no pip.
"""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASH = shutil.which("bash")


def fake_python(bin_dir: Path, name: str, version: str) -> None:
    script = bin_dir / name
    script.write_text(
        "#!/bin/sh\n"
        f'if [ "$1" = "-c" ]; then echo "{version}"; exit 0; fi\n'
        'echo "fake python: refusing to run $*" >&2\n'
        "exit 1\n"
    )
    script.chmod(0o755)


def run_build(tmp_path: Path, interpreters: dict[str, str], python: str | None = None):
    """Run build.sh with only `interpreters` ({name: version}) on PATH.

    `python` names one of the fakes to pass as the PYTHON override.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, version in interpreters.items():
        fake_python(bin_dir, name, version)
    os.symlink(shutil.which("dirname"), bin_dir / "dirname")
    shutil.copy(ROOT / "build.sh", tmp_path / "build.sh")
    env = {"PATH": str(bin_dir)}
    if python is not None:
        env["PYTHON"] = str(bin_dir / python)
    return subprocess.run(
        [BASH, str(tmp_path / "build.sh")], env=env, capture_output=True, text=True, timeout=30
    )


def test_picks_the_newest_interpreter_that_is_new_enough(tmp_path):
    result = run_build(tmp_path, {"python3": "3.9.6", "python3.11": "3.11.4", "python3.12": "3.12.1"})
    assert "Creating .venv with python3.12 (3.12.1)" in result.stdout


def test_judges_candidates_by_version_not_by_name(tmp_path):
    result = run_build(tmp_path, {"python3.11": "3.10.0", "python3": "3.11.9"})
    assert "Creating .venv with python3 (3.11.9)" in result.stdout


def test_prefers_python3_when_it_is_new_enough(tmp_path):
    result = run_build(tmp_path, {"python3": "3.11.9", "python3.13": "3.13.0"})
    assert "Creating .venv with python3 (3.11.9)" in result.stdout


def test_otherwise_picks_the_newest_python3_n_on_path(tmp_path):
    # No fixed list: a python3.14 is found even though nothing names it.
    result = run_build(tmp_path, {"python3": "3.10.0", "python3.14": "3.14.0"})
    assert "Creating .venv with python3.14 (3.14.0)" in result.stdout


def test_newest_is_judged_by_reported_version(tmp_path):
    result = run_build(tmp_path, {"python3": "3.9.6", "python3.12": "3.12.1", "python3.15": "3.10.2"})
    assert "Creating .venv with python3.12 (3.12.1)" in result.stdout


def test_ignores_names_that_are_not_python3_n(tmp_path):
    result = run_build(tmp_path, {"python3": "3.9.6", "python3.11": "3.11.4", "python3.13-config": "3.13.0"})
    assert "Creating .venv with python3.11 (3.11.4)" in result.stdout


def test_fails_clearly_when_nothing_is_new_enough(tmp_path):
    result = run_build(tmp_path, {"python3": "3.9.6"})
    assert result.returncode != 0
    assert "Python 3.11 or newer is required" in result.stderr
    assert "python3 3.9.6" in result.stderr
    assert "PYTHON=" in result.stderr
    assert "Creating .venv" not in result.stdout


def test_python_override_wins_over_discovery(tmp_path):
    result = run_build(tmp_path, {"python3.13": "3.13.0", "python3.11": "3.11.4"}, python="python3.11")
    assert f"Creating .venv with {tmp_path / 'bin' / 'python3.11'} (3.11.4)" in result.stdout


def test_python_override_that_is_too_old_is_an_error(tmp_path):
    result = run_build(tmp_path, {"python3.12": "3.12.1", "python3": "3.9.6"}, python="python3")
    assert result.returncode != 0
    assert "Python 3.11 or newer is required" in result.stderr
    assert "Creating .venv" not in result.stdout
