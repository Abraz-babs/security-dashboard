# Railway Deployment Guide

## Option 1: Railway Dashboard (Recommended)

1. Go to https://railway.com/new
2. Select "Deploy from GitHub repo"
3. Choose `Abraz-babs/security-dashboard`
4. Add Environment Variables:

```bash
NASA_FIRMS_KEY=your_key_here
N2YO_API_KEY=your_key_here
COPERNICUS_CLIENT_ID=your_id_here
COPERNICUS_CLIENT_SECRET=your_secret_here
GROQ_API_KEY=your_key_here
ADMIN_PASSWORD=KebbiSecure@2024
ANALYST_PASSWORD=KebbiAnalyst@2024
OPERATOR_PASSWORD=KebbiOps@2024
```

5. Configure:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Option 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init --name citadel-kebbi-backend

# Add variables
railway variables set NASA_FIRMS_KEY=xxx
railway variables set N2YO_API_KEY=xxx
# ... add all other variables

# Deploy
railway up
```

## Post-Deployment

Get your Railway URL: `https://citadel-kebbi-backend.up.railway.app`
Use this for Vercel's `VITE_API_URL`.
