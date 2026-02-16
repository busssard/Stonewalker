# StoneWalker Developer Wiki

> **THE onboarding document for new developers**. Everything you need to understand, run, test, and contribute to StoneWalker.

**Last updated:** February 2026
**Target audience:** Developers, interns, contributors who know Django basics but have never seen this codebase

---

## Table of Contents

1. [Welcome & Project Overview](#welcome--project-overview)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Project Architecture](#project-architecture)
4. [Core Features (How They Work)](#core-features-how-they-work)
5. [Database Schema](#database-schema)
6. [URL Map](#url-map)
7. [Frontend Architecture](#frontend-architecture)
8. [Testing](#testing)
9. [Translation System](#translation-system)
10. [Deployment](#deployment)
11. [Business Context](#business-context)
12. [Common Tasks (How-To Guide)](#common-tasks-how-to-guide)
13. [Troubleshooting](#troubleshooting)

---

## Welcome & Project Overview

### What is StoneWalker?

StoneWalker is a Django-based web application that combines **geocaching**, **painted rock art**, and **global tracking** into one unique experience. Users paint stones, attach QR codes, hide them in the world, and watch as others find and move them — all tracked on an interactive world map.

**Think of it as:** Geocaching meets rock painting meets Instagram for stones.

**The gap we fill:** The rock painting community is massive (millions of participants via The Kindness Rocks Project, Facebook groups with 6,800+ members), but it has zero digital infrastructure. Geocaching has the tech but no creative art component. StoneWalker sits at the exact intersection.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.8+, Django 4.2 |
| **Database** | PostgreSQL (required for both dev and prod) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Map** | Leaflet.js |
| **Payments** | Stripe (Checkout + Subscriptions + Webhooks) |
| **Email** | Maileroo (transactional emails) |
| **File Storage** | Django FileField (profile pics, stone images, QR codes) |
| **Testing** | pytest + Django TestCase |
| **Translation** | Django i18n (7 languages: en, ru, zh-hans, fr, es, de, it) |
| **Deployment** | Render.com (recommended) or self-hosted VPS |

### Key Concepts

- **Stones:** Painted rocks tracked on the map. Each has a unique UUID, QR code, name, creator, and journey history.
- **Stone Types:**
  - **Hidden:** Created by a user and hidden somewhere in the world.
  - **Hunted:** Created with a known location for others to find (treasure hunt style).
- **QR Codes:** Each stone gets a unique QR code linking to `/stone-link/<uuid>/`. Scanning starts the "found" flow.
- **Moves:** When someone finds a stone, they log a "move" — a new location + optional photo + comment.
- **Premium Supporter Tier:** Monthly ($3.99) or yearly ($29.99) subscription via Stripe. Unlocks analytics, unlimited drafts, priority features.
- **Shop:** QR code packs (free single, paid 3/10/30-packs) for purchase. PDFs generated, stones pre-created as "unclaimed" until the user claims them.
- **Unclaimed Stones:** Pre-generated stones from shop purchases. Status = `unclaimed`, no owner. Users claim them via `/claim-stone/<uuid>/`.

---

## Quick Start (5 Minutes)

### Prerequisites

- **Python 3.8+**
- **PostgreSQL** (SQLite NOT supported)
- **Node.js** (optional, only if you need to rebuild frontend assets)
- **gettext** (for translations: `brew install gettext` on macOS, `apt install gettext` on Linux)

### Clone & Setup

```bash
# 1. Clone
git clone https://github.com/busssard/Stonewalker.git
cd Stonewalker

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up PostgreSQL
# Create a database and user, then set DATABASE_URL
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"

# 5. Run migrations
cd source
python manage.py migrate

# 6. Compile translations
python manage.py compilemessages

# 7. Create superuser
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

**Or use the convenience script:**

```bash
./run_dev.sh
```

### Verify It Works

Visit `http://localhost:8000/stonewalker/` — you should see the main map page.

Log in with your superuser account and explore:
- `/my-stones/` — your personal stone dashboard
- `/create-stone/` — smart router (redirects to shop if no unclaimed QR, otherwise to claim flow)
- `/admin/` — Django admin panel

---

## Project Architecture

### Directory Structure

```
simple-django-login-and-register/
├── source/                     # Django project root
│   ├── accounts/               # User authentication & profiles
│   │   ├── models.py           # User, Profile, Activation, Subscription, etc.
│   │   ├── views.py            # Login, signup, profile editing, Discourse SSO
│   │   ├── tests.py            # Account tests (15 tests)
│   │   └── templates/          # Login, signup, profile templates
│   ├── main/                   # Core stone tracking app
│   │   ├── models.py           # Stone, StoneMove, StoneScanAttempt, QRPack
│   │   ├── views.py            # Main views (map, my-stones, stone scan, etc.)
│   │   ├── shop_views.py       # Shop checkout, claim stone, download PDFs
│   │   ├── premium_views.py    # Premium landing, checkout, manage, billing portal
│   │   ├── stripe_service.py   # Stripe integration (checkout, webhooks, subscriptions)
│   │   ├── qr_service.py       # QR code generation
│   │   ├── pdf_service.py      # PDF generation for QR packs
│   │   ├── certificate_service.py # Stone certificate PDF
│   │   ├── shop_utils.py       # Load shop_config.json, caching
│   │   ├── shop_config.json    # Product catalog (digital QR packs, subscriptions)
│   │   ├── tests/              # Main tests (224 tests across 12 files)
│   │   │   ├── base.py         # Shared test base classes
│   │   │   ├── test_models.py
│   │   │   ├── test_qr_system.py
│   │   │   ├── test_stone_scanning.py
│   │   │   ├── test_stone_workflow.py
│   │   │   ├── test_premium.py # Premium subscription tests (40 tests)
│   │   │   └── ... (8 more test files)
│   │   └── translation_tests.py # Translation QA tests
│   ├── app/                    # Project configuration
│   │   ├── conf/
│   │   │   ├── development/    # Dev settings (console email, relaxed SSL)
│   │   │   │   └── settings.py
│   │   │   └── production/     # Prod settings (Maileroo, SSL required)
│   │   │       └── settings.py
│   │   ├── urls.py             # Main URL configuration
│   │   ├── wsgi.py             # WSGI entry point
│   │   ├── context_processors.py # Shop visibility, premium status
│   │   └── backends.py         # Maileroo email backend
│   ├── content/                # Static assets, templates, media
│   │   ├── assets/
│   │   │   ├── css/styles.css  # Main CSS (200+ utility classes)
│   │   │   ├── js/header.js    # Burger menu, dark mode, breakpoints
│   │   │   └── js/image-upload.js # Client-side image validation
│   │   ├── templates/
│   │   │   ├── layouts/default/
│   │   │   │   ├── page.html   # Base template (header, nav, modals)
│   │   │   │   └── nav_links.html # Centralized navigation
│   │   │   ├── main/           # Main app templates (19 files)
│   │   │   └── accounts/       # Account templates
│   │   ├── locale/             # Translation files (7 languages)
│   │   │   ├── de/LC_MESSAGES/
│   │   │   ├── en/LC_MESSAGES/
│   │   │   └── ... (5 more)
│   │   ├── media/              # User uploads (stones, profile pics, QR codes)
│   │   └── static/             # Collected static files (production)
│   └── manage.py
├── docs/                       # Documentation
│   ├── WIKI.md                 # This file
│   ├── README.md               # Main README
│   ├── CLAUDE.md               # Development notes for Claude Code
│   ├── DEPLOYMENT.md           # Render.com deployment guide
│   ├── DEPLOYMENT_SELFHOSTED.md # VPS deployment guide
│   ├── TRANSLATION.md          # Translation management
│   └── BUSINESS_STRATEGY.md    # Business context & roadmap
├── .claude/                    # Claude Code workspace
│   └── tasks.md                # Task tracking
├── run_tests.py                # Test runner (compiles translations first)
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Pytest plugin (auto-marks, silent pass, verbose fail)
├── run_dev.sh                  # Development convenience script
├── requirements.txt            # Python dependencies
└── .git/hooks/pre-push         # Runs full test suite before push

```

### Django Apps

| App | Purpose | Key Models |
|-----|---------|------------|
| **accounts** | User authentication, profiles, email activation, Discourse SSO | User (Django), Profile, Activation, EmailAddressState, Subscription |
| **main** | Stone tracking, QR codes, map, shop, premium | Stone, StoneMove, StoneScanAttempt, QRPack |
| **app** | Project configuration, URL routing, context processors | N/A |

### Settings Configuration

The project uses **environment-based settings**:

- **Development:** `source/app/conf/development/settings.py`
- **Production:** `source/app/conf/production/settings.py`

Settings are selected via the `IS_PRODUCTION` environment variable:
- Unset/False → development
- True → production

**Key differences:**

| Setting | Development | Production |
|---------|-------------|------------|
| Email backend | Console (prints to terminal) | Maileroo SMTP |
| SSL/HTTPS | Optional | Required |
| Database SSL | `sslmode=prefer` | `sslmode=require` |
| Static files | Django dev server | WhiteNoise |
| Debug | True | False |

### Template Hierarchy

```
layouts/default/page.html (base template)
  ├── Header (logo, nav, burger menu, dark mode toggle)
  ├── Profile modal overlay
  └── {% block content %}
       └── Child templates inherit and override this
```

**Child templates:**
- `main/stonewalker_start.html` — Main map page
- `main/my_stones.html` — User's stones dashboard
- `main/shop.html` — Shop page
- `main/premium.html` — Premium landing page
- `accounts/log_in.html`, `sign_up.html`, etc.

**Shared components:**
- `layouts/default/nav_links.html` — Centralized navigation (used in both main nav and burger menu)
- `main/shared_modals.html` — Shared modal templates (stone scan, QR scanner)

### Static Files vs Media Files

| Type | Location | Purpose | Served by |
|------|----------|---------|-----------|
| **Static** | `source/content/assets/` (dev)<br>`source/content/static/` (prod) | CSS, JS, fonts, images, favicon | Django dev server (dev)<br>WhiteNoise (prod) |
| **Media** | `source/content/media/` | User uploads: profile pics, stone images, QR codes | Django (dev)<br>nginx (prod self-hosted) |

---

## Core Features (How They Work)

### Authentication & Profiles

**Files involved:**
- `accounts/models.py` — User, Profile, Activation
- `accounts/views.py` — Login, signup, profile editing, password reset
- `accounts/templates/` — All auth templates

**Flow:**

1. **Registration (`/accounts/sign-up/`):**
   - User fills form (username, email, password)
   - Creates User and Profile (via post_save signal)
   - Generates Activation code
   - Sends activation email
   - User clicks link → account activated

2. **Login (`/accounts/log-in/`):**
   - Username/email + password
   - Django session created
   - Redirects to main map

3. **Profile Editing (`/accounts/change/profile/`):**
   - Modal or full-page form
   - Edit username, email, password, profile picture, social links
   - Email change triggers new activation flow

4. **Profile Picture:**
   - Uploaded to `source/content/media/profile_pics/`
   - Client-side validation: max 800x800px, 5MB
   - Server-side resize if oversized
   - Fallback: `static/user_picture.png`

**Social Links:**
- Facebook URL, Instagram handle, Twitter handle, Mastodon handle, TikTok handle
- Used for stone sharing (e.g., "Check out this stone by @username!")

---

### Stones & QR Codes

**Files involved:**
- `main/models.py` — Stone, StoneMove, StoneScanAttempt, QRPack
- `main/views.py` — add_stone, StoneScanView, StoneLinkView, StoneEditView
- `main/qr_service.py` — QR code generation
- `main/shop_views.py` — Shop, claim flow
- `main/templates/main/` — stone_scan.html, my_stones.html, stone_edit.html

**Stone Creation Flow:**

1. **User clicks "Create New Stone"** (`/create-stone/`)
   - Smart router: checks if user has unclaimed QR codes
   - If yes → redirect to `/claim-stone/<uuid>/`
   - If no → redirect to `/shop/`

2. **Shop Purchase** (or free single QR):
   - User selects product → Stripe Checkout
   - Webhook triggers → creates unclaimed stones
   - QR codes generated, PDF created
   - User downloads PDF with QR codes

3. **Claim Stone** (`/claim-stone/<uuid>/`):
   - User enters stone name, description, uploads image
   - Stone status: `unclaimed` → `draft`
   - User can edit draft stones

4. **Publish Stone:**
   - User marks stone as "published" (visible on map)

5. **Send Off Stone:**
   - User finalizes stone (status: `wandering`, no more editing)

**QR Code System:**

- Each stone has a unique UUID (not the PK)
- QR code links to: `https://stonewalker.org/stone-link/<uuid>/`
- QR code stored in `source/content/media/qr_codes/`
- Format: 3:4 portrait PNG with cleartext URL at bottom
- Banner: "Stone #N" (sequential number based on creation order)
- Persistent: even if stone name changes, UUID stays the same

**Stone Types:**

- **Hidden:** Created by user, gets circle shape auto
- **Hunted:** Requires location, gets triangle shape, treasure hunt style

**Name Validation:**

- Max 50 characters
- No whitespace allowed (enforced at model level via `validate_no_whitespace`)
- Unique across all stones

---

### Stone Scanning & Movement

**Files involved:**
- `main/views.py` — StoneScanView, StoneLinkView
- `main/models.py` — StoneMove, StoneScanAttempt

**Flow:**

1. **User finds stone** → scans QR code
2. **Stone Link Page** (`/stone-link/<uuid>/`):
   - Shows stone details (creator, journey, photos)
   - "Log Your Find" button → redirect to `/stonescan/?stone=<uuid>`
3. **Scan Form** (`/stonescan/`):
   - Pre-filled with stone UUID (locked field)
   - User enters: location (lat/lon), optional photo, comment
   - Submits → creates StoneMove
   - Distance calculated from previous move
4. **Cooldown Enforcement:**
   - Users can only scan the same stone once every **3 days**
   - Tracked via StoneScanAttempt model
   - If within cooldown → form shows error message

**Distance Calculation:**

- Haversine formula
- Distance between consecutive moves
- Accumulated in `Stone.distance_km`
- Displayed on stone detail pages and map

---

### Interactive Map

**Files involved:**
- `main/views.py` — StoneWalkerStartPageView
- `main/templates/main/stonewalker_start.html`
- Leaflet.js (loaded via CDN)

**Map Features:**

- **Markers:** One per stone (color/shape from stone data)
- **Polylines:** Connect consecutive moves (journey path)
- **Popups:** Click marker → stone name, creator, distance, "View Details" link
- **Filtering:** Toggle checkboxes for Hidden/Hunted stones
- **Stone Click:** Opens stone detail modal

**Data Flow:**

1. View queries all published stones with moves
2. Uses `select_related` and `prefetch_related` to avoid N+1 queries
3. Serializes to JSON in template context
4. JavaScript renders markers + polylines

---

### Premium Supporter Tier

**Files involved:**
- `accounts/models.py` — Subscription
- `main/premium_views.py` — PremiumView, PremiumCheckoutView, PremiumManageView, PremiumBillingPortalView
- `main/stripe_service.py` — Subscription checkout, webhook handling
- `main/templates/main/premium.html`, `premium_manage.html`
- `app/context_processors.py` — premium_status (exposes `is_premium_user` to templates)

**Subscription Plans:**

| Plan | Price | Features |
|------|-------|----------|
| Monthly | $3.99/mo | Unlimited drafts, analytics, premium badge, priority support |
| Yearly | $29.99/yr | Same as monthly + 37% discount |
| Lifetime | Free | Early supporters (first 1000 users) get lifetime premium |

**Flow:**

1. **User visits** `/premium/`
   - Landing page with features, pricing, FAQ
2. **Click "Subscribe"** → POST to `/premium/checkout/`
   - Creates Stripe Customer (if new)
   - Creates Stripe Checkout Session
   - Redirects to Stripe-hosted checkout
3. **User completes payment** → Stripe webhook
   - Event: `customer.subscription.created`
   - Creates/updates Subscription record
4. **User visits** `/premium/manage/`
   - Shows subscription status, next billing date
   - "Manage Billing" button → Stripe Billing Portal
5. **Cancel/Resubscribe:** via Stripe Billing Portal

**Subscription Model:**

- `stripe_customer_id` — Stripe Customer ID
- `stripe_subscription_id` — Stripe Subscription ID
- `plan` — monthly, yearly, or lifetime
- `status` — active, canceled, past_due, unpaid, trialing, incomplete
- `current_period_start`, `current_period_end` — billing period
- `canceled_at` — when user canceled (null if active)
- `grants_premium` property — True if status is active/trialing OR canceled but still in paid period

**Premium Features (planned):**

- Unlimited draft stones (non-premium: 1 draft max)
- Journey analytics dashboard
- Photobook PDF export
- Priority in "Featured Stones"

---

### Shop / QR Code Packs

**Files involved:**
- `main/shop_views.py` — ShopView, CheckoutView, CheckoutSuccessView, DownloadPackPDFView
- `main/stripe_service.py` — Checkout session, webhook fulfillment
- `main/pdf_service.py` — Multi-pack PDF generation
- `main/shop_config.json` — Product catalog
- `main/shop_utils.py` — Load config, caching
- `main/models.py` — QRPack, Stone

**Product Catalog (`shop_config.json`):**

```json
{
  "free_single": {
    "name": "Free Single QR",
    "price_cents": 0,
    "pack_size": 1,
    "category": "starter"
  },
  "paid_3pack": {
    "name": "Starter 3-Pack",
    "price_cents": 499,
    "pack_size": 3,
    "category": "group"
  },
  "paid_10pack": {
    "name": "Explorer 10-Pack",
    "price_cents": 999,
    "pack_size": 10,
    "category": "group"
  },
  "paid_30pack": {
    "name": "Classroom 30-Pack",
    "price_cents": 1999,
    "pack_size": 30,
    "category": "classroom"
  }
}
```

**Purchase Flow:**

1. **User visits** `/shop/`
2. **Selects product** → `/shop/checkout/<product_id>/`
3. **Stripe Checkout:**
   - Creates pending QRPack
   - Creates Stripe Checkout Session
   - Redirects to Stripe-hosted checkout
4. **Payment succeeds** → Stripe webhook:
   - Event: `checkout.session.completed`
   - Marks QRPack as paid
   - **Fulfillment:**
     - Creates N unclaimed stones (N = pack_size)
     - Generates QR codes for each
     - Generates PDF with all QR codes (grid layout)
     - Marks QRPack as fulfilled
5. **User redirected to** `/shop/success/?pack_id=<uuid>`
   - Download link for PDF

**Unclaimed Stones:**

- Status: `unclaimed`
- FK_user: NULL
- PK_stone: `UNCLAIMED-<random>`
- User claims via `/claim-stone/<uuid>/`

---

### Email System

**Files involved:**
- `app/backends.py` — MailerooEmailBackend
- `accounts/templates/emails/` — Branded email templates
- Settings: `EMAIL_BACKEND`, `MAILEROO_API_KEY`

**Email Types:**

| Template | Trigger | Purpose |
|----------|---------|---------|
| `activation.html` | User signs up | Account activation link |
| `reset_password.html` | User requests password reset | Reset password link |
| `change_email.html` | User changes email | Confirm new email |
| `remind_username.html` | User forgets username | Send username |

**Branding:**

- Green header (#4CAF50)
- 600px max-width, responsive
- White content area
- Footer with social links

**Production Email:**

- Backend: Maileroo API
- Free tier: 3,000 emails/month
- Domain verification required (SPF, DKIM)

---

### Dark Mode

**Files involved:**
- `source/content/assets/js/header.js` — Toggle logic
- `source/content/assets/css/styles.css` — CSS custom properties

**How it works:**

1. User clicks dark mode toggle
2. JavaScript sets `data-theme="dark"` on `<html>`
3. CSS uses `:root[data-theme="dark"]` to override custom properties
4. Preference saved to localStorage
5. Auto-detects system preference if not set

**CSS Custom Properties:**

```css
:root {
  --bg-color: #f9f9f9;
  --text-color: #333;
  --header-bg: #4CAF50;
  /* ... */
}

:root[data-theme="dark"] {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --header-bg: #2d5a2e;
  /* ... */
}
```

---

### Internationalization (7 Languages)

**Files involved:**
- `source/content/locale/` — Translation files
- Settings: `LANGUAGES`, `LOCALE_PATHS`
- `main/views.py` — ChangeLanguageView

**Supported Languages:**

- English (en)
- Russian (ru)
- Simplified Chinese (zh-hans)
- French (fr)
- Spanish (de)
- German (de)
- Italian (it)

**Translation Coverage:** ~94% for most languages, ~88% for Chinese

**How to switch language:**

1. User visits `/language/`
2. Selects language
3. Django sets session language
4. Redirects to `/stonewalker/` (main page)

**Browser language detection:** Enabled via `LocaleMiddleware`

**Translation workflow:**

1. Extract: `python manage.py makemessages -l <lang>`
2. Edit: `.po` files in `source/content/locale/<lang>/LC_MESSAGES/`
3. Compile: `python manage.py compilemessages`
4. Test: `python source/manage.py test main.translation_tests`

See `docs/TRANSLATION.md` for full details.

---

### Forum Integration (Discourse SSO)

**Files involved:**
- `accounts/discourse_sso.py` — SSO payload generation
- `accounts/views.py` — DiscourseSSOView
- Settings: `DISCOURSE_URL`, `DISCOURSE_SSO_SECRET`

**How it works:**

1. User clicks "Forum" in nav → `https://forum.stonewalker.org`
2. Discourse redirects to `/accounts/discourse-sso/?sso=...&sig=...`
3. Django verifies signature, generates response payload
4. Redirects back to Discourse with user data
5. Discourse logs user in automatically

**Configuration:**

- Discourse: `enable_discourse_connect = true`
- Discourse: `discourse_connect_url = https://stonewalker.org/accounts/discourse-sso/`
- Discourse: `discourse_connect_secret = <shared secret>`
- Django: `DISCOURSE_SSO_SECRET = <same secret>`

---

## Database Schema

### All Models

#### User (Django built-in)

Standard Django User model, extended via Profile.

#### Profile (accounts/models.py)

One-to-one extension of User.

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | OneToOneField | Linked user |
| profile_picture | ImageField | Optional profile image |
| facebook_url | URLField | Facebook profile URL |
| instagram_handle | CharField | Instagram @handle |
| twitter_handle | CharField | Twitter @handle |
| mastodon_handle | CharField | Mastodon @handle@instance |
| tiktok_handle | CharField | TikTok @handle |

**Methods:**
- `has_picture()` — True if profile picture exists
- `get_picture_url()` — Returns URL or fallback
- `is_premium` (property) — True if user has active subscription

#### Subscription (accounts/models.py)

Tracks premium supporter subscriptions via Stripe.

| Field | Type | Description |
|-------|------|-------------|
| id | BigAutoField | Primary key |
| user | OneToOneField | Linked user |
| stripe_customer_id | CharField | Stripe Customer ID |
| stripe_subscription_id | CharField | Stripe Subscription ID |
| plan | CharField | monthly, yearly, or lifetime |
| status | CharField | active, canceled, past_due, unpaid, trialing, incomplete |
| current_period_start | DateTimeField | Start of billing period |
| current_period_end | DateTimeField | End of billing period |
| canceled_at | DateTimeField | When canceled (null if active) |
| created_at | DateTimeField | When created |
| updated_at | DateTimeField | Last update |

**Properties:**
- `is_active` — status in (active, trialing)
- `is_canceled_but_active` — canceled but still in paid period
- `grants_premium` — is_active OR is_canceled_but_active

#### Stone (main/models.py)

Represents a painted stone tracked in the app.

| Field | Type | Description |
|-------|------|-------------|
| PK_stone | CharField(50) | Primary key (stone name) |
| uuid | UUIDField | Unique identifier for QR codes |
| description | TextField(500) | Optional description |
| created_at | DateTimeField | When created |
| updated_at | DateTimeField | Last update |
| FK_user | ForeignKey | Creator (nullable for unclaimed) |
| FK_pack | ForeignKey | QRPack if from shop |
| image | ImageField | Optional stone photo |
| color | CharField | Color hex code (default #4CAF50) |
| shape | CharField | circle or triangle |
| distance_km | FloatField | Total distance traveled |
| stone_type | CharField | hidden or hunted |
| status | CharField | unclaimed, draft, published, wandering |
| qr_code_url | URLField | Persistent QR code URL |
| wandering_at | DateTimeField | When stone started wandering |
| claimed_at | DateTimeField | When claimed (if unclaimed) |

**Methods:**
- `get_stone_number()` — Sequential number (1-based)
- `is_unclaimed()` — status == unclaimed
- `can_be_claimed()` — unclaimed and no owner
- `claim(user, new_name, ...)` — Claim stone for user
- `get_qr_url()` — Returns `https://stonewalker.org/stone-link/<uuid>/`

#### StoneMove (main/models.py)

Represents a scan/move of a stone.

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| FK_stone | ForeignKey | Stone being moved |
| FK_user | ForeignKey | User who moved it |
| image | ImageField | Optional photo |
| comment | TextField | Optional comment |
| latitude | FloatField | Latitude |
| longitude | FloatField | Longitude |
| timestamp | DateTimeField | When moved |

#### StoneScanAttempt (main/models.py)

Tracks scan attempts to enforce 3-day cooldown.

| Field | Type | Description |
|-------|------|-------------|
| FK_stone | ForeignKey | Stone |
| FK_user | ForeignKey | User |
| scan_time | DateTimeField | When scanned |
| ip_address | GenericIPAddressField | IP (optional) |
| user_agent | TextField | User agent (optional) |

**Methods:**
- `can_scan_again(stone, user)` — Check if 3 days passed
- `record_scan_attempt(stone, user, request)` — Record scan

#### QRPack (main/models.py)

Tracks purchased QR code packs from the shop.

| Field | Type | Description |
|-------|------|-------------|
| id | UUIDField | Primary key |
| FK_user | ForeignKey | Purchaser (nullable) |
| pack_type | CharField | Product ID from shop_config.json |
| status | CharField | pending, paid, fulfilled, failed |
| stripe_payment_intent_id | CharField | Stripe Session ID |
| price_cents | IntegerField | Price in cents |
| currency | CharField | USD |
| created_at | DateTimeField | When created |
| paid_at | DateTimeField | When paid |
| fulfilled_at | DateTimeField | When fulfilled |
| pdf_generated | BooleanField | PDF created |
| download_count | IntegerField | Times downloaded |

#### Other Models

- **Activation** — Email activation codes
- **EmailAddressState** — Tracks email confirmation
- **EmailChangeAttempt** — Logs email change attempts
- **TermsAcceptance** — Terms of use acceptance
- **NotificationPreference** — Email notification settings

### Relationship Diagram

```
User <1----1> Profile
User <1----1> Subscription
User <1----*> Stone
User <1----*> StoneMove
User <1----*> QRPack
Stone <1----*> StoneMove
Stone <*----1> QRPack (FK_pack)
Stone <1----*> StoneScanAttempt
User <1----*> StoneScanAttempt
User <1----*> Activation
```

---

## URL Map

All URLs are organized by functional area. Most have i18n language prefix (`/en/`, `/de/`, etc.).

### Public Pages (no login required)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/` | index | StoneWalkerStartPageView | Main map page |
| `/stonewalker/` | stonewalker_start | StoneWalkerStartPageView | Same as / |
| `/about/` | about | TemplateView | About StoneWalker |
| `/language/` | change_language | ChangeLanguageView | Change language |
| `/robots.txt` | robots_txt | TemplateView | Search engine rules |

### Stone Management (login required)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/my-stones/` | my_stones | MyStonesView | User's stones dashboard |
| `/create-stone/` | create_stone | CreateNewStoneView | Smart router (claim or shop) |
| `/add_stone/` | add_stone | add_stone | Legacy redirect to /create-stone/ |
| `/stonescan/` | stone_scan | StoneScanView | Scan stone form |
| `/stone/<pk>/edit/` | stone_edit | StoneEditView | Edit draft stone |
| `/stone/<pk>/qr/` | stone_qr | StoneQRCodeView | Download QR code |
| `/stone/<pk>/certificate/` | stone_certificate | StoneCertificateView | Download PDF certificate |
| `/stone/<pk>/send-off/` | stone_send_off | StoneSendOffView | Finalize stone |
| `/stone/<pk>/share/` | stone_share | StoneShareView | Share stone on social |
| `/stone-link/<uuid>/` | stone_link | StoneLinkView | Stone found page (QR scan) |
| `/claim-stone/<uuid>/` | claim_stone | ClaimStoneView | Claim unclaimed stone |

### Premium (login required for checkout)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/premium/` | premium | PremiumView | Landing page |
| `/premium/checkout/` | premium_checkout | PremiumCheckoutView | POST — create Stripe session |
| `/premium/manage/` | premium_manage | PremiumManageView | Subscription status |
| `/premium/billing/` | premium_billing | PremiumBillingPortalView | POST — Stripe portal |

### Shop (login required for checkout)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/shop/` | shop | ShopView | Browse products |
| `/shop/checkout/<product_id>/` | checkout | CheckoutView | Checkout page |
| `/shop/success/` | checkout_success | CheckoutSuccessView | Post-purchase page |
| `/shop/download/<pack_id>/` | download_pack_pdf | DownloadPackPDFView | Download QR pack PDF |
| `/shop/download-qr/<uuid>/` | download_stone_qr | DownloadStoneQRView | Download single QR |
| `/shop/free-qr/` | free_qr | FreeQRView | Legacy free QR |

### API Endpoints (no language prefix, no login)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/api/check_stone_name/` | check_stone_name | check_stone_name | Check name availability |
| `/api/check-stone-uuid/<uuid>/` | check_stone_uuid | check_stone_uuid | Check UUID exists |
| `/api/generate-qr/` | generate_qr_api | generate_qr_code_api | Generate QR preview |
| `/api/download-enhanced-qr/` | download_enhanced_qr | download_enhanced_qr_code | Download branded QR |

### Authentication (`/accounts/`)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/accounts/log-in/` | log_in | LogInView | Log in |
| `/accounts/log-out/` | log_out | LogOutView | Log out |
| `/accounts/log-out/confirm/` | log_out_confirm | LogOutConfirmView | Log out confirmation |
| `/accounts/sign-up/` | sign_up | SignUpView | Sign up |
| `/accounts/activate/<code>/` | activate | ActivateView | Activate account |
| `/accounts/change/profile/` | change_profile | ChangeProfileView | Edit profile |
| `/accounts/change/email/<code>/` | change_email | ChangeEmailView | Confirm email |
| `/accounts/resend/activation-code/` | resend_activation_code | ResendActivationCodeView | Resend activation |
| `/accounts/restore/password/` | restore_password | RestorePasswordView | Request reset |
| `/accounts/restore/password/done/` | restore_password_done | RestorePasswordDoneView | Reset sent |
| `/accounts/restore/<uidb64>/<token>/` | restore_password_confirm | RestorePasswordConfirmView | Set new password |
| `/accounts/remind/username/` | remind_username | RemindUsernameView | Recover username |
| `/accounts/api/check_username/` | check_username | check_username | Check availability |
| `/accounts/discourse-sso/` | discourse_sso | DiscourseSSOView | Discourse SSO |

### Webhooks (no language prefix, no CSRF)

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/webhooks/stripe/` | stripe_webhook | stripe_webhook | Stripe event handler |

### Admin

| URL | Name | View | Description |
|-----|------|------|-------------|
| `/admin/` | admin | Django admin | Admin panel |

---

## Frontend Architecture

### CSS System

**Main file:** `source/content/assets/css/styles.css`

**Structure:**

1. **CSS Custom Properties** (`:root`)
   - Colors, fonts, spacing, shadows
   - Dark mode overrides (`:root[data-theme="dark"]`)
2. **Utility Classes** (200+)
   - Spacing: `m-0-5`, `p-1`, `mt-10`, etc.
   - Flex: `flex-center`, `flex-between`, `flex-col`
   - Text: `text-center`, `font-bold`, `fs-1-2`
   - Layout: `position-relative`, `z-100`, `display-none`
3. **Component Styles**
   - Header, nav, burger menu
   - Modals, cards, buttons
   - Forms, inputs, tables
4. **Responsive Breakpoints**
   - Desktop: >1450px
   - Tablet: 801-1450px
   - Mobile-lg: 768-800px
   - Mobile-md: 600-767px
   - Mobile: 480-599px
   - Mobile-xs: ≤480px

**Single Source of Truth for Breakpoints:**

All breakpoints defined in `source/content/assets/js/header.js`:

```javascript
const BREAKPOINTS = {
  desktop: 1450,
  tablet: 800,
  mobileLg: 768,
  mobileMd: 600,
  mobile: 480,
  mobileXs: 360
};
```

To sync with CSS:
```bash
node source/content/assets/js/sync-breakpoints.js
```

---

### JavaScript

**Main files:**
- `source/content/assets/js/header.js` — Burger menu, dark mode, breakpoints
- `source/content/assets/js/image-upload.js` — Client-side image validation

**Key features:**

1. **Burger Menu** (mobile only, ≤800px):
   - Checkbox-based toggle (`#menu-toggle`)
   - Overlay closes on click
   - ESC key closes menu
   - Auto-closes on window resize above breakpoint

2. **Dark Mode:**
   - Toggle button in header
   - Sets `data-theme="dark"` on `<html>`
   - Saves preference to localStorage
   - Auto-detects system preference

3. **Profile Modal:**
   - Opens on "Edit Profile" click
   - Loads form via AJAX
   - AJAX form submission
   - Closes on ESC or overlay click

4. **Image Upload Validation:**
   - Max 800x800px
   - Max 5MB
   - Shows preview before upload

---

### Template Inheritance Chain

```
layouts/default/page.html
  ├── Header (logo, nav, burger menu, dark mode)
  ├── Profile modal overlay
  └── {% block content %}
       ├── main/stonewalker_start.html
       ├── main/my_stones.html
       ├── main/shop.html
       ├── main/premium.html
       ├── accounts/log_in.html
       └── ... (other child templates)
```

**Shared includes:**

- `layouts/default/nav_links.html` — Navigation (used in both main nav and burger)
- `main/shared_modals.html` — Modal templates (scan stone, QR scanner)

---

## Testing

### Test Suite Overview

**Total:** 321 tests across 13 files

| File | Tests | Type | Coverage |
|------|-------|------|----------|
| `accounts/tests.py` | 15 | Unit | Auth, profiles, nav, CSS utilities |
| `main/tests/test_models.py` | 23 | Integration | Stone, StoneMove, scan attempts |
| `main/tests/test_qr_system.py` | 10 | Integration | QR generation, download, display |
| `main/tests/test_stone_scanning.py` | 8 | Integration | Scanning, blackout periods |
| `main/tests/test_stone_workflow.py` | 26 | Integration | Creation, editing, status, name validation |
| `main/tests/test_api_endpoints.py` | 15+ | Integration | AJAX endpoints, availability checks |
| `main/tests/test_ui_templates.py` | 15+ | Integration | Page loading, modals, auth gates |
| `main/tests/test_premium.py` | 40+ | Integration | Subscription model, views, webhooks |
| `main/tests/test_shop_flow.py` | 20+ | Integration | Shop, checkout, fulfillment |
| `main/tests/test_shop_visibility.py` | 5 | Integration | Shop auto-hide logic |
| `main/tests/test_language_switching.py` | 6 | Integration | Language bug fixes |
| `main/tests/test_map_filtering.py` | 8 | Integration | Map filter UI/JS |
| `main/tests/test_stone_features.py` | 15+ | Integration | QR numbering, certificates |
| `main/translation_tests.py` | 30+ | Integration | Translation QA (PO files, coverage) |

### Running Tests

**Full suite:**

```bash
# Compiles translations first, then runs all tests
./venv/bin/python run_tests.py
```

**Subset:**

```bash
# Accounts tests only
./venv/bin/python run_tests.py accounts

# Main tests only
./venv/bin/python run_tests.py main/tests/

# By name pattern
./venv/bin/python run_tests.py -k test_scan

# By marker
./venv/bin/python run_tests.py -m unit
./venv/bin/python run_tests.py -m integration
```

**With coverage:**

```bash
make test-cov
```

**Skip translation compilation (faster for agents):**

```bash
./venv/bin/python run_tests.py --skip-translations
```

### Test Output

- **Silent on pass** — no dots, no noise
- **Verbose on failure** — full traceback, clear error message
- **Format:** `145 passed in 3:15` or `FAIL: test_path::TestClass::test_name`

### Pre-Push Hook

The `.git/hooks/pre-push` hook runs the full test suite before every push. If any test fails, the push is aborted.

Make sure it's executable:

```bash
chmod +x .git/hooks/pre-push
```

### Test Infrastructure

**Entry point:** `run_tests.py`
- Compiles translations first
- Passes args to pytest
- Defaults to `accounts/tests.py main/tests/`

**Config:** `pytest.ini`
- `--reuse-db --nomigrations` — fast DB
- `--tb=short -q --no-header` — compact output
- `--strict-markers` — catch typos
- `-W ignore::DeprecationWarning` — suppress noise

**Plugin:** `conftest.py`
- Django setup
- Auto-mark tests: `main/` = integration, `accounts/` = unit
- Custom reporter: silent pass, verbose fail

### Base Classes

All in `main/tests/base.py`:

- `BaseStoneWalkerTestCase` — Common setup (user, profile, login)
- `BaseQRTestCase` — QR code test utilities
- `BaseAuthenticatedTestCase` — Pre-logged-in user
- `BaseAnonymousTestCase` — No user

### Test Database Issues

**Problem:** After migrations, tests fail with "column does not exist" errors.

**Solution:**

```bash
# Force-recreate test database
./venv/bin/python run_tests.py --create-db
```

**When needed:**
- After pulling code with new migrations
- After running `makemigrations`
- When you see `OperationalError` about missing columns

See `docs/CLAUDE.md` → "Test Database & Migrations" for full details.

---

## Translation System

### Overview

StoneWalker supports 7 languages with comprehensive translation QA:

- **Languages:** English, Russian, Chinese (Simplified), French, Spanish, German, Italian
- **Coverage:** ~94% for most, ~88% for Chinese
- **Location:** `source/content/locale/<lang>/LC_MESSAGES/django.po`

### Translation Workflow

1. **Extract new strings:**
   ```bash
   cd source
   python manage.py makemessages -l <lang>
   ```

2. **Edit .po files:**
   - Open `source/content/locale/<lang>/LC_MESSAGES/django.po`
   - Fill in `msgstr` for each `msgid`

3. **Compile:**
   ```bash
   cd source
   python manage.py compilemessages
   ```

4. **Test:**
   ```bash
   python source/manage.py test main.translation_tests
   ```

### Translation QA Tests

The `main/translation_tests.py` suite validates:

- **PO File Structure:** Proper headers, charset, no empty msgstr
- **No Duplicates:** Each msgid appears only once
- **Compilation Success:** All .po files compile without errors
- **Functionality:** Translations actually work in views
- **Coverage:** Critical strings are translated

### Excel/CSV Workflow

For bulk editing:

```bash
# Export to CSV
python scripts/translation/po_to_excel.py source/content/locale translations.csv

# Edit translations.csv in Excel/Google Sheets

# Import back
python scripts/translation/excel_to_po.py translations.csv source/content/locale

# Compile
cd source && python manage.py compilemessages
```

See `docs/TRANSLATION.md` for full details.

---

## Deployment

### Development

**Quick start:**

```bash
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
./run_dev.sh
```

**Runs:**
- Activates venv
- Runs migrations
- Compiles translations
- Starts dev server on port 8000

### Production (Render.com)

**Requirements:**
- Render.com account
- GitHub repository
- PostgreSQL database add-on

**Steps:**

1. **Create Web Service:**
   - Connect GitHub repo
   - Python 3.12 environment
   - Build command: `./render_build.sh`
   - Start command: `cd source && ./render_start.sh`

2. **Environment Variables:**
   ```
   SECRET_KEY=<random-50-char-string>
   DEBUG=False
   ALLOWED_HOSTS=your-app.onrender.com
   DATABASE_URL=<postgres-url-from-render>
   MAILEROO_API_KEY=<optional-email>
   STRIPE_PUBLIC_KEY=<optional-payments>
   STRIPE_SECRET_KEY=<optional-payments>
   STRIPE_WEBHOOK_SECRET=<optional-payments>
   ```

3. **Add PostgreSQL Database:**
   - Render dashboard → New PostgreSQL
   - Copy connection string → DATABASE_URL

4. **Deploy:**
   - Push to GitHub main branch → auto-deploys

See `docs/DEPLOYMENT.md` for full Render guide.

### Production (Self-Hosted VPS)

**Requirements:**
- Ubuntu 22.04+ VPS, 2-4GB RAM
- PostgreSQL 15+
- nginx, gunicorn, Let's Encrypt

**Quick overview:**

1. **System setup:** PostgreSQL, nginx, Python, gettext
2. **Deploy code:** Clone repo or upload tarball
3. **Environment:** Create `.env` file with secrets
4. **Django:** migrate, compilemessages, collectstatic, createsuperuser
5. **Gunicorn:** systemd service with 5 workers
6. **nginx:** Reverse proxy + SSL
7. **Let's Encrypt:** Auto-renewing SSL certs
8. **Backups:** Daily pg_dump + media files

See `docs/DEPLOYMENT_SELFHOSTED.md` for full VPS guide (includes Discourse forum setup, auto-deploy, monitoring).

---

## Business Context

### What StoneWalker Is

StoneWalker is **geocaching meets rock painting**. The painted rock community is massive (millions of participants) but has zero digital infrastructure. We provide the tech layer.

**Market size:**
- Geocaching: 3M+ players, $40/year premium
- Rock painting: 6,800+ member Facebook groups, 100-200 new joins/week
- The gap: Nobody combines art + digital tracking

### Revenue Model

| Stream | Products | Margin |
|--------|----------|--------|
| **Digital QR Packs** | Free single, $4.99 3-pack, $9.99 10-pack, $19.99 30-pack | ~95% |
| **Premium Subscriptions** | $3.99/mo or $29.99/yr | ~97% (Stripe fees only) |
| **Physical Products** | Starter kits, metal plaques, sticker packs (planned) | 50-75% |
| **Group/Education** | School packs, corporate team-building (planned) | 60-80% |

### Growth Strategy

**Phase 1 (Months 1-3):** Content & Community
- YouTube/TikTok rock painting videos
- SEO ("rock painting ideas", "kindness rocks")
- Reddit, Facebook groups
- Creator partnerships

**Phase 2 (Months 3-6):** Partnerships
- Scout groups, schools (STEM angle)
- Geocaching crossover
- Art supply stores (affiliate links)

**Phase 3 (Months 6-12):** Viral mechanics
- Built-in virality: every stone IS marketing
- Gamification: leaderboards, achievements
- Seasonal events: "Summer Stone Drop 2026"

### Financials

**Monthly costs:** ~$15 (Render.com hosting)

**Break-even:** ~20 paid 10-packs/month or 7 subscribers

**Target (Month 12):** $1,500/month revenue (moderate scenario)

See `docs/BUSINESS_STRATEGY.md` for full strategy, product roadmap, and market research.

---

## Common Tasks (How-To Guide)

### How to Add a New Page

1. **Create view** in `main/views.py` or `accounts/views.py`:
   ```python
   from django.views.generic import TemplateView

   class MyNewPageView(TemplateView):
       template_name = 'main/my_new_page.html'

       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context['my_data'] = 'Hello!'
           return context
   ```

2. **Create template** in `source/content/templates/main/my_new_page.html`:
   ```django
   {% extends "layouts/default/page.html" %}
   {% load i18n %}

   {% block title %}{% trans "My New Page" %}{% endblock %}

   {% block content %}
   <div class="container">
       <h1>{% trans "My New Page" %}</h1>
       <p>{{ my_data }}</p>
   </div>
   {% endblock %}
   ```

3. **Add URL** in `source/app/urls.py`:
   ```python
   from main.views import MyNewPageView

   urlpatterns += i18n_patterns(
       # ... existing patterns ...
       path('my-new-page/', MyNewPageView.as_view(), name='my_new_page'),
   )
   ```

4. **Add nav link** (optional) in `source/content/templates/layouts/default/nav_links.html`:
   ```django
   <a class="nav-link avant-btn header-nav-btn" href="{% url 'my_new_page' %}">{% trans 'My New Page' %}</a>
   ```

5. **Extract translatable strings:**
   ```bash
   cd source
   python manage.py makemessages -a
   ```

6. **Compile translations:**
   ```bash
   python manage.py compilemessages
   ```

---

### How to Add a New Translatable String

1. **In template**, wrap with `{% trans %}`:
   ```django
   {% load i18n %}
   <h1>{% trans "Welcome to StoneWalker" %}</h1>
   ```

2. **In Python**, use `gettext` or `gettext_lazy`:
   ```python
   from django.utils.translation import gettext as _

   messages.success(request, _('Stone created successfully!'))
   ```

3. **Extract strings:**
   ```bash
   cd source
   python manage.py makemessages -a
   ```

4. **Edit .po files:**
   - Open `source/content/locale/<lang>/LC_MESSAGES/django.po`
   - Find your string (msgid)
   - Fill in msgstr

5. **Compile:**
   ```bash
   python manage.py compilemessages
   ```

6. **Test:**
   - Switch language in UI
   - Verify string appears translated

---

### How to Add a New Model/Migration

1. **Define model** in `main/models.py` or `accounts/models.py`:
   ```python
   class MyNewModel(models.Model):
       name = models.CharField(max_length=100)
       created_at = models.DateTimeField(auto_now_add=True)

       def __str__(self):
           return self.name
   ```

2. **Create migration:**
   ```bash
   cd source
   python manage.py makemigrations
   ```

3. **Review migration:**
   - Check `source/<app>/migrations/0XXX_my_new_model.py`
   - Verify fields, defaults, dependencies

4. **Apply migration:**
   ```bash
   python manage.py migrate
   ```

5. **Update test database:**
   ```bash
   # If tests fail with "column does not exist"
   cd ..
   ./venv/bin/python run_tests.py --create-db
   ```

6. **Register in admin** (optional):
   ```python
   # in app/admin.py
   from .models import MyNewModel

   admin.site.register(MyNewModel)
   ```

---

### How to Add a New Test

1. **Choose location:**
   - Unit tests: `accounts/tests.py`
   - Integration tests: `main/tests/test_<feature>.py`

2. **Write test:**
   ```python
   from main.tests.base import BaseStoneWalkerTestCase

   class MyNewFeatureTests(BaseStoneWalkerTestCase):
       def test_my_feature(self):
           # Setup
           self.client.login(username='testuser', password='testpass')

           # Action
           response = self.client.get('/my-new-page/')

           # Assert
           self.assertEqual(response.status_code, 200)
           self.assertContains(response, 'My New Page')
   ```

3. **Run test:**
   ```bash
   ./venv/bin/python run_tests.py -k test_my_feature
   ```

4. **Add to suite:**
   - If in new file, it auto-runs
   - If marker needed, add to `pytest.ini`

---

### How to Modify the Navigation

**All navigation is centralized** in `source/content/templates/layouts/default/nav_links.html`.

1. **Edit nav_links.html:**
   ```django
   {% load i18n %}
   <nav id="main-nav" class="header-main-nav{% if burger %} header-burger-nav-list{% endif %}">
     <a class="nav-link avant-btn header-nav-btn" href="{% url 'about' %}">{% trans 'About' %}</a>
     <a class="nav-link avant-btn header-nav-btn" href="{% url 'my_new_page' %}">{% trans 'New Link' %}</a>
     <!-- ... more links ... -->
   </nav>
   ```

2. **The template is included twice:**
   - Main nav (desktop/tablet, always visible)
   - Burger nav (mobile, hidden by default)

3. **Conditional links:**
   ```django
   {% if shop_visible %}
   <a href="{% url 'shop' %}">{% trans 'Shop' %}</a>
   {% endif %}
   ```

4. **Extract & compile translations:**
   ```bash
   cd source
   python manage.py makemessages -a
   python manage.py compilemessages
   ```

---

### How to Add Dark Mode Support

**All dark mode styling is via CSS custom properties.**

1. **Define light mode variables** in `styles.css`:
   ```css
   :root {
     --my-bg-color: #ffffff;
     --my-text-color: #333333;
   }
   ```

2. **Define dark mode overrides:**
   ```css
   :root[data-theme="dark"] {
     --my-bg-color: #1a1a1a;
     --my-text-color: #e0e0e0;
   }
   ```

3. **Use variables in your styles:**
   ```css
   .my-component {
     background-color: var(--my-bg-color);
     color: var(--my-text-color);
   }
   ```

4. **Test:**
   - Click dark mode toggle in header
   - Verify colors change
   - Check localStorage persistence

---

## Troubleshooting

### Common Errors

#### "Missing stone name" even when name was entered

**Cause:** JavaScript calling `closeModal()` before `form.submit()`. `closeModal()` calls `resetForm()` which clears all fields.

**Fix:** Always call `form.submit()` first, remove premature `closeModal()`.

**Location:** `source/content/templates/main/new_add_stone_modal.html` line ~406

**Tests:** `main/tests/test_stone_workflow.py::StoneNameSubmissionTests`

---

#### "Invalid stone link" after scanning freshly created QR

**Cause:** Frontend generates preview UUID, but backend generates different UUID on save. QR points to UUID-A, DB has UUID-B.

**Fix:** Pass frontend UUID through hidden form field. Backend reads UUID from POST and uses it.

**Location:** `main/views.py::add_stone`, form hidden field `stone_uuid`

**Tests:** `main/tests/test_qr_system.py::test_qr_uuid_matches_db`

---

#### Tests fail with "no such column" after migrations

**Cause:** Test database is cached and doesn't have new schema.

**Fix:**

```bash
./venv/bin/python run_tests.py --create-db
```

**When needed:**
- After `makemigrations`
- After pulling code with new migrations
- When you see `OperationalError` about missing columns

**See:** `docs/CLAUDE.md` → "Test Database & Migrations"

---

#### Translations not appearing

**Causes:**
1. Forgot to compile after editing .po files
2. Empty msgstr in .po file
3. Template missing `{% load i18n %}`
4. Not using `{% trans %}` tag

**Fixes:**

```bash
# 1. Compile translations
cd source
python manage.py compilemessages

# 2. Check .po file
# Open source/content/locale/<lang>/LC_MESSAGES/django.po
# Ensure msgstr is not empty

# 3. Add to template
{% load i18n %}

# 4. Wrap string
{% trans "My String" %}
```

**Test:**

```bash
# Run translation QA tests
python source/manage.py test main.translation_tests
```

---

#### PostgreSQL connection issues

**Error:** `could not connect to server`

**Fixes:**

```bash
# 1. Check PostgreSQL is running
pg_isready

# 2. Check DATABASE_URL
echo $DATABASE_URL

# 3. Test connection manually
psql $DATABASE_URL

# 4. Check credentials
# Edit DATABASE_URL with correct user/password

# 5. Create database if missing
createdb stone_dev
```

---

#### Stripe webhook not triggering

**Causes:**
1. STRIPE_WEBHOOK_SECRET not set or wrong
2. Webhook URL not configured in Stripe dashboard
3. Webhook signature verification failing

**Fixes:**

```bash
# 1. Check environment variable
echo $STRIPE_WEBHOOK_SECRET

# 2. Check Stripe dashboard
# Webhooks → Add endpoint → https://yourdomain.com/webhooks/stripe/
# Events: checkout.session.completed, customer.subscription.*

# 3. Check logs
tail -f /var/log/stonewalker/error.log
```

**Test locally:**

```bash
# Install Stripe CLI
stripe login
stripe listen --forward-to localhost:8000/webhooks/stripe/

# Trigger test event
stripe trigger checkout.session.completed
```

---

#### Email not sending (production)

**Causes:**
1. MAILEROO_API_KEY not set
2. Domain not verified in Maileroo
3. Wrong "From" address (not matching verified domain)

**Fixes:**

```bash
# 1. Check API key
echo $MAILEROO_API_KEY

# 2. Check Maileroo dashboard
# Domains → Verify status (should be green)

# 3. Check FROM email
# Must be noreply@yourdomain.org (not @forum.yourdomain.org)
# Edit DEFAULT_FROM_EMAIL in settings

# 4. Test manually
cd source
python manage.py shell

from django.core.mail import send_mail
send_mail('Test', 'Email works!', 'noreply@yourdomain.org', ['your@email.com'])
```

**Check Maileroo logs:** Maileroo Dashboard → Logs

---

### Debug Mode Indicator

The base template has a **debug mode indicator** (hidden by default). To enable:

1. Edit `source/content/templates/layouts/default/page.html`
2. Find `<div id="debug-mode-indicator" ... style="display: none;">`
3. Change to `style="display: flex;"`

**Shows:**
- Current responsive breakpoint
- Window width
- User authentication status
- Profile picture URL
- Static file paths

---

### Need More Help?

1. **Check docs:**
   - `docs/CLAUDE.md` — Development notes, learnings, gotchas
   - `docs/README.md` — Main README
   - `docs/TRANSLATION.md` — Translation system
   - `docs/DEPLOYMENT.md` — Deployment guides

2. **Ask on forum:** `https://forum.stonewalker.org`

3. **File bug report:** `https://github.com/busssard/Stonewalker/issues`

4. **Run tests:** `./venv/bin/python run_tests.py -v` for verbose output

---

**End of Wiki**

This wiki is a living document. Update it as you learn, fix bugs, and add features. Keep it accurate, concise, and helpful for the next person.

Happy coding!
