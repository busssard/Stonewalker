---
title: How to Write Tests
tags: [guide, how-to, testing, pytest]
last-updated: 2026-02-10
---

# How to Write Tests

StoneWalker has 118+ tests with comprehensive coverage. This guide explains how to add new tests.

## Test Organization

| Location | Type | Auto-marked as |
|----------|------|----------------|
| `source/accounts/tests.py` | Unit tests | `unit` |
| `source/main/tests/*.py` | Integration tests | `integration` |
| `source/main/translation_tests.py` | Translation QA | (standalone) |

Markers are applied automatically by `conftest.py` based on file path -- you don't need `@pytest.mark` decorators.

## Running Tests

```bash
# Full suite (recommended)
./venv/bin/python run_tests.py

# Unit tests only
make test-fast

# Integration tests only
make test-slow

# With coverage
make test-cov

# Specific file
cd source && python manage.py test main.tests.test_models
```

The test runner compiles translations first, then runs pytest with a tqdm progress bar. Failures are reported as `TEST_FAIL: [test_name] - [reason]`.

## Base Test Classes

Use the shared base classes from `source/main/tests/base.py`:

| Class | What it provides |
|-------|-----------------|
| `BaseStoneWalkerTestCase` | Test user creation, login helper, convenience methods |
| `BaseQRTestCase` | Extends above with stone and QR code setup |
| `BaseAuthenticatedTestCase` | Pre-logged-in user |
| `BaseAnonymousTestCase` | No user logged in |

Example:

```python
from main.tests.base import BaseAuthenticatedTestCase

class MyFeatureTests(BaseAuthenticatedTestCase):
    def test_my_feature_works(self):
        response = self.client.get('/my-feature/')
        self.assertEqual(response.status_code, 200)
```

## Writing a New Test File

1. Create a file in `source/main/tests/` (e.g., `test_my_feature.py`)
2. Import a base class
3. Write test methods (must start with `test_`)

```python
from django.test import TestCase
from main.tests.base import BaseAuthenticatedTestCase
from main.models import Stone

class MyFeatureTests(BaseAuthenticatedTestCase):
    def test_page_loads(self):
        """Verify the page returns 200 for authenticated users"""
        response = self.client.get('/my-feature/')
        self.assertEqual(response.status_code, 200)

    def test_requires_auth(self):
        """Verify anonymous users are redirected to login"""
        self.client.logout()
        response = self.client.get('/my-feature/')
        self.assertEqual(response.status_code, 302)

    def test_form_submission(self):
        """Verify the form creates the expected object"""
        response = self.client.post('/my-feature/', {
            'name': 'TestItem',
            'description': 'Test description',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(MyModel.objects.filter(name='TestItem').exists())
```

## What to Test

Every feature should cover:

1. **Happy path** -- Does it work with valid input?
2. **Authentication** -- Is it properly gated?
3. **Validation** -- Does it reject bad input?
4. **Edge cases** -- Empty strings, very long strings, special characters, unicode
5. **Error handling** -- Does it fail gracefully?

## Important Gotchas

### Django TestCase vs TransactionTestCase

Django's `TestCase` wraps each test in an `atomic()` block. If a test triggers a **database-level error** (e.g., `IntegrityError` for duplicate PK), PostgreSQL aborts the transaction. After that, no further DB queries work in that test -- you'll get `TransactionManagementError`.

**Workaround:** Don't query the DB after an expected DB error, or use `TransactionTestCase` instead.

### Never Have Both tests.py and tests/ Directory

Python/pytest gets confused when both exist. If using a `tests/` package, delete any `tests.py` and move its contents into the package.

### Test Output Convention

- Do **not** add `-v` or `--tb=short` flags unless actively debugging
- The default output is lean (~3 lines for 118 tests)
- Failures print `TEST_FAIL: [test_name] - [failure message]`
- This is configured in `pytest.ini` and `conftest.py`

### CSS Inline Style Test

`CSSUtilityClassTests` in `accounts/tests.py` scans all templates for inline styles. If you add a new inline style to a template, you must either:
- Replace it with a utility class from `styles.css`
- Add it to the exclusion list in the test

## Bug-Driven Testing Policy

When a bug is reported:
1. Write a test that reproduces the bug (it should fail)
2. Fix the bug
3. Verify the test passes
4. Add edge case variations

Tests should be resilient -- test the **behavior**, not the **implementation**. If a form field name changes, the test should still validate the concept.

## Test Config

- **Entry point:** `run_tests.py` -- compiles translations, then runs pytest
- **Config file:** `pytest.ini` (single source of truth)
- **Conftest:** `conftest.py` -- Django setup, path config, tqdm progress bar, auto-marking
- **Coverage config:** `source/pyproject.toml` under `[tool.coverage.*]`

## Related Pages

- [[getting-started]] -- Running the test suite for the first time
- [[architecture]] -- Where test files live
- [[guides/add-a-feature]] -- Full feature workflow including testing
