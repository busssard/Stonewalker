# Sitemap — every route

Snapshot: working tree of `refactor/coherence-and-qr-reliability` on 2026-09-26 (base `2b6a940`), while other agents were fixing bugs. `/stonescan/` has already been removed from the working tree (F6). Line numbers can drift. Source: `source/app/urls.py`, `source/accounts/urls.py`.

## Language prefixes

- `i18n_patterns(..., prefix_default_language=False)` (`app/urls.py:40-92`) plus `LocaleMiddleware` in both settings files. **English (`LANGUAGE_CODE='en'`) has no prefix**: `https://stonewalker.org/shop/`. The other languages get one: `/de/shop/`, `/fr/`, `/es/`, `/it/`, `/ru/`, `/zh-hans/`.
- An `/en/...` path also resolves (Django accepts the explicit default prefix). A bare path always serves English, whatever the cookie says, because `prefix_default_language=False` makes an unprefixed path mean English.
- The consequence: a hardcoded `'/stone/...'` or `'/stonewalker/?focus='` redirect drops a German user into English (F13). `main/views.py` now uses `_map_focus_url()` / `_stone_edit_url()`, but the **JS in `my_stones.html:216,234` still builds `/stone/${pk}/edit/` and `/stone/${pk}/qr/`**.
- Not prefixed: `admin/`, `i18n/` (Django `set_language`, POST), `api/*`, `webhooks/stripe/`, `robots.txt`, and `/media/` (DEBUG only; nginx serves it on prod).
- `ChangeLanguageView` strips the `/(en|ru|zh-hans|fr|es|de|it)/` prefix from the Referer path and hands it to `set_language` as `next`.

## Main routes (`app/urls.py`)

Auth: **no** = public · **login** = `login_required`/`LoginRequiredMixin` · **owner** = the query filters by `FK_user=request.user` · **confirmed** = `_require_confirmed_email` (email-first accounts are bounced to My Stones) · **key** = `?key=`/`stone_uuid` must equal `stone.uuid`.

| Path | Name | View | Auth | Methods | Template | Notes |
|---|---|---|---|---|---|---|
| `/` | `index` | `StoneWalkerStartPageView` | no | GET | `main/stonewalker_start.html` | Duplicate of `/stonewalker/`. `IndexPageView` + `main/index.html` are imported but not routed (dead). `LOGIN_REDIRECT_URL='index'` |
| `/stonewalker/` | `stonewalker_start` | same | no | GET | same | Map. Only stones with ≥1 **confirmed** move are included (`views.py:143`) ⚠ see flows.md §a |
| `/my-stones/` | `my_stones` | `MyStonesView` | login | GET | `main/my_stones.html` | Owned stones, unclaimed codes via `FK_pack__FK_user`, fulfilled packs, interactions |
| `/add_stone/` | `add_stone` | `add_stone` (fn) | login | any | — (redirect) | Deprecated: redirects to `terms` or `create_stone`. Only linked from `shared_modals.html` and the orphan `new_add_stone_modal.html` |
| `/forum/` | `forum` | `TemplateView` | no | GET | `main/forum.html` | **Orphan**: the nav links to `https://forum.stonewalker.org` instead |
| `/create-stone/` | `create_stone` | `CreateNewStoneView` | login+confirmed | GET | — (redirect) | ⚠ **Mints a QRPack and an unclaimed Stone on GET** (CSRF-able, burns the free allowance) |
| `/premium/` | `premium` | `PremiumView` | no | GET | `main/premium.html` | Pricing hidden below `SHOP_VISIBLE_USER_THRESHOLD` users |
| `/premium/checkout/` | `premium_checkout` | `PremiumCheckoutView` | login | POST | — | Stripe subscription Checkout. `plan` POST param → `premium_<plan>` |
| `/premium/manage/` | `premium_manage` | `PremiumManageView` | login | GET | `main/premium_manage.html` | Also the subscription `success_url` (`?subscription=1`, ignored) |
| `/premium/billing/` | `premium_billing` | `PremiumBillingPortalView` | login | POST | — | Stripe Billing Portal. Needs `Subscription.stripe_customer_id` |
| `/shop/` | `shop` | `ShopView` | no | GET | `main/shop.html` | ⚠ Lists **every** enabled product, including `premium_monthly/yearly`, each with a "Buy Now" that POSTs to `checkout` (see flows.md §c) |
| `/shop/checkout/<str:product_id>/` | `checkout` | `CheckoutView` | login+confirmed | POST | — | Free path → `_handle_free_product`. Paid path → Stripe Checkout (mode=payment) |
| `/shop/success/` | `checkout_success` | `CheckoutSuccessView` | login, pack owner | GET | `main/checkout_success.html` | `?pack_id=`. ⚠ The GET can fulfil a pack (fallback) |
| `/shop/download/<uuid:pack_id>/` | `download_pack_pdf` | `DownloadPackPDFView` | login, pack owner | GET | — (PDF) | Regenerates the PDF on **every** download |
| `/shop/download-qr/<int:n>/` | `download_stone_qr` | `DownloadStoneQRView` | login (pack owner **only if the stone has a pack**) | GET | — (PNG) | F12 |
| `/shop/free-qr/` | `free_qr` | `FreeQRView` | login+confirmed | GET | — (PNG) | **Orphan** legacy route. ⚠ Mints on GET |
| `/claim-stone/<int:n>/` | `claim_stone` | `ClaimStoneView` | login+confirmed+key | GET, POST | `main/claim_stone.html` | Linked from `my_stones.html` and redirected to from `stone_link` |
| `/about/` | `about` | `TemplateView` | no | GET | `main/about.html` | |
| `/impressum/` | `impressum` | `ImpressumView` | no | GET | `main/impressum.html` | Reads `main/impressum.json` |
| `/privacy/` | `privacy` | `PrivacyView` | no | GET | `main/privacy.html` | same JSON |
| `/terms/` | `terms` | `accounts.views.TermsView` | GET no / POST login | GET, POST | `accounts/terms.html` | POST records `TermsAcceptance`, then redirects to a safe `next` |
| `/stone/<str:pk>/edit/` | `stone_edit` | `StoneEditView` | login+owner | GET, POST | `main/stone_edit.html` | Editable if draft, or if `?key=` and `can_last_minute_edit()`. `<str:>` can't reverse names containing `/` (F10) |
| `/stone/<str:pk>/qr/` | `stone_qr` | `StoneQRCodeView` | login+owner | GET | — (PNG) | unclaimed/draft/published only. F2 fixed |
| `/stone/<str:pk>/certificate/` | `stone_certificate` | `StoneCertificateView` | login+owner | GET | — (PDF) | Wandering only. ⚠ The PDF prints the keyed URL |
| `/stone/<str:pk>/send-off/` | `stone_send_off` | `StoneSendOffView` | login+owner | POST | — | **The seal action** (draft/published → wandering). Old docs call it "deprecated" (wrong) |
| `/stone/<str:pk>/share/` | `stone_share` | `StoneShareView` | no | GET | `main/stone_share.html` | **Orphan** (no template links; keyless `stone_link` renders the same template). Shows draft/published stones too |
| `/stone-link/<int:n>/` | `stone_link` | `StoneLinkView` | GET no / key | GET, POST | `stone_share.html` / `stone_seal_confirm.html` / `stone_found.html` | The QR target. Full flow in flows.md §b |
| `/stone-link/<uuid>/` | `stone_link_legacy` | `StoneLinkLegacyRedirectView` | no | GET | — | For old printed QR codes. No template link needed, and it **must stay** |
| `/debug/modals/` | `debug_modals` | `TemplateView` | no | GET | `main/debug_modals.html` | ⚠ **Debug page routed in production** |
| `/qr-test/` | `qr_test` | `TemplateView` | no | GET | `main/qr_test.html` | ⚠ **Debug page routed in production** (links to `/debug/modals/`) |
| `/language/` | `change_language` | `ChangeLanguageView` | no | GET | `main/change_language.html` | Form POSTs to `set_language` |
| `/accounts/…` | — | `include('accounts.urls')` | | | | See below |

## Unprefixed routes

| Path | Name | View | Auth | Methods | Notes |
|---|---|---|---|---|---|
| `/admin/` | — | Django admin | staff | * | |
| `/i18n/setlang/` | `set_language` | Django | no | POST | Used by `change_language.html` |
| `/api/generate-qr/` | `generate_qr_api` | `generate_qr_code_api` | no | GET | Base64 PNG (PIL) for any UUID. Used by `shared_modals.html`, `new_add_stone_modal.html`, `assets/js/qr-code.js`. ⚠ Unauthenticated CPU work with no rate limit |
| `/api/download-enhanced-qr/` | `download_enhanced_qr` | `download_enhanced_qr_code` | no | GET | Only the orphan `new_add_stone_modal.html` uses it. For an unknown UUID it builds a `TempStone` whose URL is `/stone-link/0/?key=…` |
| `/api/check-stone-uuid/<uuid>/` | `check_stone_uuid` | fn | no | GET | UUID existence check (oracle, low risk) |
| `/api/check_stone_name/` | `check_stone_name` | fn | no | GET | Only the orphan `new_add_stone_modal.html` uses it. Validation doesn't match `ClaimStoneView` (F10) |
| `/webhooks/stripe/` | `stripe_webhook` | fn | Stripe signature (F11: skipped if the secret is empty) | POST, csrf_exempt | |
| `/robots.txt` | `robots_txt` | `TemplateView` | no | GET | `templates/robots.txt` |
| `/media/…` | — | `static()` | no | GET | DEBUG only. On prod nginx serves `content/media/` (includes `qr_codes/{PK}_{uuid}.png`) |

## Accounts (`accounts/urls.py`, `app_name='accounts'`, under the i18n prefix at `/accounts/`)

| Path | Name | View | Auth | Methods | Template | Notes |
|---|---|---|---|---|---|---|
| `log-in/` | `log_in` | `LogInView` | guest only | GET, POST | `accounts/log_in.html` | Email-or-username on prod, email on dev. Honours a safe `next` |
| `log-out/confirm/` | `log_out_confirm` | `LogOutConfirmView` | login | GET | `accounts/log_out_confirm.html` | Nav link |
| `log-out/` | `log_out` | `LogOutView` (Django `LogoutView`) | login | POST (GET is deprecated in 4.2 but still works) | `accounts/log_out.html` | |
| `resend/activation-code/` | `resend_activation_code` | `ResendActivationCodeView` | guest | GET, POST | `accounts/resend_activation_code.html` | **Orphan**: no template link, so a user who loses the activation mail has no path in the UI |
| `sign-up/` | `sign_up` | `SignUpView` | guest | GET, POST | `accounts/sign_up.html` | Stores a safe `next` in the session as `post_activation_redirect` |
| `activate/<code>/` | `activate` | `ActivateView` | no (code) | GET | — | Signup codes only (`email=''`, A4 fix). Grants early premium |
| `restore/password/` | `restore_password` | `RestorePasswordView` | guest | GET, POST | `accounts/restore_password.html` | |
| `restore/password/done/` | `restore_password_done` | `RestorePasswordDoneView` | no | GET | `accounts/restore_password_done.html` | |
| `restore/<uidb64>/<token>/` | `restore_password_confirm` | `RestorePasswordConfirmView` | token | GET, POST | `accounts/restore_password_confirm.html` | ⚠ Doesn't confirm the email and doesn't release held finds (flows.md §e) |
| `confirm/<uidb64>/<token>/` | `confirm_account` | `ConfirmAccountView` | token | GET, POST | `accounts/confirm_account.html` | Email-first finder: sets a password, which confirms the email and releases held finds |
| `remind/username/` | `remind_username` | `RemindUsernameView` | guest | GET, POST | `accounts/remind_username.html` | |
| `change/profile/` | `change_profile` | `ChangeProfileView` | login | GET, POST | `accounts/profile/change_profile.html` (`?modal=1` → `change_profile_form.html`) | ⚠ Sets a new password without asking for the current one |
| `change/email/<code>/` | `change_email_activation` | `ChangeEmailActivateView` | no (code) | GET | — | Change codes only (A4 fix) |
| `resend-email-activation/` | `resend_email_activation` | `ResendEmailActivationView` | login | POST | — | |
| `cancel-email-change/` | `cancel_email_change` | `CancelEmailChangeView` | login | POST | — | ⚠ Marks `old_email` confirmed even if it never was (flows.md §e) |
| `api/check_username/` | `check_username` | fn | no | GET | — | Username enumeration (low) |
| `discourse-sso/` | `discourse_sso` | `DiscourseSSOView` | Discourse HMAC, then login | GET | — | A3 (`require_activation`) is being fixed |

## Orphans and dead code

- **Orphaned routes** (nothing links to them): `forum`, `free_qr`, `stone_share`, `resend_activation_code`, `debug_modals`, `qr_test`. `add_stone` is linked only from a modal. `stone_scan` has been removed (F6).
- **Orphan templates** (never rendered): `main/stone_sealed.html` (old docs still describe it as the post-seal page), `main/new_add_stone_modal.html` (not `{% include %}`d anywhere; it is the only user of `/api/check_stone_name/` and `/api/download-enhanced-qr/`), and `main/index.html` (its view is not routed).
- **Dead code**: `IndexPageView`, `Stone.user_can_create_stone` / `get_user_draft_stone` (the "1 draft" limit is not enforced anywhere), the stray `Command` class at the bottom of `main/models.py`, and `source/_old_qr_implementation/`.
- **Email-only entry points** (fine): `activate`, `confirm_account`, `restore_password_confirm`, `change_email_activation`.
