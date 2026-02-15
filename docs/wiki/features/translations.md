---
title: Translation System
tags: [feature, i18n, translations, languages]
last-updated: 2026-02-10
---

# Translation System

StoneWalker supports 7 languages with comprehensive quality assurance testing. For the authoritative and detailed reference, see `TRANSLATION.md` in the project root.

## Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `ru` | Russian |
| `zh-hans` | Chinese (Simplified) |
| `fr` | French |
| `es` | Spanish |
| `de` | German |
| `it` | Italian |

## How It Works

1. **Template strings** are wrapped in `{% trans "text" %}` tags
2. **`makemessages`** extracts these strings into `.po` files
3. Translators edit the `.po` files (manually or via CSV/Excel workflow)
4. **`compilemessages`** compiles `.po` files into binary `.mo` files
5. Django serves the correct language based on browser detection or user preference

## File Locations

```
source/content/locale/
  en/LC_MESSAGES/django.po    -- English
  ru/LC_MESSAGES/django.po    -- Russian
  zh-hans/LC_MESSAGES/django.po -- Chinese (Simplified)
  fr/LC_MESSAGES/django.po    -- French
  es/LC_MESSAGES/django.po    -- Spanish
  de/LC_MESSAGES/django.po    -- German
  it/LC_MESSAGES/django.po    -- Italian
```

## Language Detection

Django's `LocaleMiddleware` detects the user's preferred language:
1. First checks the URL prefix (e.g., `/fr/shop/`)
2. Then checks the session
3. Then checks the `Accept-Language` header from the browser
4. Falls back to English

Users can manually change language at `/language/` and are automatically redirected to the main page.

## Translation Workflow

### For Quick Edits
1. Edit the `.po` file directly
2. Compile: `cd source && python manage.py compilemessages`
3. Restart the dev server

### For Bulk Editing (CSV/Excel)
See `TRANSLATION.md` for the full workflow using `scripts/translation/po_to_excel.py` and `scripts/translation/excel_to_po.py`.

### When Adding New UI Text
1. Wrap the text in `{% trans "..." %}` in the template
2. Run `cd source && python manage.py makemessages -l <lang_code>` for each language
3. Edit the new entries in each `.po` file
4. Compile and test

## Quality Assurance

Translation quality is automatically tested in `source/main/translation_tests.py`:

- **PO file structure** -- Proper headers, no empty translations, no duplicates
- **Compilation** -- All files compile without errors
- **Functionality** -- Translated content appears on pages
- **Coverage** -- Critical strings are translated in all languages

Run translation tests specifically:
```bash
python source/manage.py test main.translation_tests
```

## Compilation Timing

Translations must be compiled before:
- Running tests (handled automatically by `run_tests.py`)
- Deploying to production

The `run_tests.py` script compiles translations before running pytest. Do NOT rely on conftest.py for compilation -- that was removed during the February 2026 quality sweep.

## Related Pages

- [[guides/add-a-translation]] -- Step-by-step guide for adding translations
- [[getting-started]] -- Initial setup includes translation compilation
- See `TRANSLATION.md` in the project root for the complete reference
