---
title: API Endpoints Reference
tags: [api, endpoints, ajax]
last-updated: 2026-02-10
---

# API Endpoints Reference

StoneWalker has several API endpoints used by the frontend via AJAX and for external integrations. All API endpoints return JSON unless otherwise noted.

## Public API Endpoints (No Language Prefix)

These endpoints sit outside the `i18n_patterns` block, so they don't have a language prefix.

### Check Stone Name Availability

```
GET /api/check_stone_name/?PK_stone=<name>
```

Checks if a stone name is available for use.

**Parameters:**
- `PK_stone` (string, required) -- The stone name to check. Falls back to `name` param for backward compatibility.

**Response:**
```json
{
  "taken": false,
  "reason": null,
  "PK_stone": "MyStone"
}
```

**Possible `reason` values:**
- `null` -- Name is available
- `"empty"` -- Empty string provided
- `"whitespace"` -- Name contains whitespace
- `"taken"` -- Name already exists in database

**Auth required:** No

**Source:** `source/main/views.py:check_stone_name`

---

### Check Stone UUID

```
GET /api/check-stone-uuid/<uuid>/
```

Checks if a stone UUID exists in the database. Used by the frontend QR scanner to validate scanned UUIDs.

**Parameters:**
- `uuid` (string, path) -- The UUID to check

**Response:**
```json
{
  "exists": true,
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Error response:**
```json
{
  "exists": false,
  "error": "Invalid UUID format"
}
```

**Auth required:** No

**Source:** `source/main/views.py:check_stone_uuid`

---

### Generate QR Code

```
GET /api/generate-qr/?stone_name=<name>&stone_uuid=<uuid>
```

Generates a QR code image as base64 PNG. Used by the stone creation modal to show a preview before the stone is saved to the database.

**Parameters:**
- `stone_name` (string, required) -- The stone name
- `stone_uuid` (string, required) -- A valid UUID

**Response:**
```json
{
  "success": true,
  "qr_code": "<base64-encoded-PNG>",
  "qr_url": "https://stonewalker.org/stone-link/<uuid>/",
  "stone_name": "MyStone",
  "stone_uuid": "<uuid>"
}
```

The QR code is a 3:4 portrait PNG with the QR image at the top and the cleartext URL at the bottom.

**Auth required:** No (allows preview before login)

**Source:** `source/main/views.py:generate_qr_code_api`

---

### Download Enhanced QR Code

```
GET /api/download-enhanced-qr/?stone_name=<name>&stone_uuid=<uuid>
```

Downloads a branded QR code PNG file. Returns a binary PNG response with `Content-Disposition: attachment`.

**Parameters:**
- `stone_name` (string, required)
- `stone_uuid` (string, required)

**Response:** Binary PNG file download

**Auth required:** No

**Source:** `source/main/views.py:download_enhanced_qr_code`

---

### Stripe Webhook

```
POST /webhooks/stripe/
```

Receives Stripe webhook events for payment processing. CSRF exempt.

**Auth required:** No (verified via Stripe signature)

**Source:** `source/main/stripe_service.py:stripe_webhook`

---

## Authenticated API Endpoints

### Check Username Availability

```
GET /accounts/api/check_username/?username=<name>
```

Checks if a username is available for registration or profile update.

**Parameters:**
- `username` (string, required) -- The username to check

**Response:**
```json
{
  "taken": false,
  "reason": null,
  "username": "newuser"
}
```

**Possible `reason` values:**
- `null` -- Username available
- `"empty"` -- Empty string
- `"whitespace"` -- Contains whitespace
- `"taken"` -- Already registered

**Auth required:** No

**Source:** `source/accounts/views.py:check_username`

---

## Page Endpoints (HTML Responses)

These are not APIs in the REST sense, but views that accept POST requests and are called by forms:

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/add_stone/` | POST | Yes | Create a new stone |
| `/stonescan/` | GET/POST | Yes | Scan a stone (log a move) |
| `/stone/<pk>/edit/` | GET/POST | Yes | Edit a draft stone |
| `/stone/<pk>/send-off/` | POST | Yes | Send off a published stone |
| `/stone-link/<uuid>/` | GET/POST | Mixed | Stone found page, log find |
| `/claim-stone/<uuid>/` | GET/POST | Yes | Claim an unclaimed stone |
| `/shop/checkout/<id>/` | POST | Yes | Purchase a product |
| `/shop/free-qr/` | GET | Yes | Get free QR code |
| `/accounts/change/profile/` | GET/POST | Yes | Edit profile |

## Frontend JavaScript Integration

The frontend calls these APIs primarily from:

- `source/content/templates/main/new_add_stone_modal.html` -- Calls `/api/check_stone_name/` and `/api/generate-qr/` during stone creation
- `source/content/templates/main/shared_modals.html` -- Calls `/api/check-stone-uuid/` during QR scanning
- `source/content/assets/js/header.js` -- Calls `/accounts/api/check_username/` during profile editing

## Related Pages

- [[architecture]] -- Overall system architecture
- [[features/qr-system]] -- QR code generation details
- [[features/shop]] -- Shop and checkout flow
