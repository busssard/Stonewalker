# Translation Management

This document covers the complete translation management, testing, and workflow setup for the StoneWalker project.

## Overview

StoneWalker supports 7 languages: English, Russian, Chinese (Simplified), French, Spanish, German, and Italian. The setup includes:

- Automatic translation compilation before tests
- Pre-commit hooks for translation compilation
- Django management commands for translation management
- Excel/CSV translation editing workflow
- Comprehensive test suite for translation quality

## File Structure

Translation files are stored in:
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

### Key Files

- `scripts/translation/po_to_excel.py` - Extract translations from .po files to Excel/CSV
- `scripts/translation/excel_to_po.py` - Convert Excel/CSV back to .po files
- `run_tests.py` - Test runner with automatic translation compilation
- `conftest.py` - Pytest configuration with translation compilation
- `scripts/translation/translation_requirements.txt` - Dependencies for Excel support
- `source/main/management/commands/compile_translations.py` - Django command for translation compilation
- `source/main/translation_tests.py` - Translation quality assurance tests

## Translation Workflow

### For Developers

1. **Extract Strings**: `python source/manage.py makemessages -l [language_code]`
2. **Edit Translations**: Modify the `.po` files in `source/content/locale/[lang]/LC_MESSAGES/`
3. **Run QA Tests**: `python source/manage.py test main.translation_tests`
4. **Fix Issues**: Address any errors reported by the QA tests
5. **Compile Messages**: `python source/manage.py compilemessages`
6. **Test Functionality**: Verify translations work in the browser

### For CI/CD

1. Tests run with automatic translation compilation
2. Translation quality is validated
3. Compilation errors fail the build
4. Coverage reports include translation tests

## Excel/CSV Editing Workflow

For bulk translation editing, you can export translations to a spreadsheet and import them back.

### Install Dependencies

```bash
pip install -r scripts/translation/translation_requirements.txt
```

### Step 1: Extract Translations

```bash
# Extract to CSV (recommended for large files)
python scripts/translation/po_to_excel.py source/content/locale translations.csv

# Extract to Excel
python scripts/translation/po_to_excel.py source/content/locale translations.xlsx --format excel
```

This creates a file with all translations in spreadsheet format:
- First column: Translation key (msgid)
- Subsequent columns: Translations for each language

### Step 2: Edit the Translations

Open the generated CSV/Excel file and:
- Edit translations in the respective language columns
- Add new translation keys in the first column
- Fill in translations for all languages

### Step 3: Convert Back to .po Files

```bash
# From CSV
python scripts/translation/excel_to_po.py translations.csv source/content/locale

# From Excel
python scripts/translation/excel_to_po.py translations.xlsx source/content/locale --format excel
```

### Step 4: Compile the Translations

```bash
cd source
python manage.py compilemessages
```

**Tips:**
- **CSV vs Excel**: Use CSV for large files (faster, smaller), Excel for easier editing
- **Backup**: Always backup your original .po files before running the scripts
- **Validation**: Check the generated .po files to ensure they're correctly formatted
- **Empty translations**: Empty cells in the spreadsheet will result in empty translations in the .po files

## Running Tests

### Using Make Commands

```bash
make test           # Run all tests
make test-fast      # Unit tests only
make test-slow      # Integration tests only
make test-cov       # With coverage report
```

### Using the Test Runner

```bash
python run_tests.py
```

### Running Translation Tests Only

```bash
# Run all translation QA tests
python source/manage.py test main.translation_tests

# Run specific test classes
python source/manage.py test main.translation_tests.TranslationQualityAssuranceTests
python source/manage.py test main.translation_tests.TranslationFunctionalityTests
python source/manage.py test main.translation_tests.TranslationCoverageTests
```

### Managing Translations via Make

```bash
make translations          # Extract translations to CSV
make compile-translations  # Compile translations manually
```

Or use the Django management command directly:

```bash
cd source && python manage.py compile_translations
```

## Automatic Translation Compilation

Translations are automatically compiled in several places:

1. **Before Tests**: The `conftest.py` file automatically compiles translations before any test runs
2. **Pre-commit Hook**: The pre-commit hook compiles translations before commits
3. **Test Runner**: The `run_tests.py` script ensures translations are compiled before running tests

### Pre-commit Hook

The pre-commit hook (`.git/hooks/pre-commit`):
- Detects modified .po files
- Compiles translations automatically
- Adds compiled .mo files to the commit
- Prevents commits if compilation fails

## Translation Quality Tests

The test suite (`source/main/translation_tests.py`) includes comprehensive translation quality checks:

### PO File Structure Validation (`TranslationQualityAssuranceTests`)
- **Proper Headers**: Ensures all PO files have correct charset and language specifications
- **No Empty Translations**: Checks that no `msgstr` entries are empty (except headers)
- **No Duplicate Entries**: Prevents duplicate `msgid` entries that cause compilation errors
- **Compilation Success**: Verifies all PO files can be compiled without errors

### Translation Functionality Tests (`TranslationFunctionalityTests`)
- **Cross-Language Testing**: Tests that translations work for all configured languages
- **Page Content Verification**: Ensures specific pages show translated content
- **Language Switching**: Validates URL-based language switching works correctly

### Translation Coverage Tests (`TranslationCoverageTests`)
- **Critical String Coverage**: Ensures important user-facing strings are translated
- **Translation Quality**: Checks that translations are actually different from source text

## Common Issues Detected

The QA system automatically detects and reports these common issues:

### Forbidden Characters (Cause encoding errors)
- Smart quotes (use regular quotes instead)
- Ellipsis (use three dots instead)
- En/Em dashes (use regular hyphens instead)
- German quotes (use regular quotes instead)

### PO File Structure Issues
- Missing charset specification (`Content-Type: text/plain; charset=UTF-8`)
- Missing language specification (`Language: xx`)
- Empty `msgstr` entries (untranslated strings)
- Duplicate `msgid` entries (causes compilation failures)

### Compilation Errors
- Syntax errors in PO files
- Invalid escape sequences
- Malformed headers

## Adding New Languages

1. Add language to `LANGUAGES` in settings:
   ```python
   LANGUAGES = [
       ('en', _('English')),
       ('de', _('German')),
       # Add new language here
       ('xx', _('Language Name')),
   ]
   ```

2. Create locale directory: `mkdir -p source/content/locale/xx/LC_MESSAGES/`

3. Extract messages: `python source/manage.py makemessages -l xx`

4. Run QA tests to ensure proper setup

## Translation Best Practices

- Use consistent terminology across all translations
- Consider cultural context when translating
- Always compile translations after editing
- Run QA tests before committing changes

## Troubleshooting

### "compilemessages generated one or more errors"

1. **Check for Duplicates**: Look for duplicate `msgid` entries
2. **Validate Syntax**: Check for unescaped quotes or invalid characters
3. **Verify Headers**: Ensure proper PO file headers are present
4. **Run QA Tests**: Use the automated tests to identify specific issues

### "UnicodeDecodeError"

1. **Check File Encoding**: Ensure PO files are saved as UTF-8
2. **Remove Smart Quotes**: Replace with regular quotes
3. **Clean Special Characters**: Use `iconv` to clean encoding issues

### "Translation not appearing"

1. **Check msgstr**: Ensure the translation is not empty
2. **Verify Compilation**: Run `compilemessages` after editing
3. **Clear Cache**: Restart Django server after changes
4. **Check Template Tags**: Ensure `{% trans %}` tags are properly used

### Debug Commands

```bash
# Check if translations compile
cd source && python manage.py compile_translations

# Run tests with verbose output
python run_tests.py -v

# Check test collection
python run_tests.py --collect-only

# Run specific test file
python run_tests.py accounts/tests.py
```
