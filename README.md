# StoneWalker

**Track the journey of painted stones across the world.**

StoneWalker is an open-source web app that combines rock painting with digital tracking. Paint a stone, stick on a QR code, hide it somewhere — then watch it travel as people find it, scan it, and hide it again.

Think geocaching meets collaborative art.

## How It Works

1. **Create** a stone and get a unique QR code
2. **Paint** your stone and attach the QR code
3. **Hide** it somewhere for others to find
4. **Track** its journey on an interactive map as it moves from person to person

## Features

- **Interactive World Map** — see where stones have traveled with connected route lines
- **QR Code System** — each stone gets a unique, downloadable QR code with sequential numbering
- **Two Stone Types** — *Hidden* (leave it, hope someone finds it) and *Hunted* (share the location, race to find it)
- **Stone Certificates** — downloadable PDF certificates for your creations
- **7 Languages** — English, German, French, Spanish, Italian, Russian, and Simplified Chinese
- **Dark Mode** — full dark mode support across all pages
- **Forum Integration** — built-in Discourse SSO so users log in once
- **Premium Tier** — optional Stripe-powered subscriptions for extra features
- **Mobile Friendly** — responsive design that works on any device

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.8+, Django 4.2 |
| Database | PostgreSQL |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 4 |
| Maps | Leaflet.js |
| Payments | Stripe |
| Email | Maileroo |
| Forum | Discourse (SSO) |

## Quick Start

```bash
# Clone and set up
git clone https://github.com/busssard/Stonewalker.git
cd Stonewalker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
export DATABASE_URL="postgresql://your_user:your_pass@localhost:5432/your_db"

# Run
cd source
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://localhost:8000/stonewalker/` to see the app.

For the full development setup with translations and convenience scripts, see [Development Guide](docs/README.md).

## Deployment

StoneWalker runs on any VPS with Python, PostgreSQL, and nginx. The full self-hosted deployment guide covers everything from scratch:

**[Self-Hosted Deployment Guide](docs/DEPLOYMENT_SELFHOSTED.md)** — Ubuntu 22.04+, PostgreSQL 15, nginx, gunicorn, Let's Encrypt SSL, automated backups, CI/CD auto-deploy.

## Running Tests

```bash
# Full test suite (370+ tests)
./venv/bin/python run_tests.py

# Quick subset
./venv/bin/python run_tests.py -m unit
./venv/bin/python run_tests.py -k stone
```

Tests run automatically via GitHub Actions on every push to `main`.

## Project Structure

```
source/
  accounts/     # Authentication, profiles, email activation
  main/         # Stones, QR codes, maps, scanning, shop, premium
  app/          # Django project settings (dev/prod split)
  content/
    templates/  # HTML templates
    assets/     # CSS, JS, images
    locale/     # Translation files (7 languages)
docs/           # Deployment guides, wiki, developer docs
```

## Contributing

Contributions are welcome. Please run the test suite before submitting a PR:

```bash
./venv/bin/python run_tests.py
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Credits

- Original auth scaffold: [egorsmkv/simple-django-login-and-register](https://github.com/egorsmkv/simple-django-login-and-register)
- Maps: [Leaflet.js](https://leafletjs.com/)
- Maintained by [StoneWalker.org](https://stonewalker.org)
