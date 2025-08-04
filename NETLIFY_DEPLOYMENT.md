# StoneWalker Netlify Deployment Guide

This guide explains how to deploy the StoneWalker Django application on Netlify.

## ⚠️ Important Note

**Netlify is primarily designed for static sites and serverless functions. While we've created a configuration that works with Netlify, for a full Django application with database functionality, we recommend using a platform that natively supports Python/Django such as:**

- **Heroku** - Excellent Django support with PostgreSQL
- **Railway** - Modern platform with great Python support
- **DigitalOcean App Platform** - Reliable Django hosting
- **PythonAnywhere** - Specialized Python hosting
- **Render** - Modern platform with good Django support

## Current Netlify Setup

The current setup provides:

1. **Static File Hosting** - All CSS, JS, and images are served from Netlify's CDN
2. **Serverless Functions** - Basic Django routing via Netlify Functions
3. **Redirects** - All Django routes are redirected to the serverless function
4. **Build Process** - Automated build and deployment

## Deployment Steps

### 1. Connect to Netlify

1. Go to [netlify.com](https://netlify.com) and sign up/login
2. Click "New site from Git"
3. Connect your GitHub/GitLab/Bitbucket repository
4. Select the repository containing this project

### 2. Configure Build Settings

Netlify will automatically detect the `netlify.toml` file, but you can also set these manually:

- **Build command:** `bash build.sh`
- **Publish directory:** `source`
- **Functions directory:** `netlify/functions`

### 3. Set Environment Variables

In your Netlify dashboard, go to Site settings > Environment variables and add:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.netlify.app,.netlify.com
```

### 4. Deploy

Click "Deploy site" and Netlify will:
1. Run the build script
2. Collect static files
3. Deploy the site
4. Set up redirects

## What Works

✅ **Static Files** - CSS, JS, images served from CDN  
✅ **Basic Routing** - All routes redirect to serverless function  
✅ **Build Process** - Automated deployment from Git  
✅ **HTTPS** - Automatic SSL certificates  
✅ **CDN** - Global content delivery network  

## What Doesn't Work (Limitations)

❌ **Database** - Netlify doesn't support persistent databases  
❌ **User Sessions** - No persistent session storage  
❌ **File Uploads** - No persistent file storage  
❌ **Email Sending** - No SMTP support  
❌ **Admin Panel** - Django admin requires database  
❌ **User Registration/Login** - Requires database and sessions  

## Alternative Deployment Options

### Option 1: Heroku (Recommended)

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-stonewalker-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python source/manage.py migrate
```

### Option 2: Railway

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will automatically detect Django and set up the environment
4. Add PostgreSQL database from the Railway dashboard
5. Set environment variables in Railway dashboard

### Option 3: DigitalOcean App Platform

1. Go to [digitalocean.com](https://digitalocean.com)
2. Create a new App
3. Connect your GitHub repository
4. Select Python as the runtime
5. Add PostgreSQL database
6. Configure environment variables

## Testing the Deployment

After deployment, you can test:

1. **Static Files:** Visit `https://your-site.netlify.app/static/css/styles.css`
2. **Landing Page:** Visit `https://your-site.netlify.app/`
3. **Serverless Function:** Visit `https://your-site.netlify.app/.netlify/functions/django`

## Custom Domain

To use a custom domain:

1. Go to your Netlify dashboard
2. Navigate to Site settings > Domain management
3. Add your custom domain
4. Configure DNS settings as instructed

## Monitoring and Analytics

Netlify provides:

- **Build logs** - View deployment history
- **Function logs** - Monitor serverless function performance
- **Analytics** - Basic site analytics
- **Forms** - Handle form submissions (if needed)

## Troubleshooting

### Build Failures

1. Check the build logs in Netlify dashboard
2. Ensure all dependencies are in `requirements.txt`
3. Verify the build script has execute permissions

### Function Errors

1. Check function logs in Netlify dashboard
2. Verify environment variables are set correctly
3. Test functions locally with Netlify CLI

### Static File Issues

1. Ensure files are in the correct `static` directory
2. Check that `collectstatic` ran successfully
3. Verify file permissions

## Local Development

To test the Netlify setup locally:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Test functions locally
netlify dev

# Test build process
netlify build
```

## Security Considerations

1. **Environment Variables** - Never commit secrets to Git
2. **HTTPS** - Netlify provides automatic SSL
3. **Headers** - Security headers are configured in `netlify.toml`
4. **CORS** - Configure CORS if needed for API endpoints

## Performance Optimization

1. **CDN** - Static files are served from global CDN
2. **Caching** - Static files are cached for 1 year
3. **Compression** - Automatic gzip compression
4. **Image Optimization** - Consider using Netlify's image optimization

## Support

For issues with this deployment setup:

1. Check the Netlify documentation
2. Review the build logs
3. Test locally with Netlify CLI
4. Consider migrating to a Django-native platform

## Migration Path

If you need full Django functionality, the migration path is:

1. **Export Data** - Backup any existing data
2. **Choose Platform** - Select Heroku, Railway, or DigitalOcean
3. **Update Settings** - Modify Django settings for the new platform
4. **Deploy** - Follow the platform-specific deployment guide
5. **Import Data** - Restore data to the new platform

The current Netlify setup serves as a good starting point and can be used for static content while the backend is deployed elsewhere. 