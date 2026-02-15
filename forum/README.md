# Discourse Forum Development Setup

This folder contains Docker Compose configuration for running Discourse locally for SSO testing.

## Current Status: INCOMPLETE

The Docker Compose file exists but **does not work** because:
- `discourse/discourse_dev:release` is a base image with an **empty** `/var/www/discourse`
- This image is meant for Discourse contributors who mount the source code

## What Works
- PostgreSQL container: `postgres:15-alpine` - healthy
- Redis container: `redis:7-alpine` - healthy
- Django SSO endpoint: COMPLETE (see `source/accounts/discourse_sso.py`)

## Next Steps to Complete Setup

### Option 1: Official Launcher (Recommended)
```bash
cd forum
git clone https://github.com/discourse/discourse_docker.git
cd discourse_docker
./discourse-setup
```
This uses the official installation method but requires 2GB+ RAM.

### Option 2: Skip Local, Use Remote VPS
Spin up a $6/mo VPS (DigitalOcean, Hetzner) and run Discourse there for testing.
See `idea_scratchpad.md` for production deployment checklist.

### Option 3: Test in Production
Django SSO code is complete. Deploy StoneWalker + Discourse to production and test there.

## If Setup Is Completed Later

### Quick Start
```bash
# From project root:
./run_dev.sh discourse-start   # Start Discourse
./run_dev.sh discourse-logs    # View logs
./run_dev.sh discourse-stop    # Stop Discourse
./run_dev.sh discourse-reset   # Delete all data

# Or directly:
docker compose -f forum/docker-compose.yml up -d
```

### First Boot
First boot takes **3-5 minutes** (database migrations, asset compilation).

### Access
- **URL:** http://localhost:4200
- **Admin:** admin / admin123456

### Configure SSO
After Discourse is running:

1. Go to Admin -> Settings -> Login
2. Enable `enable_discourse_connect`
3. Set `discourse_connect_url` = `http://host.docker.internal:8000/accounts/discourse-sso/`
4. Set `discourse_connect_secret` = `dev_secret_change_me`

### Resource Usage

| Service | RAM |
|---------|-----|
| PostgreSQL | ~200MB |
| Redis | ~50MB |
| Discourse | ~1-1.5GB |

Requires swap if your machine has < 4GB RAM.

## Documentation

- Full architecture and production checklist: `../idea_scratchpad.md`
- Django SSO implementation: `../source/accounts/discourse_sso.py`
