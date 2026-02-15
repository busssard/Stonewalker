---
title: QR Code System
tags: [feature, qr-code, uuid]
last-updated: 2026-02-10
---

# QR Code System

The QR code system is the core product feature of StoneWalker. Each stone gets a unique QR code that links to its "stone found" page, allowing anyone who finds the stone to log its new location.

## How It Works

1. **Stone creation** -- User fills in the stone creation modal (name, description, type)
2. **UUID generation** -- JavaScript generates a UUID in the browser and calls `/api/generate-qr/` to preview the QR code
3. **QR preview** -- The modal shows a preview of the QR code with the cleartext URL underneath
4. **Form submission** -- The UUID is passed as a hidden form field (`stone_uuid`) so the backend uses the same UUID
5. **Backend saves** -- `add_stone` view creates the Stone with the provided UUID (or auto-generates if missing)
6. **QR persistence** -- `QRCodeService.generate_qr_for_stone()` generates and saves the QR code image

## QR URL Format

All QR codes point to production URLs regardless of environment:

```
https://stonewalker.org/stone-link/<uuid>/
```

The production domain is hardcoded in `Stone.PRODUCTION_DOMAIN` (`source/main/models.py`). This ensures QR codes printed on physical stones always work, even if generated during development.

## QR Code Image Format

- **Dimensions:** 3:4 portrait ratio (QR code at top, text at bottom)
- **QR size:** 400x400 pixels
- **Text area:** 100px below the QR code
- **Cleartext URL:** Displayed beneath the QR code in black text on light background
- **Format:** PNG
- **Font:** DejaVu Sans (Linux) or Arial (fallback), 16px (12px if URL is long)

## Key Files

| File | Purpose |
|------|---------|
| `source/main/qr_service.py` | `QRCodeService` -- generation, download, enhanced QR |
| `source/main/views.py:generate_qr_code_api` | API endpoint for JS preview |
| `source/main/views.py:download_enhanced_qr_code` | Enhanced QR download endpoint |
| `source/main/views.py:StoneQRCodeView` | Download QR for owned stone |
| `source/content/templates/main/new_add_stone_modal.html` | Frontend modal with QR preview |

## The UUID Consistency Problem (Solved)

A previous bug caused QR codes to be invalid immediately after stone creation. The root cause:

1. JavaScript generated UUID-A for the QR preview
2. The form submitted without passing the UUID
3. `Stone(default=uuid.uuid4)` generated UUID-B
4. The QR code pointed to UUID-A, but the database had UUID-B

**Fix:** A hidden `<input name="stone_uuid">` field carries the JS-generated UUID through to the backend. The `add_stone` view reads and uses it:

```python
stone_uuid = request.POST.get('stone_uuid')
if stone_uuid:
    try:
        stone_kwargs['uuid'] = uuid_lib.UUID(stone_uuid)
    except ValueError:
        pass  # Invalid UUID, let model generate one
```

## QR Code Regeneration

If a QR code is lost or corrupted, it can be regenerated:

- **Endpoint:** `GET /stone/<pk>/qr/` -- downloads QR for a stone the user owns
- **Service:** `QRCodeService.generate_qr_for_stone(stone, request)`

The `get_qr_url()` method on the Stone model always returns the canonical production URL and updates the stored `qr_code_url` field if it differs.

## Error Handling

QR code generation is designed to be non-blocking:
- If QR generation fails during stone creation, the stone is still saved
- The user gets a success message with a note that QR generation failed
- They can regenerate the QR code later from the stone edit page

## Dependencies

- `qrcode==7.4.2` -- QR code generation
- `pillow==10.0.1` -- Image manipulation (creating the 3:4 portrait format, adding text)

## Related Pages

- [[api]] -- QR-related API endpoints
- [[features/stone-management]] -- Stone creation workflow
- [[features/scanning]] -- What happens when someone scans the QR code
