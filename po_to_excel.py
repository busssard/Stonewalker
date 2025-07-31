#!/usr/bin/env python3
"""
Script to extract translations from .po files and create an Excel/CSV file.
First column: msgid (key)
Subsequent columns: translations for each language
"""

import os
import re
import csv
import argparse
from pathlib import Path
from collections import defaultdict

def parse_po_file(po_file_path):
    """Parse a .po file and extract msgid/msgstr pairs."""
    translations = {}
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by message blocks
    blocks = content.split('\n\n')
    
    for block in blocks:
        if not block.strip():
            continue
            
        # Extract msgid and msgstr
        msgid_match = re.search(r'msgid "(.*?)"', block, re.DOTALL)
        msgstr_match = re.search(r'msgstr "(.*?)"', block, re.DOTALL)
        
        if msgid_match and msgstr_match:
            msgid = msgid_match.group(1)
            msgstr = msgstr_match.group(1)
            
            # Skip empty msgid (header)
            if msgid:
                translations[msgid] = msgstr
    
    return translations

def get_language_code_from_path(po_file_path):
    """Extract language code from the path."""
    # Extract language from path like .../locale/de/LC_MESSAGES/django.po
    path_parts = Path(po_file_path).parts
    for i, part in enumerate(path_parts):
        if part == 'locale' and i + 1 < len(path_parts):
            return path_parts[i + 1]
    return 'unknown'

def find_po_files(locale_dir):
    """Find all django.po files in the locale directory."""
    po_files = []
    locale_path = Path(locale_dir)
    
    if not locale_path.exists():
        print(f"Error: Locale directory {locale_dir} does not exist")
        return []
    
    for lang_dir in locale_path.iterdir():
        if lang_dir.is_dir() and not lang_dir.name.startswith('.'):
            po_file = lang_dir / 'LC_MESSAGES' / 'django.po'
            if po_file.exists():
                po_files.append(po_file)
    
    return po_files

def create_translation_matrix(po_files):
    """Create a matrix of translations from all .po files."""
    all_keys = set()
    translations_by_lang = {}
    
    # Parse all .po files
    for po_file in po_files:
        lang_code = get_language_code_from_path(str(po_file))
        translations = parse_po_file(str(po_file))
        translations_by_lang[lang_code] = translations
        all_keys.update(translations.keys())
    
    return all_keys, translations_by_lang

def write_csv(output_file, all_keys, translations_by_lang):
    """Write translations to CSV file."""
    languages = sorted(translations_by_lang.keys())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = ['key'] + languages
        writer.writerow(header)
        
        # Write translations
        for key in sorted(all_keys):
            row = [key]
            for lang in languages:
                translation = translations_by_lang[lang].get(key, '')
                row.append(translation)
            writer.writerow(row)

def write_excel(output_file, all_keys, translations_by_lang):
    """Write translations to Excel file."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required for Excel output. Install with: pip install pandas openpyxl")
        return False
    
    languages = sorted(translations_by_lang.keys())
    
    # Create data for DataFrame
    data = []
    for key in sorted(all_keys):
        row = {'key': key}
        for lang in languages:
            translation = translations_by_lang[lang].get(key, '')
            row[lang] = translation
        data.append(row)
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    return True

def main():
    parser = argparse.ArgumentParser(description='Extract translations from .po files to Excel/CSV')
    parser.add_argument('locale_dir', help='Path to locale directory')
    parser.add_argument('output_file', help='Output file (CSV or Excel)')
    parser.add_argument('--format', choices=['csv', 'excel'], default='csv',
                       help='Output format (default: csv)')
    
    args = parser.parse_args()
    
    # Find all .po files
    po_files = find_po_files(args.locale_dir)
    
    if not po_files:
        print("No .po files found!")
        return
    
    print(f"Found {len(po_files)} .po files:")
    for po_file in po_files:
        lang = get_language_code_from_path(str(po_file))
        print(f"  - {lang}: {po_file}")
    
    # Create translation matrix
    all_keys, translations_by_lang = create_translation_matrix(po_files)
    
    print(f"\nFound {len(all_keys)} unique translation keys")
    
    # Write output file
    if args.format == 'csv' or args.output_file.endswith('.csv'):
        write_csv(args.output_file, all_keys, translations_by_lang)
        print(f"Translations written to {args.output_file}")
    else:
        if write_excel(args.output_file, all_keys, translations_by_lang):
            print(f"Translations written to {args.output_file}")
        else:
            print("Failed to write Excel file")

if __name__ == '__main__':
    main() 