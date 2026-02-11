# Self-Hosted Deployment Guide

Deploy StoneWalker on your own VPS (Ubuntu 22.04+ recommended, 2-4GB RAM).

All config files referenced below live in `docs/deploy/` and can be dropped in place.

## Prerequisites

- Ubuntu 22.04 LTS (or Debian 12)
- 2GB+ RAM, 20GB+ disk
- A domain name (you'll point it at your server in a later step)
- Root or sudo access
- SSH access to your server (`ssh root@YOUR_SERVER_IP`)

## 0. Point Your Domain at the Server

Before or during setup, you need to point your domain's DNS to your server's IP address. Do this at your domain registrar (wherever you bought your domain — Namecheap, GoDaddy, Cloudflare, etc.):

1. Log into your registrar's dashboard
2. Find **DNS settings** or **DNS management** for your domain
3. Find the existing **A record** (it may point to your old host)
4. Change it to your server's IP:

```
Type: A
Name: @                    (this means yourdomain.org itself)
Value: YOUR_SERVER_IPV4    (e.g. 116.203.xx.xx — find in your hosting panel)
TTL: 300                   (5 minutes — low for fast propagation)
```

```
Type: A
Name: www
Value: YOUR_SERVER_IPV4
TTL: 300
```

If your server has an IPv6 address, also add AAAA records:

```
Type: AAAA
Name: @
Value: YOUR_SERVER_IPV6    (e.g. 2001:db8::1)
TTL: 300
```

```
Type: AAAA
Name: www
Value: YOUR_SERVER_IPV6
TTL: 300
```

To find your server's IP: check your hosting panel (Hetzner Cloud, DigitalOcean, etc.), or run `hostname -I` when SSH'd in.

**Tip**: Lower the TTL to 300 a day *before* switching the IP. That way the old cached DNS expires quickly and users get routed to the new server within minutes instead of hours. After everything is stable, raise TTL back to 3600.

DNS propagation typically takes 5 minutes to 1 hour (can take up to 48 hours in rare cases). You can check propagation status at [dnschecker.org](https://dnschecker.org).

**Note**: SSL (step 8) requires DNS to already be pointing at your server. You can do steps 1-7 first while DNS propagates, then do step 8 once DNS is live.

## 1. System Setup

```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-venv python3-pip python3-dev \
    postgresql postgresql-contrib nginx certbot python3-certbot-nginx \
    gettext git build-essential libpq-dev

# Create application user
useradd --system --shell /bin/bash --home /opt/stonewalker stonewalker
mkdir -p /opt/stonewalker
chown stonewalker:stonewalker /opt/stonewalker
```

## 2. PostgreSQL

```bash
# Create database and user
sudo -u postgres psql <<SQL
CREATE USER stonewalker WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';
CREATE DATABASE stonewalker OWNER stonewalker;
GRANT ALL PRIVILEGES ON DATABASE stonewalker TO stonewalker;
SQL

# Apply tuning (copy from docs/deploy/postgresql.conf.snippet)
# Edit /etc/postgresql/15/main/postgresql.conf with the values from the snippet
# Key settings for 2GB VPS:
#   shared_buffers = 512MB
#   effective_cache_size = 1536MB
#   work_mem = 8MB
#   random_page_cost = 1.1 (SSD)

systemctl restart postgresql
```

See `docs/deploy/postgresql.conf.snippet` for the full tuning parameters.

## 3. Get the Code onto the Server

There are two ways to get the repo onto your server:

### Option A: Clone from GitHub (recommended)

```bash
sudo -u stonewalker bash
cd /opt/stonewalker

# Clone the repository (uses HTTPS — no SSH key needed)
git clone https://github.com/busssard/Stonewalker.git .
```

If the repo is private, you'll need a GitHub Personal Access Token (PAT):

```bash
# Generate a PAT at: https://github.com/settings/tokens
# Select scope: repo (full control of private repositories)
git clone https://YOUR_TOKEN@github.com/busssard/Stonewalker.git .
```

### Option B: Upload from your local machine

If you prefer not to give the server GitHub access:

```bash
# On your LOCAL machine — create a tarball
tar czf /tmp/stonewalker.tar.gz --exclude=venv --exclude=__pycache__ --exclude=.git --exclude='*.pyc' .

# Copy to server
scp /tmp/stonewalker.tar.gz root@YOUR_SERVER_IP:/tmp/

# On the SERVER — extract as the stonewalker user
sudo -u stonewalker bash -c 'cd /opt/stonewalker && tar xzf /tmp/stonewalker.tar.gz'
rm /tmp/stonewalker.tar.gz
```

**Note**: With Option B you won't have `git pull` for updates or auto-deploy. Option A is strongly recommended.

### Install dependencies

```bash
sudo -u stonewalker bash
cd /opt/stonewalker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

## 4. Environment Variables

```bash
# Copy and edit the environment template
cp docs/deploy/env.template /opt/stonewalker/.env
chmod 600 /opt/stonewalker/.env
# Edit .env with your actual values (DATABASE_URL, SECRET_KEY, etc.)
```

See `docs/deploy/env.template` for the full list of variables.

Generate a Django secret key:

```bash
python3 -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"
```

## 5. Django Setup

```bash
source /opt/stonewalker/venv/bin/activate
export $(grep -v '^#' /opt/stonewalker/.env | xargs)

cd /opt/stonewalker/source

# Run migrations
python manage.py migrate

# Compile translations
python manage.py compilemessages

# Collect static files
python manage.py collectstatic --noinput

# Create admin user
python manage.py createsuperuser

# Verify everything works
python manage.py check --deploy
```

## 6. Gunicorn (Application Server)

```bash
# Create log directory
mkdir -p /var/log/stonewalker
chown stonewalker:www-data /var/log/stonewalker

# Install the systemd service
cp docs/deploy/gunicorn.service /etc/systemd/system/stonewalker.service

# Start and enable
systemctl daemon-reload
systemctl enable stonewalker
systemctl start stonewalker

# Verify it's running
systemctl status stonewalker
```

The service file binds gunicorn to a Unix socket at `/run/stonewalker/gunicorn.sock`. Workers are set to 5 (suitable for a 2-core VPS; adjust with `2 * CPU_CORES + 1`).

See `docs/deploy/gunicorn.service` for the full service file.

## 7. Nginx (Reverse Proxy)

```bash
# Install the nginx config
cp docs/deploy/nginx.conf /etc/nginx/sites-available/stonewalker
ln -sf /etc/nginx/sites-available/stonewalker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload
nginx -t
systemctl reload nginx
```

See `docs/deploy/nginx.conf` for the full configuration. It handles:
- HTTP to HTTPS redirect
- Static file serving with caching headers
- Media file serving
- Proxy to gunicorn via Unix socket
- Security headers (HSTS, X-Frame-Options, etc.)
- 5MB upload limit (matching Django settings)

## 8. SSL with Let's Encrypt

```bash
# Obtain certificate (nginx must be running on port 80)
certbot --nginx -d stonewalker.org -d www.stonewalker.org

# Auto-renewal is set up by certbot automatically
# Test it:
certbot renew --dry-run
```

Certbot modifies your nginx config to include the SSL certificate paths. The provided `nginx.conf` already has the expected paths.

## 9. Backups

```bash
# Install backup script
cp docs/deploy/backup.sh /opt/stonewalker/backup.sh
chmod +x /opt/stonewalker/backup.sh

# Add cron job (runs daily at 3 AM)
echo "0 3 * * * stonewalker /opt/stonewalker/backup.sh" > /etc/cron.d/stonewalker-backup

# Test it
sudo -u stonewalker /opt/stonewalker/backup.sh
```

The backup script:
- Creates a compressed PostgreSQL dump
- Creates a custom-format dump (for `pg_restore`)
- Backs up media files (QR codes, profile pictures, stone images)
- Retains 14 days of backups automatically

See `docs/deploy/backup.sh` for the full script.

### Restore from backup

```bash
# SQL format
gunzip -c /opt/stonewalker/backups/stonewalker_20260210.sql.gz | psql -U stonewalker -d stonewalker

# Custom format (more flexible)
pg_restore -U stonewalker -d stonewalker /opt/stonewalker/backups/stonewalker_20260210.dump

# Media files
tar -xzf /opt/stonewalker/backups/media_20260210.tar.gz -C /opt/stonewalker/source/content/
```

## 10. Monitoring

### Basic health checks

```bash
# Check services are running
systemctl is-active stonewalker nginx postgresql

# Check gunicorn socket
curl --unix-socket /run/stonewalker/gunicorn.sock http://localhost/ -s -o /dev/null -w '%{http_code}\n'

# Check disk space
df -h /opt/stonewalker

# Check PostgreSQL connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='stonewalker';"

# Check gunicorn workers
ps aux | grep gunicorn | grep -v grep | wc -l
```

### Log locations

| Service    | Log Path                              |
|------------|---------------------------------------|
| Gunicorn   | `/var/log/stonewalker/access.log`     |
| Gunicorn   | `/var/log/stonewalker/error.log`      |
| Nginx      | `/var/log/nginx/stonewalker_access.log` |
| Nginx      | `/var/log/nginx/stonewalker_error.log`  |
| PostgreSQL | `/var/log/postgresql/postgresql-15-main.log` |
| System     | `journalctl -u stonewalker`           |

### Log rotation

Nginx logs are rotated by the system's `logrotate` automatically. For gunicorn logs:

```bash
cat > /etc/logrotate.d/stonewalker <<'EOF'
/var/log/stonewalker/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload stonewalker
    endscript
}
EOF
```

## Updating the Application

```bash
sudo -u stonewalker bash
cd /opt/stonewalker
source venv/bin/activate
export $(grep -v '^#' .env | xargs)

git pull origin main
pip install -r requirements.txt
cd source
python manage.py migrate
python manage.py compilemessages
python manage.py collectstatic --noinput

# Restart application (zero-downtime with graceful reload)
sudo systemctl reload stonewalker
```

## Firewall

```bash
# Allow only SSH, HTTP, HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

## Auto-Deploy on Git Push

Every push to `main` automatically deploys to the server: GitHub Actions runs the tests, and if they pass, SSHs into the server and runs the deploy script.

### Server-side setup

```bash
# Install the deploy script
cp docs/deploy/deploy.sh /opt/stonewalker/deploy.sh
chmod +x /opt/stonewalker/deploy.sh

# Allow the stonewalker user to reload the service without a password
echo "stonewalker ALL=(ALL) NOPASSWD: /bin/systemctl reload stonewalker" > /etc/sudoers.d/stonewalker-deploy
chmod 440 /etc/sudoers.d/stonewalker-deploy
```

### Generate an SSH key for GitHub Actions

```bash
# On the SERVER — generate a deploy key (no passphrase)
ssh-keygen -t ed25519 -f /tmp/deploy_key -N "" -C "github-actions-deploy"

# Add the public key to the stonewalker user's authorized_keys
mkdir -p /opt/stonewalker/.ssh
cat /tmp/deploy_key.pub >> /opt/stonewalker/.ssh/authorized_keys
chmod 700 /opt/stonewalker/.ssh
chmod 600 /opt/stonewalker/.ssh/authorized_keys
chown -R stonewalker:stonewalker /opt/stonewalker/.ssh

# Display the PRIVATE key — you'll paste this into GitHub
cat /tmp/deploy_key

# Clean up
rm /tmp/deploy_key /tmp/deploy_key.pub
```

### Add secrets to GitHub

Go to your repo: **Settings > Secrets and variables > Actions > New repository secret**

Add these 3 secrets:

| Secret name | Value |
|-------------|-------|
| `DEPLOY_HOST` | Your server's IP address |
| `DEPLOY_USER` | `stonewalker` |
| `DEPLOY_SSH_KEY` | The full private key from the step above (including `-----BEGIN/END-----` lines) |

### How it works

```
git push origin main
  → GitHub Actions: run tests (tests.yml)
    → Tests pass?
      → Yes: SSH into server as stonewalker
        → Run /opt/stonewalker/deploy.sh
          → git pull, pip install, migrate, collectstatic, reload gunicorn
      → No: deploy is skipped, you get a notification
```

The deploy workflow is at `.github/workflows/deploy.yml`. The deploy script is at `docs/deploy/deploy.sh`.

### Manual deploy

You can always deploy manually by SSHing in:

```bash
ssh root@YOUR_SERVER_IP
sudo -u stonewalker /opt/stonewalker/deploy.sh
```

## Migrating from Render (or another host)

If you're moving from an existing deployment (e.g. Render.com), you need to migrate the database and media files.

### Export the database from your old host

```bash
# On your LOCAL machine — dump from the old host
# Replace the URL with your old database connection string
pg_dump "postgresql://user:password@host:5432/dbname" --format=custom -f stonewalker_old.dump

# Copy the dump to your server
scp stonewalker_old.dump root@YOUR_SERVER_IP:/tmp/
```

### Import on the new server

```bash
# On the SERVER — restore into the local PostgreSQL
sudo -u postgres pg_restore --clean --if-exists -d stonewalker /tmp/stonewalker_old.dump
rm /tmp/stonewalker_old.dump
```

### Copy media files

If your old host has uploaded images (profile pictures, stone photos, QR codes):

```bash
# Upload media to the server
scp -r media_files/ root@YOUR_SERVER_IP:/opt/stonewalker/source/content/media/
chown -R stonewalker:stonewalker /opt/stonewalker/source/content/media/
```

### Cutover checklist

1. Set up everything on new server (steps 1-9) while old host is still live
2. Do a final database export from the old host (to capture last-minute data)
3. Import on new server
4. Switch DNS A record to new server's IP
5. Wait for DNS propagation (check at [dnschecker.org](https://dnschecker.org))
6. Verify the site works (`curl -I https://stonewalker.org`)
7. Keep the old host running for a few days as fallback
8. Decommission the old host once confident

## Config Files Reference

| File                           | Install Location                          |
|--------------------------------|-------------------------------------------|
| `docs/deploy/nginx.conf`      | `/etc/nginx/sites-available/stonewalker`  |
| `docs/deploy/gunicorn.service` | `/etc/systemd/system/stonewalker.service` |
| `docs/deploy/env.template`    | `/opt/stonewalker/.env`                   |
| `docs/deploy/postgresql.conf.snippet` | Merge into `/etc/postgresql/15/main/postgresql.conf` |
| `docs/deploy/backup.sh`       | `/opt/stonewalker/backup.sh`              |
| `docs/deploy/deploy.sh`       | `/opt/stonewalker/deploy.sh`              |
