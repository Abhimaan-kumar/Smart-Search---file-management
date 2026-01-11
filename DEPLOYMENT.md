# Deployment Guide for Render

This guide will help you deploy your Personal Smart Search & Organizer application on Render.

## Prerequisites

1. A GitHub account (or GitLab/Bitbucket)
2. A Render account (sign up at https://render.com)
3. Your code pushed to a Git repository

## Deployment Steps

### Option 1: Deploy Backend Only (Recommended for Start)

If you want to deploy just the API backend first:

#### Step 1: Prepare Your Repository

1. Make sure all your files are committed and pushed to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

#### Step 2: Create a New Web Service on Render

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

#### Step 3: Configure the Service

Use these settings:

- **Name**: `smart-search-api` (or any name you prefer)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Plan**: Choose Free tier (or paid if you prefer)

#### Step 4: Environment Variables (Optional)

You can add environment variables if needed:
- `PYTHON_VERSION`: `3.11.0` (optional, Render usually auto-detects)

#### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Wait for the build to complete (usually 2-5 minutes)

#### Step 6: Get Your API URL

Once deployed, Render will provide a URL like:
- `https://smart-search-api.onrender.com`

Your API will be available at:
- API: `https://smart-search-api.onrender.com/api`
- Docs: `https://smart-search-api.onrender.com/docs`
- Health: `https://smart-search-api.onrender.com/health`

### Option 2: Deploy Full Stack (Backend + Frontend)

The FastAPI app is configured to serve the frontend from the same service.

#### Configuration

The same settings as Option 1 work, but the frontend will be served at:
- Frontend: `https://smart-search-api.onrender.com/`
- API: `https://smart-search-api.onrender.com/api`

#### Update Frontend API URL

The frontend (`frontend/app.js`) automatically detects the environment:
- **Local**: Uses `http://localhost:8000/api`
- **Production**: Uses the same host with `/api` prefix

No manual changes needed!

### Option 3: Separate Frontend Deployment (Advanced)

If you want to deploy the frontend separately:

1. **Deploy Backend** (follow Option 1)
2. **Deploy Frontend as Static Site**:
   - Create a new **Static Site** on Render
   - Point to your `frontend` folder
   - Set build command: (none needed, it's static)
   - Set publish directory: `frontend`
3. **Update API URL**:
   - In `frontend/app.js`, you can set a custom API URL:
   ```javascript
   const API_BASE = 'https://your-api-url.onrender.com/api';
   ```

## Important Notes

### Free Tier Limitations

Render's free tier has some limitations:
- **Spins down after 15 minutes of inactivity**: First request after spin-down takes ~30 seconds
- **Limited resources**: 512MB RAM, 0.1 CPU
- **Build time limits**: 45 minutes

### Data Persistence

⚠️ **Important**: Your current implementation stores data in memory. This means:
- Data is **lost** when the service restarts
- Data is **lost** when Render spins down the service

**Solutions**:
1. **For production**: Add a database (PostgreSQL, MongoDB, etc.)
2. **For testing**: Use Render's PostgreSQL (free tier available)
3. **Quick fix**: Use file-based storage (JSON files) - data persists across restarts but not across deployments

### Health Checks

Render automatically uses the `/health` endpoint to check if your service is running.

### Custom Domain

You can add a custom domain in Render dashboard:
1. Go to your service settings
2. Click **"Custom Domains"**
3. Add your domain
4. Follow DNS configuration instructions

## Testing Your Deployment

1. **Check Health**:
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **Test API**:
   ```bash
   curl https://your-app.onrender.com/api
   ```

3. **View Docs**:
   Open `https://your-app.onrender.com/docs` in your browser

4. **Test Frontend**:
   Open `https://your-app.onrender.com/` in your browser

## Troubleshooting

### Build Fails

- Check that `requirements.txt` is in the root directory
- Verify Python version compatibility
- Check build logs in Render dashboard

### Service Won't Start

- Verify the start command is correct
- Check that port uses `$PORT` environment variable
- Review logs in Render dashboard

### CORS Issues

- The API already has CORS enabled for all origins
- If issues persist, check the CORS middleware configuration

### Frontend Not Loading

- Verify `frontend` folder exists in repository
- Check that static file serving is configured in `api/main.py`
- Review Render logs for errors

## Updating Your Deployment

1. Push changes to your Git repository
2. Render automatically detects changes and redeploys
3. Monitor the deployment in Render dashboard

## Using render.yaml (Alternative Method)

If you prefer configuration as code, you can use the `render.yaml` file:

1. The `render.yaml` file is already in your repository
2. In Render dashboard:
   - Click **"New +"** → **"Blueprint"**
   - Connect your repository
   - Render will read `render.yaml` and create services automatically

## Next Steps

1. **Add Database**: Implement persistent storage
2. **Add Authentication**: Secure your API
3. **Add Monitoring**: Set up logging and error tracking
4. **Optimize**: Add caching, rate limiting, etc.

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- FastAPI Documentation: https://fastapi.tiangolo.com

---

**Happy Deploying! 🚀**
