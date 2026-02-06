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
- **Development**: `source/app/conf/development/settings.py` (uses file-based email, relaxed SSL)
- **Production**: `source/app/conf/production/settings.py` (requires PostgreSQL, Mailjet email, SSL)
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
- **Unit tests**: `accounts` app (marked with `@pytest.mark.unit`)
- **Integration tests**: `main` app (marked with `@pytest.mark.integration`)
- **Translation QA**: Automated validation of PO files and functionality
- **Pre-push hook**: Automatic test running before git push

### Coverage Areas
- User authentication and profile management
- Stone creation, scanning, QR code generation
- Translation compilation and functionality
- API endpoints and permissions
- CSS utility classes and responsive design

### Test Runner Features
- Automatic translation compilation before tests
- Django settings isolation (uses development config)
- Pytest with custom markers and configuration
- Coverage reporting with HTML output

## Security & Performance

### Security Features
- CSRF protection on all forms
- File upload validation for images
- User authentication required for stone operations
- Cooldown enforcement prevents spam scanning
- SSL required in production

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

1. **PostgreSQL is required** - SQLite not supported
2. **Translation compilation** - Must run `compilemessages` before production deploy
3. **Environment variables** - `DATABASE_URL` and `SECRET_KEY` required for production
4. **QR code permissions** - Media directory must be writable
5. **Email backend** - Development uses file-based, production uses Mailjet
6. **Static files** - Run `collectstatic` before production deployment

## File Structure Key Points

- **Templates**: `source/content/templates/` (shared layouts in `layouts/default/`)
- **Static assets**: `source/content/assets/` (CSS, JS, images)
- **Media uploads**: `source/content/media/` (profile pics, QR codes)
- **Translations**: `source/content/locale/` (PO/MO files)
- **Database scripts**: Root level `db` script for production management
- **Build scripts**: `build.sh`, `run_dev.sh` convenience scripts

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

### Git Commit Strategy
- **Always create multiple commits** - separate features/changes logically rather than one large commit
- Group related changes together (e.g., one commit for Stripe integration, another for PDF generation)
- Write clear, descriptive commit messages

### Claude Code Session Notes
- Regularly update this CLAUDE.md file with new learnings and preferences
- Document any new patterns or conventions discovered during development

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
- Run `pip3 install stripe reportlab` if tests fail with ModuleNotFoundError

### Test Output Convention
- **Minimal output**: pytest is configured with `-q --tb=line --no-header` so passing tests show only `.` and the context stays brief
- **Failure format**: Failures print `TEST_FAIL: [test_name] - [failure message]` via the conftest.py `pytest_terminal_summary` hook
- **Always run tests this way** - do not add `-v` or `--tb=short` unless actively debugging a specific failure
- This keeps Claude Code context lean when running test suites

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

#### Team Workflow Notes
- When spawning agent teams, assign non-overlapping file sets to avoid merge conflicts
- Documentation-only agents should never touch test files and vice versa
- CLAUDE.md updates should be done by the team lead after all agents finish to avoid conflicts
- Creative agents are great for CI/CD and holistic review tasks where fresh eyes add value