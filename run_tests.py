#!/usr/bin/env python3
"""
StoneWalker test runner.

Usage:
    ./venv/bin/python run_tests.py                       # all tests
    ./venv/bin/python run_tests.py accounts              # account tests only
    ./venv/bin/python run_tests.py main/tests/           # main tests only
    ./venv/bin/python run_tests.py -k test_scan          # by name pattern
    ./venv/bin/python run_tests.py -m unit               # unit tests only
    ./venv/bin/python run_tests.py -m integration        # integration only
    ./venv/bin/python run_tests.py --skip-translations   # skip compilemessages
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = PROJECT_ROOT / "source"
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"


def get_python():
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


def compile_translations():
    python = get_python()
    try:
        result = subprocess.run(
            [python, "manage.py", "compilemessages"],
            capture_output=True,
            text=True,
            cwd=SOURCE_DIR,
        )
        if result.returncode != 0:
            print(f"Warning: compilemessages failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"Warning: compilemessages failed: {e}")


def run_tests(test_args):
    python = get_python()

    has_path = any(not arg.startswith("-") for arg in test_args)
    if not has_path:
        test_args = list(test_args) + ["accounts/tests.py", "main/tests/"]

    cmd = [python, "-m", "pytest"] + test_args
    env = dict(
        os.environ,
        DJANGO_SETTINGS_MODULE="app.settings",
        IS_PRODUCTION="false",
    )
    result = subprocess.run(cmd, cwd=SOURCE_DIR, env=env)
    return result.returncode


def main():
    args = list(sys.argv[1:])

    skip = "--skip-translations" in args
    args = [a for a in args if a != "--skip-translations"]

    if not skip:
        compile_translations()

    sys.exit(run_tests(args))


if __name__ == "__main__":
    main()
