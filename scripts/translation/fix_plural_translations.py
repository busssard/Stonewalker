#!/usr/bin/env python3
"""
Script to fix plural form translations in PO files.
"""

import re

def fix_plural_translations(po_file_path):
    """Fix empty plural msgstr entries by copying the corresponding msgid."""
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into entries
    entries = content.split('\n\n')
    fixed_entries = []
    
    for entry in entries:
        lines = entry.split('\n')
        if not lines or not lines[0].strip():
            fixed_entries.append(entry)
            continue
        
        # Check if this entry has plural forms
        has_plural = False
        msgid_lines = []
        msgid_plural_lines = []
        msgstr_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('msgid '):
                msgid_lines = [line]
                i += 1
                # Check for multi-line msgid
                while i < len(lines) and lines[i].startswith('"'):
                    msgid_lines.append(lines[i])
                    i += 1
            elif line.startswith('msgid_plural '):
                has_plural = True
                msgid_plural_lines = [line]
                i += 1
                # Check for multi-line msgid_plural
                while i < len(lines) and lines[i].startswith('"'):
                    msgid_plural_lines.append(lines[i])
                    i += 1
            elif line.startswith('msgstr['):
                msgstr_lines.append(line)
                i += 1
            else:
                msgstr_lines.append(line)
                i += 1
        
        # If this entry has plural forms and empty msgstr entries, fix them
        if has_plural and any('msgstr[' in line and '""' in line for line in msgstr_lines):
            # Extract msgid content
            msgid_content = extract_msg_content(msgid_lines)
            msgid_plural_content = extract_msg_content(msgid_plural_lines)
            
            # Create new entry with fixed plural forms
            new_lines = []
            for line in lines:
                if line.startswith('msgstr[0] ""'):
                    new_lines.append(f'msgstr[0] "{msgid_content}"')
                elif line.startswith('msgstr[1] ""'):
                    new_lines.append(f'msgstr[1] "{msgid_plural_content}"')
                else:
                    new_lines.append(line)
            
            fixed_entries.append('\n'.join(new_lines))
        else:
            fixed_entries.append(entry)
    
    # Write back to file
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(fixed_entries))
    
    print(f"Fixed plural translations in {po_file_path}")

def extract_msg_content(msg_lines):
    """Extract the actual content from msgid or msgid_plural lines."""
    if not msg_lines:
        return ""
    
    # Remove the msgid/msgid_plural prefix
    content_lines = []
    for line in msg_lines:
        if line.startswith('msgid "') or line.startswith('msgid_plural "'):
            content_lines.append(line[8:-1])  # Remove 'msgid "' or 'msgid_plural "' and '"'
        elif line.startswith('"') and line.endswith('"'):
            content_lines.append(line[1:-1])  # Remove quotes
    
    return ''.join(content_lines)

if __name__ == "__main__":
    po_file = "source/content/locale/en/LC_MESSAGES/django.po"
    fix_plural_translations(po_file) 