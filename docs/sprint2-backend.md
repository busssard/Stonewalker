# Sprint 2 - Backend Features

## Overview

Sprint 2 backend work implements four features: Terms of Use system, Email Notification System, Social Sharing Pages, and Social Media Profile Connections.

## Features Implemented

### 1. Terms of Use System

**Models:**
- `TermsAcceptance` (accounts/models.py) - OneToOneField to User, tracks `accepted_at` and `version`

**Flow:**
- Signup form requires `accept_terms` checkbox (BooleanField, required=True)
- On signup, `TermsAcceptance` record is created automatically in `SignUpView.form_valid`
- Terms gate enforced before stone creation in `add_stone` view and `ClaimStoneView`
- Users without accepted terms are redirected to `/terms/` page

**Files:**
- `source/accounts/models.py` - TermsAcceptance model
- `source/accounts/forms.py` - accept_terms field on SignUpForm
- `source/accounts/views.py` - SignUpView creates TermsAcceptance
- `source/main/views.py` - Terms gate on add_stone
- `source/main/shop_views.py` - Terms gate on ClaimStoneView
- `source/accounts/templates/accounts/terms.html` - Terms page (7 sections)
- `source/accounts/templates/accounts/sign_up.html` - Checkbox added
- `source/app/urls.py` - `/terms/` route

### 2. Email Notification System

**Models:**
- `NotificationPreference` (accounts/models.py) - OneToOneField to User, boolean fields: `stone_scanned`, `stone_moved`, `weekly_digest`

**Flow:**
- Django signal (`post_save` on `StoneMove`) triggers email to stone owner
- Skips notification if mover is the owner
- Checks `NotificationPreference.stone_scanned` before sending
- Uses `EmailMultiAlternatives` for HTML + plain text
- Branded email templates (green #4CAF50 header, 600px max-width, inline CSS)

**Files:**
- `source/accounts/models.py` - NotificationPreference model
- `source/main/signals.py` - post_save signal handler
- `source/main/apps.py` - Signal registration in ready()
- `source/accounts/views.py` - Notification prefs saved in ChangeProfileView
- `source/accounts/forms.py` - Notification toggle fields on CombinedProfileForm
- `source/accounts/templates/accounts/emails/stone_scanned.html` - HTML email
- `source/accounts/templates/accounts/emails/stone_scanned.txt` - Plain text email
- `source/accounts/templates/accounts/emails/stone_moved.html` - HTML email
- `source/accounts/templates/accounts/emails/stone_moved.txt` - Plain text email

### 3. Social Sharing Pages

**View:**
- `StoneShareView` (main/views.py) - Public view at `/stone/<pk>/share/`
- Builds share URLs for Twitter, Facebook, WhatsApp (URL-based, no JS SDKs)
- Provides Open Graph meta tags (og:title, og:description, og:image)
- Includes journey stats (total moves, distance, countries)
- Mini Leaflet map showing stone journey

**Files:**
- `source/main/views.py` - StoneShareView class
- `source/content/templates/main/stone_share.html` - Share page template
- `source/app/urls.py` - `/stone/<pk>/share/` route

### 4. Social Media Profile Connections

**Model fields added to Profile:**
- `facebook_url` (URLField)
- `instagram_handle` (CharField, max 50)
- `twitter_handle` (CharField, max 50)
- `mastodon_handle` (CharField, max 100)
- `tiktok_handle` (CharField, max 50)

**Helper methods on Profile:**
- `has_social_links()` - Returns True if any social field is populated
- `get_share_handle()` - Returns best social handle for sharing (prefers Twitter, then Instagram, then username)

**Files:**
- `source/accounts/models.py` - Social fields and methods on Profile
- `source/accounts/forms.py` - Social fields on CombinedProfileForm
- `source/accounts/views.py` - Social fields saved in ChangeProfileView

## Database Migration

Migration `0009_*` adds:
- 5 social media fields to Profile
- TermsAcceptance table
- NotificationPreference table

## Tests

**New test files:**
- `source/accounts/test_social_terms.py` - Tests for TermsAcceptance, signup with/without terms, terms page, NotificationPreference, social media profile fields
- `source/main/tests/test_backend_features.py` - Tests for StoneShareView (public access, OG tags, share buttons, journey stats, 404, owner info, social links), signal notifications (fires on move, skips self-scan, respects prefs), terms gate

**Modified test files:**
- `source/main/tests/base.py` - BaseStoneWalkerTestCase creates TermsAcceptance in setUp
- `source/accounts/tests.py` - Added accept_terms to signup POST data
- `source/main/tests/test_stone_workflow.py` - Removed duplicate TermsAcceptance setup
- `source/main/tests/test_ui_templates.py` - Removed duplicate TermsAcceptance setup

**Result: 224 tests pass.**

## Notable Bug Fix

Fixed a variable shadowing bug where `prefs, _ = NotificationPreference.objects.get_or_create(user=user)` in `ChangeProfileView.form_valid` shadowed the module-level `_` import (gettext_lazy) with the boolean `created` value. This caused `'bool' object is not callable` when `_('...')` was called later. Fixed by using `prefs, _created = ...`.
