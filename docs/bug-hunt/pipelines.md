# Pipelines: CI, deploy, static, translations, QR/PDF, email

Snapshot 2026-09-26 (base `2b6a940`). Summarised from the files themselves, not copied. `⚠` marks a fragility.

## 1. Tests

**Runner: `run_tests.py`** (repo root)
- Runs `manage.py compilemessages` in `source/`. ⚠ A failure only prints a warning.
- Then runs `python -m pytest` with `cwd=source`, `DJANGO_SETTINGS_MODULE=app.settings` and `IS_PRODUCTION=false`, so the **development settings** are always used.
- `--skip-translations` skips the compile step.
- ⚠ **If no path argument is given, it appends `accounts/tests.py main/tests/`.** The following match `pytest.ini`'s `python_files` but are never run by `run_tests.py`, CI or the pre-push hook: `accounts/test_email_templates.py`, `accounts/test_social_terms.py`, `main/translation_tests.py`. Run them explicitly or fix the defaults.
- Flags such as `--cov=...` start with `-`, so they don't count as paths and the defaults still apply.

**`pytest.ini`** (root): `testpaths=source`, `--reuse-db --nomigrations --tb=short -q --strict-markers`. `conftest.py` auto-applies the unit/integration markers.
- ⚠ With `--nomigrations`, **migrations are never exercised** in any test run, and nothing runs `makemigrations --check`. A model change without a migration passes CI and then breaks on `migrate` during deploy, or at runtime.
- `--reuse-db` means a stale test DB after a schema change needs `--create-db` (see CLAUDE.md).

**Pre-push hook**: `.git/hooks/pre-push`. It activates `venv` and runs `python run_tests.py accounts/tests.py main/tests/`, aborting the push on failure.
- ⚠ It is **not versioned** (lives only in `.git/hooks`), so other clones don't have it. `docs/wiki/getting-started.md` implies everyone does.
- Same subset as CI, with the same blind spots.

**CI: `.github/workflows/tests.yml`**. Triggers: push/PR to `main`, plus `workflow_call` (used by the deploy workflow). A `concurrency` block cancels superseded runs.
- **lint** job: `ruff check --exit-zero` and `ruff format --check || true`. ⚠ It **never fails**, so it's informational only.
- **test** job: Postgres 15 service container, Python 3.10, apt `gettext libpq-dev`, `pip install -r requirements.txt`, a psycopg2 connectivity probe, then `python run_tests.py --cov=app --cov=accounts --cov=main --cov-report=term`.
- ⚠ The upload step looks for `source/coverage.xml`, but only `term` is requested, so the artifact is always missing (`if-no-files-found: ignore` hides this).
- ⚠ CI only runs development settings. `CompressedManifestStaticFilesStorage` (a missing `{% static %}` file becomes a 500 on prod), `SECURE_SSL_REDIRECT`/cookie flags and `MailerooEmailBackend` are never exercised. `CLAUDE.md`'s "production-ready, comprehensive testing" claim overstates this.
- A push to `main` runs the suite **twice**: once from `tests.yml` directly, once through `deploy.yml`.

## 2. Deploy

**`.github/workflows/deploy.yml`**: on push to `main`, a `test` job reuses `tests.yml`. On success, a `deploy` job runs `appleboy/ssh-action@v1` with secrets `DEPLOY_HOST`, `DEPLOY_USER` and `DEPLOY_SSH_KEY`, and executes `/opt/stonewalker/deploy.sh` on the server. `concurrency: deploy` (no cancel).

**`docs/deploy/deploy.sh`** (`set -euo pipefail`) does:
1. Loads `.env`.
2. `git fetch` + `git reset --hard origin/main`.
3. `pip install -r requirements.txt`.
4. `migrate --noinput`.
5. `compilemessages` (failure only logged).
6. `collectstatic --noinput --clear`.
7. `sudo systemctl reload stonewalker` (HUP → graceful gunicorn reload; needs a sudoers entry, see guide §15).

Fragilities:
- ⚠ `export $(grep -v '^#' .env | xargs)` breaks on values containing spaces, quotes, `#` or `$`. The copy embedded in `docs/DEPLOYMENT_SELFHOSTED.md` §15 differs slightly (it also filters blank lines), so the two can drift. gunicorn itself reads `.env` via systemd `EnvironmentFile`, which parses differently from this shell export.
- ⚠ There is no rollback and no health check after reload. Migrations run before collectstatic and reload, so if a later step fails, the new schema runs against the old code.
- ⚠ `git reset --hard` throws away any hotfix made on the server.
- **Server layout**:
  - nginx serves `/static/` → `source/content/static/` and `/media/` → `source/content/media/` (no autoindex), and proxies `/` to the unix socket (`docs/deploy/nginx.conf`).
  - gunicorn runs 5 workers, `--timeout 120`, `--max-requests 1000` (`docs/deploy/gunicorn.service`).
- **Backups**: `docs/deploy/backup.sh` via cron at 03:00. Makes a custom-format dump, a gzipped plain SQL dump and a media tarball, keeping 14 days. ⚠ Everything stays **on the same server**; there's no off-site copy.
- ⚠ **`manage.py cleanup_unconfirmed` is not scheduled anywhere** (no cron in the guide). Its `--dry-run` deletes images (flows.md NEW-6).
- `docs/DEPLOYMENT_SELFHOSTED.md` is a top-to-bottom VPS guide (DNS, apt, Postgres tuning, venv, `.env`, gunicorn, nginx, certbot, ufw, backups, Maileroo, Stripe webhook, Discourse in docker, logrotate, auto-deploy, monitoring, and migrating from Render). ⚠ In §4 it says "leave [Maileroo] blank to disable email". In reality the backend raises without a key, `send_mail` returns False, and **`SignUpView` deletes every new signup**. An empty `STRIPE_WEBHOOK_SECRET` means unsigned webhooks are accepted (F11).
- ⚠ The prod `ALLOWED_HOSTS` fallback (when the env var is unset) includes `.onrender.com` and `.netlify.app`. Combined with `build_absolute_uri()` in email links, that would allow host-header poisoning of reset links. `env.template` sets the variable correctly.
- `postgres_production.json` / `./db` point at the old Aiven host (F20).

## 3. Static files

- **Source of truth: `source/content/assets/`** (`STATICFILES_DIRS`). **`source/content/static/`** is `STATIC_ROOT`, the collectstatic output.
- Prod uses `CompressedManifestStaticFilesStorage` (WhiteNoise), which produces hashed names, `.gz` and `.br` files. Dev uses the default storage, so no hashing.
- ⚠ **`content/static/` is tracked in git (1062 files)** even though it's a build artifact. Deploy runs `collectstatic --clear` on top of the checkout, so the tracked copy only adds noise and a risk of stale-file confusion.
- ⚠ The untracked `content/static/js/{common-passwords,form-validation,image-upload}.js` are local collectstatic output of new assets (unhashed, dev storage). **Don't commit or edit them.** Edit `content/assets/js/` instead.
- ⚠ `CLAUDE.md` gotcha #12 ("header.js has two copies, change both") is misleading. The `static/` copy is overwritten on every collectstatic.
- `STATICFILES_STORAGE` is deprecated in Django 4.2 in favour of `STORAGES`; it's removed in 5.1.

## 4. Translations

- There are 7 languages: `content/locale/<lang>/LC_MESSAGES/django.po`, with URL prefixes as described in sitemap.md.
- `.mo` files are compiled by `run_tests.py`, by `deploy.sh`, and by `manage.py compile_translations` (a custom wrapper, and the target of `make compile-translations`).
- ⚠ `.gitignore` has `*.mo`, yet 3 of the 7 `.mo` files are tracked (es, fr, ru). If `compilemessages` fails silently (for example, gettext is missing), those three serve **stale** translations and the other four serve none. Neither CI nor deploy fails.
- There is also clutter: `django.po.backup*` and `django_content.mo`.
- `make translations` and `make install` reference `po_to_excel.py` and `translation_requirements.txt` at the repo root. ⚠ Both actually live in `scripts/translation/`, so those Makefile targets are broken.

## 5. QR images (`main/qr_service.py`)

- **The URL is always `https://stonewalker.org/stone-link/<stone_number>/?key=<uuid>`** (`Stone.get_qr_url()`, which writes `qr_code_url` to the DB as a side effect). The UUID is the only secret.
- **`generate_qr_for_stone`** runs on every mint and every claim. It makes a PIL PNG (M error-correction level, 3:4 with the URL text) and saves it to `media/qr_codes/{PK_stone}_{uuid}.png`.
  - ⚠ Downloads never use this file.
  - ⚠ It is orphaned on claim (the PK rename changes the filename).
  - ⚠ nginx serves it publicly with the key in the name.
  - ⚠ Before the F10 fix, a PK containing `/` or `..` flowed straight into the file path.
- **`create_download_response` / `generate_enhanced_qr_for_download`** generate an in-memory label (H error-correction level, "STONEWALKER.org" + "Stone #N") for `/stone/<pk>/qr/`, `/shop/download-qr/<n>/`, free single codes, and `/api/download-enhanced-qr/`. Fonts are DejaVu, falling back to PIL's default.
- `/api/generate-qr/` (`views.py` `generate_qr_code_api`) is a separate, older inline PIL implementation that duplicates `qr_service`. It is unauthenticated.

## 6. Pack PDF (`main/pdf_service.py`)

- ReportLab A4 page grid of 30×30 mm QR labels (H error-correction level), each with "STONEWALKER.org" and `#<n>` in a dashed rounded cut box. There's a title image rendered from `fonts/GiantBoomDEMO`, falling back if the font is missing.
- Written to `media/qr_packs/<pack.id>.pdf` and served through `FileResponse`.
- Callers:
  - Free multi-packs: `_handle_free_product`.
  - Webhook fulfilment: `_fulfill_pack`, only if `pack_size > 1`.
  - The success-page fallback.
  - `DownloadPackPDFView`, which regenerates on **every** download.
- ⚠ The PDF is always English; `QRPack.language` is unused.

## 7. Certificate PDF (`main/certificate_service.py`)

- ReportLab A4 with border, header, the stone image from `stone.image`, name, `Stone #N`, details, and a QR code. Wandering stones only, owner only (`StoneCertificateView`), generated in memory.
- ⚠ It prints the **full keyed URL** as text and as a QR code (`certificate_service.py:206,236`). A shared certificate leaks the key.

## 8. Email

- Prod: `app.backends.MailerooEmailBackend`, calling the REST v2 API through stdlib `urllib` with the `MAILEROO_API_KEY` env var. Dev: the console backend.
- `accounts/utils.send_mail()` renders `accounts/emails/<t>.html` + `.txt` and returns True/False.
- Callers:
  - activation (signup)
  - change-email
  - find confirmation
  - code-claimed
  - reset password
  - forgotten username
  - `main/signals.notify_stone_owner_on_move`: owner notification on every new `StoneMove`, including held ones (F15); it has its own `EmailMultiAlternatives`.
- ⚠ Everything is **synchronous inside the request**, and `urlopen` has **no timeout** (`app/backends.py:106`). A slow Maileroo stalls a worker for up to gunicorn's 120 s.
- ⚠ Failures are handled inconsistently:
  - Signup deletes the user.
  - Resend deletes the activation.
  - Find confirmation and reset/username emails ignore the result.
  - The signal logs it.
- Subjects are lazy translations resolved via `force_str`, in whatever language the request happens to be in. The owner-notification signal's subject is a hardcoded English f-string.
