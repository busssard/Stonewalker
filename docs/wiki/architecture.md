---
title: System Architecture
tags: [architecture, models, views, django]
last-updated: 2026-02-10
---

# System Architecture

StoneWalker is a Django monolith with two main apps, a shared content directory, and separate settings for development and production.

## Django Applications

### `accounts/` -- User Authentication & Profiles
Handles everything related to user identity:
- Registration with email activation
- Login/logout (supports username, email, or both)
- Password reset via email
- Profile editing (username, email, password, profile picture) via modal overlay
- Email change with re-verification
- Discourse SSO integration (DiscourseConnect)
- Username availability API

**Key files:**
- `source/accounts/views.py` -- All auth views (class-based)
- `source/accounts/models.py` -- `Profile`, `Activation`, `EmailAddressState`, `EmailChangeAttempt`
- `source/accounts/forms.py` -- Login, signup, profile forms
- `source/accounts/urls.py` -- URL routing under `/accounts/`
- `source/accounts/discourse_sso.py` -- Discourse SSO payload handling
- `source/accounts/utils.py` -- Email sending utilities

### `main/` -- Core Stone Tracking
The heart of the application:
- Stone creation, editing, publishing, and send-off workflow
- QR code generation and download
- Stone scanning with cooldown enforcement
- Interactive map with stone visualization
- Shop for purchasing QR code packs
- Stone claiming (for shop-purchased QR codes)
- Language change page

**Key files:**
- `source/main/views.py` -- Stone views, scanning, QR API, map
- `source/main/shop_views.py` -- Shop, checkout, claiming, PDF download
- `source/main/models.py` -- `Stone`, `StoneMove`, `StoneScanAttempt`, `QRPack`
- `source/main/qr_service.py` -- QR code generation service
- `source/main/stripe_service.py` -- Stripe payment integration
- `source/main/pdf_service.py` -- PDF generation for QR packs
- `source/main/shop_utils.py` -- Product config and pricing utilities
- `source/main/translation_tests.py` -- Translation quality assurance tests

### `app/` -- Project Configuration
Django project settings and URL routing:
- `source/app/urls.py` -- Root URL configuration
- `source/app/conf/development/settings.py` -- Dev settings (console email, relaxed SSL)
- `source/app/conf/production/settings.py` -- Production settings (Maileroo, SSL required)

## Data Models

### Core Models (in `main/models.py`)

#### Stone
The central entity. Each stone represents a painted stone tracked by the app.

| Field | Type | Notes |
|-------|------|-------|
| `PK_stone` | CharField(50) | Primary key, unique, no whitespace |
| `uuid` | UUIDField | Auto-generated, used in QR URLs |
| `description` | TextField(500) | Optional |
| `FK_user` | ForeignKey(User) | Creator, nullable for unclaimed stones |
| `FK_pack` | ForeignKey(QRPack) | Shop pack this stone belongs to |
| `image` | ImageField | Optional stone photo |
| `color` | CharField(7) | Hex color code, default `#4CAF50` |
| `shape` | CharField(20) | `circle` (hidden) or `triangle` (hunted) |
| `stone_type` | CharField(20) | `hidden` or `hunted` |
| `status` | CharField(20) | `unclaimed`, `draft`, `published`, `sent_off` |
| `distance_km` | FloatField | Total distance traveled |
| `qr_code_url` | URLField | Persistent production QR URL |
| `sent_off_at` | DateTimeField | When stone was sent off |
| `claimed_at` | DateTimeField | When stone was claimed from shop |

**Status lifecycle:** `unclaimed` -> `draft` -> `published` -> `sent_off`

#### StoneMove
Records each time someone finds/scans a stone and logs its new location.

| Field | Type | Notes |
|-------|------|-------|
| `FK_stone` | ForeignKey(Stone) | Which stone was moved |
| `FK_user` | ForeignKey(User) | Who moved it |
| `image` | ImageField | Optional photo |
| `comment` | TextField | Optional comment |
| `latitude` | FloatField | New latitude |
| `longitude` | FloatField | New longitude |
| `timestamp` | DateTimeField | Auto-set on creation |

#### StoneScanAttempt
Enforces the one-week cooldown between scans of the same stone by the same user.

| Field | Type | Notes |
|-------|------|-------|
| `FK_stone` | ForeignKey(Stone) | |
| `FK_user` | ForeignKey(User) | |
| `scan_time` | DateTimeField | Auto-set |
| `ip_address` | GenericIPAddressField | From request |
| `user_agent` | TextField | From request |

Has `unique_together = ['FK_stone', 'FK_user']` and a compound index.

#### QRPack
Tracks purchased QR code packs from the shop.

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUIDField | Primary key |
| `FK_user` | ForeignKey(User) | Purchaser |
| `pack_type` | CharField(20) | `free_single` or `paid_10pack` |
| `status` | CharField(20) | `pending`, `paid`, `fulfilled`, `failed` |
| `stripe_payment_intent_id` | CharField(255) | Stripe reference |
| `price_cents` | IntegerField | Price in cents |
| `pdf_generated` | BooleanField | Whether PDF has been created |
| `download_count` | IntegerField | Times downloaded |

### Account Models (in `accounts/models.py`)

#### Profile
One-to-one extension of Django's User model.

| Field | Type | Notes |
|-------|------|-------|
| `user` | OneToOneField(User) | |
| `profile_picture` | ImageField | Optional, upload to `profile_pics/` |

Auto-created via `post_save` signal on User.

#### Activation
Used for email verification during signup and email changes.

#### EmailAddressState
Tracks the current/pending email state for a user. Supports rollback if email change is cancelled.

#### EmailChangeAttempt
Rate-limiting model: max 3 email change attempts per 15 minutes.

## Model Relationships

```
User <1----1> Profile
User <1----1> EmailAddressState
User <1----*> Stone
User <1----*> StoneMove
User <1----*> StoneScanAttempt
User <1----*> QRPack
User <1----*> Activation
User <1----*> EmailChangeAttempt
Stone <1----*> StoneMove
Stone <1----*> StoneScanAttempt
QRPack <1----*> Stone
```

## Settings Configuration

Settings are split by environment, controlled by the `IS_PRODUCTION` env var:

| Setting | Development | Production |
|---------|-------------|------------|
| Email backend | Console (prints to terminal) | Maileroo |
| SSL mode | `prefer` | `require` |
| Debug | `True` | `False` |
| Static files | Django dev server | WhiteNoise |
| Database | PostgreSQL (local) | PostgreSQL (remote, SSL) |

Both environments require `DATABASE_URL` to be set.

## URL Structure

URLs are split into two groups in `source/app/urls.py`:

**Non-prefixed (no language prefix):**
- `/admin/` -- Django admin
- `/api/generate-qr/` -- QR generation API
- `/api/download-enhanced-qr/` -- Enhanced QR download
- `/api/check-stone-uuid/<uuid>/` -- UUID validation
- `/api/check_stone_name/` -- Stone name availability
- `/webhooks/stripe/` -- Stripe webhook

**Language-prefixed (via `i18n_patterns`):**
- `/` and `/stonewalker/` -- Main map/dashboard
- `/my-stones/` -- User's stones
- `/add_stone/` -- Create stone (POST)
- `/stonescan/` -- Scan a stone
- `/shop/` -- QR shop
- `/stone/<pk>/edit/` -- Edit stone
- `/stone/<pk>/qr/` -- Download QR
- `/stone/<pk>/send-off/` -- Send off stone
- `/stone-link/<uuid>/` -- Stone found page (from QR scan)
- `/claim-stone/<uuid>/` -- Claim an unclaimed stone
- `/accounts/` -- All auth URLs
- `/language/` -- Change language
- `/about/`, `/forum/` -- Static pages

See the full site map in `README.md` for the complete list.

## Template Structure

```
source/content/templates/
  layouts/default/
    page.html          -- Base layout (header, footer, modal containers)
    nav_links.html     -- Navigation links (shared between header and burger menu)
  main/
    stonewalker_start.html   -- Main map/dashboard page
    my_stones.html           -- User's personal stones
    stone_scan.html          -- Scan stone form
    stone_edit.html          -- Edit stone form
    stone_found.html         -- Stone found page (from QR scan)
    shop.html                -- QR shop
    claim_stone.html         -- Claim an unclaimed stone
    checkout_success.html    -- Post-purchase page
    new_add_stone_modal.html -- Stone creation modal (2-step)
    shared_modals.html       -- Shared modal templates
    change_language.html     -- Language selector
    about.html, forum.html   -- Static pages
    debug_modals.html        -- Debug/test page
    qr_test.html             -- QR scanner test page

source/accounts/templates/accounts/
    log_in.html              -- Login page
    sign_up.html             -- Registration (modal-style popup)
    profile/change_profile.html -- Profile editing
    restore_password*.html   -- Password reset flow
    resend_activation_code.html
    log_out*.html
    emails/                  -- Email templates (activation, password reset, etc.)
```

## Static Assets

```
source/content/assets/
  css/styles.css       -- Main stylesheet (200+ utility classes)
  js/header.js         -- Header, burger menu, responsive breakpoints
  js/sync-breakpoints.js -- Syncs JS breakpoints to CSS media queries
  fonts/               -- Local GiantBoom font
  images/              -- Static images
```

## File Upload Locations

```
source/content/media/
  stones/         -- Stone photos
  stonemoves/     -- Scan/move photos
  profile_pics/   -- Profile pictures
  qr_codes/       -- Generated QR code images
  qr_packs/       -- Generated PDF packs
```

## Related Pages

- [[getting-started]] -- How to set up the development environment
- [[api]] -- Full API endpoint reference
- [[features/shop]] -- Shop architecture details
- [[features/qr-system]] -- QR code system details
