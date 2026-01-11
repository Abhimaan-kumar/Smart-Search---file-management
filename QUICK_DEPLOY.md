# Quick Deployment Guide - Render

## 🚀 Fastest Way to Deploy

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Use these settings:

   **Basic Settings:**
   - **Name**: `smart-search-api`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)

   **Build & Deploy:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

5. Click **"Create Web Service"**

### Step 3: Wait & Test

- Wait 2-5 minutes for deployment
- Your app will be at: `https://smart-search-api.onrender.com`
- Frontend: `https://smart-search-api.onrender.com/`
- API Docs: `https://smart-search-api.onrender.com/docs`
- Health Check: `https://smart-search-api.onrender.com/health`

## 📝 What's Included

✅ Backend API (FastAPI)  
✅ Frontend (HTML/CSS/JS) - served from same service  
✅ Automatic API URL detection  
✅ Health check endpoint  
✅ CORS enabled  

## ⚠️ Important Notes

1. **Free tier spins down after 15 min inactivity** - first request may take ~30 seconds
2. **Data is in-memory** - will be lost on restart (add database for persistence)
3. **Auto-deploys** on every git push

## 🔧 Alternative: Using render.yaml

If you prefer, you can use the `render.yaml` file:
1. Click **"New +"** → **"Blueprint"**
2. Connect repository
3. Render reads `render.yaml` automatically

## 📚 Full Guide

See `DEPLOYMENT.md` for detailed instructions and troubleshooting.
