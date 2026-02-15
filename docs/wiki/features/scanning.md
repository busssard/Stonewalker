---
title: Stone Scanning & Finding
tags: [feature, scanning, stone-found, cooldown]
last-updated: 2026-02-10
---

# Stone Scanning & Finding

When someone finds a stone in the real world, they scan its QR code. This page describes what happens next.

## The "Stone Found" Flow

1. Person finds a physical stone with a QR code
2. Scans the QR code with their phone camera
3. Browser opens `https://stonewalker.org/stone-link/<uuid>/`
4. `StoneLinkView` handles the request:
   - Looks up the stone by UUID
   - If the stone is `unclaimed` (from shop), redirects to claim flow
   - If the user is authenticated, records a `StoneScanAttempt`
   - Renders the `stone_found.html` template

### Stone Found Page Features

- **Stone information:** Name, type, description, creator
- **First-time detection:** If this is the user's first ever stone scan, shows a welcome explanation
- **Location input:** Interactive Leaflet.js map for selecting where the stone was found
- **Comment and photo:** Optional fields for the finder
- **Hunted stone special handling:** Congratulates the user and asks them to set a new location for the next finder

### Form Submission

When the finder submits the form:

1. **Validates coordinates** -- Must provide valid latitude/longitude
2. **Checks cooldown** -- If the user scanned this stone within the last week, blocks the submission
3. **Records scan attempt** -- Creates/updates `StoneScanAttempt`
4. **Creates StoneMove** -- New movement record with location, comment, and optional photo
5. **Updates distance** -- Recalculates total distance via Haversine formula
6. **For hunted stones** -- Stores the new hiding location in the session
7. **Redirects** to the map page focused on this stone

## Cooldown System

The `StoneScanAttempt` model enforces a **one-week cooldown** per user per stone:

```python
@classmethod
def can_scan_again(cls, stone, user):
    one_week_ago = timezone.now() - timedelta(weeks=1)
    recent_attempt = cls.objects.filter(
        FK_stone=stone, FK_user=user, scan_time__gte=one_week_ago
    ).first()
    return recent_attempt is None
```

- `unique_together = ['FK_stone', 'FK_user']` ensures one record per pair
- On repeat scans, the `scan_time` is updated rather than creating a new record
- The cooldown is checked on both the stone-link GET (shows lock message) and POST (blocks submission)

## Direct Scanning (Legacy)

There's also a direct scan page at `/stonescan/`:

- **GET:** Shows a scan form, optionally pre-filled with `?stone=<PK_stone>` or `?stone=<uuid>`
- **POST:** Creates a StoneMove (same cooldown rules apply)
- Supports both UUID and PK_stone lookup for backward compatibility

## Cookie Tracking

When someone visits a stone-link page, a cookie is set:

```python
response.set_cookie(
    f'stone_scan_{stone_uuid}',
    timezone.now().isoformat(),
    max_age=7*24*60*60,  # 7 days
    httponly=True,
    samesite='Lax'
)
```

This is used for analytics and to track visits even from non-authenticated users.

## Unclaimed Stone Handling

If someone scans a QR code for an `unclaimed` stone (from the shop):
- Authenticated users are redirected to the claim page (`/claim-stone/<uuid>/`)
- Anonymous users are redirected to login, with `next` pointing back to the stone link

## Key Files

| File | Purpose |
|------|---------|
| `source/main/views.py:StoneLinkView` | Stone found page handler |
| `source/main/views.py:StoneScanView` | Direct scan page |
| `source/main/models.py:StoneScanAttempt` | Cooldown enforcement |
| `source/content/templates/main/stone_found.html` | Stone found template |
| `source/content/templates/main/stone_scan.html` | Direct scan template |

## Related Pages

- [[features/qr-system]] -- How QR codes are generated
- [[features/stone-management]] -- Stone lifecycle
- [[features/map]] -- Where stones appear after scanning
