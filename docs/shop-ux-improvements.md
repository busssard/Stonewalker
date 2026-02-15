# Shop UX Improvements

## Summary

The shop page, claim stone page, and checkout success page were redesigned for clarity and better user onboarding. The core problem was that new visitors had no idea what they were buying or why -- the pages showed minimal product cards with no explanation of the QR-to-stone workflow.

## Changes Made

### 1. Shop Page (`source/content/templates/main/shop.html`)

**"How It Works" section added** above product cards:
- 3-step visual flow: Get a QR Code -> Paint & Hide -> Watch It Travel
- Each step has a numbered badge, SVG icon, headline, and short description
- Collapses to vertical on mobile with rotated arrow connectors
- Light green background to visually separate it from products

**Product cards enhanced**:
- Free product gets a green "Start Here" badge and highlighted border
- New `.shop-product-hint` line gives contextual detail (e.g., "No payment needed. Just click and your QR downloads instantly.")
- Per-unit price shown for multi-packs (e.g., "$0.99 each" for 10-pack)
- Button text changed from "Get Free" to "Get Free QR" for clarity

**FAQ section added** below products:
- 3 collapsible `<details>` items answering common questions
- "What do I get when I buy a QR code?"
- "What is the 10-Pack for?"
- "Can I re-download my QR codes later?"

**Floating Purchases bar improved**:
- Added hint text "Click to download your QR codes" in header
- Each pack now shows a count label (e.g., "10 QR codes")
- Stone buttons show the stone name if claimed
- PDF download button now has a download icon and full text instead of just "PDF"

### 2. Claim Stone Page (`source/content/templates/main/claim_stone.html`)

**Progress indicator added**:
- 3-step horizontal progress bar: QR Code (done) -> Name It (active) -> Paint & Hide (upcoming)
- Green dots for completed steps, outlined dot with glow for active step
- Connecting lines in green/gray to show progress

**Copy improved**:
- Welcome message now explains the full journey: "Give it a unique name. After claiming, you can paint your stone, attach the QR code, and hide it for someone to find."
- Removed emoji from heading (was: "Name Your Stone!")
- Button text simplified from "Claim My Stone!" to "Claim My Stone"

### 3. Checkout Success Page (`source/content/templates/main/checkout_success.html`)

**Next steps redesigned**:
- Replaced plain `<ol>` with card-based layout
- Each step gets a green numbered badge, bold action word, and description
- Steps: Print -> Paint & Attach -> Hide -> Track
- More specific copy (e.g., "attach the QR code with clear tape or varnish")

**Header copy changed**:
- "Thank You!" -> "You are all set!" (more informative)
- "Your purchase is complete!" -> "Your QR codes are ready." (focuses on what matters)

### 4. Shop Views (`source/main/shop_views.py`)

**Per-unit price calculation added**:
- `ShopView.get_context_data` now computes `price_per_unit` for multi-packs
- Uses integer division of `price_cents // pack_size` then formats via `format_price()`
- Template conditionally displays it below the total price

## All Text Uses i18n

Every new user-facing string uses `{% trans %}` or `{% blocktrans %}` for translation support.

## Files Modified

| File | Type of Change |
|------|---------------|
| `source/content/templates/main/shop.html` | Major redesign: how-it-works flow, enhanced cards, FAQ |
| `source/content/templates/main/claim_stone.html` | Progress indicator, improved copy |
| `source/content/templates/main/checkout_success.html` | Card-based next steps, clearer messaging |
| `source/main/shop_views.py` | Added per-unit price calculation |
| `docs/shop-ux-improvements.md` | This documentation file |

## Testing

All 13 shop flow tests pass. No new tests needed since changes are template/copy-only with one minor view enhancement (per-unit price is purely presentational).
