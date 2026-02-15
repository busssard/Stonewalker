#!/usr/bin/env python3
"""
Simple script to fix all empty msgstr entries in PO files.
"""

import re
import os

def fix_po_file(po_file_path):
    """Fix all empty msgstr entries by copying the msgid value."""
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match msgid followed by empty msgstr (including plural forms)
    # This handles both single-line and multi-line msgids
    pattern = r'(msgid(?: ""\n(?:".*"\n)*| "[^"]*")\n(?:msgid_plural(?: ""\n(?:".*"\n)*| "[^"]*")\n)?)msgstr(?:\[[0-9]+\])? ""\n'
    
    def replace_func(match):
        msgid_part = match.group(1)
        # Extract the actual msgid content
        msgid_lines = msgid_part.strip().split('\n')
        
        # Handle multi-line msgids
        if msgid_lines[0] == 'msgid ""':
            # Multi-line msgid
            msgid_content = []
            for line in msgid_lines[1:]:
                if line.startswith('"') and line.endswith('"'):
                    msgid_content.append(line[1:-1])  # Remove quotes
            full_msgid = ''.join(msgid_content)
        else:
            # Single-line msgid
            full_msgid = msgid_lines[0][7:-1]  # Remove 'msgid "' and '"'
        
        # Create the replacement
        if len(full_msgid) > 70:  # Long string, use multi-line format
            # Split into chunks of ~70 characters
            chunks = []
            current_chunk = ""
            for word in full_msgid.split():
                if len(current_chunk) + len(word) + 1 <= 70:
                    current_chunk += (word + " ")
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = word + " "
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            msgstr_part = 'msgstr ""\n'
            for chunk in chunks:
                msgstr_part += f'"{chunk}"\n'
        else:
            # Single-line format
            msgstr_part = f'msgstr "{full_msgid}"\n'
        
        return msgid_part + msgstr_part
    
    # Apply the replacement
    new_content = re.sub(pattern, replace_func, content)
    
    # Also handle plural forms specifically
    plural_pattern = r'(msgstr\[[0-9]+\]) ""\n'
    def replace_plural_func(match):
        plural_key = match.group(1)
        return f'{plural_key} ""\n'
    
    new_content = re.sub(plural_pattern, replace_plural_func, new_content)
    
    # Write back to file
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    # Count how many replacements were made
    original_count = len(re.findall(r'msgstr(?:\[[0-9]+\])? ""\n', content))
    new_count = len(re.findall(r'msgstr(?:\[[0-9]+\])? ""\n', new_content))
    fixed_count = original_count - new_count
    
    print(f"Fixed {fixed_count} empty msgstr entries in {po_file_path}")
    return fixed_count

if __name__ == "__main__":
    po_file = "source/content/locale/en/LC_MESSAGES/django.po"
    if os.path.exists(po_file):
        fixed_count = fix_po_file(po_file)
        print(f"Translation file has been updated! Total entries fixed: {fixed_count}")
    else:
        print(f"PO file not found: {po_file}") 