# Bug Hunt — Task Board

Started 2026-09-26. Goal: StoneWalker reliable end-to-end before it goes out to artists.

Workflow: pick a task → mark `[current] (owner)` → write a failing test → fix → run tests → mark `[DONE]` and log in `findings.md`.
File ownership (to avoid edit collisions between agents) is listed per task.

Legend: `[ ]` open · `[current]` in progress · `[DONE]` · `[WONTFIX]` · severity P0 (broken core flow / security) → P3 (polish)

## P0 — core flow broken / security

- [DONE] **F1 Logged-in finders can never record a find** — GET of the scan link records a scan attempt, POST then hits the 1-week blackout. Root cause of "stone scanned twice but not on map". Owner: lead. Files: `main/views.py`, `main/models.py`
- [DONE] **F2 `/stone/<pk>/qr/` 500 for logged-out visitors** (missing `login_required`). Owner: lead. Seen live on stonewalker.org.
- [DONE] **F3 Stored XSS** — `stones_json|safe` / `moves_json|safe` inside `<script>`; `</script>` in a description or comment breaks out. Files: `main/views.py`, `templates/main/stonewalker_start.html`, `templates/main/stone_share.html`
- [DONE] (payments) **F4 Premium subscriptions never linked to the paying user** — `user_id` only on Checkout Session metadata; webhook can't find user. Files: `main/stripe_service.py`
- [DONE] **F5 Account takeover via anonymous find form** — typing an existing *unconfirmed* account's email logs you in as that user. Files: `main/views.py`
- [DONE] **F6 Legacy `/stonescan/` adds confirmed moves to any stone without the QR key** (orphaned route, no template links to it). Files: `main/views.py`, `app/urls.py`, tests
- [DONE] **F7 `StoneLinkView.post` skips status/owner rules** — anyone with the key can seal someone else's published stone or add finds to drafts. Files: `main/views.py`

## P1 — money / data integrity

- [DONE] (payments) **F8 Stone-number race** (`Max+1` without lock) → IntegrityError mid pack fulfilment → partial packs. Files: `main/models.py`, `main/shop_views.py`
- [DONE] (payments) **F9 Webhook and success-page fallback can both fulfil same pack** (duplicate stones). Files: `main/stripe_service.py`, `main/shop_views.py`
- [DONE] (payments) **F10 Stone names barely validated** — `/`, `..`, `\`, `?` accepted → NoReverseMatch 500s, path traversal in QR file path. Files: `main/shop_views.py`, `main/views.py` (`check_stone_name`)
- [DONE] (payments) **F11 Webhook accepts unsigned events when `STRIPE_WEBHOOK_SECRET` empty** in production. Files: `main/stripe_service.py`
- [DONE] (payments) **F12 `/shop/download-qr/<n>/` open to any logged-in user for pack-less stones** (sequential numbers → key leak). Files: `main/shop_views.py`
- [DONE] (payments) **NEW-1 Premium products bought as one-time payment in the shop** — shop lists premium_* with Buy Now; CheckoutView doesn't reject is_subscription → user pays, gets 0-stone pack. Files: `main/shop_views.py`, `main/stripe_service.py`, `templates/main/shop.html`
- [DONE] (payments) **NEW-10 `/create-stone/` and `/shop/free-qr/` mint on GET** (CSRF-able allowance burn) → POST-only. Files: `main/shop_views.py`, templates linking to them
- [DONE] (payments) **NEW-11 Success page never fulfils without webhook; paid single pack shows nothing** — verify session with Stripe; add single-code block. Files: `main/shop_views.py`, `main/stripe_service.py`, `templates/main/checkout_success.html`

## P2 — wrong behaviour

- [DONE] **F13 Hardcoded unprefixed redirects drop the user's language** (`/stonewalker/?focus=`, `/stone/.../edit/`). Files: `main/views.py`
- [DONE] **F14 Scan attempt + move not atomic** — failed move still locks finder out. Files: `main/views.py`
- [DONE] **F15 Owner emailed for held (unconfirmed) finds.** Files: `main/signals.py`, `main/models.py`
- [DONE] **F16 `StoneEditView.post` returns None on missing `action`** → 500. Files: `main/views.py`
- [DONE] **F17 Anonymous-find IP limit compares X-Forwarded-For vs stored REMOTE_ADDR.** Files: `main/views.py`, `main/models.py`
- [ ] **F18 Hunted stone "new location" only stored in finder's session, never read.** Needs product decision — parked.

## P3 — polish

- [DONE] **F19 Footer overflows horizontally on 390px mobile** (link at x=-2, copyright to 392px). Files: `assets/css/styles.css`
- [DONE] **F21 Find form lat/lng inputs overflow on 390px** (flex items min-width:auto; Longitude ended at x=495). Fixed with `.flex > .avant-input.flex-1 { min-width: 0 }`.
- [DONE] **F22 Map filter pills overlap Leaflet zoom +/- on mobile** (top-left). Files: `assets/css/styles.css`
- [DONE] **P1 PRODUCT (user chose 1c, 2026-09-26): sealed stones never appear on the map until someone else finds them.** Seal page copy says "makes it public on the map", but the map only lists stones with ≥1 confirmed find. The user's "scanned twice, not on map" stone is likely claim-scan + seal-scan (neither is a find). Options: (a) capture hide location at seal time and show it (spoils hidden stones?), (b) show sealed-but-unfound stones only in My Stones and fix the copy, (c) record the seal location privately and reveal after first find. Needs user decision. → **Implemented 1c:** seal page captures the hiding spot (GPS or map pin) into `Stone.hide_latitude/hide_longitude` (migration 0014). Hidden stones: kept private, prepended as journey start (map line, share page, distance) only once a confirmed find exists. Hunted stones: location required at seal and published immediately as the owner's first StoneMove (hunted mode had no location source before). Seal-page copy updated. Tests: `HidingSpotTests`. Verified in browser (Bern → Zurich = 95.5 km).
- [DONE] **F23 No visible "I found a stone" entry; scan modal broken** — button removed in 19a3f21; the leftover modal required login (strangers bounced to log-in), asked for a 36-char UUID nobody can type, and its "Found This Stone" button only showed a fake alert. Now: "Found a Stone" FAB back on the map; modal = camera scanner only, no login gate, accepts only stonewalker.org / same-origin `/stone-link/...` URLs and navigates to that exact path+query (keeps `?key=`), camera released on close, camera-app fallback hint. Lead. Verified in browser (logged out, mobile).
- [ ] **F24 User reports an error after "Create New Stone" while logged out** — not reproduced: button → `/accounts/log-in/?next=/create-stone/` works on prod and local. Suspect a later step (sign-up → activation email; prod deletes the new user if the email send fails, NEW-13). Need exact message/step from user.
- [ ] **F25 Login page renders the footer links at the top under the header** (content is a fixed modal, so the footer has nothing above it). Cosmetic.
- [ ] **F20 Prod DB helper (`./db`, `postgres_production.json`) points at old Aiven host** — can't inspect prod. Needs user.

## Accounts / templates (from second audit)

- [DONE] **A1 Email-change pending ⇒ anon find form logs attacker in** — merged into F5 (lead).
- [DONE] (accounts) **A2 Prod setting name mismatch** — production sets `EMAIL_ACTIVATION_AFTER_CHANGING`, code reads `ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE` ⇒ unverified email changes on prod. Files: `app/conf/production/settings.py`, `accounts/views.py`. Depends on F5.
- [DONE] (accounts) **A3 Discourse SSO passes unverified emails** — add `require_activation` / refuse for unconfirmed. Files: `accounts/views.py`, `accounts/discourse_sso.py`
- [DONE] (accounts) **A4 Old email-change link confirms a different (newer, unverified) address**; signup codes and change codes interchangeable. Files: `accounts/views.py`
- [DONE] (accounts) **A5 Every profile save wipes notify_* and social fields** (not rendered in form). Files: `accounts/views.py`, `accounts/forms.py`, profile templates
- [DONE] (accounts) **A6 Profile unsavable while email unconfirmed** (disabled required input). Files: profile templates, `accounts/forms.py`
- [DONE] (accounts) **A7 Header profile modal broken** (innerHTML scripts don't run; success redirect injects full page). Files: `layouts/default/page.html`, `assets/js/header.js`, profile templates
- [DONE] (accounts) **A8 Password reset doesn't confirm email / release held finds** ⇒ email-first finders stuck. Files: `accounts/views.py`
- [DONE] (accounts) **A9 Username change lost when email also changes** (no save). Files: `accounts/views.py`
- [DONE] (accounts) **A10 Sign-up 500 when email pending on another account** (EmailAddressState unique). Files: `accounts/forms.py`, `accounts/views.py`
- [DONE] (accounts) **A11 `resizeImage` global clash on profile page** ⇒ TypeError on large images. Files: profile templates
- [DONE] (accounts) **A12 Client image validation never runs** on stone_edit / claim_stone / stone_found (parse-time `typeof` check). Files: those templates
- [DONE] (accounts) **A13 Low:** trans-in-JS HTML-escaped (`&#x27;`), Escape key on login/signup modals navigates away, sign-up drops `next`, debug `print`, empty `LANGUAGE_CODE` (no i18n context processor), double flash messages, Edit-Profile selector never matches, `sync-breakpoints.js` regex no-op.
- [DONE] (accounts) **NEW-4 Profile password change needs no current password and works while the email is unconfirmed** (provisional finders squat an address). Files: `accounts/forms.py`, `accounts/views.py`, profile templates
- [DONE] (accounts) **NEW-5 Cancel email change confirms a never-verified `old_email`.** Files: `accounts/views.py`
- [DONE] (accounts) **NEW-19 `resend_activation_code` has no link in the UI.** Files: `accounts/templates/accounts/log_in.html`
- [DONE] **X1 Stored XSS in `stone-modal.js`** (description/username/comment into innerHTML) + `my_stones.html` fallback — merged into F3 (lead).
- [DONE] **X2 `stone_found.html` shows owner "Unknown"** (`stone.user` vs `FK_user`). Lead.
- [DONE] **X3 Guest welcome modal never shows** (script order). Lead.
- [DONE] **X4 `/debug/modals/` and `/qr-test/` public in production.** Lead.
- [ ] **X5 `content/static/` committed but stale manifest** — trap; recommend untracking. Needs user.

## From docs agent's "New suspicions" (flows.md)

- [DONE] **NEW-2 Provisional finder's 2nd+ find skipped the hold** (soft session made later POSTs "authenticated"). Held = anonymous or (unconfirmed and no usable password). Lead. Test: `ProvisionalFinderHoldTests`.
- [DONE] **NEW-3 Anonymous find with an email pending on another account → IntegrityError 500 + orphan user.** Now redirects to login. Lead.
- [DONE] **NEW-6 `cleanup_unconfirmed --dry-run` deleted held-find images.** Dry-run check moved first. Lead. (Command still not scheduled anywhere — see pipelines.md.)
- [DONE] **NEW-13 Maileroo `urlopen` had no timeout** (a hung API held a gunicorn worker). Added `timeout=15`. Lead. Missing `MAILEROO_API_KEY` still makes signup fail — config, left as is.
- [DONE] **NEW-14 Failed find-confirmation email silently ignored.** User now sees a warning with the recovery path. Lead.
- [DONE] **NEW-16 No owner notification when held find confirmed** — covered by F15.
- [DONE] **NEW-18 `my_stones.html` JS hardcoded `/stone/…/edit|qr/`** — now `{% url %}` templates + HTML escaping. Lead.
- [DONE] **NEW-9** = X4.
- [DONE] **NEW-7** = P1 PRODUCT, implemented as 1c.
- NEW-1, NEW-10, NEW-11 → payments. NEW-4, NEW-5, NEW-19 → accounts.
- [ ] **NEW-8 Certificate PDF prints the keyed QR URL** (key = only secret for recording finds; certificates get shared). Low — needs product call (the certificate is owner-facing).
- [ ] **NEW-12 Unauthenticated PIL QR generation, no rate limit** (`/api/generate-qr/`, `/api/download-enhanced-qr/`). Low.
- [ ] **NEW-15 QR PNGs written to public `media/qr_codes/{PK}_{uuid}.png`**, orphaned on rename, key in filename. Low-medium.
- [DONE] **NEW-17 Keyless `/stone-link/<n>/` and `/stone/<pk>/share/` show draft/published stones** (sequential numbers ⇒ enumerable). Now hidden for unclaimed/draft unless owner; published stays public pending the P1 product decision. Lead.

## Docs

- [DONE] (docs) **D1 Sitemap** (`sitemap.md`) — every route, auth requirement, template
- [DONE] (docs) **D2 Process flows** (`flows.md`) — stone lifecycle, find flow, email-first finder, shop/Stripe, premium
- [DONE] (docs) **D3 Pipelines** (`pipelines.md`) — CI tests, deploy workflow, QR/PDF generation, static build
- [DONE] (docs) **D4 Translations of new strings** — `makemessages` for all 7 locales (zh-hans merged via msgmerge, since `-l zh_Hans` would create a second dir), 215 strings translated per de/fr/es/it/ru, 242 for zh-hans (27 older gaps too), en filled with msgid. All fuzzy cleared after review. Also fixed pre-existing QA failures: de "Welcome to StoneWalker!" was "Hallo bei…" → "Willkommen bei…", zh-hans header had an empty `Language:`. **Chinese never rendered on the site**: Django only looks in `locale/zh_Hans/`, not `zh-hans/`. I renamed the dir with `git mv` (the rename is staged) and added a `zh-hans -> zh_Hans` symlink (untracked) so the QA tests still find it. `translation_tests.py`: 9 passed. Files: `content/locale/**`
