#!/usr/bin/env python3
"""
Script to automatically fill empty msgstr entries in PO files with their msgid values.
This is useful for English translations where the translation is the same as the source.
"""

import re
import os

def fix_po_file(po_file_path):
    """Fix empty msgstr entries by copying the msgid value."""
    
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
            
        # Check if this entry has an empty msgstr
        has_empty_msgstr = False
        msgid_lines = []
        msgstr_start = -1
        
        for i, line in enumerate(lines):
            if line.startswith('msgid '):
                msgid_lines = [line]
                # Check if it's multi-line
                j = i + 1
                while j < len(lines) and lines[j].startswith('"'):
                    msgid_lines.append(lines[j])
                    j += 1
            elif line == 'msgstr ""':
                has_empty_msgstr = True
                msgstr_start = i
                break
        
        if has_empty_msgstr and msgid_lines:
            # Extract the msgid content
            msgid_content = ''
            for line in msgid_lines:
                if line.startswith('msgid "'):
                    msgid_content += line[7:-1]  # Remove 'msgid "' and '"'
                elif line.startswith('"') and line.endswith('"'):
                    msgid_content += line[1:-1]  # Remove quotes
            
            # Create the replacement msgstr
            if len(msgid_content) > 70:
                # Multi-line format
                chunks = []
                current_chunk = ""
                for word in msgid_content.split():
                    if len(current_chunk) + len(word) + 1 <= 70:
                        current_chunk += (word + " ")
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = word + " "
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Replace the empty msgstr with multi-line format
                new_lines = lines[:msgstr_start]
                new_lines.append('msgstr ""')
                for chunk in chunks:
                    new_lines.append(f'"{chunk}"')
                new_lines.extend(lines[msgstr_start + 1:])
                fixed_entries.append('\n'.join(new_lines))
            else:
                # Single-line format
                new_lines = lines[:msgstr_start]
                new_lines.append(f'msgstr "{msgid_content}"')
                new_lines.extend(lines[msgstr_start + 1:])
                fixed_entries.append('\n'.join(new_lines))
        else:
            fixed_entries.append(entry)
    
    # Write back to file
    new_content = '\n\n'.join(fixed_entries)
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Fixed empty msgstr entries in {po_file_path}")

if __name__ == "__main__":
    po_file = "source/content/locale/en/LC_MESSAGES/django.po"
    if os.path.exists(po_file):
        fix_po_file(po_file)
        print("Translation file has been updated!")
    else:
        print(f"PO file not found: {po_file}") 