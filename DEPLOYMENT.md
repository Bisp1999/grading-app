# Railway Deployment Guide

## Step-by-Step Deployment to Railway Staging

### 1. Railway Dashboard Setup
1. Go to [Railway](https://railway.app) and sign in
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `grading-app` repository
4. Name the project: `grading-app-staging`

### 2. Add PostgreSQL Database
1. In your Railway project dashboard
2. Click **"Add Service"** → **"Database"** → **"PostgreSQL"**
3. Railway will automatically provision and connect the database

### 3. Configure Environment Variables
In Railway project settings → Variables tab, add:
```
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
```
*Note: Railway automatically provides `DATABASE_URL` from PostgreSQL service*

### 4. GitHub Integration
1. Railway automatically connects to your GitHub repo
2. **Auto-deploy**: Every push to `main` branch triggers deployment
3. View deployments in Railway dashboard

### 5. Database Migration (First Deploy)
After first deployment, run in Railway console:
```bash
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

## Files Created for Deployment

- **`Procfile`**: Tells Railway to use Gunicorn
- **`config.py`**: Production/development configurations
- **`requirements.txt`**: Updated with Gunicorn and PostgreSQL driver
- **`env.example`**: Template for environment variables

## Local Development vs Railway

**Local**: Uses SQLite, Flask dev server
**Railway**: Uses PostgreSQL, Gunicorn production server

## Deployment URLs
- **Staging**: `https://your-app-name.railway.app`
- **Production** (future): Create second environment later

## Cost Estimate
- **Web Service**: ~$5/month
- **PostgreSQL**: ~$5/month
- **Total**: ~$10/month (well under $20 budget)

## Next Steps
1. Push changes to GitHub
2. Railway will auto-deploy
3. Access your live app via Railway-provided URL
4. Test all functionality in staging environment
