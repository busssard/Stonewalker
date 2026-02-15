---
title: How to Add a Feature
tags: [guide, how-to, development, workflow]
last-updated: 2026-02-10
---

# How to Add a Feature

This guide walks through the end-to-end process of adding a new feature to StoneWalker.

## 1. Understand the Architecture

Before writing code, read [[architecture]] to understand:
- Which Django app the feature belongs to (`accounts/` for auth, `main/` for everything else)
- Which models are involved
- Where templates and static assets live

## 2. Plan the Changes

Identify what you need to create or modify:

- **Model changes** -- New fields or models in `models.py`?
- **View logic** -- New views or modifications to existing ones?
- **URL routes** -- New paths in `urls.py`?
- **Templates** -- New pages or modifications to existing templates?
- **Static assets** -- New CSS classes or JavaScript?
- **Translations** -- New user-facing strings?
- **Tests** -- What test cases cover the new behavior?

## 3. Create the Migration (if needed)

If you changed any model:

```bash
cd source
../venv/bin/python manage.py makemigrations
../venv/bin/python manage.py migrate
```

Review the generated migration file to make sure it does what you expect.

## 4. Implement the View

- Use **class-based views** (CBV) for page views: `TemplateView`, `FormView`, `View`
- Use **function views** for simple API endpoints
- Use `LoginRequiredMixin` or `@login_required` for authenticated endpoints
- Use `@require_POST` for POST-only endpoints
- Always handle errors with try/except and provide user-friendly messages via `django.contrib.messages`

Example pattern (from the codebase):

```python
class MyNewView(LoginRequiredMixin, TemplateView):
    template_name = 'main/my_new_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your data here
        return context
```

## 5. Add URL Routes

In `source/app/urls.py`:
- API endpoints go in the non-prefixed `urlpatterns` list
- Page routes go inside `i18n_patterns()` for language prefix support

```python
# Inside i18n_patterns:
path('my-feature/', MyNewView.as_view(), name='my_feature'),
```

## 6. Create the Template

- New templates go in `source/content/templates/main/`
- Extend the base layout: `{% extends "layouts/default/page.html" %}`
- Use `{% trans "text" %}` for all user-facing strings
- Use utility classes from `styles.css` instead of inline styles
- The CSS test in `accounts/tests.py` will flag unauthorized inline styles

## 7. Add Translations

For every new `{% trans %}` string:

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

Then edit each `.po` file in `source/content/locale/<lang>/LC_MESSAGES/` and compile:

```bash
python manage.py compilemessages
```

See [[guides/add-a-translation]] for more details.

## 8. Write Tests

Every new feature should have test coverage. See [[guides/write-tests]] for the full guide.

Key points:
- Put tests in `source/main/tests/` (they'll be auto-marked as `integration`)
- Use the base classes from `source/main/tests/base.py`
- Test both the happy path and error cases
- Test authentication requirements

## 9. Run the Full Test Suite

```bash
./venv/bin/python run_tests.py
```

All 118+ tests must pass before committing.

## 10. Commit

Create separate commits for logically distinct changes:

```bash
git add source/main/models.py source/main/migrations/
git commit -m "Add MyFeature model and migration"

git add source/main/views.py source/app/urls.py source/content/templates/main/my_new_page.html
git commit -m "Add MyFeature view, URL route, and template"

git add source/main/tests/test_my_feature.py
git commit -m "Add tests for MyFeature"
```

The pre-push hook runs the full test suite (~3 minutes) before pushing.

## Checklist

- [ ] Model changes with migrations
- [ ] View with proper auth guards
- [ ] URL route (in the correct urlpatterns group)
- [ ] Template extending base layout
- [ ] Translations for all 7 languages
- [ ] Tests for happy path and error cases
- [ ] Full test suite passes
- [ ] Separate, descriptive commits

## Related Pages

- [[architecture]] -- Where things live in the codebase
- [[guides/add-a-translation]] -- Translation workflow
- [[guides/write-tests]] -- Testing guide
