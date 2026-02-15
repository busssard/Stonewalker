---
title: How to Add or Update Translations
tags: [guide, how-to, translations, i18n]
last-updated: 2026-02-10
---

# How to Add or Update Translations

This guide covers the practical steps for adding or editing translations. For the full reference, see `TRANSLATION.md` in the project root.

## Quick Reference

| Language | Code | Locale Dir |
|----------|------|------------|
| English | `en` | `source/content/locale/en/` |
| Russian | `ru` | `source/content/locale/ru/` |
| Chinese (Simplified) | `zh-hans` | `source/content/locale/zh-hans/` |
| French | `fr` | `source/content/locale/fr/` |
| Spanish | `es` | `source/content/locale/es/` |
| German | `de` | `source/content/locale/de/` |
| Italian | `it` | `source/content/locale/it/` |

## Adding New Translatable Text to a Template

### Step 1: Mark the String

In your template, wrap the text with `{% trans %}`:

```html
{% load i18n %}

<h1>{% trans "Welcome to the shop" %}</h1>
<p>{% trans "Browse our products below." %}</p>
```

### Step 2: Extract Strings

Run `makemessages` for each language:

```bash
cd source
python manage.py makemessages -l en
python manage.py makemessages -l ru
python manage.py makemessages -l zh_Hans
python manage.py makemessages -l fr
python manage.py makemessages -l es
python manage.py makemessages -l de
python manage.py makemessages -l it
```

This updates the `.po` files with the new `msgid` entries.

### Step 3: Translate

Open each `.po` file and find the new entries (they'll have empty `msgstr`):

```po
#: content/templates/main/shop.html:15
msgid "Welcome to the shop"
msgstr ""
```

Fill in the translations:

```po
#: content/templates/main/shop.html:15
msgid "Welcome to the shop"
msgstr "Bienvenue dans la boutique"
```

### Step 4: Compile

```bash
cd source
python manage.py compilemessages
```

### Step 5: Verify

Run the translation QA tests:

```bash
python source/manage.py test main.translation_tests
```

And visually check in the browser by switching languages at `/language/`.

## Editing Existing Translations

1. Open the `.po` file for the target language
2. Find the `msgid` you want to change
3. Edit the `msgstr` value
4. Compile: `cd source && python manage.py compilemessages`

## Bulk Editing via CSV

For large-scale translation work:

```bash
# Export to CSV
python scripts/translation/po_to_excel.py source/content/locale translations.csv

# Edit the CSV (all languages in columns)

# Import back
python scripts/translation/excel_to_po.py translations.csv source/content/locale

# Compile
cd source && python manage.py compilemessages
```

Install dependencies first: `pip install -r scripts/translation/translation_requirements.txt`

## Adding a New Language

1. Add to `LANGUAGES` in both settings files:
   ```python
   LANGUAGES = [
       ('en', _('English')),
       # ... existing languages ...
       ('ja', _('Japanese')),  # New
   ]
   ```

2. Create the locale directory:
   ```bash
   mkdir -p source/content/locale/ja/LC_MESSAGES/
   ```

3. Extract strings:
   ```bash
   cd source && python manage.py makemessages -l ja
   ```

4. Translate all entries in the new `.po` file

5. Compile and test

## Common Mistakes

- **Forgetting to compile** -- `.po` edits have no effect until compiled to `.mo`
- **Smart quotes** -- Use regular `"quotes"`, never curly ones
- **Encoding** -- Save `.po` files as UTF-8
- **Duplicate msgid** -- Causes compilation errors; the QA tests catch this
- **Empty msgstr** -- Will show the English fallback; the QA tests catch this

## Related Pages

- [[features/translations]] -- Translation system overview
- [[guides/add-a-feature]] -- Full feature development workflow
- See `TRANSLATION.md` in the project root for the complete reference
