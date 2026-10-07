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
