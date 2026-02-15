---
title: Stone Management
tags: [feature, stones, creation, editing, workflow]
last-updated: 2026-02-10
---

# Stone Management

Stones are the core entities in StoneWalker. This page covers creation, editing, publishing, and the full stone lifecycle.

## Stone Lifecycle

```
[unclaimed] --> [draft] --> [published] --> [sent_off]
     |              |
     |  (claim)     |  (edit)
     v              v
  draft          draft
```

### Status Definitions

| Status | Meaning | Can Edit? | On Map? |
|--------|---------|-----------|---------|
| `unclaimed` | Pre-generated from shop, no owner yet | No | No |
| `draft` | Owned by a user, being set up | Yes | No |
| `published` | Visible on the map, ready for journey | No | Yes |
| `sent_off` | Finalized, physically placed in the world | No | Yes |

## Creating a Stone

There are two paths to create a stone:

### Path 1: Direct Creation (Legacy)
1. User clicks "Create New Stone" on the main page
2. The `new_add_stone_modal.html` modal opens (two-step process)
3. **Step 1:** Enter name, description, type (hidden/hunted), and optional image
4. **Step 2:** Preview the QR code, confirm
5. Form submits to `POST /add_stone/`
6. Backend creates the stone as a `draft`

### Path 2: Shop Purchase + Claim
1. User visits the shop (`/shop/`)
2. Purchases a QR pack (free single or paid 10-pack)
3. Backend creates `unclaimed` stones with temporary names like `UNCLAIMED-ABC12345`
4. User is redirected to claim the stone (`/claim-stone/<uuid>/`)
5. User enters a name, description, and optional image
6. Stone status changes from `unclaimed` to `draft`

### Non-Premium Limitation
Non-premium users can only have **one draft stone** at a time. The `Stone.user_can_create_stone(user)` class method enforces this.

## Stone Types

| Type | Shape | Location Required? | Special Behavior |
|------|-------|--------------------|------------------|
| `hidden` | Circle | No | Standard stone, placed anywhere |
| `hunted` | Triangle | Yes (at creation) | Creates initial StoneMove with the location |

For hunted stones, the initial location is provided during creation and a `StoneMove` is automatically created. When someone finds a hunted stone, they're asked to set a new location for the next week.

## Editing a Stone

- **URL:** `GET/POST /stone/<pk>/edit/`
- **View:** `StoneEditView` (`source/main/views.py`)
- **Editable fields:** Description, image, color
- **Guard:** Only the owner can edit. Only `draft` stones can be edited.
- **Actions from the edit page:**
  - **Save** -- Save changes, stay on edit page
  - **Publish** -- Change status to `published`, redirect to map

## Publishing

- Changes status from `draft` to `published`
- Stone becomes visible on the interactive map
- No more editing allowed after publishing

## Sending Off

- **URL:** `POST /stone/<pk>/send-off/`
- **View:** `StoneSendOffView`
- Changes status from `published` to `sent_off`
- Records `sent_off_at` timestamp
- The stone is finalized -- the physical stone has been placed in the world

## Name Validation

Stone names (`PK_stone`) have these constraints:

| Rule | Where Enforced |
|------|----------------|
| Max 50 characters | Database level (`CharField(max_length=50)`) |
| Unique | Database level (`unique=True`) |
| No whitespace | Model validator (`validate_no_whitespace`), API check |
| Not empty | View level (`if not PK_stone`) |

**Known gap:** Whitespace-only names like `"   "` pass the `if not PK_stone` check (truthy string) but the model validator only catches names that *contain* whitespace, not names that *are entirely* whitespace. The DB constraint catches the length but not the content.

## Distance Calculation

When a stone is scanned (new `StoneMove` created), the total distance is recalculated using the Haversine formula:

```python
def calculate_stone_distance(stone):
    moves = list(stone.moves.order_by('timestamp').all())
    total_distance = 0.0
    for i in range(1, len(moves)):
        # Haversine formula between consecutive moves
        ...
    return round(total_distance, 1)
```

The result is stored in `stone.distance_km` and displayed on the map and in My Stones.

## Key Files

| File | Purpose |
|------|---------|
| `source/main/models.py` | `Stone` model with lifecycle methods |
| `source/main/views.py` | `add_stone`, `StoneEditView`, `StoneSendOffView` |
| `source/main/shop_views.py` | `ClaimStoneView`, `CreateNewStoneView` |
| `source/content/templates/main/new_add_stone_modal.html` | Creation modal |
| `source/content/templates/main/stone_edit.html` | Edit page |
| `source/content/templates/main/claim_stone.html` | Claim page |

## Related Pages

- [[features/qr-system]] -- QR code generation during creation
- [[features/scanning]] -- What happens when someone finds the stone
- [[features/shop]] -- Purchasing QR codes before creating stones
- [[architecture]] -- Stone model details
