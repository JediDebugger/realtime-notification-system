import subprocess
import sys


def run_demo() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "notifications"],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_demo_runs_and_exits_zero():
    result = run_demo()
    assert result.returncode == 0, result.stderr


def test_demo_shows_T1():
    out = run_demo().stdout
    assert "[in-app] to player 1: Congratulations! You've reached level 15!" in out
    assert "SENT LEVEL_UP to player 1 (Game Events)" in out
