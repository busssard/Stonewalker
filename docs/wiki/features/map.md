---
title: Interactive Map
tags: [feature, map, leaflet, visualization]
last-updated: 2026-02-10
---

# Interactive Map

The interactive map is the centerpiece of the StoneWalker user experience. It shows all published stones and their journeys around the world.

## Overview

- **Library:** [Leaflet.js](https://leafletjs.com/)
- **Page:** `/stonewalker/` (main page)
- **View:** `StoneWalkerStartPageView` (`source/main/views.py`)
- **Template:** `source/content/templates/main/stonewalker_start.html`

## How It Works

1. `StoneWalkerStartPageView.get_context_data()` queries all stones with their moves
2. For each stone with at least one move, it builds a JSON data structure
3. The data is passed to the template as `stones_json`
4. JavaScript on the frontend initializes a Leaflet map and renders:
   - **Markers** at each stone's latest location
   - **Polylines** showing the stone's travel path
   - **Popups** with stone details (name, description, image, distance, creator)

## Stone Data Structure (JSON)

Each stone in the `stones_json` array contains:

```json
{
  "PK_stone": "MyStone",
  "uuid": "a1b2c3d4-...",
  "description": "A blue painted stone",
  "created_at": "2026-01-15T10:30:00Z",
  "user": "alice",
  "user_picture": "/media/profile_pics/alice.jpg",
  "image": "/media/stones/mystone.jpg",
  "color": "#4CAF50",
  "shape": "circle",
  "latest_latitude": 48.8566,
  "latest_longitude": 2.3522,
  "latest_image": "/media/stonemoves/latest.jpg",
  "distance_km": 1234.5,
  "moves": [
    {
      "latitude": 52.5200,
      "longitude": 13.4050,
      "timestamp": "2026-01-15T10:30:00Z",
      "timestamp_display": "Jan 15, 2026",
      "image": "",
      "comment": "Found it in Berlin!",
      "user": "bob",
      "user_picture": "/static/user_picture.png"
    }
  ]
}
```

## Welcome Modal

For unauthenticated users, a welcome modal appears on the main page:
- Shows only once per IP per hour (tracked via session)
- Encourages sign up or login
- Styled with the avant-garde design system (decorative gradient circles)
- Uses `localStorage` to avoid repeat popups

## Focus Mode

When redirected from a stone creation or scan (`/stonewalker/?focus=<PK_stone>`), the map centers on and highlights the specified stone.

## Distance Calculation

Stone distance is pre-calculated server-side using the Haversine formula and stored in `stone.distance_km`. This avoids recalculating on every page load. The distance is updated whenever a new `StoneMove` is created (in `StoneScanView.post()` and `StoneLinkView.post()`).

## Performance Considerations

- Stones without any moves are not included in the JSON (no location to display)
- Profile pictures are resolved server-side to avoid additional API calls
- Distance is pre-calculated and stored, not computed on render

## Related Pages

- [[features/scanning]] -- How new moves are added to stones
- [[features/stone-management]] -- Stone lifecycle (only published/wandering stones appear)
- [[architecture]] -- Template structure and static assets
