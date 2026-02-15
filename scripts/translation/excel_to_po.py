#!/usr/bin/env python3
"""
Script to convert Excel/CSV file back to .po files.
First column: msgid (key)
Subsequent columns: translations for each language
"""

import os
import csv
import argparse
from pathlib import Path

def read_csv(input_file):
    """Read translations from CSV file."""
    translations = {}
    languages = []
    
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Get language columns (all except 'key')
        languages = [col for col in reader.fieldnames if col != 'key']
        
        for row in reader:
            key = clean_dangerous_characters(row['key'])
            for lang in languages:
                if lang not in translations:
                    translations[lang] = {}
                # Use key as fallback if no translation provided
                translation = row.get(lang, '').strip()
                if not translation:
                    translation = key
                else:
                    translation = clean_dangerous_characters(translation)
                translations[lang][key] = translation
    
    return translations, languages

def read_excel(input_file):
    """Read translations from Excel file."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required for Excel input. Install with: pip install pandas openpyxl")
        return None, None
    
    df = pd.read_excel(input_file)
    
    # Get language columns (all except 'key')
    languages = [col for col in df.columns if col != 'key']
    
    translations = {}
    for lang in languages:
        translations[lang] = {}
        for _, row in df.iterrows():
            key = clean_dangerous_characters(str(row['key']))
            # Use key as fallback if no translation provided
            translation = str(row.get(lang, '')).strip()
            if not translation or translation == 'nan':
                translation = key
            else:
                translation = clean_dangerous_characters(translation)
            translations[lang][key] = translation
    
    return translations, languages

def create_po_header(language_code):
    """Create the header for a .po file."""
    header = f'''# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE PACKAGE'S COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-01-27 18:03+0000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: {language_code.upper()} <{language_code}@li.org>\\n"
"Language: {language_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

'''
    return header

def clean_dangerous_characters(text):
    """Replace dangerous characters that can cause issues in .po files."""
    if not text:
        return text
    
    # Replace smart quotes with regular quotes (these interfere with .po parsing)
    text = text.replace('"', '"').replace('"', '"')  # Smart double quotes
    text = text.replace(''', "'").replace(''', "'")  # Smart single quotes
    text = text.replace('‚', ',').replace('„', '"').replace('"', '"')  # German quotes
    text = text.replace('‹', '<').replace('›', '>')  # Single angle quotes
    text = text.replace('«', '"').replace('»', '"')  # Double angle quotes
    text = text.replace('‶', '"').replace('″', '"')  # Double prime
    text = text.replace('‵', "'").replace('′', "'")  # Prime
    
    # Replace other characters that can interfere with .po parsing
    text = text.replace('…', '...')  # Ellipsis
    text = text.replace('–', '-').replace('—', '-')  # En and em dashes
    
    return text

def escape_po_string(text):
    """Escape special characters for .po format."""
    if not text:
        return '""'
    
    # Clean dangerous characters first
    text = clean_dangerous_characters(text)
    
    # Escape quotes and backslashes
    escaped = text.replace('\\', '\\\\').replace('"', '\\"')
    
    # Handle newlines
    escaped = escaped.replace('\n', '\\n')
    
    return f'"{escaped}"'

def write_po_file(po_file_path, translations, language_code):
    """Write translations to a .po file."""
    # Create directory if it doesn't exist
    po_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(po_file_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write(create_po_header(language_code))
        
        # Write translations
        for key in sorted(translations.keys()):
            translation = translations[key]
            
            # Skip empty translations (shouldn't happen now with fallback)
            if not translation.strip():
                continue
            
            # Write msgid and msgstr
            f.write(f'msgid {escape_po_string(key)}\n')
            f.write(f'msgstr {escape_po_string(translation)}\n')
            f.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Convert Excel/CSV file to .po files')
    parser.add_argument('input_file', help='Input file (CSV or Excel)')
    parser.add_argument('locale_dir', help='Path to locale directory')
    parser.add_argument('--format', choices=['csv', 'excel'], default='auto',
                       help='Input format (auto-detect if not specified)')
    
    args = parser.parse_args()
    
    # Determine format
    if args.format == 'auto':
        if args.input_file.endswith('.csv'):
            args.format = 'csv'
        elif args.input_file.endswith(('.xlsx', '.xls')):
            args.format = 'excel'
        else:
            print("Error: Cannot auto-detect format. Please specify --format csv or --format excel")
            return
    
    # Read input file
    if args.format == 'csv':
        translations, languages = read_csv(args.input_file)
    else:
        translations, languages = read_excel(args.input_file)
    
    if not translations:
        print("Error: Could not read input file")
        return
    
    print(f"Found translations for {len(languages)} languages: {', '.join(languages)}")
    print(f"Found {len(next(iter(translations.values()))) if translations else 0} translation keys")
    
    # Write .po files
    locale_dir = Path(args.locale_dir)
    
    for lang in languages:
        po_file_path = locale_dir / lang / 'LC_MESSAGES' / 'django.po'
        write_po_file(po_file_path, translations[lang], lang)
        print(f"Written: {po_file_path}")
    
    print(f"\nAll .po files have been written to {args.locale_dir}")

if __name__ == '__main__':
    main() 