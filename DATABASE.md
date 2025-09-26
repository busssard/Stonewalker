# Database Documentation

This document covers database configuration, management, and troubleshooting for both development and production environments.

## Overview

The StoneWalker application uses **PostgreSQL** as the database backend for both development and production environments.

## Database Configuration

### Development Environment

Development requires a PostgreSQL database. The `DATABASE_URL` environment variable must be set to a valid PostgreSQL connection string.

### Production Environment

Production uses PostgreSQL via `DATABASE_URL` environment variable set on Render.com.

## Database Setup

### Local PostgreSQL Setup

1. **Install PostgreSQL** (if not already installed):
   ```bash
   sudo apt update && sudo apt install -y postgresql postgresql-contrib
   ```

2. **Create database and user**:
   ```bash
   sudo -u postgres psql -c "CREATE USER stone_user WITH PASSWORD 'stone_pass';"
   sudo -u postgres psql -c "ALTER ROLE stone_user CREATEDB;"
   sudo -u postgres psql -c "CREATE DATABASE stone_dev OWNER stone_user;"
   ```

3. **Run migrations**:
   ```bash
   export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
   cd source
   python manage.py migrate
   ```

### Production Database (Render.com)

1. Create PostgreSQL service in Render dashboard
2. Set environment variables:
   - `IS_PRODUCTION=true`
   - `DATABASE_URL=postgres://username:password@host:port/dbname`
   - `DEBUG=false`
   - `ALLOWED_HOSTS=your-app.onrender.com`

## Database Management Commands

### Check Current Database

```bash
# Check PostgreSQL database configuration
cd source
python manage.py shell -c "from django.conf import settings; print('Engine:', settings.DATABASES['default']['ENGINE']); print('Name:', settings.DATABASES['default']['NAME'])"
```

### Check Database Contents

```bash
# Using Django shell
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
cd source
python manage.py shell -c "
from django.contrib.auth.models import User
from main.models import Stone
from accounts.models import Profile
print(f'Users: {User.objects.count()}, Stones: {Stone.objects.count()}, Profiles: {Profile.objects.count()}')
"
```

### Direct PostgreSQL Access

```bash
# Connect to PostgreSQL directly
psql -h localhost -U stone_user -d stone_dev

# Or using DATABASE_URL
psql "postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
```

### Database Operations

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Dump data
python manage.py dumpdata --natural-foreign --natural-primary > backup.json

# Load data
python manage.py loaddata backup.json

# Reset database (WARNING: deletes all data)
python manage.py flush
```

## Development Workflow

### Running the Development Server

1. **Using the convenience script**:
   ```bash
   ./run_dev.sh
   ```

2. **Or manually**:
   ```bash
   export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
   cd source
   python manage.py runserver
   ```

3. **With custom database**:
   ```bash
   export DATABASE_URL="postgresql://your_user:your_pass@your_host:5432/your_db"
   cd source
   python manage.py runserver
   ```

## Database Schema

### Main Models

- **User** (Django auth): User accounts
- **Profile** (accounts): User profile information
- **Stone** (main): Stone objects with UUID and location data
- **StoneMove** (main): Stone movement history
- **StoneScanAttempt** (main): QR code scan attempts
- **Activation** (accounts): User account activation
- **EmailAddressState** (accounts): Email verification states
- **EmailChangeAttempt** (accounts): Email change requests

### Key Relationships

- User → Profile (OneToOne)
- User → Stone (ForeignKey)
- Stone → StoneMove (ForeignKey)
- User → Activation (ForeignKey)

## Troubleshooting

### Common Issues

1. **"DATABASE_URL environment variable is required"**
   - **Cause**: `DATABASE_URL` not set
   - **Solution**: Set `DATABASE_URL` to a valid PostgreSQL connection string

2. **"FOREIGN KEY constraint failed"**
   - **Cause**: Trying to save objects with invalid foreign keys
   - **Solution**: Ensure referenced objects exist first

3. **"Could not parse DATABASE_URL"**
   - **Cause**: `dj_database_url` compatibility issue with Python 3.8
   - **Solution**: Manual PostgreSQL parsing is implemented as fallback

4. **"psql: command not found"**
   - **Cause**: PostgreSQL client not installed
   - **Solution**: Install with `sudo apt install postgresql-client`

5. **"Invalid DATABASE_URL format"**
   - **Cause**: `DATABASE_URL` doesn't start with `postgresql://`
   - **Solution**: Use proper PostgreSQL URL format: `postgresql://user:pass@host:port/dbname`

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U stone_user -d stone_dev -c "SELECT version();"

# Test Django database connection
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
cd source
python manage.py dbshell -c "SELECT current_database();"
```

### Data Migration

To migrate data between PostgreSQL databases:

```bash
# 1. Dump data from source database
export DATABASE_URL="postgresql://source_user:source_pass@source_host:5432/source_db"
cd source
python manage.py dumpdata --natural-foreign --natural-primary > ../data_backup.json

# 2. Load into target database
export DATABASE_URL="postgresql://target_user:target_pass@target_host:5432/target_db"
python manage.py loaddata ../data_backup.json

# 3. Verify migration
python manage.py shell -c "
from django.contrib.auth.models import User
from main.models import Stone
print(f'Users: {User.objects.count()}, Stones: {Stone.objects.count()}')
"
```

## Environment Variables

### Development

```bash
# Required: PostgreSQL database URL
export DATABASE_URL="postgresql://stone_user:stone_pass@localhost:5432/stone_dev"
```

### Production (Render.com)

```bash
IS_PRODUCTION=true
DATABASE_URL=postgres://username:password@host:port/dbname
DEBUG=false
ALLOWED_HOSTS=your-app.onrender.com
```

## Database URLs

### PostgreSQL Format
```
postgresql://username:password@host:port/database_name
```

### Examples
```bash
# Local development
postgresql://stone_user:stone_pass@localhost:5432/stone_dev

# Render production
postgresql://user:pass@dpg-abc123-a.oregon-postgres.render.com:5432/stonewalker_db
```

## Backup and Restore

### Backup

```bash
# Full database backup
pg_dump -h localhost -U stone_user stone_dev > backup.sql

# Django fixture backup
python manage.py dumpdata --natural-foreign --natural-primary > data.json
```

### Restore

```bash
# From SQL dump
psql -h localhost -U stone_user -d stone_dev < backup.sql

# From Django fixture
python manage.py loaddata data.json
```

## Performance Considerations

### PostgreSQL Optimization

1. **Connection pooling**: Use `conn_max_age` in database settings
2. **Indexes**: Ensure proper indexes on frequently queried fields
3. **Query optimization**: Use `select_related()` and `prefetch_related()`

### Monitoring

```bash
# Check database size
psql -h localhost -U stone_user -d stone_dev -c "
SELECT pg_size_pretty(pg_database_size('stone_dev'));
"

# Check table sizes
psql -h localhost -U stone_user -d stone_dev -c "
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

## Security Notes

1. **Never commit database credentials** to version control
2. **Use environment variables** for all sensitive data
3. **Regular backups** of production data
4. **Monitor database access** and queries
5. **Use strong passwords** for database users

## Quick Reference

| Task | Command |
|------|---------|
| Check current DB | `python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default'])"` |
| Run migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Dump data | `python manage.py dumpdata > backup.json` |
| Load data | `python manage.py loaddata backup.json` |
| Connect to PostgreSQL | `psql "postgresql://stone_user:stone_pass@localhost:5432/stone_dev"` |
| Check table contents | `python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())"` |
