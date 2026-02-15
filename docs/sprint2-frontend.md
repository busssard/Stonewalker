# Sprint 2 - Frontend Features

## Features Implemented

### 1. Forum Integration (External Link)
**Files changed:** `source/content/templates/layouts/default/nav_links.html`, `source/content/assets/css/styles.css`

- Changed Forum nav link from internal Django URL (`{% url 'forum' %}`) to external URL (`https://forum.stonewalker.org`)
- Added `target="_blank"` and `rel="noopener"` for security
- Added inline SVG external-link icon (12px, Feather-style) next to "Forum" text
- Icon styled with `.external-link-icon` CSS class (opacity 0.7, vertically aligned)

### 2. Client-Side Image Compression
**Files changed:** `source/content/assets/js/image-upload.js`

- Added `getQuality()` function: files >2MB get quality 0.6, >1MB get 0.7, else 0.85
- Added WebP format support: `supportsWebP()` detects browser capability, uses WebP if available with JPEG fallback
- Added `formatSize()` helper for human-readable file sizes
- Compression feedback shown to user: "Image compressed from 3.2MB to 450KB (WebP)"
- Refactored `resizeImage()` to return metadata object `{ file, originalSize, compressed }` for feedback
- Simplified `setupImageUpload()` handler to always go through resizeImage pipeline

### 3. Clickable Stones on Map (Leaflet Popups)
**Files changed:** `source/content/templates/main/stonewalker_start.html`, `source/content/assets/css/styles.css`

- Added Leaflet popup on each map marker with preview card containing:
  - Stone name (bold), 48x48 thumbnail image, distance traveled, owner username
  - "View Journey" button that closes popup and opens the full stone modal
- Used `marker.bindPopup()` with custom `sw-popup-container` CSS class
- Popup event handler (`popupopen`) attaches click listener to "View Journey" button
- Popup styled with StoneWalker's design: green accents, clean typography, rounded corners
- CSS classes: `.sw-popup`, `.sw-popup-header`, `.sw-popup-thumb`, `.sw-popup-name`, `.sw-popup-meta`, `.sw-popup-stats`, `.sw-popup-btn`

### 4. Dark Mode
**Files changed:** `source/content/assets/css/styles.css`, `source/content/assets/js/header.js`, `source/content/templates/layouts/default/page.html`

#### CSS Custom Properties (styles.css)
- Added theme tokens in `:root`: `--bg-primary`, `--bg-secondary`, `--text-primary`, `--text-secondary`, `--card-bg`, `--border-color`, `--accent-green`, `--header-bg`, `--shadow-color`, `--input-bg`, `--input-border`, `--modal-bg`, `--body-bg`, `--popup-bg`, `--filter-bg`
- Added `[data-theme="dark"]` selector with dark values for all tokens
- Dark theme overrides existing CSS custom properties (`--color-bg-card`, `--color-text-main`, etc.)

#### Dark Mode Overrides (styles.css)
- Body/HTML: dark gradient background, muted decorative blobs
- Header: dark translucent background with backdrop blur
- Cards (`.avant-card`): dark card background, dark border
- Modals (`.avant-modal`): dark modal background
- Forms/inputs: dark input backgrounds, adjusted borders and text colors
- Map filter controls: dark background
- Floating action buttons: dark secondary variant
- Profile modal: dark overlay and content
- Leaflet popups: dark background and text
- Selection styling: green tint instead of pink
- Links: lighter primary color for contrast

#### JS Toggle (header.js)
- IIFE at top of file applies theme immediately on script load (no flash)
- `getPreferredTheme()`: checks localStorage first, then `prefers-color-scheme` media query, defaults to light
- `toggleDarkMode()`: flips `data-theme` attribute on `<html>`, saves to localStorage
- Listens for OS theme changes when no user preference is saved
- Exposed `window.toggleDarkMode` globally

#### HTML Toggle Button (page.html)
- Moon/sun SVG toggle button placed before burger menu container
- Uses CSS to show/hide appropriate icon based on `[data-theme]`
- Accessible: has `aria-label="Toggle dark mode"` and `title` attribute

## Tests
**File created:** `source/main/tests/test_frontend_features.py` (31 tests)

| Test Class | Tests | What it validates |
|-----------|-------|-------------------|
| `ForumExternalLinkTests` | 4 | target="_blank", rel="noopener", external URL, SVG icon |
| `DarkModeToggleTests` | 4 | Toggle button present, moon/sun icons, aria-label |
| `DarkModeStylesTests` | 11 | CSS custom properties, dark theme selector, element overrides |
| `DarkModeJSTests` | 5 | toggleDarkMode function, localStorage, prefers-color-scheme, data-theme |
| `MapPopupTests` | 3 | Popup CSS classes, View Journey button, bindPopup usage |
| `ImageCompressionTests` | 4 | Quality reduction, WebP support, compression feedback, formatSize |

## Key Decisions

1. **WebP with JPEG fallback**: Canvas WebP support detection at module load time; if browser doesn't support WebP encoding, falls back to JPEG transparently
2. **Immediate theme application**: Dark mode JS runs before DOMContentLoaded to prevent flash of wrong theme
3. **CSS custom properties approach**: Dark mode uses `[data-theme="dark"]` attribute selector on `<html>` element, overriding CSS custom properties rather than duplicating every rule
4. **Popup over direct modal**: Map markers now show a lightweight Leaflet popup first, letting users preview stone info before committing to the full modal view
5. **No inline styles**: All popup and dark mode styles use CSS classes per project convention (CSSUtilityClassTests)
