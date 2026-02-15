# Quality Engineering Guide

This document covers the code quality infrastructure, how to use it, and the security audit findings for the StoneWalker project.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Linting with Ruff](#linting-with-ruff)
3. [Pre-commit Hooks](#pre-commit-hooks)
4. [CI/CD Integration](#cicd-integration)
5. [Makefile Targets](#makefile-targets)
6. [Security Audit](#security-audit)
7. [Coding Standards](#coding-standards)

---

## Quick Start

```bash
# Install quality tools
pip install ruff pre-commit bandit

# Run lint check
make lint

# Run format check
make format

# Run both
make quality-check

# Install pre-commit hooks (once per clone)
pre-commit install
```

---

## Linting with Ruff

[Ruff](https://docs.astral.sh/ruff/) is the project's Python linter and formatter. It replaces flake8, isort, and black in a single fast tool.

### Configuration

All ruff config lives in `source/pyproject.toml` under `[tool.ruff]`. Key settings:

- **Line length**: 88 (matches black)
- **Target version**: Python 3.8+
- **Enabled rule sets**:
  - `E`, `W` -- pycodestyle (style)
  - `F` -- pyflakes (logic errors, unused imports)
  - `I` -- isort (import ordering)
  - `S` -- flake8-bandit (security)
  - `B` -- flake8-bugbear (common bugs)
  - `UP` -- pyupgrade (Python version upgrades)
  - `T20` -- flake8-print (stray print statements)

### Running Ruff

```bash
# Check for lint issues (no auto-fix)
ruff check source/ --config source/pyproject.toml

# Check with auto-fix (use carefully, review changes)
ruff check source/ --config source/pyproject.toml --fix

# Check formatting
ruff format --check --diff source/ --config source/pyproject.toml

# Auto-format
ruff format source/ --config source/pyproject.toml
```

### Current Policy

Ruff runs with `--exit-zero` in CI and pre-commit hooks. This means:
- Lint issues are **reported but do not block** merges or commits
- This is intentional -- the existing codebase has not been reformatted
- As the team cleans up files, the goal is to eventually remove `--exit-zero`

**When editing a file**: Fix any ruff warnings in the lines you touch. Do not reformat entire files in unrelated PRs.

---

## Pre-commit Hooks

Pre-commit hooks run automatically before each `git commit`.

### Setup

```bash
pip install pre-commit
pre-commit install
```

### What Runs

| Hook | What it does | Blocking? |
|------|-------------|-----------|
| `trailing-whitespace` | Removes trailing whitespace | Yes |
| `end-of-file-fixer` | Ensures files end with newline | Yes |
| `check-yaml` | Validates YAML syntax | Yes |
| `check-json` | Validates JSON syntax (excludes content/) | Yes |
| `check-merge-conflict` | Catches leftover merge conflict markers | Yes |
| `check-added-large-files` | Warns on files > 500KB | Yes |
| `debug-statements` | Catches `breakpoint()`, `pdb.set_trace()` | Yes |
| `ruff` (lint) | Python linting | No (exit-zero) |
| `ruff-format` | Python formatting check | No (check only) |
| `bandit` | Security scanning | No (exit-zero) |

### Skipping Hooks

If you need to bypass hooks for a specific commit (e.g., WIP commit):

```bash
git commit --no-verify -m "WIP: work in progress"
```

Use sparingly. The pre-push hook will still catch issues before push.

### Running Manually

```bash
# Run all hooks against all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff --all-files
```

---

## CI/CD Integration

The GitHub Actions workflow at `.github/workflows/tests.yml` has two jobs:

### 1. `lint` job (fast, no database)
- Installs ruff
- Runs `ruff check` with `--exit-zero` (non-blocking)
- Runs `ruff format --check` (non-blocking)
- Takes ~30 seconds

### 2. `test` job (full suite, requires PostgreSQL)
- Installs all dependencies
- Spins up PostgreSQL 15
- Runs `python run_tests.py` with coverage
- Takes ~3 minutes

The lint job runs in parallel with the test job, so it doesn't add time to CI.

---

## Makefile Targets

| Target | Command | Description |
|--------|---------|-------------|
| `make lint` | `ruff check source/` | Run linter |
| `make format` | `ruff format --check --diff source/` | Check formatting |
| `make quality-check` | lint + format | All quality checks |
| `make security-scan` | `bandit -r source/` | Security scan |

---

## Security Audit

Conducted February 2026. This audit covers the Django application code in `source/`.

### Summary

| Category | Severity | Count | Status |
|----------|----------|-------|--------|
| CSRF exemption on debug endpoint | HIGH | 1 | Documented, needs fix |
| Unvalidated filename in Content-Disposition | MEDIUM | 2 | Documented |
| Comment field without content filtering | LOW | 1 | Documented |
| Stripe webhook without signature in dev | LOW | 1 | By design |
| Exception message exposure to users | LOW | 3 | Documented |

### HIGH: CSRF Exemption on Debug Endpoint

**File**: `source/main/views.py:137`

```python
@csrf_exempt  # For quick debug, remove in production
def debug_add_stone(request):
```

**Issue**: The `debug_add_stone` view has `@csrf_exempt` and allows unauthenticated users to create stones (falls back to `User.objects.first()`). The comment says "remove in production" but there is no mechanism to enforce this.

**Recommendation**:
1. Remove this endpoint entirely, or
2. Gate it behind `settings.DEBUG` with an early return in production
3. At minimum, remove `@csrf_exempt` and add `@login_required`

### MEDIUM: Unvalidated Filenames in Content-Disposition

**Files**:
- `source/main/qr_service.py:233`
- `source/main/views.py:732`

```python
response['Content-Disposition'] = f'attachment; filename="{stone.PK_stone}_stonewalker_qr.png"'
```

**Issue**: `stone.PK_stone` is user-controlled input used directly in the `Content-Disposition` header. A stone name containing `"` or newline characters could cause header injection.

**Recommendation**: Sanitize the filename before use:
```python
import re
safe_name = re.sub(r'[^\w\-.]', '_', stone.PK_stone)
response['Content-Disposition'] = f'attachment; filename="{safe_name}_stonewalker_qr.png"'
```

### LOW: Comment Field Without Content Filtering

**File**: `source/main/views.py` (StoneScanView.post and StoneLinkView.post)

```python
comment = request.POST.get('comment', '')
```

**Issue**: Stone move comments are stored and displayed without filtering for:
- Email addresses
- Phone numbers
- URLs/links
- Profanity

Comments are rendered in templates via `{{ m.comment }}`, which is auto-escaped by Django's template engine (no XSS risk), but there is no content policy enforcement.

**Recommendation**: Consider adding a `sanitize_comment()` utility if the product requires filtering personal information from comments. This is a product decision, not a security vulnerability per se.

### LOW: Stripe Webhook Without Signature Verification in Development

**File**: `source/main/stripe_service.py:206-215`

```python
if not webhook_secret:
    logger.warning("STRIPE_WEBHOOK_SECRET not set - webhook verification disabled")
    try:
        import json
        event = json.loads(payload)
```

**Issue**: When `STRIPE_WEBHOOK_SECRET` is not set, the webhook accepts any JSON payload without signature verification. This is documented as development-only behavior.

**Status**: Acceptable for development. In production, the `STRIPE_WEBHOOK_SECRET` environment variable must be set (documented in DEPLOYMENT.md).

### LOW: Exception Messages Exposed to Users

**Files**:
- `source/main/views.py:249`: `f'Could not add stone: {str(e)}'`
- `source/main/views.py:325`: `f'Could not add scan: {str(e)}'`
- `source/main/views.py:569`: `f'Could not record stone find: {str(e)}'`

**Issue**: Raw exception messages are shown to users via `messages.error()`. These could leak internal details (database table names, field constraints, etc.).

**Recommendation**: Log the full exception, show a generic message to the user:
```python
logger.error(f"Stone creation failed: {e}", exc_info=True)
messages.error(request, "Could not add stone. Please try again.")
```

### Not Vulnerable: SQL Injection

The application uses Django's ORM exclusively. No raw SQL queries, `.extra()`, or `RawSQL()` calls were found. All database queries go through Django's parameterized query builder. **No SQL injection risk.**

### Not Vulnerable: XSS

Django templates auto-escape all variables by default. The one use of `|safe` (`{{ stones_json|safe }}` in `stonewalker_start.html:137`) is inside a `<script type="application/json">` tag where the data is JSON-serialized by Python's `json.dumps()`, which escapes special characters. **No XSS risk.**

### Not Vulnerable: Open Redirect

The login view uses Django's `is_safe_url()` to validate redirect targets (`accounts/views.py:90`). **No open redirect risk.**

---

## Coding Standards

### For New Code

1. **Run `ruff check` on your file before committing** -- fix any issues flagged
2. **Use Django ORM** -- never write raw SQL
3. **Never use `@csrf_exempt`** unless handling webhook signatures (like Stripe)
4. **Never expose exception messages to users** -- log them, show generic errors
5. **Sanitize user input in HTTP headers** (Content-Disposition, etc.)
6. **Use `login_required` or `LoginRequiredMixin`** on all views that modify data

### For Existing Code

- Fix lint issues in lines you touch
- Do not reformat entire files in unrelated PRs
- If you encounter a security issue, fix it and add a regression test

### Import Order (enforced by ruff)

```python
# 1. Standard library
import json
import uuid

# 2. Third-party
from django.conf import settings
from django.http import JsonResponse

# 3. First-party
from .models import Stone
from accounts.models import Profile
```
