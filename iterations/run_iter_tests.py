"""Run unit tests for one iteration folder."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main():
    iter_dir = Path(__file__).resolve().parent
    if len(sys.argv) > 1:
        iter_dir = Path(sys.argv[1]).resolve()
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-t", ".", "-q"],
        cwd=iter_dir,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
