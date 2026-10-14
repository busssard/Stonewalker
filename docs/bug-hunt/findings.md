
## Accounts fixes (accounts agent)

Tests: `source/accounts/test_bughunt.py`.

- **A2** Prod set `EMAIL_ACTIVATION_AFTER_CHANGING`; code reads `ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE` → prod email changes applied unverified. Renamed in `app/conf/production/settings.py`.
- **A3** SSO vouched for unverified emails. `discourse_sso.generate_discourse_payload` now sends `require_activation=true` unless `user.email` is verified (a pending change's old, confirmed address still counts). Tests: `DiscourseSSOActivationTests`.
- **A4** `ChangeEmailActivateView` copied `email_state.email` regardless of the link's `act.email`; signup and change codes were interchangeable. Now: `ActivateView` only accepts `email=''` codes, the change view only accepts `email!=''` codes that match the still-pending address; a new change request deletes older change links; confirming also releases held finds. Tests: `EmailChangeActivationTests`.
- **A5** Profile save wrote social/notify fields from cleaned_data even though no template renders them → wiped. Now only updates social fields present in POST, notify prefs only when notify_* (or a `notify_prefs` marker) is posted. Test: `ProfileSavePreservesFieldsTests`.
- **A6** Disabled + required email input ⇒ "This field is required". Input is now `readonly`; form field `required=False` and falls back to current email; re-submitting the own pending address is not treated as a new change. Also: changing an email whose current address is itself unverified (email-first finder) is refused — change + "cancel" used to flag the unverified address as confirmed. Tests: `ProfileUnconfirmedEmailTests`.
- **A7** Header modal: fragment scripts never ran (innerHTML), success redirect injected a full page. Modal JS moved to new `content/assets/js/profile-modal.js` (loaded for authenticated users; binds picture/username/cancel after each insert; URL comes from a language-prefixed `data-url`). `?modal=1` success returns `{"success": true}` → page reloads so flash messages show. Removed old modal code from `page.html` and `header.js`. Tests: `ProfileModalTests`.
- **A8** Password reset didn't confirm the email / release held finds. `RestorePasswordConfirmView` now confirms `EmailAddressState` when it matches `user.email`, calls `confirm_pending_finds` and `grant_early_premium`. Tests: `PasswordResetConfirmsEmailTests`.
- **A9** Username not saved when email change requires verification. Username is now saved before the email branches. Test: `UsernameAndEmailChangeTests`.
- **A10** Sign-up with an email pending on another account → IntegrityError. `SignUpForm.clean_email` also checks `EmailAddressState`; creation wrapped in `transaction.atomic`. Test: `SignUpPendingEmailTests`.
- **A11** Local `resizeImage` in `change_profile.html` clobbered by `window.resizeImage` from image-upload.js → renamed `resizeProfileImage`.
- **A12** `typeof setupImageUpload` ran before image-upload.js loaded → wrapped in DOMContentLoaded in stone_edit/claim_stone/stone_found.
- **A13** i18n context processor added (dev + prod) → `<html lang>` set; `trans` strings in change_profile.html JS use `escapejs`; Escape on login/sign-up no longer navigates away while focus is in a field; sign-up "Log in" link forwards `?next=`; debug `print` removed; duplicate flash loops removed from stone_edit, claim_stone, premium, premium_manage, shop (page.html renders them); stale Edit-Profile selector replaced (now `a[href$="/accounts/change/profile/"]` in profile-modal.js). `sync-breakpoints.js`: left as is — it replaces each value with itself by design (can't know old values); needs a rewrite, not a trivial fix.

## Lead fixes (scan / find / map)

### F1 — Logged-in finders could never record a find (why the map was empty)
- **Root cause:** `StoneLinkView.get` recorded a `StoneScanAttempt` to render the find form; `post()` then checked `StoneScanAttempt.can_scan_again` and rejected the find as "already scanned this week". Tests posted without the preceding GET, so they never caught it. The production map JSON was `[]`.
- **Fix:** blackout is now keyed on recorded finds: `StoneMove.found_recently(stone, user)` (`main/models.py`), used by both GET and POST of `StoneLinkView`. GET still records the attempt, because `can_last_minute_edit` uses it.
- **Tests:** `test_scan_then_submit_find_records_move` (real GET→POST flow, then asserts the stone is on the map) and `StoneLinkBlackoutTests`, which covers reloading the link and a second find within vs after the week.

### F2 — `/stone/<pk>/qr/` returned 500 when logged out
- **Fix:** added `login_required`. Seen live on stonewalker.org.

### F3 / X1 — Stored XSS
- **Map and share-page JSON:** now emitted via `_script_safe_json`, which escapes `<`, `>` and `&` the same way `json_script` does.
- **`stone-modal.js`:** every user value goes through `esc()`, and colour is validated as hex. `StoneEditView` only accepts `#rrggbb` colours.
- **Test:** `MapDataEscapingTests`.

### F5 / A1 — Account takeover via the anonymous find form
- **Behaviour now:** the form never logs anyone into an existing account. A real account (confirmed, or with a usable password, e.g. one with an email change pending) is sent to login. An earlier provisional account gets the held find and a confirmation email, but no session.
- **Test:** `AnonymousFindAccountSafetyTests`.

### F6 — Legacy `/stonescan/` removed
- It had no links, created confirmed moves for any stone by name and ignored the key and status.
- Removed the route, `StoneScanView` and `stone_scan.html`. The blackout tests that used it now go through `/stone-link/`.

### F7 — Find POST allowed on non-wandering stones
- `post()` now rejects anything not `wandering`, matching GET, and no longer auto-seals published stones.
- **Test:** `test_find_on_non_wandering_stone_rejected`.

### Smaller fixes
- **F13:** redirects built with `reverse()` helpers (`_map_focus_url`, `_stone_edit_url`, `_stone_link_key_url`) keep the language prefix.
- **F14:** move creation and attempt recording happen in one `transaction.atomic()`, move first.
- **F15:** held finds don't email the owner. `confirm_pending_finds` sends the notification on release (`notify_owner_of_find` in `main/signals.py`).
  - **Test:** `HeldFindNotificationTests`.
- **F16:** unknown or missing `action` in the stone edit POST now redirects with an error instead of returning a 500.
- **F17:** one `client_ip(request)` helper (X-Real-IP from nginx, else REMOTE_ADDR, validated) is used for both storing attempts and the anonymous rate limit.
- **X2:** the stone-found page showed "Unknown" for the owner (`stone.user` → `stone.FK_user.username`).
- **X3:** the guest welcome modal script now runs on DOMContentLoaded, after `showWelcomeModal` is defined.
- **X4:** `/debug/modals/` and `/qr-test/` are only routed when `DEBUG`.

## Payments (F4, F8–F12) — owner: payments

Tests: `source/main/tests/test_payments_hardening.py` (27 tests; they failed before the fixes and pass now).

- **F4 Premium subscriptions not linked to the payer.** Cause: `user_id` was only set on the Checkout Session's metadata. Stripe does not copy that to the Subscription, and `checkout.session.completed` was ignored for `mode=subscription`. Fix: the session now also sets `client_reference_id` and `subscription_data.metadata`. The new `handle_subscription_checkout_completed` links the customer and subscription to the user and never overwrites a status that `customer.subscription.*` already recorded. `_get_or_create_stripe_customer` reuses an existing Customer (`Customer.search` on `metadata.user_id`) instead of creating a new one on every checkout. Side fix: `_handle_subscription_created` no longer matches `stripe_customer_id=''`, which could have linked a subscription to a random lifetime user.
- **F8 Stone-number race.** Cause: `Max+1` with no lock. Fix: `Stone.save` assigns the number inside a savepoint and retries (up to 10 times) when the number was taken; any other `IntegrityError` is re-raised. Fulfilment now tops up to `pack_size` (`StripeService._fulfill_pack`) instead of accepting a partial set of stones.
- **F9 Double fulfilment.** Cause: the webhook committed `paid` and then created stones outside any lock, while the success page could fulfil the same pack at the same time. Fix: the webhook locks the pack (`select_for_update`) and marks it paid, creates the stones and marks it fulfilled in one transaction. The success page calls `StripeService.fulfill_paid_pack_fallback`, which uses `select_for_update(skip_locked=True)` on `status='paid'` packs only. No new status, so no migration. The old `CheckoutSuccessView._generate_pack_pdf` was removed. A `TransactionTestCase` covers the race with a real concurrent thread.
- **F10 Stone names.** Fix: `validators.validate_stone_name` allows only `^[A-Za-z0-9_-]{1,10}$`. Error codes are empty/whitespace/too_long/invalid_chars, and the first three reuse the already-translated messages. It is used by `ClaimStoneView` and by `check_stone_name`, whose `reason` is now the error code. Open: the new msgid "Stone name can only contain letters, numbers, hyphens and underscores." still needs translations. `claim_stone.html` still has `pattern="[^\s]+"` (template, lead-owned).
- **F11 Unsigned webhooks.** Fix: when `STRIPE_WEBHOOK_SECRET` is empty, the webhook returns 400 unless `DEBUG` is on.
- **F12 QR download.** Fix: `DownloadStoneQRView` requires the user to own the stone or own its pack. Stones with no pack and no owner are blocked.

- **NEW-4** (accounts) The profile password change asked for no current password and worked before the email was confirmed, so a provisional finder could squat an address. `CombinedProfileForm` now has `current_password`, which is required whenever the user already has a usable password. Setting a password is refused until `user.email` is verified, and the error points to the confirmation email and the resend button on the profile. The input is rendered in both the profile page and the modal. The helper moved to `accounts.models.is_current_email_verified`, which Discourse SSO also uses. Password reset for provisional users was already fixed by A8, which confirms the email and releases held finds. Tests: `ProfilePasswordChangeTests`.
- **NEW-5** (accounts) Cancelling an email change could confirm a never-verified `old_email`. The A6 guard already blocks changes when `user.email` is unverified. As a second layer, `ChangeProfileView` now stores `old_email` only when `is_current_email_verified(user)` is true, so a cancel can only restore a verified address. Tests: `CancelEmailChangeTests`, plus `test_cannot_change_unverified_email` from A6.
- **NEW-19** (accounts) The resend-activation page had no link anywhere. The login page now links to it under the "Forgot your password?" and "Forgot your username?" links. Test: `ResendActivationLinkTests`.

## Payments follow-ups (NEW-1, NEW-10, NEW-11, F10 template) — owner: payments

Tests: added to `source/main/tests/test_payments_hardening.py` (40 tests in total). Minting tests in `test_shop_flow.py` now use POST.

- **NEW-1 Premium sold as a one-time shop pack.** Fix: `ShopView` leaves `is_subscription` products out of the product loop (the shop's "Support Us" link still goes to /premium/). `CheckoutView` redirects subscription products to `premium` before any Stripe session or pack is created.
- **NEW-10 Minting on GET (CSRF).** Fix: `CreateNewStoneView` and `FreeQRView` only mint on POST. A GET never mints: create-stone sends the user to the shop (beyond the allowance) or to My Stones, and free-qr sends them to the shop. URLs and names are unchanged. Templates: My Stones and About use small POST forms with `{% csrf_token %}`. The stonewalker_start FAB submits a hidden POST form. A logged-out user goes POST → login → GET → My Stones, which is one extra click.
- **NEW-11a Success page relied on the webhook.** Fix: for a `pending` pack, `CheckoutSuccessView` calls `StripeService.fulfill_pack_from_session`. That retrieves the Checkout Session, checks `metadata.pack_id` matches and `payment_status == 'paid'`, then runs the same locked `handle_checkout_completed` the webhook uses. If Stripe returns an error, the pack stays pending and the page shows "processing".
- **NEW-11b Paid single-code pack showed nothing.** Fix: `checkout_success.html` now shows per-code "Download QR Code" buttons for a fulfilled pack without a PDF. The "processing" block also appears for `paid`.
- **F10 template:** `claim_stone.html` input now has `pattern="[A-Za-z0-9_-]+"` and title "Letters, numbers, - and _ only". The new msgid needs translations.

## Combined-diff review (fresh-eyes agent) — fixes

- **R1 Anonymous visitors saw public pages for unclaimed stones.** The NEW-17 check compared `FK_user_id != request.user.id`, and for an unclaimed stone viewed while logged out both sides are `None`. Now uses `_is_stone_owner()` (authenticated and matching). Test: `ReviewRegressionTests.test_unclaimed_stone_hidden_from_anonymous`.
- **R2 Changing a stone's type after sealing broke the hiding-spot model.**
  - Hidden → hunted: no public spot.
  - Hunted → hidden: the spot was already public and got drawn twice.
  - Fix: the type is locked once the stone is `wandering`. The server ignores the posted value and the edit page shows a read-only pill. Test: `test_stone_type_locked_after_sealing`.
- **R3 The warning for a failed find-confirmation email pointed to the login-page password reset**, which logged-in (soft-session) finders can't reach. It now points to the profile's "Resend activation code".
- **Checks:** `makemigrations --check` and `manage.py check` are clean. No hide-spot leaks were found in the map JSON, share page, stone-link page, My Stones or the APIs.
- **Not a bug:** the dev `SHOP_VISIBLE_USER_THRESHOLD` 1000→100 change is the user's own pre-existing uncommitted edit, so it was left as is.
