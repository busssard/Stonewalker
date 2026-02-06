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
- **Change Language:** Users can change the UI language (`/language/`) and are automatically redirected to the main page after language change.

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-fork-or-this-repo-url>
cd simple-django-login-and-register
```

### 2. Deployment Options

#### Option A: Local Development
Follow the steps below for local development.

#### Option B: Render Deployment (Recommended)
For deploying the full Django application, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Render deployment instructions.

### 3. Set Up a Virtual Environment

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

### 4. Configure Settings

- For development: edit `source/app/conf/development/settings.py`
- For production: edit `source/app/conf/production/settings.py`

Set up email backend, allowed hosts, and any other environment-specific options.

#### Key Settings & Environment Variables

- `SECRET_KEY`: Set a unique secret key for your environment.
- `DEBUG`: Set to `True` for development, `False` for production.
- `ALLOWED_HOSTS`: List of allowed hostnames (e.g., `['localhost', '127.0.0.1']`).
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`: Configure for email sending.
- `DATABASES`: Uses PostgreSQL for both development and production.
- `LANGUAGE_CODE`, `LANGUAGES`, `LOCALE_PATHS`: For internationalization.
- `STATIC_ROOT`, `STATIC_URL`, `MEDIA_ROOT`, `MEDIA_URL`: For static/media files.

#### Local development (PostgreSQL)

```bash
# Set up local PostgreSQL database
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"

# Run migrations and start server
cd source
python manage.py migrate
python manage.py runserver
```

#### Using the convenience script

```bash
# Uses default local PostgreSQL database
./run_dev.sh
```

- The application requires PostgreSQL for both development and production. Set `DATABASE_URL` to your PostgreSQL connection string.

### 5. Apply Migrations

```bash
python source/manage.py migrate
```

### 6. (Production Only) Collect Static Files

```bash
python source/manage.py collectstatic
```

### 7. Run the Development Server

```bash
python source/manage.py runserver
```

Visit [http://localhost:8000/stonewalker/](http://localhost:8000/stonewalker/) to see the app.
## Translation Quality Assurance System

This project includes a comprehensive translation quality assurance system to ensure all translations work correctly and maintain high quality standards.

> For detailed information about translation management, testing, and workflows, see [TRANSLATION.md](TRANSLATION.md)

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
| `/stone-link/<str:stone_uuid>/` | Stone found page with UUID-based routing (`StoneLinkView`) |
| `/download-qr/` | Download QR code (`download_qr_code`) |
| `/regenerate-qr/<str:stone_pk>/` | Regenerate QR code for existing stone (`regenerate_qr_code`) |
| `/api/generate-qr/` | Generate QR code API (`generate_qr_code`) |
| `/api/check-stone-uuid/<str:uuid>/` | Check if stone UUID exists (`check_stone_uuid`) |
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

## Database Management

For production database management, the project includes a comprehensive CLI tool for CRUD operations on users and stones.

### Setup

1. **Create production credentials file:**
   ```bash
   # Create postgres_production.json (excluded from git)
   {
     "host": "your-production-host",
     "port": 5432,
     "database": "your-database-name", 
     "user": "your-username",
     "password": "your-password",
     "sslmode": "require"
   }
   ```

2. **Make the database manager executable:**
   ```bash
   chmod +x db
   ```

### Usage

The database manager provides easy-to-use commands for managing your production PostgreSQL database:

#### User Management
```bash
# List users (active only by default)
./db list-users --limit 10

# List all users including inactive
./db list-users --all

# Get specific user
./db get-user --username john_doe
./db get-user --id 123
./db get-user --email user@example.com

# Create new user
./db create-user --username newuser --email user@example.com --password secretpass

# Update user
./db update-user --id 123 --first_name John --last_name Doe

# Delete specific user
./db delete-user --id 123 --confirm

# Delete old inactive users (older than 5 minutes by default)
./db delete-old-inactive --confirm --minutes 10
```

#### Stone Management
```bash
# List stones
./db list-stones --limit 20

# List stones for specific user
./db list-stones --user-id 123

# List stones by type
./db list-stones --type hidden

# Get specific stone
./db get-stone --id STONE001

# Create new stone
./db create-stone --id STONE001 --user-id 123 --description "My test stone"

# Update stone
./db update-stone --id STONE001 --description "Updated description" --color "#FF0000"

# Delete stone
./db delete-stone --id STONE001 --confirm
```

#### Utility Commands
```bash
# Show database statistics
./db stats

# Find problematic users/stones
./db find-problems

# Test database connection
./db test-connection
```

### Safety Features

- **Confirmation required** for all destructive operations
- **Preview before deletion** - shows exactly what will be deleted
- **Detailed logging** - shows each operation as it happens
- **Error handling** - graceful failure with helpful error messages

### Security

- Database credentials are stored in `postgres_production.json` (excluded from git)
- All management scripts are excluded from version control
- Production database access requires explicit confirmation flags

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
- After changing language, users are automatically redirected to the main page (`/stonewalker/`) for a seamless experience.
- Language preferences are preserved across sessions and don't affect user authentication.

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
- **Welcome Modal:** Shown to guests on the main page, encouraging sign up or login. Features modern avant-garde styling with decorative background elements, improved typography hierarchy, and localStorage functionality to avoid repeat popups.

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
- **Database:** PostgreSQL (required for both development and production)

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

### QR Code Logic Implementation (2024)
- **Server-Side QR Generation**: Implemented complete QR code generation system using Python qrcode library
- **StoneScanAttempt Model**: Added new model to track scan attempts and enforce one-week blackout period
- **Stone-Link System**: Created stone-link URLs with UUID-based routing and cookie tracking
- **QR Code API**: Added API endpoints for QR code generation and UUID validation
- **Real QR Scanner**: Implemented actual QR code scanning using html5-qrcode library with camera access
- **Database Integration**: UUID is automatically generated and stored in database when stone is created
- **Cookie Tracking**: Stone-link visits are tracked with cookies for analytics and blackout enforcement
- **Comprehensive Testing**: Added 24 new tests covering QR generation, stone-link functionality, blackout enforcement, and UUID validation
- **Dependencies**: Added qrcode==7.4.2 and pillow==10.0.1 for QR code generation
- **Complete Sequence**: Implemented full workflow from stone creation → QR generation → stone-link → scanning → blackout enforcement
- **QR Test Page**: Created dedicated test page at `/qr-test/` for testing QR scanner functionality
- **Debug Modals Integration**: Fixed QR code generation and display in debug modals with real image download
- **API Authentication**: Removed login requirement from QR generation API for debug functionality
- **Shared Modals System**: Created shared modals template for consistent modal behavior across pages with working JavaScript functions, resolved duplicate modal conflicts, fixed global function accessibility, centralized JavaScript functionality in shared_modals.html for code reuse, fixed circular reference issues between debug and shared modal functions, implemented complete QR scanner functionality in the shared scan stone modal with camera access, UUID validation, and stone information display, added hunted stone location field with map integration, implemented scan modal congratulations and automatic forwarding to stone UUID weblink, and created comprehensive stone found page with first-time user experience and hunted stone special handling

### QR System Robustness Improvements (2025)
- **Enhanced Error Handling**: Improved QR code generation with proper error handling that doesn't fail stone creation if QR generation fails
- **Robust Stone Creation**: Stone creation now succeeds even if QR generation fails, with appropriate user feedback
- **QR Code Regeneration**: Added `/regenerate-qr/<stone_pk>/` endpoint to regenerate QR codes for existing stones
- **Improved Persistence**: QR codes are now more persistent with better file handling and error recovery
- **Consistent URL Structure**: All QR codes now use stone-link URLs (`/stone-link/<uuid>/`) for consistency
- **Better Logging**: Added proper error logging for QR generation failures without affecting user experience
- **Session Management**: Improved session data handling for QR code downloads with proper cleanup on errors
- **Comprehensive Testing**: Added 9 new tests covering improved error handling, regeneration functionality, and robustness
- **Backward Compatibility**: Maintained all existing functionality while improving reliability and user experience

### QR Code Cleartext Display (2025)
- **Cleartext URL Display**: QR codes display the actual URL in cleartext underneath the QR code image for better user understanding
- **3:4 Portrait PNG Format**: Downloaded QR code images are in 3:4 portrait format with QR code at top and cleartext URL at bottom
- **Embedded in Downloaded PNG**: The cleartext URL is embedded directly in the PNG image file that users download, making it visible when printed or shared
- **Improved User Experience**: Users can see exactly what URL the QR code points to without needing to scan it, both on screen and in downloaded images
- **High Contrast Text**: Cleartext URLs use black text (#000000) on light background with 18px font size for maximum readability
- **Generous Text Space**: 120px dedicated space below QR code ensures text is clearly visible and readable
- **Centered Layout**: QR code is centered horizontally in the top portion, text is centered in the bottom portion
- **Multiple Display Locations**: Cleartext URLs appear in both the main QR code display, QR code modal popups, and downloaded PNG files
- **Responsive Design**: Cleartext URLs use word-break styling to handle long URLs gracefully on all screen sizes
- **Template Integration**: Updated both shared_modals.html template and JavaScript QR code display functions
- **Comprehensive Testing**: Added 7 tests covering cleartext URL display, 3:4 format verification, text rendering validation, and PNG embedding
- **User-Friendly**: Text is positioned to not interfere with QR code scanning but provides helpful context
- **Verified Working**: All QR code functionality has been verified to work correctly with 25 passing tests covering QR generation, cleartext display, and API integration

### Stone Creation Refactoring (2024)
- **UUID Integration**: Added UUID field to Stone model for secure QR code generation and unique stone identification
- **Automatic Shape Selection**: Stones now automatically get circle shape for hidden stones and triangle shape for hunted stones
- **QR Code Generation**: Each stone creation now generates a unique QR code linking to the stone's scan page using UUID
- **QR Download Functionality**: Users can download the generated QR code after stone creation via the success message link
- **Enhanced Stone Scanning**: Stone scanning now supports both UUID and PK_stone parameters for backward compatibility
- **Improved Validation**: Hunted stones now properly require location before creation, preventing invalid stones
- **Comprehensive Testing**: Added 18 new tests covering UUID generation, QR functionality, automatic shape selection, and stone scanning
- **Database Migrations**: Created proper migration sequence for UUID field addition with data population for existing records

### Fixed Header Implementation (2024)
- **Fixed Header Positioning**: Implemented a fixed header that remains visible at the top of the viewport during scrolling
- **Header Lock**: The header-bar is now locked visible even when the rest of the page is scrolling down in all device configurations
- **Content Spacing**: Added proper top padding to the body to prevent content from being hidden behind the fixed header
- **Z-Index Management**: Properly managed z-index values to ensure the header stays above other content while allowing overlays to work correctly
- **Burger Menu Compatibility**: Updated burger menu overlay and navigation to work seamlessly with the fixed header
- **Responsive Design**: Ensured the fixed header works correctly across all device sizes and orientations
- **Scrolling Functionality**: Fixed CSS issues that were preventing scrolling on pages like About, Create Stone, Scan Stone, and Create Account
- **Overlay Height Fixes**: Changed problematic `height: 100vh` rules to `height: 100%` to prevent viewport overflow issues
- **Test Coverage**: Added comprehensive test coverage for fixed header functionality including positioning, padding, and scrolling behavior
- **Cross-Browser Compatibility**: Ensured the fixed header works consistently across different browsers and devices

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

### Welcome Modal Styling Improvements (2024)
- Enhanced the welcome modal styling to match the modern avant-garde design system
- Added decorative background elements (gradient circles) consistent with other pages
- Improved typography hierarchy with better font weights and spacing
- Enhanced button layout with proper flexbox centering and gap spacing
- Added comprehensive test coverage for welcome modal functionality and styling
- Maintained all existing functionality including localStorage behavior and responsive design

### My-Stones Functionality Verification (2024)
- Verified that the my-stones page is working correctly and not actually broken
- Confirmed that empty state messages are properly displayed when users have no stones
- Added comprehensive test coverage for my-stones functionality including:
  - Page loading for authenticated users
  - Authentication requirements
  - Empty state handling
  - Stone display with distance calculations
  - Interaction tracking (stones moved by user but not created by user)
  - Context data validation
- The my-stones page correctly shows user's created stones and interactions with other users' stones
- Distance calculations work correctly for stones with multiple moves
- Empty state messages guide users to create stones or scan existing ones

### Stone Modal Popup Fix (2024)
- Fixed the stone modal popup functionality that was not working when clicking on stones
- Resolved ES6 module import conflicts that were preventing the modal from loading
- Fixed CSS class conflicts where `display-none` was overriding `display: flex`
- Implemented proper modal container creation and cleanup for existing modals
- Added fallback functionality using `showSimpleModal` when ES6 import fails
- Enhanced error handling with proper catch blocks for import failures
- Added comprehensive test coverage for stone modal functionality including:
  - Modal import and function availability
  - Fallback modal functionality
  - CSS conflict resolution
  - Click handler setup
  - Modal content generation
- The stone modal now properly displays stone details, images, moves, and comments
- Modal can be closed by clicking the X button or clicking outside the modal
- All stone interactions in my-stones page now work correctly

### Stone Modal Popup Fix (2024)
- Identified and fixed the stone modal popup functionality in my-stones page
- The issue was with ES6 module import reliability in the browser
- Implemented a robust solution with:
  - Primary ES6 module import for the full stone modal functionality
  - Fallback modal function for cases where ES6 modules fail to load
  - Comprehensive error handling and user feedback
  - Maintained all existing modal features (images, comments, distance, etc.)
- Added fallback modal function that provides basic stone information display
- Enhanced error logging and user feedback for debugging modal issues
- The stone modal now works reliably across different browsers and network conditions

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
- **Language Change Redirect:** Users are now automatically redirected to the main page (`/stonewalker/`) after changing their language preference, providing a seamless user experience
- **Enhanced Language Change Testing:** Added comprehensive test coverage for language change functionality including redirect behavior, session preservation, and context data validation

### Signup Popup Redesign

The sign-up page (`/accounts/sign-up/`) now renders as a modal-style popup overlay.
- Accessible dialog semantics (`role="dialog"`, `aria-modal`, labeled title)
- Close via outside click, ESC, or the close button
- Background scroll is locked while open
- All styles live in `source/content/static/css/styles.css` and mirrored in `source/content/assets/css/styles.css`

### Database: PostgreSQL (dev and prod)

- Both development and production use PostgreSQL.
- Set `DATABASE_URL` environment variable to your PostgreSQL connection string.

Run with PostgreSQL locally:

```bash
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
cd source
python manage.py migrate
python manage.py runserver
```

Or use the convenience script:

```bash
./run_dev.sh
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Original authentication base: [egorsmkv/simple-django-login-and-register](https://github.com/egorsmkv/simple-django-login-and-register)
- UI/UX design: Busssard
- Map: [Leaflet.js](https://leafletjs.com/)
- Project maintained by StoneWalker.org

## Recent Updates (2024-2025)

### Netlify Deployment Setup (2025)
- **Netlify Configuration**: Created comprehensive Netlify deployment setup with `netlify.toml`, build script, and serverless functions
- **Static Site Hosting**: Configured for hosting static files (CSS, JS, images) on Netlify's CDN with automatic HTTPS
- **Serverless Functions**: Implemented basic Django routing via Netlify Functions for API endpoints
- **Build Automation**: Created `build.sh` script for automated deployment with static file collection and migration support
- **Environment Variables**: Added support for environment variable configuration in production settings
- **Security Headers**: Configured security headers and caching rules for optimal performance
- **Comprehensive Documentation**: Created detailed deployment guide with alternative platform recommendations
- **Testing Coverage**: Added 10 new tests covering Netlify configuration, build scripts, and deployment functionality
- **Deployment Limitations**: Clearly documented Netlify's limitations for Django applications and provided migration paths to Django-native platforms

### Stone Found Experience Implementation (August 2025)
- **Hunted Stone Location Field**: Added location input fields (latitude/longitude) that appear when "hunted" stone type is selected in create-new modal
- **Interactive Map Integration**: Integrated Leaflet.js maps for easy location selection with drag-and-drop functionality
- **Location Validation**: Added validation to require location coordinates for hunted stones with coordinate range checking
- **Scan Modal Congratulations**: Updated scan modal to show congratulations message when QR code is scanned with automatic forwarding to stone UUID weblink
- **Stone UUID Weblink Page**: Created comprehensive `stone_found.html` template with:
  - **First-time User Experience**: Detects if this is user's first stone and provides welcome explanation
  - **Stone Information Display**: Shows stone name, type, description, and creator
  - **Location Selection**: Interactive map for selecting where stone was found
  - **Hunted Stone Special Handling**: Congratulates user for finding hunted stone, explains that many others were looking for it, requires new location selection for next week placement
  - **Form Validation**: Comprehensive error handling and validation for coordinates
  - **Session Storage**: New locations stored for future placement
- **Database Schema Update**: Added `stone_type` field to Stone model with choices for 'hidden' and 'hunted'
- **Translation Support**: Added all frontend text from stone_found.html to translations.csv with complete translations in 7 languages
- **Comprehensive Testing**: Added 18 new test cases covering all functionality including:
  - Stone found page loading and form submission
  - Hunted stone location field presence and validation
  - Scan modal congratulations and forwarding functionality
  - Stone found template rendering and map functionality
  - First-time user detection and special messages
  - Coordinate validation and error handling
  - Session storage for hunted stone new locations

### QR Code Logic Implementation (2024)
- **Debug Modals Integration**: Fixed QR code generation and display in debug modals with real image download
- **API Authentication**: Removed login requirement from QR generation API for debug functionality
- **Shared Modals System**: Created shared modals template for consistent modal behavior across pages with working JavaScript functions, resolved duplicate modal conflicts, fixed global function accessibility, centralized JavaScript functionality in shared_modals.html for code reuse, fixed circular reference issues between debug and shared modal functions, implemented complete QR scanner functionality in the shared scan stone modal with camera access, UUID validation, and stone information display, added hunted stone location field with map integration, implemented scan modal congratulations and automatic forwarding to stone UUID weblink, and created comprehensive stone found page with first-time user experience and hunted stone special handling
