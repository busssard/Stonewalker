# StoneWalker Render Deployment Guide

This guide explains how to deploy the StoneWalker Django application on Render


### Render.com (Recommended for Full Django Support)

Render.com is a modern cloud platform that natively supports Django, PostgreSQL, and background workers. Here’s how to deploy this project on Render:

1. **Create a Render Account**
   - Go to [render.com](https://render.com) and sign up or log in.

2. **Create a New Web Service**
   - Click "New +" > "Web Service".
   - Connect your GitHub repository containing this project.
   - **Important:** In the Environment settings, set Python version to 3.12 (not 3.13)
   - For the build and start commands, use:
     - **Build Command:** `./render_build.sh`
     - **Start Command:** `cd source && ./render_start.sh`
     - (Adjust the path if your wsgi.py is not at `source/app/wsgi.py`)

3. **Set Environment Variables**
   - In the Render dashboard, go to your service > Environment > Add Environment Variable.
   - Add the following variables:
     - `SECRET_KEY=your-secret-key`
     - `DEBUG=False`
     - `ALLOWED_HOSTS=your-app-name.onrender.com`
     - `DATABASE_URL=postgres://username:password@host:port/dbname` (see below)

4. **Add a PostgreSQL Database**
   - In the Render dashboard, click "New +" > "PostgreSQL".
   - After creation, copy the database connection string and set it as your `DATABASE_URL` environment variable.

5. **Configure Static Files**
   - Render can serve static files from a specified directory. In your Django settings, ensure `STATIC_ROOT` is set (e.g., `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`).
   - In the Render dashboard, set the static files path to `/staticfiles` (or your configured path).

6. **Deploy**
   - Click "Manual Deploy" or push to your repository to trigger a deployment.

7. **Run Migrations**
   - The start script runs migrations automatically on each deploy.
   - If you need to run them manually, open Shell and run:
     ```bash
     cd source && python manage.py migrate --noinput
     ```

8. **(Optional) Create a Superuser**
   - In the Shell, run:
     ```bash
     cd source && python manage.py createsuperuser
     ```

**Notes:**
- Make sure your `.env` file is not committed to Git. Use Render’s environment variable settings instead.
- If you use `environs` and `dj-database-url`, your `settings.py` should read the `DATABASE_URL` from the environment.
- For background tasks (e.g., Celery), use Render’s Background Worker service.

#### Local vs Production settings

- The app switches settings via `IS_PRODUCTION` env var:
  - Unset/False: development settings (SQLite) for local debugging
  - True: production settings (`DATABASE_URL` via `dj-database-url`)
  
Examples:
```bash
# Local dev (SQLite)
unset IS_PRODUCTION
cd source && python manage.py runserver

# Local prod-like (Postgres)
export IS_PRODUCTION=true
export DATABASE_URL="postgresql://USER:PASS@HOST:PORT/DBNAME"
cd source && python manage.py runserver
```

**References:**
- [Render Django Guide](https://render.com/docs/deploy-django)
- [Render Environment Variables](https://render.com/docs/environment-variables)

#### Using Gunicorn on Render.com

Gunicorn is a production-grade WSGI server recommended for serving Django applications on Render.com. Here’s how to set it up:

1. **Install Gunicorn**
   - Add Gunicorn to your dependencies:
     ```bash
     pip install gunicorn
     ```
   - Make sure `gunicorn` is listed in your `requirements.txt` or `pyproject.toml` so it is installed during deployment.

2. **Configure the Start Command**
   - In the Render dashboard, set the Start Command to:
     ```bash
     gunicorn app.wsgi:application
     ```
     - If your `wsgi.py` is in a subdirectory, adjust the import path accordingly (e.g., `source.app.wsgi:application`).

3. **Procfile (Optional)**
   - If you want to use a `Procfile` (supported by Render), add a file named `Procfile` to your project root with the following content:
     ```
     web: gunicorn app.wsgi:application
     ```

4. **Static Files**
   - Gunicorn does not serve static files. Make sure you run `python source/manage.py collectstatic` during the build process and configure Render to serve static files from the correct directory (e.g., `/staticfiles`).

5. **Environment Variables**
   - Ensure `DEBUG=False`, `ALLOWED_HOSTS`, and `DATABASE_URL` are set in the Render dashboard for production security and database connectivity.

**References:**
- [Gunicorn Documentation](https://docs.gunicorn.org/en/stable/run.html)
- [Render Django Guide](https://render.com/docs/deploy-django)

## Testing the Deployment


## Custom Domain

To use a custom domain with your Render.com deployment:
1. Go to your Render dashboard and select your web service.
2. Navigate to the "Settings" tab and scroll to the "Custom Domains" section.
3. Click "Add Custom Domain" and enter your domain name.
4. Follow the provided DNS instructions to point your domain to Render’s servers (usually by adding a CNAME or A record).
5. Once DNS propagates, Render will automatically provision an SSL certificate for your domain.

## Monitoring and Analytics

Render provides built-in monitoring for your services:
- **Logs:** View real-time and historical logs from the "Logs" tab of your service.
- **Metrics:** Basic CPU, memory, and disk usage metrics are available in the "Metrics" tab.
- For advanced analytics, consider integrating with third-party tools like Sentry (for error tracking) or Google Analytics (for frontend analytics).

## Troubleshooting

### Build Failures
- Check the "Logs" tab for build errors.
- Ensure all dependencies are listed in `requirements.txt` or `pyproject.toml`.
- Verify your build and start commands are correct.

### Runtime Errors
- Check the "Logs" tab for runtime errors and stack traces.
- Ensure all environment variables are set correctly in the Render dashboard.
- Make sure database migrations have been run.

### Static File Issues
- Confirm that `python source/manage.py collectstatic` runs successfully during the build.
- Ensure `STATIC_ROOT` is set and matches the static files path configured in Render.
- Check file permissions and that files exist in the expected directory.

## Local Development

To test your Django project locally before deploying:
1. Create a `.env` file with your local environment variables (do not commit this file).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python source/manage.py migrate
   ```
4. Collect static files:
   ```bash
   python source/manage.py collectstatic
   ```
5. Start the development server:
   ```bash
   python source/manage.py runserver
   ```
6. For production-like testing, you can run:
   ```bash
   gunicorn app.wsgi:application
   ```

## Security Considerations

- **Environment Variables:** Never commit secrets or sensitive data to your repository. Use Render’s environment variable settings.
- **DEBUG:** Always set `DEBUG=False`