# Old QR Code Implementation

This directory contains the extracted QR code implementation from the original StoneWalker system for reference purposes.

## Issues with Previous Implementation

1. **Inconsistent QR URL generation** - Multiple different patterns for generating QR codes
2. **No readable text in downloads** - Downloaded QR codes don't show the URL properly
3. **Complex state management** - Session-based QR code storage is fragile
4. **No stone editing workflow** - Stones are immediately published, no draft state
5. **Multiple QR generation endpoints** - Scattered across different views
6. **No user limits** - No restriction on how many stones users can create

## Previous Architecture

- QR codes generated immediately on stone creation
- Session storage for download paths
- Multiple views: `StoneQRCodeView`, `generate_qr_code`, `regenerate_qr_code`  
- Files stored in `media/qr_codes/` with complex naming patterns
- Base64 encoding for AJAX responses

## Extracted Files

- `old_views.py` - Original QR-related views
- `old_qr_code.js` - Original JavaScript QR manager
- `old_urls.py` - Original URL patterns

Date extracted: 2025-01-16