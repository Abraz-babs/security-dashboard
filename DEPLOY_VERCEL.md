# Vercel Deployment Guide

## Option 1: Vercel Dashboard (Recommended)

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Enter: `https://github.com/Abraz-babs/security-dashboard`
4. Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build: `npm run build`
   - Output: `dist`

5. Add Environment Variable:
```
VITE_API_URL=https://your-railway-url.up.railway.app
```

6. Click "Deploy"

## Option 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod

# Set environment variable
vercel env add VITE_API_URL
# Enter: https://your-railway-url.up.railway.app
```

## Post-Deployment

Your frontend will be at: `https://citadel-kebbi.vercel.app`
