# StoneWalker - A Global Stone Traveling Community

StoneWalker is a Django-based web application for tracking the journeys of painted stones as they travel the world. Inspired by geocaching and collaborative art, StoneWalker lets users log in, register, and follow the artistic adventures of unique stones on an interactive map.

## Features

- **Modern UI & Navigation:** Responsive, artsy/avantgarde design with a unified header and burger menu. The header includes a logo, navigation links (My Stones, Forum, Shop, About, Change Language), and a login/profile button that turns into your profile picture after login. The menu is mobile-friendly and consistent across all pages.
- **Profile Popup Modal:** Edit your profile (username, email, password, profile picture) in a popup modal window that overlays the current page, with a close (cross) button. Accessible from the header via the "Edit Profile" link or your profile picture.
- **Interactive Map:** Visualize the journeys of painted stones across the globe on `/stonewalker/`. Filter by stone type (hidden/hunted) with pill-shaped toggle controls floating over the bottom-left of the map.
- **User Authentication:** Register, log in, log out, activate accounts via email, reset password, and manage your profile securely (username, email, password, profile info).
- **Personal Dashboard:** View your stones and submissions in a dedicated area (`/my-stones/`).
- **Add Stones:** Authenticated users can add new stones with name, description, color, shape, and image. The "Create New Stone" button is visually prominent, with a random color highlight on hover and a clear subtitle.
- **Scan Stones:** Authenticated users can scan (log a move for) a stone, updating its location and optionally uploading a photo and comment. The "Scan a Stone" button is clearly labeled.
- **Stone Update QR Codes:** Each stone has a unique QR code with sequential stone number (e.g., "Stone #42") displayed prominently on the download.
- **Stone Certificate:** Download a professional PDF certificate after creating a stone, featuring the stone image, owner name, creation date, and QR code.
- **Cooldown for Updates:** Users can only update (scan) a given stone once every 3 days; the scan form is locked if accessed again within this period.
- **Branded Transactional Emails:** All account emails (activation, password reset, email change, username recovery) use consistent StoneWalker branding with green header, responsive layout, and professional footer.
- **Premium Supporter Tier:** Optional subscription via Stripe recurring billing. Unlocks journey analytics, premium badge, unlimited drafts, priority support, and early access. Includes subscription management page, Stripe Billing Portal integration, and webhook handling for subscription lifecycle events.
- **Forum (Discourse SSO):** Built-in Discourse SSO integration — users clicking "Forum" are automatically logged in with their StoneWalker account.
- **Multilingual Support:** English, French, Russian, Simplified Chinese, Spanish, German, and Italian with browser language detection.
- **Admin Panel:** Manage users and content via Django admin (`/admin/`).
- **Mobile-friendly:** Works on desktop and mobile browsers. Burger menu scrolls properly on small screens without overlapping the floating action buttons.
- **Dark Mode:** Full dark mode support across all pages including the about page, change language page, and mobile burger menu.
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
export DATABASE_URL="postgresql://your_user:your_pass@localhost:5432/your_db"

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

### Public Pages

| URL Pattern | View / Description |
|-------------|-------------------|
| `/` or `/stonewalker/` | Main map and dashboard (`StoneWalkerStartPageView`) |
| `/about/` | About StoneWalker |
| `/forum/` | Forum page |
| `/language/` | Change language (`ChangeLanguageView`) |
| `/robots.txt` | Search engine crawler rules |

### Stone Management (login required)

| URL Pattern | View / Description |
|-------------|-------------------|
| `/my-stones/` | User's personal stones dashboard (`MyStonesView`) |
| `/create-stone/` | Smart router: unclaimed QR -> claim, else -> shop (`CreateNewStoneView`) |
| `/add_stone/` | Legacy redirect to `/create-stone/` (`add_stone`) |
| `/stonescan/` | Scan a stone (GET/POST, supports `?stone=<uuid or name>` for prefill/lock) (`StoneScanView`) |
| `/stone/<pk>/edit/` | Edit a draft stone (`StoneEditView`) |
| `/stone/<pk>/qr/` | Download QR code for a stone with "Stone #N" banner (`StoneQRCodeView`) |
| `/stone/<pk>/certificate/` | Download PDF certificate of stone creation (`StoneCertificateView`) |
| `/stone/<pk>/send-off/` | Finalize a published stone (`StoneSendOffView`) |
| `/stone-link/<uuid>/` | Stone found page from QR scan (`StoneLinkView`) |
| `/claim-stone/<uuid>/` | Claim an unclaimed stone (`ClaimStoneView`) |

### Premium Supporter (login required)

| URL Pattern | View / Description |
|-------------|-------------------|
| `/premium/` | Premium landing page with features, pricing, FAQ (`PremiumView`) |
| `/premium/checkout/` | POST — creates Stripe Checkout Session (`PremiumCheckoutView`) |
| `/premium/manage/` | Subscription status and billing portal access (`PremiumManageView`) |
| `/premium/billing/` | POST — redirects to Stripe Billing Portal (`PremiumBillingPortalView`) |

### Shop (login required for checkout)

| URL Pattern | View / Description |
|-------------|-------------------|
| `/shop/` | Browse QR code products (`ShopView`) |
| `/shop/checkout/<product_id>/` | Checkout for a product (`CheckoutView`) |
| `/shop/success/` | Post-checkout confirmation (`CheckoutSuccessView`) |
| `/shop/download/<pack_id>/` | Download PDF of QR pack (`DownloadPackPDFView`) |
| `/shop/download-qr/<uuid>/` | Download single QR from pack (`DownloadStoneQRView`) |
| `/shop/free-qr/` | Legacy free QR endpoint (`FreeQRView`) |

### API Endpoints (no language prefix)

| URL Pattern | View / Description |
|-------------|-------------------|
| `/api/check_stone_name/` | Check stone name availability (JSON) |
| `/api/check-stone-uuid/<uuid>/` | Check if stone UUID exists (JSON) |
| `/api/generate-qr/` | Generate QR code preview (JSON + base64) |
| `/api/download-enhanced-qr/` | Download branded QR code (PNG) |
| `/webhooks/stripe/` | Stripe payment webhook (POST only) |

### Authentication (`/accounts/`)

| URL Pattern | View / Description |
|-------------|-------------------|
| `/accounts/log-in/` | Log in |
| `/accounts/log-out/` | Log out |
| `/accounts/log-out/confirm/` | Log out confirmation |
| `/accounts/sign-up/` | Sign up |
| `/accounts/activate/<code>/` | Activate account via email link |
| `/accounts/change/profile/` | Edit profile (modal or full page) |
| `/accounts/change/email/<code>/` | Confirm email change |
| `/accounts/resend/activation-code/` | Resend activation code |
| `/accounts/resend-email-activation/` | Resend email activation link |
| `/accounts/cancel-email-change/` | Cancel pending email change |
| `/accounts/restore/password/` | Request password reset |
| `/accounts/restore/password/done/` | Password reset confirmation |
| `/accounts/restore/<uidb64>/<token>/` | Set new password via reset link |
| `/accounts/remind/username/` | Recover forgotten username |
| `/accounts/api/check_username/` | Check username availability (JSON) |
| `/accounts/discourse-sso/` | Discourse SSO endpoint |

### Admin

| URL Pattern | View / Description |
|-------------|-------------------|
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
| PK_stone     | CharField    | Primary Key (max 50 chars, unique, no whitespace) |
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

### Subscription
- Tracks premium supporter subscriptions via Stripe recurring billing.
- One-to-one relationship with User.

| Field                   | Type           | Description                                     |
|-------------------------|----------------|-------------------------------------------------|
| id                      | BigAutoField   | Primary key                                     |
| user                    | OneToOneField  | Linked user                                     |
| stripe_customer_id      | CharField      | Stripe Customer ID                              |
| stripe_subscription_id  | CharField      | Stripe Subscription ID                          |
| plan                    | CharField      | Plan type: monthly, yearly, or lifetime |
| status                  | CharField      | Status: active, canceled, past_due, unpaid, trialing, incomplete |
| current_period_start    | DateTimeField  | Start of current billing period                 |
| current_period_end      | DateTimeField  | End of current billing period                   |
| canceled_at             | DateTimeField  | When subscription was canceled (null if active) |
| created_at              | DateTimeField  | When subscription was created                   |
| updated_at              | DateTimeField  | Last update timestamp                           |

#### Model Relationships Diagram

```
User <1----1> Profile
User <1----1> Subscription
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Original authentication base: [egorsmkv/simple-django-login-and-register](https://github.com/egorsmkv/simple-django-login-and-register)
- UI/UX design: Busssard
- Map: [Leaflet.js](https://leafletjs.com/)
- Project maintained by StoneWalker.org

