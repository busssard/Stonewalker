#!/usr/bin/env python3
"""
Script to automatically fill empty msgstr entries in PO files with their msgid values.
This is useful for English translations where the translation is the same as the source.
"""

import polib
import os

def fix_po_file(po_file_path):
    """Fix empty msgstr entries by copying the msgid value."""
    
    # Load the PO file
    po = polib.pofile(po_file_path)
    
    # Fix empty msgstr entries
    fixed_count = 0
    for entry in po:
        if entry.msgstr == "" and entry.msgid != "":
            entry.msgstr = entry.msgid
            fixed_count += 1
    
    # Save the file
    po.save(po_file_path)
    
    print(f"Fixed {fixed_count} empty msgstr entries in {po_file_path}")
    return fixed_count

if __name__ == "__main__":
    po_file = "source/content/locale/en/LC_MESSAGES/django.po"
    if os.path.exists(po_file):
        # Keep running until no more empty entries are found
        total_fixed = 0
        while True:
            fixed_count = fix_po_file(po_file)
            if fixed_count == 0:
                break
            total_fixed += fixed_count
        
        print(f"Translation file has been updated! Total entries fixed: {total_fixed}")
    else:
        print(f"PO file not found: {po_file}") 