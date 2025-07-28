# StoneWalker - A Global Stone Traveling Community

StoneWalker is a Django-based web application for tracking the journeys of painted stones as they travel the world. Inspired by geocaching and collaborative art, StoneWalker lets users log in, register, and follow the artistic adventures of unique stones on an interactive map.

## Features

- **Modern UI & Navigation:** Responsive, artsy/avantgarde design with a unified header and burger menu. The header includes a logo, navigation links (My Stones, Forum, Shop, About, Change Language), and a login/profile button that turns into your profile picture after login. The menu is mobile-friendly and consistent across all pages.
- **Profile Popup Modal:** Edit your profile (username, email, password, profile picture) in a popup modal window that overlays the current page, with a close (cross) button. Accessible from the header via the "Edit Profile" link or your profile picture.
- **Interactive Map:** Visualize the journeys of painted stones across the globe on `/stonewalker/`.
- **User Authentication:** Register, log in, log out, activate accounts via email, reset password, and manage your profile securely (username, email, password, profile info).
- **Personal Dashboard:** View your stones and submissions in a dedicated area (`/my-stones/`).
- **Add Stones:** Authenticated users can add new stones with name, description, color, shape, and image. The "Create New Stone" button is visually prominent, with a random color highlight on hover and a clear subtitle.
- **Scan Stones:** Authenticated users can scan (log a move for) a stone, updating its location and optionally uploading a photo and comment. The "Scan a Stone" button is clearly labeled.
- **Stone Update QR Codes:** Each stone has a unique QR code that links directly to its scan page, pre-filling and locking the stone name for easy updates.
- **Cooldown for Updates:** Users can only update (scan) a given stone once every 3 days; the scan form is locked if accessed again within this period.
- **Forum & Shop Placeholders:** Dedicated pages for a future forum and shop are available from the main navigation.
- **Multilingual Support:** English, French, Russian, Simplified Chinese, Spanish, German, and Italian with browser language detection.
- **Admin Panel:** Manage users and content via Django admin (`/admin/`).
- **Mobile-friendly:** Works on desktop and mobile browsers.
- **API Endpoint:** Check if a stone name is available (`/api/check_stone_name/`).
- **Change Language:** Users can change the UI language (`/language/`).

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-fork-or-this-repo-url>
cd simple-django-login-and-register
```

### 2. Set Up a Virtual Environment

#### Using Poetry (Recommended)

```bash
pip install poetry
poetry install
poetry shell
```

#### Or Using venv (Manual)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Settings

- For development: edit `source/app/conf/development/settings.py`
- For production: edit `source/app/conf/production/settings.py`

Set up email backend, allowed hosts, and any other environment-specific options.

#### Key Settings & Environment Variables

- `SECRET_KEY`: Set a unique secret key for your environment.
- `DEBUG`: Set to `True` for development, `False` for production.
- `ALLOWED_HOSTS`: List of allowed hostnames (e.g., `['localhost', '127.0.0.1']`).
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`: Configure for email sending.
- `DATABASES`: Default is SQLite, can be changed to Postgres/MySQL.
- `LANGUAGE_CODE`, `LANGUAGES`, `LOCALE_PATHS`: For internationalization.
- `STATIC_ROOT`, `STATIC_URL`, `MEDIA_ROOT`, `MEDIA_URL`: For static/media files.

### 4. Apply Migrations

```bash
python source/manage.py migrate
```

### 5. (Production Only) Collect Static Files

```bash
python source/manage.py collectstatic
```

### 6. Run the Development Server

```bash
python source/manage.py runserver
```

Visit [http://localhost:8000/stonewalker/](http://localhost:8000/stonewalker/) to see the app.
## Translation Quality Assurance System

This project includes a comprehensive translation quality assurance system to ensure all translations work correctly and maintain high quality standards.

### Translation QA Tests

The project includes automated tests located in `source/main/translation_tests.py` that validate:

#### 1. PO File Structure Validation (`TranslationQualityAssuranceTests`)
- **Proper Headers**: Ensures all PO files have correct charset and language specifications
- **No Empty Translations**: Checks that no `msgstr` entries are empty (except headers)
- **No Duplicate Entries**: Prevents duplicate `msgid` entries that cause compilation errors
- **Compilation Success**: Verifies all PO files can be compiled without errors

#### 2. Translation Functionality Tests (`TranslationFunctionalityTests`)
- **Cross-Language Testing**: Tests that translations work for all configured languages
- **Page Content Verification**: Ensures specific pages show translated content
- **Language Switching**: Validates URL-based language switching works correctly

#### 3. Translation Coverage Tests (`TranslationCoverageTests`)
- **Critical String Coverage**: Ensures important user-facing strings are translated
- **Translation Quality**: Checks that translations are actually different from source text

### Common Translation Issues Detected

The QA system automatically detects and reports these common issues:

#### 1. **Forbidden Characters** (Cause encoding errors)
- Smart quotes (`"`, `"`, `'`, `'`) - Use regular quotes (`"`, `'`)
- Ellipsis (`…`) - Use three dots (`...`)
- En/Em dashes (`–`, `—`) - Use regular hyphens (`-`)
- German quotes (`„`, `"`, `‚`, `'`) - Use regular quotes

#### 2. **PO File Structure Issues**
- Missing charset specification (`Content-Type: text/plain; charset=UTF-8`)
- Missing language specification (`Language: xx`)
- Empty `msgstr` entries (untranslated strings)
- Duplicate `msgid` entries (causes compilation failures)

#### 3. **Compilation Errors**
- Syntax errors in PO files
- Invalid escape sequences
- Malformed headers

### Running Translation Tests

```bash
# Run all translation QA tests
python source/manage.py test main.translation_tests

# Run specific test classes
python source/manage.py test main.translation_tests.TranslationQualityAssuranceTests
python source/manage.py test main.translation_tests.TranslationFunctionalityTests
python source/manage.py test main.translation_tests.TranslationCoverageTests
```

### Translation Workflow

1. **Extract Strings**: `python source/manage.py makemessages -l [language_code]`
2. **Edit Translations**: Modify the `.po` files in `source/content/locale/[lang]/LC_MESSAGES/`
3. **Run QA Tests**: `python source/manage.py test main.translation_tests`
4. **Fix Issues**: Address any errors reported by the QA tests
5. **Compile Messages**: `python source/manage.py compilemessages`
6. **Test Functionality**: Verify translations work in the browser

### Adding New Languages

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

### Translation Best Practices
n Issues

#### Common Error: "compilemessages generated one or more errors"

1. **Check for Duplicates**: Look for duplicate `msgid` entries
2. **Validate Syntax**: Check for unescaped quotes or invalid characters
3. **Verify Headers**: Ensure proper PO file headers are present
4. **Run QA Tests**: Use the automated tests to identify specific issues

#### Common Error: "UnicodeDecodeError"

1. **Check File Encoding**: Ensure PO files are saved as UTF-8
2. **Remove Smart Quotes**: Replace with regular quotes
3. **Clean Special Characters**: Use `iconv` to clean encoding issues

#### Common Error: "Translation not appearing"

1. **Check msgstr**: Ensure the translation is not empty
2. **Verify Compilation**: Run `compilemessages` after editing
3. **Clear Cache**: Restart Django server after changes
4. **Check Template Tags**: Ensure `{% trans %}` tags are properly usedse consistent terminology across all translations
5. **Context Matters**: Consider cultural context when translating

### Troubleshooting Translation Issues

#### Common Error: "compilemessages generated one or more errors"

1. **Check for Duplicates**: Look for duplicate `msgid` entries
2. **Validate Syntax**: Check for unescaped quotes or invalid characters
3. **Verify Headers**: Ensure proper PO file headers are present
4. **Run QA Tests**: Use the automated tests to identify specific issues

#### Common Error: "UnicodeDecodeError"

1. **Check File Encoding**: Ensure PO files are saved as UTF-8
2. **Remove Smart Quotes**: Replace with regular quotes
3. **Clean Special Characters**: Use `iconv` to clean encoding issues

#### Common Error: "Translation not appearing"

1. **Check msgstr**: Ensure the translation is not empty
2. **Verify Compilation**: Run `compilemessages` after editing
3. **Clear Cache**: Restart Django server after changes
4. **Check Template Tags**: Ensure `{% trans %}` tags are properly used

## Project Structure

- `source/` — Django project source code
  - `accounts/` — User authentication and profile management
  - `main/` — Main app views and logic (stones, moves, dashboard, map)
  - `content/` — Static assets, templates, translations
    - `assets/` — CSS, JS, images
    - `templates/` — HTML templates
    - `locale/` — Translation files
- `screenshots/` — UI screenshots
- `README.md` — This file

## Site Map

| URL Pattern | View / Description |
|-------------|-------------------|
| `/` or `/stonewalker/` | Main map and dashboard (`StoneWalkerStartPageView`) |
| `/my-stones/` | User's personal stones dashboard (`MyStonesView`) |
| `/add_stone/` | Add a new stone (POST only, login required) (`add_stone`) |
| `/stonescan/` | Scan a stone (GET/POST, login required, supports `?stone=PK_stone` for prefill/lock) (`StoneScanView`) |
| `/stone/<PK_stone>/qr/` | QR code for a stone's update link (`StoneQRCodeView`) |
| `/forum/` | Forum placeholder page |
| `/shop/` | Shop placeholder page |
| `/about/` | About page |
| `/api/check_stone_name/` | API endpoint to check stone name availability |
| `/language/` | Change language (`ChangeLanguageView`) |
| `/accounts/log-in/` | Log in |
| `/accounts/log-out/` | Log out |
| `/accounts/log-out/confirm/` | Log out confirmation |
| `/accounts/sign-up/` | Sign up |
| `/accounts/activate/<code>/` | Activate account |
| `/accounts/change/profile/` | Change profile (modal/profile page) |
| `/accounts/change/email/<code>/` | Change email activation |
| `/accounts/resend/activation-code/` | Resend activation code |
| `/accounts/resend-email-activation/` | Resend email activation |
| `/accounts/cancel-email-change/` | Cancel email change |
| `/accounts/restore/password/` | Restore password |
| `/accounts/restore/password/done/` | Restore password done |
| `/accounts/restore/<uidb64>/<token>/` | Restore password confirm |
| `/accounts/remind/username/` | Remind username |
| `/accounts/api/check_username/` | API endpoint to check username availability |
| `/admin/` | Django admin panel |

## Database Architecture

The StoneWalker application uses Django ORM models to represent its core data:

### User (Django built-in)
- Standard Django user model, extended via Profile.

### Profile
- Extends the User model with a profile picture.
- One-to-one relationship with User.

| Field           | Type           | Description                                   |
|-----------------|----------------|-----------------------------------------------|
| id              | AutoField      | Primary key                                   |
| user            | OneToOneField  | Linked user                                   |
| profile_picture | ImageField     | Optional profile image (default: user_picture.png) |

### Stone
- Represents a painted stone tracked in the app.
- Each stone is associated with a user and has a location on the map.

| Field        | Type         | Description                                 |
|--------------|--------------|---------------------------------------------|
| PK_stone     | CharField    | Primary Key (max 10 chars, unique, no whitespace) |
| description  | TextField    | Optional description of the stone (max 500char) |
| created_at   | DateTimeField| Timestamp when the stone was created        |
| FK_user      | ForeignKey   | User who created the stone                  |
| image        | ImageField   | Optional image of the stone                 |
| color        | CharField    | Color hex code (default: #4CAF50)           |
| shape        | CharField    | Shape (default: 'circle')                   |
| distance_km  | FloatField   | Total distance traveled (km)                |

### StoneMove
- Represents a scan/move of a stone by a user (i.e., a new location and optional comment/image for a stone).
- Many-to-one relationship to Stone and User.

| Field      | Type         | Description                                   |
|------------|--------------|-----------------------------------------------|
| id         | AutoField    | Primary key                                   |
| FK_stone   | ForeignKey   | The stone being moved                         |
| FK_user    | ForeignKey   | User who scanned/moved the stone              |
| image      | ImageField   | Optional image of the move                    |
| comment    | TextField    | Optional comment                              |
| latitude   | FloatField   | Latitude of the move                          |
| longitude  | FloatField   | Longitude of the move                         |
| timestamp  | DateTimeField| When the move was recorded                    |

### Activation
- Used for account activation and email confirmation.
- Many-to-one relationship to User.

| Field      | Type         | Description                                   |
|------------|--------------|-----------------------------------------------|
| id         | AutoField    | Primary key                                   |
| user       | ForeignKey   | User to activate                              |
| created_at | DateTimeField| When the activation was created               |
| code       | CharField    | Unique activation code                        |
| email      | EmailField   | Email for activation (optional)               |

#### Model Relationships Diagram

```
User <1----1> Profile
User <1----*> Stone
User <1----*> StoneMove
Stone <1----*> StoneMove
User <1----*> Activation
```

## Backend Logic

The backend of StoneWalker is built with Django and follows a modular, class-based view structure:

### Authentication & Profile Management
- **Registration, Login, Logout:** Handled via Django's authentication system and custom views in `accounts`.
- **Account Activation:** Users must activate their account via a unique code sent to their email (`Activation` model).
- **Profile Editing:** Users can edit their profile (username, email, password, profile picture) via a modal or dedicated page.
- **Password Reset:** Users can request a password reset link via email and set a new password securely.

### Stone Management
- **Add Stone:** Authenticated users can create new stones with a unique name, description, color, shape, and image.
- **Scan Stone (Move):** Authenticated users can scan a stone (log a move), updating its location, uploading a photo, and adding a comment. Enforces a cooldown (users can only scan the same stone once every 3 days).
- **QR Codes:** Each stone has a unique QR code that links directly to its scan page, pre-filling and locking the stone name for easy updates.
- **Personal Dashboard:** Users can view all their stones and moves on `/my-stones/`.

### API Endpoints
- **Check Stone Name:** `/api/check_stone_name/` returns JSON indicating if a stone name is available.
- **Check Username:** `/accounts/api/check_username/` returns JSON indicating if a username is available.

### Internationalization
- All user-facing text is translatable. Language can be changed via `/language/`.

### Error Handling & Security
- All sensitive actions require authentication.
- CSRF protection is enabled for all forms.
- File uploads (images) are validated and stored securely.
- Cooldown logic prevents abuse of the stone scanning feature.

## Frontend Logic

The frontend of StoneWalker is designed for a modern, responsive, and user-friendly experience:

### Navigation & Layout
- **Header & Burger Menu:** The header contains the logo, navigation links, and profile picture (if logged in). Navigation links are centralized in `layouts/default/nav_links.html`.
- **Burger Menu:** On mobile, the burger menu provides access to all main navigation links, including My Stones, Edit Profile, Logout (if logged in), and Change Language.
- **Profile Picture:** After login, the user's profile picture appears in the header and can be clicked to open the profile modal.

### Modals & Popups
- **Profile Edit Modal:** Accessible from the header or burger menu, the profile modal overlays the current page and loads the profile edit form via AJAX.
- **Welcome Modal:** Shown to guests on the main page, encouraging sign up or login. Uses localStorage to avoid repeat popups.

### Main Templates
- **Base Layout:** `layouts/default/page.html` provides the main structure, header, and modal containers.
- **Main Pages:**
  - `main/index.html`: Welcome page with quick actions.
  - `main/stonewalker_start.html`: Main map/dashboard with guest modal and map display.
  - `main/my_stones.html`: User's stones and moves.
  - `main/stone_scan.html`: Scan a stone (move form).
  - `main/about.html`, `main/forum.html`, `main/shop.html`: Informational/placeholder pages.

### JavaScript Interactions
- **header.js:** Handles burger menu toggling, profile modal open/close, and AJAX profile form submission.
- **stone-modal.js:** Handles modal logic for stones (if present).
- **Responsive Design:** All navigation and modal actions are mobile-friendly and touch-optimized.

### Styles
- **styles.css:** Centralized CSS for layout, navigation, modals, and custom UI elements. Bootstrap 4 is used for base styling, with custom overrides for the avantgarde look.

## Responsive Design

StoneWalker is optimized for seamless viewing and usability across desktop, tablet, and mobile devices. The layout uses a combination of Bootstrap 4 and custom CSS with multiple breakpoints for a fluid, modern experience.

### Responsive Breakpoints: Single Source of Truth & Automation

All responsive breakpoints for this project are defined in a single place: the `BREAKPOINTS` object at the top of `source/content/assets/js/header.js`.

**How to change breakpoints:**
1. Edit the `BREAKPOINTS` object in `header.js`.
2. Run the sync script to update all hardcoded px values in `styles.css`:

   ```sh
   node source/content/assets/js/sync-breakpoints.js
   ```

This will automatically update all media queries in your CSS to match the breakpoints in JS. You only need to change breakpoints in one place!

### Approach
- All main containers, cards, nav, and modals use flexible widths and padding.
- Header, navigation, and floating action buttons scale and reflow for touch and small screens.
- Font sizes, button sizes, and touch targets are adjusted for readability and usability.
- No fixed widths or paddings that break on small screens.

## Testing

This project uses Django's built-in test runner for backend and API testing. The test suite covers:
- User authentication (sign up, login, activation, password reset)
- Profile management (view, edit, change email, password, profile picture)
- Stone creation (valid/invalid data, permissions)
- Stone scanning/moves (valid/invalid, cooldown enforcement)
- API endpoints (check stone name, check username)
- Permissions and security (access control, unauthenticated access)
- CSS utility classes and responsive design

### Git Pre-push Hook

A git pre-push hook is set up in `.git/hooks/pre-push` to automatically run all backend tests before any push. If any test fails, the push will be aborted.

If you clone the repo or set up a new environment, make sure the hook is executable:

```bash
chmod +x .git/hooks/pre-push
```

### Running the Tests

Activate your virtual environment, then run:

```bash
python source/manage.py test accounts main
```

All tests should pass. The test suite is designed to be run automatically on every code change to ensure robustness and prevent regressions.

## Tech Stack

- **Backend:** Python 3.8+, Django 4.2
- **Frontend:** HTML5, CSS3, JavaScript (Leaflet.js for maps, Bootstrap 4 for UI)
- **Auth:** Django's built-in authentication system
- **Package Management:** Poetry (see `pyproject.toml`) or pip/venv (see `requirements.txt`)
- **Database:** SQLite (default, easy to swap for Postgres/MySQL)

## Screenshots

| Log In | Create an Account | Authorized Page |
|--------|------------------|-----------------|
| <img src="./screenshots/login.png" width="200"> | <img src="./screenshots/create_an_account.png" width="200"> | <img src="./screenshots/authorized_page.png" width="200"> |

| Password Reset | Set New Password | Password Change |
|----------------|------------------|-----------------|
| <img src="./screenshots/password_reset.png" width="200"> | <img src="./screenshots/set_new_password.png" width="200"> | <img src="./screenshots/password_change.png" width="200"> |

## Live Demo

The main StoneWalker experience is available at:

    http://localhost:8000/stonewalker/

This page features the interactive map, login modal, and personal dashboard.

## Recent Refactoring Work

### Font System Refactoring (2024)
- Replaced Google Fonts imports with OpenSans from Google Fonts
- Added local GiantBoom font using @font-face declaration
- Updated CSS variables for consistent typography across the application
- Font files available in `source/content/assets/fonts/GiantBoomDEMO/GiantBoomFont.otf`

### CSS Centralization and Deduplication (2024)
- Created comprehensive utility class system with over 200 utility classes
- Replaced all inline styles with utility classes across all templates
- Automated CSS deduplication script (`dedupe_css.py`) reduced CSS by 43% (2,112 lines)
- Added comprehensive test coverage for utility classes

### Burger/Profile Menu & Navigation (2024)
- Improved mobile responsiveness and menu interactions
- Fixed z-index and pointer-events for better usability
- Simplified menu toggle logic using pure CSS
- Enhanced overlay and menu visibility for mobile/desktop

### Header Scaling Improvements (2024)
- Implemented CSS variable `--header-height` for consistent scaling
- All header elements now scale properly across all breakpoints
- Removed redundant hardcoded heights
- Improved visual balance and responsiveness

### Change Language Page Styling (2024)
- Redesigned the change language page to match the avant-garde design system
- Replaced Bootstrap classes with custom utility classes for consistent styling
- Added proper responsive design with avant-card layout and background gradients
- Implemented comprehensive test coverage for the change language functionality
- Ensured the page is accessible to both authenticated and unauthenticated users

### Comprehensive Localization Implementation (2024)
- Added complete i18n support with `{% trans %}` tags across all templates
- Localized all hardcoded text in main pages (index, about, stonewalker_start, stone_scan, forum, shop, my_stones)
- Added Italian language support to the language settings
- Created locale directories and translation files for all languages (English, Spanish, French, Russian, Chinese, German, Italian)
- All new translatable strings automatically added to all language files
- Updated tests to work with localized text
- Ready for manual translation of all strings in each language file
- English translation file allows customization of English text tone and wording
- Implemented browser language detection for automatic initial language selection
- Added language detection settings and middleware configuration
- Created debug tools for testing language detection functionality
- Fixed translation file compilation issues and syntax errors
- Resolved language code mismatches between settings and directory names
- Ensured all .mo files are properly compiled and working
- Added sample Italian translations for key strings (About StoneWalker, Welcome to StoneWalker)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Original authentication base: [egorsmkv/simple-django-login-and-register](https://github.com/egorsmkv/simple-django-login-and-register)
- UI/UX design: Busssard
- Map: [Leaflet.js](https://leafletjs.com/)
- Project maintained by StoneWalker.org
