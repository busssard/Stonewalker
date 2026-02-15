---
title: Shop System
tags: [feature, shop, stripe, payments, qr-packs]
last-updated: 2026-02-10
---

# Shop System

The shop allows users to acquire QR codes for their stones. It supports both free and paid products via Stripe.

## Products

Products are configured via `source/main/shop_utils.py` (not in the database):

| Product ID | Name | Price | Pack Size | Limit per User |
|------------|------|-------|-----------|----------------|
| `free_single` | Free Single QR | Free | 1 | 1 (bypassed in dev mode) |
| `paid_10pack` | 10-Pack QR Codes | Paid | 10 | None |

## User Flow

### Free QR Code
1. User visits `/shop/`
2. Clicks "Get Free QR" on the free single product
3. `CheckoutView` handles the POST, calls `_handle_free_product()`
4. Creates a `QRPack` with `status='fulfilled'`
5. Creates an `unclaimed` Stone with a temporary name (e.g., `UNCLAIMED-ABC12345`)
6. Generates the QR code and returns it as a download
7. User prints the QR code and attaches it to a stone
8. Later, user visits `/create-stone/` which finds the unclaimed stone and redirects to claim it

### Paid 10-Pack
1. User visits `/shop/` and selects the 10-pack
2. `CheckoutView` creates a Stripe Checkout session via `StripeService.create_checkout_session()`
3. User is redirected to Stripe's hosted checkout page
4. After payment, Stripe sends a webhook to `/webhooks/stripe/`
5. Webhook handler fulfills the pack (creates 10 unclaimed stones, generates PDF)
6. User is redirected to the success page
7. User can download the PDF with all 10 QR codes

### Claiming a Stone
1. User visits `/create-stone/` (`CreateNewStoneView`)
2. View checks for unclaimed stones in the user's fulfilled packs
3. If found, redirects to `/claim-stone/<uuid>/` (`ClaimStoneView`)
4. User enters a name, description, and optional image
5. The old temporary PK is deleted, a new Stone is created with the user's chosen name
6. The UUID and QR code URL are preserved
7. Stone status changes from `unclaimed` to `draft`

## Architecture

### Key Files

| File | Purpose |
|------|---------|
| `source/main/shop_views.py` | All shop views (ShopView, CheckoutView, ClaimStoneView, etc.) |
| `source/main/shop_utils.py` | Product configuration, pricing utilities |
| `source/main/stripe_service.py` | Stripe integration (checkout sessions, webhooks) |
| `source/main/pdf_service.py` | PDF generation for multi-QR packs |
| `source/main/qr_service.py` | QR code generation service |
| `source/main/models.py:QRPack` | Pack tracking model |
| `source/content/templates/main/shop.html` | Shop page template |
| `source/content/templates/main/claim_stone.html` | Claim stone template |
| `source/content/templates/main/checkout_success.html` | Post-purchase page |

### QRPack Lifecycle

```
[pending] --> [paid] --> [fulfilled]
    |                        |
    v                        v
 [failed]               (stones created,
                          PDF generated)
```

For free products, the pack goes directly to `fulfilled` status.

### Stripe Configuration

```python
# Settings
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
```

The webhook endpoint (`/webhooks/stripe/`) is CSRF exempt and verifies the Stripe signature.

## URL Reference

| URL | View | Purpose |
|-----|------|---------|
| `/shop/` | `ShopView` | Main shop page |
| `/shop/checkout/<id>/` | `CheckoutView` | Purchase a product |
| `/shop/success/` | `CheckoutSuccessView` | Post-purchase page |
| `/shop/download/<pack_id>/` | `DownloadPackPDFView` | Download PDF |
| `/shop/download-qr/<uuid>/` | `DownloadStoneQRView` | Download single QR |
| `/shop/free-qr/` | `FreeQRView` | Legacy free QR endpoint |
| `/create-stone/` | `CreateNewStoneView` | Smart router to claim or shop |
| `/claim-stone/<uuid>/` | `ClaimStoneView` | Claim an unclaimed stone |

## Dev Mode Behavior

When `DEBUG=True`:
- The `free_single` product limit is bypassed (developers can get multiple free QR codes)
- No Stripe keys needed for free products

## Related Pages

- [[features/qr-system]] -- QR code generation details
- [[features/stone-management]] -- What happens after claiming a stone
- [[api]] -- Stripe webhook endpoint
