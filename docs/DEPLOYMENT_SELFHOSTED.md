# Self-Hosted Deployment Guide

Deploy StoneWalker on your own VPS (Ubuntu 22.04+ recommended, 2-4GB RAM).

All config files referenced below live in `docs/deploy/` and can be dropped in place.

## Prerequisites

- Ubuntu 22.04 LTS (or Debian 12)
- 2GB+ RAM, 20GB+ disk
- A domain name pointed at your server's IP (A record)
- Root or sudo access

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

## 3. Application Code

```bash
sudo -u stonewalker bash
cd /opt/stonewalker

# Clone repository
git clone https://github.com/YOUR_ORG/simple-django-login-and-register.git .

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

## Config Files Reference

| File                           | Install Location                          |
|--------------------------------|-------------------------------------------|
| `docs/deploy/nginx.conf`      | `/etc/nginx/sites-available/stonewalker`  |
| `docs/deploy/gunicorn.service` | `/etc/systemd/system/stonewalker.service` |
| `docs/deploy/env.template`    | `/opt/stonewalker/.env`                   |
| `docs/deploy/postgresql.conf.snippet` | Merge into `/etc/postgresql/15/main/postgresql.conf` |
| `docs/deploy/backup.sh`       | `/opt/stonewalker/backup.sh`              |
