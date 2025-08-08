#!/usr/bin/env python3
"""
Test runner that ensures translations are compiled before running tests.
Usage: python run_tests.py [pytest-args...]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def compile_translations():
    """Compile translations before running tests."""
    print("🔄 Compiling translations before tests...")
    
    try:
        # Change to source directory
        source_dir = Path(__file__).parent / "source"
        
        # Run translation compilation using the virtual environment
        result = subprocess.run(
            ["python", "manage.py", "compile_translations", "--force"],
            capture_output=True,
            text=True,
            cwd=source_dir,
            env=dict(os.environ, PYTHONPATH=str(source_dir))
        )
        
        if result.returncode == 0:
            print("✅ Translations compiled successfully")
            return True
        else:
            print(f"⚠️  Translation compilation warnings: {result.stderr}")
            return True  # Don't fail tests for warnings
            
    except Exception as e:
        print(f"⚠️  Translation compilation failed: {e}")
        return False  # Don't fail tests if compilation fails


def run_tests(test_args):
    """Run the actual tests."""
    print("🧪 Running tests...")
    
    # If no explicit test paths are provided (either no args or only flags),
    # target app test files explicitly to avoid cwd/testpaths issues
    only_flags = all(arg.startswith('-') for arg in test_args) if test_args else True
    if only_flags:
        test_args = list(test_args) if test_args else []
        test_args += [
            "accounts/tests.py",
            "main/tests.py",
        ]
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"] + test_args
    
    # Run tests from source directory with proper Django settings
    env = dict(os.environ, DJANGO_SETTINGS_MODULE="app.settings")
    result = subprocess.run(cmd, cwd=Path(__file__).parent / "source", env=env)
    return result.returncode


def main():
    # Get all command line arguments except the script name
    test_args = sys.argv[1:]
    
    # Compile translations first
    if compile_translations():
        # Run tests
        exit_code = run_tests(test_args)
        sys.exit(exit_code)
    else:
        print("❌ Failed to compile translations, but continuing with tests...")
        exit_code = run_tests(test_args)
        sys.exit(exit_code)


if __name__ == '__main__':
    main() 