# Translation Management Scripts

This directory contains scripts to manage Django translations using Excel/CSV files for easier editing.

## Scripts

### 1. `po_to_excel.py` - Extract translations from .po files
Extracts all translations from your existing .po files and creates an Excel/CSV file with:
- First column: Translation key (msgid)
- Subsequent columns: Translations for each language

### 2. `excel_to_po.py` - Convert Excel/CSV back to .po files
Converts your edited Excel/CSV file back to individual .po files for each language.

## Installation changes

Install the required dependencies:

```bash
pip install -r translation_requirements.txt
```

## Usage

### Step 1: Extract existing translations to Excel/CSV

```bash
# Extract to CSV (recommended for large files)
python po_to_excel.py source/content/locale translations.csv

# Extract to Excel
python po_to_excel.py source/content/locale translations.xlsx --format excel
```

This will create a file with all your translations in a spreadsheet format.

### Step 2: Edit the translations

Open the generated CSV/Excel file and:
- Edit translations in the respective language columns
- Add new translation keys in the first column
- Fill in translations for all languages

### Step 3: Convert back to .po files

```bash
# From CSV
python excel_to_po.py translations.csv source/content/locale

# From Excel
python excel_to_po.py translations.xlsx source/content/locale --format excel
```

This will regenerate all your .po files with the updated translations.

### Step 4: Compile the translations

After converting back to .po files, compile them:

```bash
cd source
python manage.py compilemessages
```

## File Structure

The scripts expect this directory structure:
```
source/content/locale/
├── de/LC_MESSAGES/django.po
├── en/LC_MESSAGES/django.po
├── es/LC_MESSAGES/django.po
├── fr/LC_MESSAGES/django.po
├── it/LC_MESSAGES/django.po
├── ru/LC_MESSAGES/django.po
└── zh-hans/LC_MESSAGES/django.po
```

## Example Workflow

1. **Initial extraction:**
   ```bash
   python po_to_excel.py source/content/locale translations.csv
   ```

2. **Edit translations in your preferred spreadsheet editor**

3. **Convert back to .po files:**
   ```bash
   python excel_to_po.py translations.csv source/content/locale
   ```

4. **Compile for Django:**
   ```bash
   cd source
   python manage.py compilemessages
   ```

## Tips

- **CSV vs Excel**: Use CSV for large files (faster, smaller), Excel for easier editing
- **Backup**: Always backup your original .po files before running the scripts
- **Validation**: Check the generated .po files to ensure they're correctly formatted
- **Empty translations**: Empty cells in the spreadsheet will result in empty translations in the .po files

## Troubleshooting

- **Missing pandas**: Install with `pip install pandas openpyxl`
- **Encoding issues**: The scripts use UTF-8 encoding for all files
- **Large files**: For very large translation files, use CSV format instead of Excel 