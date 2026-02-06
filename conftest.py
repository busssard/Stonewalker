# -*- coding: utf-8 -*-
"""
Pytest configuration for Django project.
Compact output: tqdm progress bar, TEST_FAIL: lines for failures.
"""

import os
import sys
import django
from pathlib import Path

# Add the source directory to Python path
source_dir = Path(__file__).parent / "source"
sys.path.insert(0, str(source_dir))

# Set Django settings and configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        if "main" in str(item.fspath):
            item.add_marker("integration")
        elif "accounts" in str(item.fspath):
            item.add_marker("unit")


# ---------------------------------------------------------------------------
# Minimal output: tqdm progress bar + TEST_FAIL: for failures
# ---------------------------------------------------------------------------

_bar = None
_failures = []


def pytest_collection_finish(session):
    """Create tqdm bar once we know total test count."""
    global _bar
    try:
        from tqdm import tqdm
        _bar = tqdm(total=len(session.items), desc="Tests", unit="test",
                    bar_format="{desc}: {bar} {n_fmt}/{total_fmt} [{elapsed}]",
                    file=sys.stderr)
    except ImportError:
        pass


def pytest_runtest_logreport(report):
    """Update progress bar on each test result."""
    if report.when == "call":
        if _bar:
            _bar.update(1)
        if report.failed:
            msg = str(report.longrepr).strip().split("\n")[-1]
            _failures.append(f"TEST_FAIL: {report.nodeid.split('::')[-1]} - {msg}")
    elif report.when == "setup" and report.failed:
        if _bar:
            _bar.update(1)
        msg = str(report.longrepr).strip().split("\n")[-1]
        _failures.append(f"TEST_FAIL: {report.nodeid.split('::')[-1]} (setup) - {msg}")


def pytest_report_teststatus(report, config):
    """Suppress default per-test output (dots/F/E)."""
    if report.when == "call" or (report.when == "setup" and report.failed):
        return report.outcome, "", ""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print failures and final count after bar completes."""
    if _bar:
        _bar.close()
    for f in _failures:
        terminalreporter.write_line(f)
    total = sum(len(v) for v in terminalreporter.stats.values() if isinstance(v, list))
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(_failures)
    terminalreporter.write_line(
        f"{passed} passed, {failed} failed" if failed else f"{passed} passed"
    )
