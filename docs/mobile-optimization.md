# Mobile Optimization Guide

## Overview

This document tracks all mobile/responsive design optimizations made to the StoneWalker application. The app targets three primary breakpoints:

- **Desktop**: >1250px (side-by-side layouts, full nav)
- **Tablet**: 600-1250px (stacked layouts, burger menu)
- **Mobile**: <600px (compact layouts, touch-optimized)

Additional sub-breakpoints exist at 480px (extra-small) and 768px (large mobile / small tablet).

## Design Principles

1. **44px minimum touch targets**: All interactive elements (buttons, links, close icons, pagination arrows) must be at least 44x44px on mobile.
2. **No iOS zoom on input focus**: All text inputs use `font-size: 16px` minimum on mobile to prevent Safari auto-zoom.
3. **Full viewport usage**: Pages should fill the viewport height on mobile -- no floating bottom gaps.
4. **Readable text**: No text smaller than 0.65rem on any device; headers never go below 0.9rem.

## Breakpoint Architecture

Breakpoints are defined in two places that must stay in sync:

- **JavaScript** (source of truth): `source/content/assets/js/header.js` -- the `BREAKPOINTS` object
- **CSS**: `source/content/assets/css/styles.css` -- hardcoded `@media` queries with comments noting which breakpoint they correspond to

The JS breakpoints are: desktop=1450, tablet=800, mobileLg=768, mobileMd=600, mobile=480, mobileXs=360.

Note: The CSS `@media` queries use slightly different values in some cases (e.g., 1250px for desktop) for historical reasons. The CSS values govern actual layout behavior.

## Changes Made (February 2026)

### Header Height & Elements

**Problem**: Header heights at mobile breakpoints were unreasonably small (32px at 600px, 24px at 480px), making the logo invisible and the profile picture a 0.7rem dot.

**Fix** (`styles.css`):
- 600px breakpoint: `--header-height` changed from 32px to 48px
- 480px breakpoint: header changed from 24px/32px to 44px minimum
- Profile image min size: 1.8-2rem instead of 0.7-1.1rem
- Logo image: 1.3-1.5rem minimum instead of 0.7-1.1rem
- Burger menu label: enforced 44x44px minimum touch target

### Touch Targets

**Problem**: Multiple interactive elements shrank below the 44px accessibility minimum on mobile.

**Fixes**:
- **Pagination arrows** (`.arrow-btn`): Now 44x44px at all mobile breakpoints (was 32-36px)
- **Floating action buttons**: Now 44px height minimum (was 28px at 600px, 36px at 768px)
- **Sort dropdowns**: Added `min-height: 44px`
- **`.avant-btn`**: Added `min-height: 44px` at mobile
- **Close buttons** (all modals): Added `min-width/min-height: 44px` with flexbox centering
- **Burger nav links**: Added `min-height: 44px` to all anchor elements
- **Header nav buttons** (mobile dropdown): Added `min-height: 44px` and full-width layout

### My Stones Page

**Problem**: Two-panel layout didn't scale equally; bottom of page didn't reach the window bottom.

**Fixes**:
- `.my-stones-split`: Added `height: calc(100vh - var(--header-height))` alongside `min-height` and `overflow-y: hidden` for desktop (side-by-side mode)
- At 1250px breakpoint: Changed to `height: auto` with `overflow-y: auto` and `min-height: 50vh` per panel, so stacked panels scroll naturally
- Stone name `max-width` increased from 80px to 90px (480px) and 100px to 120px (600px) for readability

### Modals

**Problem**: Modals used fixed padding and sizing that didn't adapt well to small screens. The new-add-stone-modal uses inline styles with no mobile overrides.

**Fixes**:
- `.avant-modal`: Reduced padding to `1.5rem 1rem`, set `width: 95vw`, `max-height: 95vh` at 600px
- `.profile-modal-content`: Same treatment
- `.modal-content`: Set `margin: 5% auto` and `width: 95%` on mobile
- **New Add Stone Modal** (`#new-add-stone-modal`): Added CSS overrides targeting `> div` to override inline styles. Input font-size forced to 16px (prevents iOS zoom). Buttons forced to 44px min-height. Preview image shrunk from 120px to 80px.
- **Stone Gallery Modal**: Close button gets 44px touch target on mobile
- **Scan/QR modals**: Reduced padding, set 95vw width

### Floating Action Bar

**Problem**: FAB buttons became too small to tap on mobile (28px height at 600px, 36px at 768px).

**Fix**: Minimum height 44px at all mobile breakpoints. Minimum width increased to ensure the text label remains readable.

## File Ownership

| File | Owner |
|------|-------|
| `source/content/assets/css/styles.css` | mobile agent |
| `source/content/templates/main/my_stones.html` | mobile agent |
| `source/content/templates/main/shared_modals.html` | mobile agent |
| `source/content/templates/main/new_add_stone_modal.html` | mobile agent (CSS only) |
| `source/content/templates/layouts/default/page.html` | mobile agent |
| `source/content/templates/layouts/default/nav_links.html` | mobile agent |

## Testing Checklist

When verifying mobile optimization, check the following at each breakpoint:

### At 480px (extra-small mobile)
- [ ] Header is visible and logo is readable
- [ ] Profile image is tappable (at least 28px)
- [ ] Burger menu opens and links are tappable
- [ ] My Stones page: both panels scroll, pagination arrows are 44px
- [ ] Floating action buttons are tappable (44px height)
- [ ] Modals open and close properly, close button is tappable

### At 600px (mobile)
- [ ] Sort dropdown is tappable (44px height)
- [ ] Stone list items show name, distance, and age clearly
- [ ] Add stone modal inputs don't trigger iOS zoom (16px font)
- [ ] QR code display fits within modal

### At 768px (large mobile)
- [ ] Stone list items maintain horizontal layout
- [ ] Floating action bar doesn't overlap content

### At 1250px (tablet)
- [ ] My Stones splits to stacked column layout
- [ ] Header burger menu works correctly
- [ ] All nav buttons are full-width in dropdown

### At >1250px (desktop)
- [ ] My Stones shows side-by-side panels filling viewport
- [ ] Both panels have equal flex sizing
- [ ] Navigation shows on header hover

## Known Limitations

1. **Inline styles on new-add-stone-modal**: The modal uses extensive inline styles. CSS overrides use `!important` to compensate. A future cleanup should move these to CSS classes.
2. **Stone list item text truncation**: At very narrow widths (480px), stone names truncate at 90px. Very long names may not be fully visible until the stone detail modal is opened.
3. **Fallback simple modal** in my_stones.html uses inline styles for layout -- these don't have mobile-specific overrides (the primary stone-modal.js module is responsive).
