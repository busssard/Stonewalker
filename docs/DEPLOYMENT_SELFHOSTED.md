# Self-Hosted Deployment Guide

Deploy StoneWalker on your own VPS. This guide is a single top-to-bottom walkthrough — everything you need is right here, no jumping between files.

**Target setup**: Ubuntu 22.04+, 2-4GB RAM, PostgreSQL 15, nginx, gunicorn, Let's Encrypt SSL.

---

## 0. Point Your Domain at the Server

Before starting server setup, point your domain's DNS to your server's IP address. Do this at your domain registrar (Namecheap, GoDaddy, Cloudflare, etc.):

1. Log into your registrar's dashboard
2. Find **DNS settings** or **DNS management** for your domain
3. Create or update these records:

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

---

## 1. System Setup

SSH into your server and run everything below as root (or with sudo):

```bash
ssh root@YOUR_SERVER_IP
```

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

---

## 2. PostgreSQL

### Create the database

```bash
sudo -u postgres psql <<SQL
CREATE USER stonewalker WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';
CREATE DATABASE stonewalker OWNER stonewalker;
GRANT ALL PRIVILEGES ON DATABASE stonewalker TO stonewalker;
SQL
```

**Important**: Replace `CHANGE_ME_STRONG_PASSWORD` with an actual strong password. You'll use this same password in Step 4 when setting up the `.env` file.

### Tune PostgreSQL for better performance (optional but recommended)

This appends optimized settings to the end of the PostgreSQL config file. PostgreSQL reads the file top-to-bottom, so later values override earlier ones — you don't need to find and edit existing lines.

```bash
cat >> /etc/postgresql/*/main/postgresql.conf << 'TUNING'

# --- StoneWalker tuning (appended) ---
# Memory (values below are for 2GB RAM — double shared_buffers and
# effective_cache_size if you have 4GB)
shared_buffers = 512MB
effective_cache_size = 1536MB
work_mem = 8MB
maintenance_work_mem = 128MB

# WAL / Checkpoints
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_wal_size = 1GB

# Connections (gunicorn workers * 2, with headroom)
max_connections = 50

# Query planner (SSD storage — if you're on spinning disks, leave defaults)
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging (queries slower than 500ms get logged)
log_min_duration_statement = 500
TUNING

systemctl restart postgresql
```

---

## 3. Get the Code onto the Server

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

### Install Python dependencies

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

---

## 4. Environment Variables

Create the `.env` file that will hold all your secrets and configuration:

```bash
cat > /opt/stonewalker/.env << 'ENV'
# =============================================================================
# StoneWalker Production Environment
# This file is read by the gunicorn systemd service (EnvironmentFile)
# =============================================================================

# === DJANGO (required) ===
IS_PRODUCTION=true
SECRET_KEY=CHANGE_ME
DEBUG=False
ALLOWED_HOSTS=stonewalker.org,www.stonewalker.org

# === DATABASE (required) ===
# The ?sslmode=disable is correct for local PostgreSQL on the same machine.
# Use sslmode=require for remote/hosted databases (e.g. Render, Supabase).
DATABASE_URL=postgresql://stonewalker:CHANGE_ME_DB_PASSWORD@localhost:5432/stonewalker?sslmode=disable

# === EMAIL — Mailjet (set up in Step 11) ===
# Leave blank to disable email (users can't verify accounts or reset passwords)
MJ_APIKEY_PUBLIC=
MJ_APIKEY_PRIVATE=

# === PAYMENTS — Stripe (set up in Step 12) ===
# Leave blank to disable the shop
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# === FORUM — Discourse SSO (set up in Step 13) ===
# Leave blank to disable forum SSO
DISCOURSE_URL=
DISCOURSE_SSO_SECRET=
ENV

chmod 600 /opt/stonewalker/.env
chown stonewalker:stonewalker /opt/stonewalker/.env
```

Now fill in the two **required** values:

**1. Generate a SECRET_KEY:**

```bash
/opt/stonewalker/venv/bin/python -c "from django.utils.crypto import get_random_string; print(get_random_string(50))"
```

Copy the output and replace `CHANGE_ME` in the `.env` file.

**2. Set the database password:**

Replace `CHANGE_ME_DB_PASSWORD` with the password you chose in Step 2.

**3. Set ALLOWED_HOSTS:**

Replace `stonewalker.org,www.stonewalker.org` with your actual domain if different.

Edit the file:

```bash
nano /opt/stonewalker/.env
```

---

## 5. Django Setup

```bash
# Switch to the stonewalker user and activate the environment
sudo -u stonewalker bash
cd /opt/stonewalker
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

cd source

# Run database migrations (creates all tables)
python manage.py migrate

# Compile translations (7 languages)
python manage.py compilemessages

# Collect static files (CSS, JS, images) into the serving directory
python manage.py collectstatic --noinput

# Create your admin account
python manage.py createsuperuser

# Verify everything is configured correctly
python manage.py check --deploy
```

If `check --deploy` shows warnings about SECURE_HSTS or SECURE_SSL_REDIRECT, that's fine — nginx handles those via headers and HTTPS redirect.

---

## 6. Gunicorn (Application Server)

### Create the log directory

```bash
# Run as root
mkdir -p /var/log/stonewalker
chown stonewalker:www-data /var/log/stonewalker
```

### Create the systemd service

```bash
cat > /etc/systemd/system/stonewalker.service << 'SERVICE'
[Unit]
Description=StoneWalker Django Application (Gunicorn)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=stonewalker
Group=www-data
RuntimeDirectory=stonewalker
WorkingDirectory=/opt/stonewalker/source
EnvironmentFile=/opt/stonewalker/.env
ExecStart=/opt/stonewalker/venv/bin/gunicorn app.wsgi:application \
    --bind unix:/run/stonewalker/gunicorn.sock \
    --workers 5 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile /var/log/stonewalker/access.log \
    --error-logfile /var/log/stonewalker/error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
Restart=on-failure
RestartSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICE
```

The `--workers 5` is suitable for a 2-core VPS. The formula is `2 * CPU_CORES + 1`. For a 4-core server, use `--workers 9`.

### Start it

```bash
systemctl daemon-reload
systemctl enable stonewalker
systemctl start stonewalker

# Verify it's running
systemctl status stonewalker
```

You should see "Active: active (running)". If it fails, check the logs:

```bash
journalctl -u stonewalker -n 50
cat /var/log/stonewalker/error.log
```

---

## 7. Nginx (Reverse Proxy)

### Create the nginx config

Replace `stonewalker.org` with your actual domain in both `server_name` lines:

```bash
cat > /etc/nginx/sites-available/stonewalker << 'NGINX'
upstream stonewalker_app {
    server unix:/run/stonewalker/gunicorn.sock fail_timeout=0;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name stonewalker.org www.stonewalker.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name stonewalker.org www.stonewalker.org;

    # SSL (managed by Certbot — paths are filled in by Step 8)
    ssl_certificate /etc/letsencrypt/live/stonewalker.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/stonewalker.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logging
    access_log /var/log/nginx/stonewalker_access.log;
    error_log /var/log/nginx/stonewalker_error.log;

    # Max upload size (matches Django's 5MB limit)
    client_max_body_size 5M;

    # Static files (collected via collectstatic)
    location /static/ {
        alias /opt/stonewalker/source/content/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files (user uploads: profile pics, stone images, QR codes)
    location /media/ {
        alias /opt/stonewalker/source/content/media/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }

    # Favicon
    location /favicon.ico {
        alias /opt/stonewalker/source/content/static/img/favicon.ico;
        access_log off;
        log_not_found off;
    }

    # Proxy to gunicorn
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_pass http://stonewalker_app;

        # Timeouts
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
NGINX
```

**Important**: If you haven't run certbot yet (Step 8), the SSL certificate paths won't exist and nginx will refuse to start. In that case, temporarily comment out the entire HTTPS `server` block and change the HTTP block to proxy directly instead of redirecting:

```bash
# Temporary HTTP-only config (use until certbot runs in Step 8)
cat > /etc/nginx/sites-available/stonewalker << 'NGINX_TEMP'
upstream stonewalker_app {
    server unix:/run/stonewalker/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name stonewalker.org www.stonewalker.org;

    client_max_body_size 5M;

    location /static/ {
        alias /opt/stonewalker/source/content/static/;
    }

    location /media/ {
        alias /opt/stonewalker/source/content/media/;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_pass http://stonewalker_app;
    }
}
NGINX_TEMP
```

### Enable and start

```bash
ln -sf /etc/nginx/sites-available/stonewalker /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test the config
nginx -t

# Reload
systemctl reload nginx
```

At this point, if DNS is pointing at your server, visiting `http://yourdomain.org` should show StoneWalker.

---

## 8. SSL with Let's Encrypt

This requires DNS to already be pointing at your server (Step 0). Replace the domain with yours:

```bash
certbot --nginx -d stonewalker.org -d www.stonewalker.org
```

Certbot will:
1. Obtain a certificate
2. Modify your nginx config to include the SSL paths
3. Set up automatic renewal

If you used the temporary HTTP-only config from Step 7, now replace it with the full HTTPS config from Step 7 (the first `cat` block), then run certbot again — it will fill in the correct paths.

**Test auto-renewal:**

```bash
certbot renew --dry-run
```

---

## 9. Firewall

```bash
# Allow only SSH, HTTP, HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

---

## 10. Backups

### Create the backup script

```bash
cat > /opt/stonewalker/backup.sh << 'BACKUP'
#!/usr/bin/env bash
# StoneWalker daily backup: database + media files
# Keeps 14 days of backups automatically.

set -euo pipefail

BACKUP_DIR="/opt/stonewalker/backups"
DB_NAME="stonewalker"
DB_USER="stonewalker"
RETENTION_DAYS=14
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Custom-format dump (for pg_restore — most flexible)
pg_dump -U "$DB_USER" -d "$DB_NAME" --format=custom --compress=6 \
    --file="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump" 2>/dev/null

# Plain SQL dump (for disaster recovery — human-readable)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"
pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE" 2>/dev/null

# Verify the backup is non-empty
if [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file is empty: $BACKUP_FILE" >&2
    exit 1
fi

# Back up media files (QR codes, profile pics, stone images)
tar -czf "${BACKUP_DIR}/media_${TIMESTAMP}.tar.gz" \
    -C /opt/stonewalker/source/content media/ 2>/dev/null || true

# Remove backups older than 14 days
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find "$BACKUP_DIR" -name "${DB_NAME}_*.dump" -mtime +${RETENTION_DAYS} -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup complete: $BACKUP_FILE"
BACKUP

chmod +x /opt/stonewalker/backup.sh
chown stonewalker:stonewalker /opt/stonewalker/backup.sh
```

### Schedule daily backups (3 AM)

```bash
echo "0 3 * * * stonewalker /opt/stonewalker/backup.sh" > /etc/cron.d/stonewalker-backup
```

### Test it

```bash
sudo -u stonewalker /opt/stonewalker/backup.sh
ls -lh /opt/stonewalker/backups/
```

### How to restore from a backup

```bash
# From the SQL dump
gunzip -c /opt/stonewalker/backups/stonewalker_20260210.sql.gz | psql -U stonewalker -d stonewalker

# From the custom-format dump (more flexible — can restore individual tables)
pg_restore -U stonewalker -d stonewalker --clean --if-exists /opt/stonewalker/backups/stonewalker_20260210.dump

# Media files
tar -xzf /opt/stonewalker/backups/media_20260210.tar.gz -C /opt/stonewalker/source/content/
```

---

## 11. Email Setup (Mailjet)

StoneWalker uses Mailjet to send emails (account verification, password reset). Without this, users can still register but can't verify their email or reset passwords.

### Create a Mailjet account

1. Go to [mailjet.com](https://www.mailjet.com/) and sign up (free tier: 200 emails/day)
2. After signing in, go to **Account Settings > API Keys** (or visit [app.mailjet.com/account/apikeys](https://app.mailjet.com/account/apikeys))
3. You'll see two keys:
   - **API Key** (public) — looks like `abc123def456...`
   - **Secret Key** (private) — looks like `xyz789ghi012...`

### Verify your sending domain

Mailjet won't deliver emails until you prove you own the sending domain:

1. Go to **Account Settings > Sender domains & addresses**
2. Add your domain (e.g. `stonewalker.org`)
3. Mailjet will give you DNS records to add (SPF, DKIM). Add them at your registrar:

**SPF record** (lets Mailjet send on behalf of your domain):
```
Type: TXT
Name: @
Value: v=spf1 include:spf.mailjet.com ~all
TTL: 3600
```

**DKIM record** (Mailjet provides the exact value — it's unique to your account):
```
Type: TXT
Name: mailjet._domainkey       (Mailjet tells you the exact name)
Value: k=rsa; p=MIGfMA0GCS...  (Mailjet tells you the exact value)
TTL: 3600
```

4. Click "Verify" in Mailjet once DNS propagates

### Add the keys to your .env

Edit `/opt/stonewalker/.env` and fill in:

```
MJ_APIKEY_PUBLIC=your_api_key_here
MJ_APIKEY_PRIVATE=your_secret_key_here
```

Then restart the application:

```bash
systemctl restart stonewalker
```

### Test it

From the server:

```bash
sudo -u stonewalker bash
cd /opt/stonewalker
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)
cd source

python -c "
from django.core.mail import send_mail
import django; django.setup()
send_mail('Test from StoneWalker', 'Email is working!', 'noreply@stonewalker.org', ['your@email.com'])
print('Sent!')
"
```

Replace `your@email.com` with your actual email. Check your inbox (and spam folder).

---

## 12. Payments Setup (Stripe)

StoneWalker uses Stripe for QR code pack purchases. Without this, the free single QR still works, but paid packs are disabled.

### Create a Stripe account

1. Go to [stripe.com](https://stripe.com/) and sign up
2. Complete identity verification (required to accept payments)
3. Go to **Developers > API Keys** ([dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys))
4. You'll see:
   - **Publishable key** — starts with `pk_live_...`
   - **Secret key** — starts with `sk_live_...` (click to reveal)

**For testing first**: Use the test mode keys (toggle "Test mode" in the Stripe dashboard). Test keys start with `pk_test_` and `sk_test_`.

### Create your products in Stripe

StoneWalker's shop is config-driven. The product catalog lives in `source/main/shop_config.json`. Each product references a `stripe_price_id` — you create these in Stripe:

1. Go to **Products** in your Stripe dashboard
2. Create products matching your shop config:

| Product Name | Price | What to set |
|---|---|---|
| Starter 3-Pack | $4.99 | One-time payment, USD |
| Explorer 10-Pack | $9.99 | One-time payment, USD |
| Classroom 30-Pack | $19.99 | One-time payment, USD |

3. After creating each product, copy its **Price ID** (starts with `price_...`)
4. Edit `source/main/shop_config.json` on the server and replace the placeholder `stripe_price_id` values with your actual Price IDs

### Set up the webhook

Stripe sends a webhook to your server when a payment succeeds, so StoneWalker can generate the QR PDF:

1. Go to **Developers > Webhooks** ([dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks))
2. Click **Add endpoint**
3. Set the endpoint URL to: `https://stonewalker.org/webhooks/stripe/`
4. Select events to listen to:
   - `checkout.session.completed`
5. Click **Add endpoint**
6. On the webhook detail page, click **Reveal** under Signing secret
7. Copy the webhook secret — it starts with `whsec_...`

### Add the keys to your .env

Edit `/opt/stonewalker/.env` and fill in:

```
STRIPE_PUBLIC_KEY=pk_live_your_publishable_key
STRIPE_SECRET_KEY=sk_live_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

Then restart the application:

```bash
systemctl restart stonewalker
```

### Test a payment

1. If using test keys: go to your shop page and buy a pack
2. Use Stripe's test card: `4242 4242 4242 4242`, any future expiry, any CVC
3. The checkout should complete and you should receive a PDF with QR codes
4. Check the Stripe dashboard under **Payments** to see the test transaction
5. Once working, switch to live keys in `.env` and restart

---

## 13. Forum Setup (Discourse)

StoneWalker has built-in Discourse SSO — when users click "Forum" they're automatically logged in with their StoneWalker account. This step sets up a Discourse instance on the same server.

**Resource requirement**: Discourse needs at least 2GB RAM. If your VPS has only 2GB total, either upgrade to 4GB or run Discourse on a separate $6/month VPS.

### Install Discourse using the official launcher

```bash
# As root on your server
mkdir -p /var/discourse
git clone https://github.com/discourse/discourse_docker.git /var/discourse
cd /var/discourse
```

### Configure Discourse

```bash
cp samples/standalone.yml containers/app.yml
nano containers/app.yml
```

In `app.yml`, change these values:

```yaml
# Your forum domain (add a DNS A record for this pointing to the same server IP)
DISCOURSE_HOSTNAME: 'forum.stonewalker.org'

# Your email (for Let's Encrypt and admin account)
DISCOURSE_DEVELOPER_EMAILS: 'your@email.com'

# SMTP settings (use your Mailjet credentials)
DISCOURSE_SMTP_ADDRESS: in-v3.mailjet.com
DISCOURSE_SMTP_PORT: 587
DISCOURSE_SMTP_USER_NAME: your_mailjet_api_key
DISCOURSE_SMTP_PASSWORD: your_mailjet_secret_key
DISCOURSE_SMTP_ENABLE_START_TLS: true
DISCOURSE_SMTP_DOMAIN: stonewalker.org
```

**Important**: Also add a DNS A record for `forum.stonewalker.org` pointing to the same server IP.

### Launch Discourse

```bash
cd /var/discourse
./launcher bootstrap app    # Takes 5-10 minutes
./launcher start app
```

Discourse runs on port 80/443 internally. Since nginx is already using those ports, you need to either:

**Option A**: Put Discourse behind nginx too (recommended). Add to your nginx config:

```nginx
# Add this as a separate server block in /etc/nginx/sites-available/stonewalker
server {
    listen 80;
    listen [::]:80;
    server_name forum.stonewalker.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name forum.stonewalker.org;

    ssl_certificate /etc/letsencrypt/live/forum.stonewalker.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/forum.stonewalker.org/privkey.pem;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:4080;  # Discourse internal port
    }
}
```

In `app.yml`, change the exposed port so Discourse doesn't conflict with nginx:

```yaml
expose:
  - "4080:80"
```

Then rebuild: `./launcher rebuild app`

Get an SSL cert for the forum subdomain:

```bash
certbot --nginx -d forum.stonewalker.org
```

**Option B**: Run Discourse on a separate VPS (simpler, avoids port conflicts).

### Enable SSO in Discourse

Once Discourse is running, open it in your browser and create your admin account. Then:

1. Go to **Admin > Settings > Login** (or visit `forum.stonewalker.org/admin/site_settings/category/login`)
2. Set these:

| Setting | Value |
|---|---|
| `enable_discourse_connect` | true |
| `discourse_connect_url` | `https://stonewalker.org/accounts/discourse-sso/` |
| `discourse_connect_secret` | A random secret string (you'll use this same string in StoneWalker's .env) |
| `discourse_connect_overrides_email` | true |
| `discourse_connect_overrides_username` | true |

### Add the SSO secret to StoneWalker's .env

Use the **exact same secret** you entered in Discourse:

```
DISCOURSE_URL=https://forum.stonewalker.org
DISCOURSE_SSO_SECRET=your_shared_secret_here
```

Restart StoneWalker:

```bash
systemctl restart stonewalker
```

### Test SSO

1. Log into StoneWalker
2. Navigate to `forum.stonewalker.org`
3. You should be automatically logged in with your StoneWalker username

---

## 14. Log Rotation

Nginx logs are rotated by the system automatically. Set up rotation for gunicorn logs:

```bash
cat > /etc/logrotate.d/stonewalker << 'LOGROTATE'
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
LOGROTATE
```

---

## 15. Auto-Deploy on Git Push

Every push to `main` can automatically deploy to the server: GitHub Actions runs the tests, and if they pass, SSHs into the server and runs the deploy script.

### Create the deploy script on the server

```bash
cat > /opt/stonewalker/deploy.sh << 'DEPLOY'
#!/bin/bash
set -euo pipefail

APP_DIR="/opt/stonewalker"
SOURCE_DIR="$APP_DIR/source"
VENV="$APP_DIR/venv/bin"
ENV_FILE="$APP_DIR/.env"
LOG_FILE="/var/log/stonewalker/deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Deploy started ==="

# Load environment
export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs)

cd "$APP_DIR"

# Pull latest code
log "Pulling latest code..."
git fetch origin main
git reset --hard origin/main

# Install/update dependencies
log "Installing dependencies..."
$VENV/pip install -q -r requirements.txt

cd "$SOURCE_DIR"

# Run migrations
log "Running migrations..."
$VENV/python manage.py migrate --noinput

# Compile translations
log "Compiling translations..."
$VENV/python manage.py compilemessages 2>/dev/null || log "Warning: compilemessages failed (gettext missing?)"

# Collect static files
log "Collecting static files..."
$VENV/python manage.py collectstatic --noinput --clear -v 0

# Reload gunicorn (graceful — no downtime)
log "Reloading application..."
sudo systemctl reload stonewalker

log "=== Deploy complete ==="
DEPLOY

chmod +x /opt/stonewalker/deploy.sh
chown stonewalker:stonewalker /opt/stonewalker/deploy.sh
```

### Allow passwordless reload

The stonewalker user needs to reload the service without a password prompt:

```bash
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
echo ""
echo "===== COPY EVERYTHING BELOW INTO GITHUB SECRET 'DEPLOY_SSH_KEY' ====="
cat /tmp/deploy_key
echo "===== END ====="

# Clean up the key files from /tmp
rm /tmp/deploy_key /tmp/deploy_key.pub
```

### Add secrets to GitHub

Go to your repo: **Settings > Secrets and variables > Actions > New repository secret**

Add these 3 secrets:

| Secret name | Value |
|---|---|
| `DEPLOY_HOST` | Your server's IP address |
| `DEPLOY_USER` | `stonewalker` |
| `DEPLOY_SSH_KEY` | The full private key from above (including the `-----BEGIN/END-----` lines) |

### How it works

```
git push origin main
  → GitHub Actions: run tests
    → Tests pass?
      → Yes: SSH into server → run /opt/stonewalker/deploy.sh
        → git pull, pip install, migrate, collectstatic, reload gunicorn
      → No: deploy is skipped, you get a notification
```

The deploy workflow lives at `.github/workflows/deploy.yml` in the repo.

### Manual deploy

You can always deploy manually:

```bash
ssh root@YOUR_SERVER_IP
sudo -u stonewalker /opt/stonewalker/deploy.sh
```

---

## 16. Monitoring

### Quick health check

```bash
# Are all services running?
systemctl is-active stonewalker nginx postgresql

# Is gunicorn responding?
curl --unix-socket /run/stonewalker/gunicorn.sock http://localhost/ -s -o /dev/null -w '%{http_code}\n'
# Should print: 200 (or 301/302 for redirects)

# Disk space
df -h /opt/stonewalker

# PostgreSQL connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='stonewalker';"

# Gunicorn worker count
ps aux | grep gunicorn | grep -v grep | wc -l
```

### Log locations

| Service | Log Path |
|---|---|
| Gunicorn access | `/var/log/stonewalker/access.log` |
| Gunicorn errors | `/var/log/stonewalker/error.log` |
| Deploy history | `/var/log/stonewalker/deploy.log` |
| Nginx access | `/var/log/nginx/stonewalker_access.log` |
| Nginx errors | `/var/log/nginx/stonewalker_error.log` |
| PostgreSQL | `/var/log/postgresql/postgresql-*-main.log` |
| System/service | `journalctl -u stonewalker` |

---

## Updating the Application (Manual)

If auto-deploy isn't set up, or you need to deploy manually:

```bash
sudo -u stonewalker bash
cd /opt/stonewalker
source venv/bin/activate
export $(grep -v '^#' .env | grep -v '^$' | xargs)

git pull origin main
pip install -r requirements.txt
cd source
python manage.py migrate
python manage.py compilemessages
python manage.py collectstatic --noinput

# Restart application (zero-downtime with graceful reload)
sudo systemctl reload stonewalker
```

---

## Migrating from Render (or Another Host)

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
6. Verify the site works: `curl -I https://stonewalker.org`
7. Keep the old host running for a few days as fallback
8. Decommission the old host once confident
