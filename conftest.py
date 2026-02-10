# -*- coding: utf-8 -*-
"""
Pytest config for StoneWalker.
Silent on pass. Verbose on failure. No dependencies.

pytest.ini: --tb=short -q --no-header for compact output.
This plugin: suppresses per-test dots, captures failures for rendering.
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


_failure_reports = []


def pytest_runtest_logreport(report):
    """Capture failure reports for verbose output."""
    if report.failed and report.when in ("call", "setup"):
        _failure_reports.append(report)


def pytest_report_teststatus(report, config):
    """Suppress call-phase dots. Let setup/teardown use defaults."""
    if report.when == "call":
        return report.outcome, "", ""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Print failure details since --tb=no suppresses them."""
    for report in _failure_reports:
        terminalreporter.write_line("")
        terminalreporter.write_line("=" * 70)
        terminalreporter.write_line(f"FAIL: {report.nodeid}")
        terminalreporter.write_line("-" * 70)
        if hasattr(report, "longrepr") and report.longrepr:
            for line in str(report.longrepr).split("\n"):
                terminalreporter.write_line(line)
