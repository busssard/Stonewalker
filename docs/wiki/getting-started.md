---
title: Getting Started
tags: [setup, development, quickstart]
last-updated: 2026-02-10
---

# Getting Started

This guide walks you through setting up the StoneWalker development environment from scratch.

## Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **PostgreSQL 14+** (required -- SQLite is not supported)
- **gettext** (for translation compilation)
- **Git**

### Install Prerequisites (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip postgresql postgresql-contrib gettext
```

### Install Prerequisites (macOS)

```bash
brew install python postgresql gettext
brew link gettext --force
```

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd simple-django-login-and-register
```

## Step 2: Set Up PostgreSQL

Create a local database and user:

```bash
sudo -u postgres psql
```

```sql
CREATE USER stone_user WITH PASSWORD 'stone_pass';
CREATE DATABASE stone_dev OWNER stone_user;
GRANT ALL PRIVILEGES ON DATABASE stone_dev TO stone_user;
\q
```

Set the environment variable:

```bash
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
```

Add this to your `~/.bashrc` or `~/.zshrc` so it persists across sessions.

## Step 3: Set Up the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install additional dependencies needed for tests:

```bash
./venv/bin/pip install stripe reportlab tqdm
```

## Step 4: Apply Migrations

```bash
cd source
python manage.py migrate
```

## Step 5: Compile Translations

```bash
cd source
python manage.py compilemessages
```

## Step 6: Create a Superuser (Optional)

```bash
cd source
python manage.py createsuperuser
```

## Step 7: Run the Development Server

```bash
cd source
python manage.py runserver
```

Visit [http://localhost:8000/](http://localhost:8000/) to see the app.

## Convenience Script

Instead of steps 4-7, you can use the convenience script:

```bash
./run_dev.sh
```

This activates the venv, runs migrations, compiles translations, and starts the server.

## Running Tests

Always use the project's venv and the dedicated test runner:

```bash
./venv/bin/python run_tests.py
```

This compiles translations first, then runs the full pytest suite with a tqdm progress bar. Expect ~118 tests to pass.

See [[guides/write-tests]] for more on writing and running tests.

## Key Development Rules

1. **Always use the venv.** Never use system Python. Use `./venv/bin/python` or activate the venv first.
2. **PostgreSQL is required.** No SQLite, no exceptions.
3. **Compile translations** after editing any template with `{% trans %}` tags.
4. **Run the full test suite** before pushing (the pre-push hook does this automatically).

## Common Issues

### "ModuleNotFoundError: No module named 'stripe'"
Install missing packages:
```bash
./venv/bin/pip install stripe reportlab tqdm
```

### Database connection errors
Check that PostgreSQL is running and `DATABASE_URL` is set:
```bash
pg_isready
echo $DATABASE_URL
```

### Translation compilation errors
Make sure `gettext` is installed:
```bash
# Ubuntu/Debian
sudo apt install gettext

# macOS
brew install gettext && brew link gettext --force
```

## What's Next?

- Read [[architecture]] to understand the codebase structure
- Read [[intern-onboarding]] for a comprehensive walkthrough
- Check out the [[features/qr-system]] to understand the core product feature
- See the `CLAUDE.md` file in the project root for the complete developer reference

## Related Pages

- [[intern-onboarding]] -- Detailed onboarding for new team members
- [[architecture]] -- System architecture deep dive
- [[guides/write-tests]] -- Testing guide
