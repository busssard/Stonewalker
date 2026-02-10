# -*- coding: utf-8 -*-
"""
Pytest config for StoneWalker.
Silent on pass. Verbose on failure. No dependencies.

pytest.ini: --tb=no -q --no-header suppress default output.
This plugin prints failure details. pytest -q prints the final count.
"""

import os
import sys

import django
from pathlib import Path

source_dir = Path(__file__).parent / "source"
sys.path.insert(0, str(source_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests: main/ = integration, accounts/ = unit."""
    for item in items:
        if "main" in str(item.fspath):
            item.add_marker("integration")
        elif "accounts" in str(item.fspath):
            item.add_marker("unit")


# ---------------------------------------------------------------------------
# Output plugin: suppress dots, show failure details
# ---------------------------------------------------------------------------

_failure_reports = []


def pytest_runtest_logreport(report):
    if report.when == "call" and report.failed:
        _failure_reports.append(report)
    elif report.when == "setup" and report.failed:
        _failure_reports.append(report)


def pytest_report_teststatus(report, config):
    """No dots for passing. Count only call phase for pytest's summary."""
    if report.when == "call":
        return report.outcome, "", ""
    # Setup/teardown: invisible and uncounted
    return "", "", ""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print failure details. pytest -q handles the final count line."""
    for report in _failure_reports:
        terminalreporter.write_line("")
        terminalreporter.write_line("=" * 70)
        terminalreporter.write_line(f"FAIL: {report.nodeid}")
        terminalreporter.write_line("-" * 70)
        if hasattr(report, "longrepr") and report.longrepr:
            for line in str(report.longrepr).split("\n"):
                terminalreporter.write_line(line)
