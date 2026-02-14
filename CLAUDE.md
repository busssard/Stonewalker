# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## StoneWalker - Django Stone Tracking Application

StoneWalker is a Django-based web application for tracking painted stones as they travel the world. This is a complex, feature-rich application with multi-language support, QR code generation, user authentication, and stone movement tracking.

## CRITICAL: Always Use the Virtual Environment

**NEVER use system Python.** Always use the project venv for ALL commands - running tests, installing packages, running the dev server, manage.py commands, everything.

```bash
# The venv lives at the project root
./venv/bin/python       # Use this, not 'python'
./venv/bin/pip          # Use this, not 'pip'

# Or activate it first
source venv/bin/activate
```

## Key Development Commands

### Development Setup
```bash
# Environment setup with PostgreSQL (required)
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"

# Quick development start (activates venv automatically)
./run_dev.sh

# Manual setup
source venv/bin/activate
cd source
python manage.py migrate
python manage.py runserver
```

### Testing
```bash
# Run all tests (includes translation compilation)
./venv/bin/python run_tests.py

# Run specific test types
make test-fast     # Unit tests only
make test-slow     # Integration tests only  
make test-cov      # With coverage report

# Run tests manually
cd source && python manage.py test accounts main
```

### Translation Management
```bash
# Extract new translatable strings
cd source && python manage.py makemessages -l [language_code]

# Compile translations (required before deployment)
cd source && python manage.py compilemessages

# Run translation quality tests
python source/manage.py test main.translation_tests

# Extract translations to CSV for editing
make translations
```

### Database Management
```bash
# Apply migrations
cd source && python manage.py migrate

# Create superuser
cd source && python manage.py createsuperuser

# Production database management (requires postgres_production.json)
./db list-users --limit 10
./db list-stones --type hidden
./db stats
```

### Build and Deployment
```bash
# Collect static files for production
cd source && python manage.py collectstatic

# Build for deployment
./build.sh

# Makefile shortcuts
make install     # Install dependencies
make setup       # Full setup including translations
make clean       # Clean generated files
```

## Project Architecture

### Django Applications
- **`accounts/`** - User authentication, registration, profiles, email activation
- **`main/`** - Core stone tracking, QR codes, scanning, map views
- **`app/`** - Project configuration with separate dev/production settings

### Key Models
- **User** (Django built-in) + **Profile** (1:1 extension with profile picture)
- **Stone** - Painted stones with UUID, QR codes, location tracking, types (hidden/hunted)
- **StoneMove** - Movement records when stones are scanned/found
- **Activation** - Email verification and account activation

### Settings Configuration
- **Development**: `source/app/conf/development/settings.py` (console email backend, relaxed SSL)
- **Production**: `source/app/conf/production/settings.py` (requires PostgreSQL, Maileroo email, SSL)
- **Environment detection**: `IS_PRODUCTION` environment variable controls which settings are used

### Database Requirements
- **PostgreSQL required for both development and production**
- Set `DATABASE_URL` environment variable
- Manual URL parsing (no dj_database_url for Python 3.8 compatibility)
- Development: SSL prefer, Production: SSL require

## Critical Development Notes

### QR Code System
- Stones automatically generate QR codes linking to `/stone-link/<uuid>/`
- QR codes stored in `source/content/media/qr_codes/`
- Cleartext URLs embedded in downloaded PNG images (3:4 portrait format)
- Robust error handling - stone creation succeeds even if QR generation fails
- Regeneration endpoint: `/regenerate-qr/<stone_pk>/`

### Translation System
- **7 languages supported**: English, Russian, Chinese, French, Spanish, German, Italian
- **Comprehensive QA testing** in `source/main/translation_tests.py`
- **Critical**: Always compile translations before deployment or tests will fail
- Translation files in `source/content/locale/[lang]/LC_MESSAGES/`
- Browser language detection enabled

### Authentication Features
- Email activation required for new users
- Profile editing via modal popup overlay
- Password reset functionality
- Profile picture uploads
- Username availability checking via API

### Stone Types & Workflow
- **Hidden stones**: Created by users, get circle shape automatically
- **Hunted stones**: Require location, get triangle shape, special finding experience
- **3-day cooldown**: Users can only scan same stone once every 3 days
- **UUID-based routing**: All stone links use UUIDs for security

### Frontend Architecture
- **Fixed header** that remains visible during scrolling
- **Burger menu** for mobile navigation
- **Modal system** for profile editing and stone interactions
- **Responsive breakpoints** managed via JavaScript (single source of truth)
- **Avant-garde design** with utility classes (200+ CSS utilities)

## Testing Strategy

### Test Organization
- **Unit tests**: `accounts/tests.py` (auto-marked `unit` by conftest.py based on directory)
- **Integration tests**: `main/tests/` directory with 6 test modules (auto-marked `integration`)
- **Translation QA**: `main/translation_tests.py` - automated PO file validation
- **Pre-push hook**: `.git/hooks/pre-push` runs full suite before every push
- **Markers are auto-applied** by `conftest.py` based on file path - no need for `@pytest.mark` decorators

### Test Files (118 tests total)
- `accounts/tests.py` - Auth, profiles, navigation, CSS utility checks (15 tests)
- `main/tests/test_models.py` - Stone model, StoneMove, scan attempts (23 tests)
- `main/tests/test_qr_system.py` - QR generation, download, display (10 tests)
- `main/tests/test_stone_scanning.py` - Scanning, blackout periods (8 tests)
- `main/tests/test_stone_workflow.py` - Creation, editing, status transitions, name validation (26 tests)
- `main/tests/test_api_endpoints.py` - AJAX endpoints, name availability (15+ tests)
- `main/tests/test_ui_templates.py` - Page loading, modals, auth gates (15+ tests)
- `main/tests/base.py` - Shared base classes: `BaseStoneWalkerTestCase`, `BaseQRTestCase`, `BaseAuthenticatedTestCase`, `BaseAnonymousTestCase`

### Test Runner
- **Entry point**: `./venv/bin/python run_tests.py` - compiles translations, then runs pytest
- **Config**: `pytest.ini` is the single source of truth (not pyproject.toml)
- **Output**: tqdm progress bar during run, `TEST_FAIL: [name] - [reason]` for failures
- **Coverage**: `source/pyproject.toml` has `[tool.coverage.*]` config; run with `make test-cov`
- **CI/CD**: GitHub Actions workflow at `.github/workflows/tests.yml`

### Coverage Areas
- User authentication and profile management
- Stone creation, name validation, scanning, QR code generation
- Translation compilation and functionality
- API endpoints and permissions
- CSS utility classes and responsive design

## Security & Performance

### Security Features
- CSRF protection on all forms
- File upload validation for images
- User authentication required for stone operations
- Cooldown enforcement prevents spam scanning
- SSL required in production
- Contact info validator blocks emails/URLs/phone numbers in comments

### SQL Safety Audit (February 2026)
- **No raw SQL anywhere**: Audited all Python files in `source/`. Zero instances of `raw()`, `extra()`, `cursor.execute()`, `RawSQL`, or string-formatted SQL.
- **All queries use Django ORM** with parameterized inputs (`.filter()`, `.get()`, `.create()`, `.exists()`, etc.)
- **Form handling is safe**: All user input goes through Django form validation or explicit `.strip()` / `.get()` before ORM calls
- **Stripe webhook**: Uses `stripe.Webhook.construct_event()` for signature verification; raw JSON payload is never used in SQL
- **f-strings in views**: Only used for log messages, file paths, and redirect URLs -- never for query construction
- **One note**: The `check_stone_name` and `check_username` views take GET parameters and pass them to `.filter()` which is safe (Django parameterizes these)
- **Conclusion**: No SQL injection vectors found. The codebase is ORM-only.

### Internationalization
- Middleware-based language detection
- Session-based language persistence
- Automatic redirect after language change
- Complete UI translation with quality assurance

### Performance Optimizations
- WhiteNoise for static file serving in production
- Database connection pooling (CONN_MAX_AGE: 600)
- Compressed static files in production
- PostgreSQL with SSL optimization

## Common Gotchas

1. **PostgreSQL is required** - SQLite not supported, never was, never will be
2. **Always use the venv** - `./venv/bin/python`, never system python
3. **Translation compilation** - Must run `compilemessages` before production deploy
4. **Environment variables** - `DATABASE_URL` and `SECRET_KEY` required for production
5. **QR code permissions** - Media directory must be writable
6. **Email backend** - Development uses console (prints to terminal), production uses Maileroo
7. **Static files** - Run `collectstatic` before production deployment
8. **GitHub PAT scope** - Needs `workflow` scope to push `.github/workflows/` changes
9. **pytest.ini section header** - Must be `[pytest]` not `[tool:pytest]` (that's the setup.cfg format)
10. **Pre-push hook runs full suite** - Budget ~3 minutes per push; stderr from `git push` appears after the hook output

## File Structure Key Points

- **Templates**: `source/content/templates/` (shared layouts in `layouts/default/`)
- **Static assets**: `source/content/assets/` (CSS, JS, images)
- **Media uploads**: `source/content/media/` (profile pics, QR codes)
- **Translations**: `source/content/locale/` (PO/MO files)
- **Database scripts**: Root level `db` script for production management
- **Build scripts**: `build.sh` (legacy Netlify), `run_dev.sh` convenience script
- **CI/CD**: `.github/workflows/tests.yml` - GitHub Actions test pipeline
- **Test config**: `pytest.ini` (pytest settings), `conftest.py` (Django setup + tqdm output), `run_tests.py` (entry point)
- **Translation docs**: `TRANSLATION.md` (single consolidated file)
- **Deployment docs**: `DEPLOYMENT.md` (Render.com focused)

## When Working on This Project

1. **Always check PostgreSQL connection** before starting development
2. **Compile translations** after any template changes
3. **Run full test suite** before committing major changes
4. **Test QR code functionality** after model changes
5. **Verify responsive design** across breakpoints
6. **Check translation coverage** for new user-facing strings
7. **Test authentication flows** after accounts app changes

This is a production-ready application with comprehensive testing, so maintain the same quality standards when making changes.

## User Preferences & Workflow

### Task Management via .claude/tasks.md
- **The user gives tasks and reports bugs via `.claude/tasks.md`** - always read it at the start of a session
- Follow the workflow defined at the top of tasks.md (mark current, plan, implement, test, document, migrate, push)
- Use agent teams for parallelizable work where it makes sense
- Mark tasks `[DONE]` when complete, `[current]` when in progress, `[BUG]` for reported bugs

### Git Commit Strategy
- **Always create multiple commits** - separate features/changes logically rather than one large commit
- Group related changes together (e.g., one commit for Stripe integration, another for PDF generation)
- Write clear, descriptive commit messages
- **Never commit real server IPs, passwords, or secrets** - use placeholders and reference environment variables or GitHub secrets

### Writing Documentation & Instructions
- **Self-contained copy-paste blocks** - when writing setup guides, deployment docs, or how-to instructions, inline everything the reader needs right where they need it. Don't say "see file X for the values" and make them cross-reference — put the actual values, commands, and config directly in the step.
- **Append-friendly over edit-in-place** - when modifying config files (e.g. postgresql.conf), prefer appending a block to the end rather than asking the reader to find and edit specific lines scattered through a 700-line file. Most config formats use "last value wins".
- **Assume the reader follows top-to-bottom** - each step should be runnable in sequence without jumping ahead or back. If step 5 depends on something from step 2, repeat the relevant info rather than saying "as configured in step 2".
- **No jargon without context** - if a step says "apply tuning parameters", show exactly what to run. If it says "edit the config", show the exact commands and content.

### Claude Code Session Notes
- Regularly update this CLAUDE.md file with new learnings and preferences
- Document any new patterns or conventions discovered during development

## Multi-Agent Team Workflow

### Team Structure
- **Optimal structure**: 3-5 specialist agents + 1 coordinating team lead
- Each specialist should own a clear domain with minimal overlap
- Give each agent a specific role, deliverable format, and file path to prevent overlap and confusion
- The team lead should NOT do specialist work - focus on orchestration, conflict resolution, and synthesis

### Model Selection for Agents
Choose the model per agent based on what the task demands. This is about cost efficiency, not hard rules - use judgment.

**Opus** is worth the cost when the task involves:
- Debugging, complex problem solving, multi-step reasoning
- Architecture decisions or resolving conflicting requirements
- Code that touches tricky logic, concurrency, security, or subtle edge cases
- Synthesizing information across many sources into coherent decisions

**Sonnet** is the right pick when the task is primarily:
- Writing documentation, analysis, marketing copy, or other prose
- Generating straightforward, well-defined code (CRUD endpoints, boilerplate, tests from a clear spec)
- Cross-review and refinement of existing drafts
- Translating requirements into structured output (config files, migration scripts, data models)

**Haiku** makes sense for:
- Quick lookups, file searches, formatting, or validation checks
- Simple boilerplate or template generation
- Tasks where speed matters more than nuance

The goal is to avoid running 5 Opus agents when 3 of them are writing docs. Match the model to the cognitive demand of the task.

### The 2-3 Round Review Pattern
1. **Round 1**: Independent specialist work with clear deliverable and file path
2. **Round 2**: Each specialist reads ALL other outputs and refines their own, with specific cross-references called out by the coordinator. This is the biggest value-add - surfaces contradictions, sharpens estimates, creates interdisciplinary insights
3. **Round 3** (optional): Final coherence pass with explicit resolution of all open tensions, number audit across documents. Diminishing returns beyond Round 2.

### Communication
- **Specific cross-team prompts outperform generic ones.** Messages that point to specific disagreements produce much better refinements than generic "review and update" instructions
- **Direct messages to specific agents are more effective and cheaper than broadcasts.** Use broadcasts only for universal policy changes
- **Direct agent-to-agent messaging resolves alignment issues faster** than routing everything through the team lead
- Agents sometimes report completion without sending a summary message - be explicit in instructions about requiring a completion report

### File Ownership
- **Assign each deliverable to exactly one agent.** Other agents provide input via messages, not direct file edits
- When spawning agent teams, assign non-overlapping file sets to avoid merge conflicts
- Documentation-only agents should never touch code/test files and vice versa
- CLAUDE.md updates should be done by the team lead after all agents finish

### Task Dependencies & Parallel Execution
- Use `blockedBy` for tasks that genuinely depend on prior work
- Don't block tasks that can start in parallel - let agents read partial outputs from peers
- All specialists working simultaneously saves significant time (5 agents can produce in ~10 min what would take 50 min sequentially)
- Pre-reading during idle time accelerates cross-review rounds

### Common Pitfalls
- **Agent context limits cause stalling** - keep documents focused; consider summary sections for cross-team consumption
- **Idle notifications create noise** - ignore them unless blocking on an agent's output
- **Cold-start for agents requires full context** - include all critical context (file paths, team decisions, specific cross-references) in every round's message
- **Consensus numbers must be established early** - key metrics should be locked in a shared location before cross-review to avoid agents diverging in opposite directions

## Learnings & Gotchas (Session Notes)

### Test Structure (February 2026)
- **Never have both `tests.py` and `tests/` directory** - Python/pytest gets confused when importing
- If using a `tests/` package, delete any `tests.py` file and move its contents to `tests/__init__.py`
- After changing test structure, clear `__pycache__` directories: `find source -name "__pycache__" -exec rm -rf {} +`
- The pre-push hook at `.git/hooks/pre-push` references test paths - update it when test structure changes

### CSS Inline Style Tests
- The `CSSUtilityClassTests` in `accounts/tests.py` check for inline styles in templates
- Allowed inline styles are explicitly listed (font-size, font-weight, font-family, margin, padding, etc.)
- When adding new inline styles to templates, add them to the regex exclusion list in the test

### Dependencies
- `stripe` package must be installed for tests to run (imported in `stripe_service.py` via `app/urls.py`)
- `tqdm` is required for test progress bar output
- Run `./venv/bin/pip install stripe reportlab tqdm` if tests fail with ModuleNotFoundError

### Test Output Convention
- **Always run tests via**: `./venv/bin/python run_tests.py`
- **Progress**: tqdm progress bar shows real-time progress during test runs
- **Failure format**: Failures print `TEST_FAIL: [test_name] - [failure message]` via conftest.py hooks
- **No verbose flags**: Do not add `-v` or `--tb=short` unless actively debugging a specific failure
- **Configured in**: `pytest.ini` (`--tb=no -q --no-header --no-summary`) + `conftest.py` (custom tqdm reporter)
- This keeps Claude Code context lean - a full 118-test run produces ~3 lines of output

### Django TestCase vs TransactionTestCase
- Django's `TestCase` wraps each test in an `atomic()` block for speed
- If a test triggers a **database-level error** (IntegrityError for duplicate PK, DataError for varchar overflow), PostgreSQL aborts the transaction
- After that, **no further DB queries work** in that test (you get `TransactionManagementError`)
- Workaround: don't query the DB after an expected DB error, or use `TransactionTestCase` instead
- The view's generic `except Exception` catches these errors and redirects, but the test's atomic block is already broken

### Stone Creation Modal (Frontend/Backend Contract)
- The stone creation form lives in `source/content/templates/main/new_add_stone_modal.html`
- It's a two-step modal: Step 1 (fill form) → Step 2 (preview QR) → submit
- **Critical**: `form.submit()` must happen BEFORE any `closeModal()` / `resetForm()` calls, because `resetForm()` clears all form fields
- The form field `PK_stone` maps to the Stone model's primary key (CharField, max 50, unique)
- The view (`main/views.py:add_stone`) checks `if not PK_stone` but does NOT strip whitespace - whitespace-only names currently slip through to the database (known limitation)

### Known Validation Gaps
- **Whitespace-only stone names**: The view checks `if not PK_stone` but `'   '` is truthy. The model has `validate_no_whitespace` but Django's `save()` doesn't call `full_clean()`. Whitespace names get saved.
- **Name length**: The model enforces `max_length=50` at the database level but the view doesn't pre-validate length - it relies on the DB constraint and the generic `except` block

### Bug-Driven Testing Policy
- **Every bug reported by the user must get a thorough regression test** before or alongside the fix
- Tests should be resilient: not break on simple refactors, but also not just test one narrow case
- Think through edge cases, boundary conditions, and related scenarios
- Test the behavior, not the implementation - if the form field name changes, the test should still validate the concept
- Include both the exact failing case and reasonable variations (empty string, whitespace, unicode, long names, etc.)

### Quality Sweep (February 2026)

#### Testing Infrastructure Cleanup
- **Deleted 2,700+ lines of dead backup test files**: `source/main/tests_backup_original.py` and `source/main/test_new_qr_system_backup.py` were deprecated backups never run by pytest - removed to reduce confusion
- **Consolidated pytest config**: `pytest.ini` (project root) is now the single source of truth. Removed conflicting `[tool.pytest.ini_options]` from `source/pyproject.toml` (coverage config sections retained there). The old pyproject.toml had `--cov` in addopts which ran coverage on every invocation.
- **Fixed `--disable-warnings`**: Replaced blanket warning suppression with targeted `-W ignore::DeprecationWarning` in pytest.ini so real warnings surface
- **Fixed double translation compilation**: `conftest.py` was compiling translations in `pytest_configure` AND `run_tests.py` compiled them too. Removed the conftest.py compilation. Translation compilation now only happens via `run_tests.py` or `make compile-translations`
- **conftest.py is now lean**: Only does path setup, Django init, and auto-marking tests as unit/integration by directory

#### CI/CD Pipeline Added
- **GitHub Actions workflow**: `.github/workflows/tests.yml` runs on push/PR to main
- Uses PostgreSQL 15 service container, Python 3.10, gettext for translations
- Runs `python run_tests.py` with coverage, uploads XML coverage artifact
- Has concurrency control to cancel stale in-flight runs

#### Documentation Consolidation
- **Translation docs merged**: `TRANSLATION_README.md` + `TRANSLATION_TESTING_SETUP.md` → single `TRANSLATION.md`. Fixed internal duplicate sections and formatting corruption in old files
- **DEPLOYMENT.md fixed**: Removed incorrect SQLite references (PostgreSQL is required everywhere), added content to empty "Testing the Deployment" section
- **Cleaned up redundant scripts**: Deleted `run_dev_postgres.sh` (was a strict subset of `run_dev.sh`)
- **Fixed broken cross-references**: README.md reference to nonexistent `NETLIFY_DEPLOYMENT.md` now points to `DEPLOYMENT.md`. Added legacy note to `build.sh` header.

#### Stone Creation Bug Fix
- **Bug**: "Missing stone name" error even when name was entered
- **Root cause**: `new_add_stone_modal.html` line 406 called `closeModal()` before `form.submit()`. `closeModal()` calls `resetForm()` which clears all form fields. The backend then received an empty `PK_stone`.
- **Fix**: Call `form.submit()` first, removed the premature `closeModal()` call
- **Regression tests**: 12 tests in `StoneNameSubmissionTests` covering valid names, empty/missing names, whitespace, unicode, boundary lengths, field integrity, hunted stones with location

#### Dev Environment Updates
- Email backend changed from `filebased` to `console` in development settings - emails now print directly to the terminal instead of being written to `source/content/tmp/emails/`
- Deleted `run_dev_postgres.sh` - was a redundant subset of `run_dev.sh`
- `run_tests.py` had hardcoded `main/tests.py` path - fixed to `main/tests/` (the tests directory)

#### Git Push & Pre-Push Hook
- The pre-push hook at `.git/hooks/pre-push` runs the full test suite (~3 min) before every push
- `git push` outputs progress/errors to **stderr** - if running in background, make sure to capture stderr with `2>&1`
- GitHub PAT needs the `workflow` scope to push `.github/workflows/` files - without it you get `remote rejected` with no obvious error unless stderr is captured

#### QR UUID Mismatch Bug Fix
- **Bug**: Scanning a freshly created stone's QR code showed "Invalid stone link"
- **Root cause**: The modal preview (step 2) generates a QR code using a JS-generated UUID. But when the form submits, `Stone(...)` creates with `default=uuid.uuid4` which generates a **different** UUID. The QR points to UUID-A, the DB has UUID-B.
- **Fix**: Added hidden `<input name="stone_uuid">` to the form, populated by JS when the preview UUID is generated. The `add_stone` view now reads `stone_uuid` from POST and passes it to `Stone(uuid=...)`. Falls back to auto-generation if UUID is missing or invalid.
- **Key lesson**: When frontend generates preview data (QR codes, links) before backend save, the identifiers MUST be passed through the form so they stay consistent

## Discourse Forum Integration (In Progress)

### Current Status
- **Django SSO endpoint**: COMPLETE - `source/accounts/discourse_sso.py` and `DiscourseSSOView` in `views.py`
- **Local Docker setup**: INCOMPLETE - base images work but Discourse dev image is empty

### What's Built
- `forum/docker-compose.yml` - Docker Compose with postgres:15-alpine, redis:7-alpine, discourse
- `forum/README.md` - Quick reference docs
- `run_dev.sh` - Helper commands: `discourse-start`, `discourse-stop`, `discourse-logs`, `discourse-reset`
- `idea_scratchpad.md` - Full architecture documentation and production deployment checklist

### The Problem
The `discourse/discourse_dev:release` image is a **base development image** - it doesn't come with Discourse pre-installed. The `/var/www/discourse` directory is empty. This image is meant for contributors who clone the Discourse source code and mount it.

### Next Steps (Pick One)
1. **Official launcher approach**: Clone `discourse_docker` into `forum/`, use `./launcher` tool (heavyweight but official)
2. **Remote VPS**: Skip local testing, spin up a $6/mo VPS for development testing
3. **Test in production**: Django SSO code is complete and tested - could deploy directly and test there

### Django Settings (Already Configured)
```python
# Development (source/app/conf/development/settings.py)
DISCOURSE_URL = 'http://localhost:4200'
DISCOURSE_SSO_SECRET = 'dev_secret_change_me'
DISCOURSE_SSO_ENABLED = True

# Production (source/app/conf/production/settings.py)
DISCOURSE_URL = 'https://forum.stonewalker.org'
DISCOURSE_SSO_SECRET = os.environ.get('DISCOURSE_SSO_SECRET', '')
DISCOURSE_SSO_ENABLED = bool(os.environ.get('DISCOURSE_SSO_SECRET'))
```

### Discourse SSO Config (Once Running)
In Discourse Admin → Settings → Login:
- `enable_discourse_connect` = true
- `discourse_connect_url` = `http://host.docker.internal:8000/accounts/discourse-sso/`
- `discourse_connect_secret` = `dev_secret_change_me`

## Sprint Session Learnings (February 2026)

### Test Infrastructure (Final Architecture)
- **pytest.ini**: `--tb=no -q --no-header` suppresses ALL default pytest output
- **conftest.py**: Custom plugin handles failure display with full tracebacks via `pytest_terminal_summary`. `pytest_report_teststatus` returns `report.outcome, "", ""` only for call phase (setup/teardown return None for default behavior). This gives correct test counts (145, not 435).
- **run_tests.py**: Fixed `compile_translations` → `compilemessages`. Added `--skip-translations` flag for fast agent runs. Supports subset running: `run_tests.py accounts`, `run_tests.py -m unit`, `run_tests.py -k pattern`.
- **Output**: `145 passed in 3:15` on all-pass. Full `FAIL: test_path::TestClass::test_name` + traceback on failure.
- **Key lesson**: Never use `--no-summary` - it suppresses the `pytest_terminal_summary` hook too.

### Multi-Agent Team Lessons (This Session)
- **Don't spawn agents before test infra works** - 4 Opus agents all running the 3-min test suite simultaneously is wasteful chaos
- **Fix foundation first** - test output, CI, then feature work
- **Agents CAN make independent commits** - each agent committed its own work cleanly
- **File conflict risk is real** - conftest.py was overwritten 3 times by different agents. Exclusive file ownership is critical.
- **`assertRedirects` follows redirect chains** - when testing `/a/ → /b/ → /c/`, use `assertEqual(status_code, 302)` + `assertIn(url)` to check just the first hop
- **Linters/hooks can revert changes** - pytest.ini kept getting `--tb=short` added back. Work WITH the linter, not against it.

### Completed This Session
1. N+1 query fix: StoneWalkerStartPageView O(N) → O(1) with select_related/prefetch_related
2. Shop flow reroute: /add_stone/ now redirects to /create-stone/ (shop pipeline)
3. Language bug: German locale broke JS floats (2.5 → 2,5), fixed with |unlocalize filter
4. Security: removed CSRF-exempt debug endpoint, added comment filtering, robots.txt, 5MB upload limit
5. CSS extraction: 600+ inline styles moved to styles.css
6. Image upload: client-side 800x800 validation + server-side PIL resize
7. Test infrastructure: silent pass, verbose fail, subset running
8. File cleanup: removed 23 obsolete files (5700 lines deleted)

### Performance Fixes Applied
- **select_related('FK_user', 'FK_user__profile')** on main page stone queries
- **Prefetch('moves', queryset=StoneMove.objects.order_by('timestamp').select_related('FK_user'))** eliminates N+1 for movement data
- **CSS extraction** enables browser caching (styles.css cached separately from HTML)
- **Image resize** prevents oversized uploads from hitting the server

## Business Strategy & Market Context

### Market Research (February 2026)
- **Geocaching**: 3.4M active caches, 3M+ players, ~124 employees at HQ. Premium subscription: $39.99/year or $6.99/month. Proves the "hide and find" model sustains a real business.
- **Stone painting community**: The Kindness Rocks Project operates in 90+ countries. Single-city Facebook groups reach 6,800+ members with 100-200 new joins/week. Massive, active, and completely unserved by tech.
- **The gap**: Nobody combines stone painting with digital tracking. Geocaching has tech but no art. Kindness Rocks has art but no tech. StoneWalker is the intersection.

### Shop Architecture
- **Config-driven**: Products defined in `source/main/shop_config.json`, loaded by `shop_utils.py` with caching
- **Current products**: Free single QR (loss leader) + 10-pack at $9.99
- **Expansion ready**: Adding new products requires only a JSON entry + Stripe price -- no code changes needed
- **Stripe integration**: Full checkout flow with webhook fulfillment in `stripe_service.py`
- **PDF generation**: Multi-pack QR codes delivered as printable PDFs via `pdf_service.py`

### Revenue Strategy
- Digital QR packs: ~95% margin (Stripe fees only)
- Physical products (kits, metal plaques): 50-75% margin
- Premium subscriptions: Recurring revenue anchor
- Education/group packs: High-value, low-volume
- Full strategy doc: `docs/BUSINESS_STRATEGY.md`

### Cost Structure
- Render.com hosting: ~$14/month (web + PostgreSQL)
- Email (Maileroo free tier): $0/month
- Domain: ~$12/year
- Break-even: ~$15/month (nearly immediate with any revenue)

## Launch Team Session (February 2026)

### Team Structure That Worked
- **3 Opus agents + 1 lead**: visionary (product/strategy), dev-alpha (frontend), dev-beta (backend)
- **Strict file ownership**: visionary owns docs/ + shop_config.json, dev-alpha owns templates/CSS/JS, dev-beta owns Python/locale/docs
- **Zero merge conflicts** across 21 commits from 4 contributors
- **Two rounds per agent**: Round 1 (main deliverable) → Round 2 (follow-up polish)
- **Visionary produced actionable strategy** that directly fed into code tasks (shop config expansion was zero-code)

### What Was Delivered (21 commits)
1. Business strategy & product roadmap (docs/BUSINESS_STRATEGY.md)
2. Shop expanded: 3-pack ($4.99) and 30-pack ($19.99) added via config-only change
3. My-Stones layout: full viewport height, responsive scaling
4. Profile menu: password autofill prevention, ARIA labels, image positioning
5. Hunted stone minimap: 4:3 Leaflet map with click-to-place, slim coordinates
6. Map marker CSS: removed Leaflet default backgrounds
7. Accessibility: ARIA labels, dialog roles, keyboard nav, aria-hidden on decorative elements
8. JS refactor: -103 lines dead code, documentation comments, deduplication, mobile scroll lock
9. Shop FAQ: 6 new entries covering all product tiers
10. About page: mission statement, "Join the Movement" CTAs
11. Open Graph + Twitter Card meta tags for social sharing
12. Self-hosted deployment guide + nginx/gunicorn/PostgreSQL/backup configs
13. SQL safety audit: clean (zero raw SQL in entire codebase)
14. README sitemap: updated with all current routes
15. Translations: 190+ strings, 94% coverage across 7 languages

### Self-Hosted Deployment (Ready)
- **Guide**: `docs/DEPLOYMENT_SELFHOSTED.md`
- **Config files**: `docs/deploy/nginx.conf`, `gunicorn.service`, `postgresql.conf.snippet`, `env.template`, `backup.sh`
- **Target**: Ubuntu 22.04+ VPS, 2-4GB RAM, PostgreSQL 15+
- **Stack**: nginx → gunicorn (Unix socket) → Django, Let's Encrypt SSL, pg_dump cron backups

### Shop Product Tiers (Current)
| Product | Price | Pack Size | Category |
|---------|-------|-----------|----------|
| Free Single QR | Free | 1 | starter |
| Starter 3-Pack | $4.99 | 3 | group |
| Explorer 10-Pack | $9.99 | 10 | group |
| Classroom 30-Pack | $19.99 | 30 | classroom |

### Translation Coverage
- European languages (de/fr/es/it): ~94% translated
- Russian: ~94%
- Chinese (zh-hans): ~88%
- All .mo files compiled and working
