---
title: Authentication System
tags: [feature, auth, accounts, login, signup]
last-updated: 2026-02-10
---

# Authentication System

StoneWalker uses Django's built-in authentication with several extensions for email verification, profile management, and Discourse SSO.

## Registration Flow

1. User visits `/accounts/sign-up/` (renders as a modal-style popup overlay)
2. Fills in username, email, password
3. Backend creates the user with `is_active=False`
4. An `Activation` record is created with a random 20-character code
5. Activation email is sent (console in dev, Maileroo in production)
6. If email fails to send, the user and activation are deleted to allow re-registration
7. User clicks the activation link: `/accounts/activate/<code>/`
8. User is activated (`is_active=True`), activation record is deleted

## Login

- Supports login via username, email, or both (configurable in settings)
- "Remember me" checkbox controls session duration
- Safe redirect after login (validates `next` parameter)
- CSRF protection, test cookie verification

## Password Reset

1. User visits `/accounts/restore/password/`
2. Enters email or username
3. Backend sends reset email with a signed token
4. User clicks link: `/accounts/restore/<uidb64>/<token>/`
5. Sets new password

## Profile Editing

Profile editing works via a modal overlay accessible from the header:

- **URL:** `/accounts/change/profile/` (or with `?modal=1` for AJAX loading)
- **Editable fields:** Username, email, password, profile picture
- **Email change** requires re-verification:
  - Sends activation email to the new address
  - Old email is stored in `EmailAddressState.old_email` for rollback
  - User can cancel the change to revert
  - Rate limited to 3 attempts per 15 minutes via `EmailChangeAttempt`

## Models

| Model | Purpose |
|-------|---------|
| `Profile` | 1:1 with User, stores profile picture |
| `Activation` | Email verification codes (signup and email change) |
| `EmailAddressState` | Tracks current/pending email state |
| `EmailChangeAttempt` | Rate-limiting for email changes |

The `Profile` model is auto-created via a `post_save` signal on `User`.

## Discourse SSO (DiscourseConnect)

StoneWalker can act as an SSO provider for a Discourse forum:

- **View:** `DiscourseSSOView` at `/accounts/discourse-sso/`
- **Implementation:** `source/accounts/discourse_sso.py`
- **Flow:**
  1. User clicks "Forum" in Discourse
  2. Discourse redirects to StoneWalker with a signed payload
  3. If not logged in, redirect to login with `next` pointing back to SSO
  4. Validate payload signature
  5. Return signed response with user data (id, email, username, avatar)
  6. Discourse logs the user in

**Configuration:**
```python
# Development
DISCOURSE_URL = 'http://localhost:4200'
DISCOURSE_SSO_SECRET = 'dev_secret_change_me'
DISCOURSE_SSO_ENABLED = True
```

**Status:** The Django SSO endpoint is complete and tested. The local Discourse Docker setup is incomplete (see `forum/README.md`).

## URL Reference

| URL | View | Purpose |
|-----|------|---------|
| `/accounts/sign-up/` | `SignUpView` | Registration |
| `/accounts/log-in/` | `LogInView` | Login |
| `/accounts/log-out/` | `LogOutView` | Logout |
| `/accounts/log-out/confirm/` | `LogOutConfirmView` | Logout confirmation |
| `/accounts/activate/<code>/` | `ActivateView` | Activate account |
| `/accounts/change/profile/` | `ChangeProfileView` | Edit profile |
| `/accounts/change/email/<code>/` | `ChangeEmailActivateView` | Confirm email change |
| `/accounts/resend/activation-code/` | `ResendActivationCodeView` | Resend signup activation |
| `/accounts/resend-email-activation/` | `ResendEmailActivationView` | Resend email change activation |
| `/accounts/cancel-email-change/` | `CancelEmailChangeView` | Cancel pending email change |
| `/accounts/restore/password/` | `RestorePasswordView` | Start password reset |
| `/accounts/restore/<uidb64>/<token>/` | `RestorePasswordConfirmView` | Set new password |
| `/accounts/remind/username/` | `RemindUsernameView` | Get username via email |
| `/accounts/api/check_username/` | `check_username` | Username availability API |
| `/accounts/discourse-sso/` | `DiscourseSSOView` | Discourse SSO |

## Security Notes

- All auth forms have CSRF protection
- Passwords are hashed using Django's default (PBKDF2)
- Session-based authentication
- Profile picture uploads are validated as images
- Email change rate limiting prevents abuse

## Related Pages

- [[architecture]] -- Account models and views in context
- [[features/stone-management]] -- Auth requirements for stone operations
- [[api]] -- Username availability API
