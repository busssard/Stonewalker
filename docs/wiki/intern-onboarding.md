---
title: Intern Onboarding Guide
tags: [onboarding, intern, getting-started, guide]
last-updated: 2026-02-10
---

# Intern Onboarding Guide

Welcome to the StoneWalker team! This guide will get you oriented with the project, the codebase, and the development workflow.

## What is StoneWalker?

StoneWalker is a web application that tracks painted stones as they travel the world. Think of it like geocaching, but for painted stones. Here's the core loop:

1. A user creates a stone in the app and gets a unique QR code
2. They paint a real stone and attach the QR code to it
3. They hide the stone somewhere in the real world
4. When someone finds the stone, they scan the QR code with their phone
5. The app records where the stone was found and shows its journey on a map
6. The finder re-hides the stone for the next person

## Tech Stack Overview

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 (Python 3.8+) |
| Database | PostgreSQL (required everywhere, no SQLite) |
| Frontend | HTML/CSS/JS, Bootstrap 4, Leaflet.js (maps) |
| Payments | Stripe (for QR code packs in the shop) |
| Translations | Django i18n, 7 languages |
| Testing | pytest with tqdm progress bar, 118+ tests |
| CI/CD | GitHub Actions |
| Deployment | Render.com |

## Day 1: Set Up Your Environment

Follow the [[getting-started]] guide completely. The key steps:

1. Install PostgreSQL and Python 3.8+
2. Clone the repo
3. Create the PostgreSQL database and set `DATABASE_URL`
4. Set up the virtual environment and install dependencies
5. Run migrations
6. Compile translations
7. Start the dev server
8. Run the test suite to verify everything works

**Critical rule:** Always use the virtual environment. Never use system Python.

```bash
# Correct
./venv/bin/python run_tests.py
./venv/bin/pip install <package>

# Wrong - never do this
python run_tests.py
pip install <package>
```

## Day 1: Explore the App

Once the server is running, walk through these flows:

1. **Register an account** at `/accounts/sign-up/` (activation email prints to terminal in dev mode)
2. **Activate** by clicking the link in the terminal output
3. **Log in** and look at the main map at `/stonewalker/`
4. **Visit the shop** at `/shop/` and get a free QR code
5. **Claim the stone** -- follow the redirect to name and describe your stone
6. **Edit the stone** -- change description, add an image
7. **Publish** and then **send off** the stone
8. **Check My Stones** at `/my-stones/`
9. **Change language** at `/language/` and see the translations
10. **Visit the admin** at `/admin/` (create a superuser first with `python manage.py createsuperuser`)

## Day 2: Understand the Codebase

### Read These First
1. `CLAUDE.md` (project root) -- The comprehensive developer guide. Read this whole thing.
2. [[architecture]] -- System architecture overview
3. [[api]] -- API endpoints

### Key Directories

```
source/
  accounts/          -- Auth, profiles, email verification
    views.py         -- All auth views
    models.py        -- Profile, Activation, EmailAddressState
    templates/       -- Login, signup, profile templates

  main/              -- Core app
    views.py         -- Stone views, scanning, QR API, map
    shop_views.py    -- Shop, checkout, claiming
    models.py        -- Stone, StoneMove, QRPack, StoneScanAttempt
    qr_service.py    -- QR code generation
    tests/           -- 6 test modules + base.py

  app/               -- Django project config
    urls.py          -- All URL routes (start here to understand the app)
    conf/development/settings.py
    conf/production/settings.py

  content/
    templates/main/  -- Main app templates
    assets/          -- CSS, JS, fonts, images
    locale/          -- Translation files (7 languages)
    media/           -- Uploaded files (stones, profiles, QR codes)
```

### Trace a Request

Pick any URL from the site map in `README.md` and trace it:

1. Find the URL pattern in `source/app/urls.py`
2. Find the view class/function it points to
3. Read the view code
4. Find the template it renders
5. Understand what models it queries

Example: `/shop/` -> `ShopView` -> `source/main/shop_views.py` -> `source/content/templates/main/shop.html` -> queries `QRPack`, product config

## Day 3: Run and Understand the Tests

```bash
./venv/bin/python run_tests.py
```

You should see ~118 tests pass with a tqdm progress bar.

### Test Files to Read

Start with these, in order of complexity:

1. `source/main/tests/base.py` -- Shared test utilities and base classes
2. `source/main/tests/test_models.py` -- Model behavior tests
3. `source/main/tests/test_stone_workflow.py` -- End-to-end stone creation tests
4. `source/main/tests/test_api_endpoints.py` -- API testing patterns
5. `source/accounts/tests.py` -- Auth tests and CSS utility checks

### Understand the Test Infrastructure

| File | Role |
|------|------|
| `run_tests.py` | Entry point: compiles translations, then runs pytest |
| `pytest.ini` | Single source of truth for pytest config |
| `conftest.py` | Django setup, path config, tqdm output, auto-markers |

## Workflow for Making Changes

### Before You Start Coding

1. Read `.claude/tasks.md` if it exists -- it may have your assigned tasks
2. Create a branch: `git checkout -b feature/my-feature`
3. Read the relevant source code and tests

### While Coding

1. Follow the patterns you see in the existing code
2. Use class-based views for pages, function views for APIs
3. Wrap user-facing text in `{% trans %}` tags
4. Write tests as you go (see [[guides/write-tests]])

### Before Committing

1. Run the full test suite: `./venv/bin/python run_tests.py`
2. All tests must pass
3. Create logical, separate commits (see [[guides/add-a-feature]])

### Before Pushing

The pre-push hook at `.git/hooks/pre-push` runs the full test suite automatically. It takes ~3 minutes. If any test fails, the push is blocked.

## Common Tasks

### "I need to add a new page"
See [[guides/add-a-feature]] for the full checklist.

### "I need to fix a translation"
See [[guides/add-a-translation]].

### "I found a bug"
1. Write a test that reproduces it (it should fail)
2. Fix the bug
3. Verify the test passes
4. Add edge case variations
5. See the Bug-Driven Testing Policy in `CLAUDE.md`

### "I need to add a model field"
1. Add the field to the model in `models.py`
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Write tests for the new field
5. Update any views/templates that need the field

## Things That Will Trip You Up

1. **PostgreSQL, not SQLite** -- There is no SQLite support. Period.
2. **Always use the venv** -- System Python will be missing dependencies.
3. **Compile translations** -- Templates with `{% trans %}` tags need compiled `.mo` files.
4. **The pre-push hook takes 3 minutes** -- Plan for it.
5. **Don't add `-v` to test commands** -- The tqdm output is designed to be lean.
6. **Inline styles get flagged** -- The CSS test will catch unauthorized inline styles in templates.
7. **`TestCase` vs `TransactionTestCase`** -- If your test triggers a DB error, the transaction is aborted and no further queries work. See [[guides/write-tests]].

## Key Documentation

| Document | What It Covers |
|----------|---------------|
| `CLAUDE.md` | Everything -- the master developer reference |
| `README.md` | Project overview, site map, database schema |
| `TRANSLATION.md` | Translation system reference |
| `DEPLOYMENT.md` | Render.com deployment |
| This wiki | Architecture, features, how-to guides |

## Questions?

- Check `CLAUDE.md` first -- it has answers to most common questions
- Check the [[README]] wiki home for links to specific topics
- Ask your team lead if you're stuck

## Related Pages

- [[getting-started]] -- Detailed setup instructions
- [[architecture]] -- System architecture
- [[guides/add-a-feature]] -- How to add a feature end-to-end
- [[guides/write-tests]] -- Testing guide
- [[guides/add-a-translation]] -- Translation guide
