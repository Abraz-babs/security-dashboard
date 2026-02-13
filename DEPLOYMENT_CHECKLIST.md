# CITADEL KEBBI - Quick Deployment Guide

## 🚀 Deploy Backend to Railway (5 minutes)

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Production ready v2.0"
git push origin main
```

### Step 2: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### Step 3: Add Environment Variables
In Railway Dashboard → Your Project → Variables:

```bash
# AI/ML APIs
GROQ_API_KEY=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
GEMINI_API_KEY=AIzaSyA4bbAHvwxikKohtOpdvSeTIEBEMFqRuPM

# Satellite/Data APIs
NASA_FIRMS_KEY=d6f184f24be054275115eba93b61d360
N2YO_API_KEY=KL63MF-MBRKB3-XR6EX3-5MVD
COPERNICUS_CLIENT_ID=sh-9e94ba4e-fafe-49d8-887d-90b2f3692d74
COPERNICUS_CLIENT_SECRET=hKPle4tbVOKmirZSUZberROjVCV0t6dr

# News APIs
GNEWS_API_KEY=4ff1f67e5dd9e476b094cbe89e6a054e

# App Config
APP_NAME=CITADEL KEBBI
APP_VERSION=2.0.0
DEBUG=false
```

### Step 4: Create Procfile
Create file `backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Deploy
Railway auto-deploys when you push to GitHub. Or use CLI:
```bash
cd backend
npm install -g @railway/cli
railway login
railway link
railway up
```

**Your Backend URL**: `https://citadel-[random].railway.app`

---

## 🌐 Deploy Frontend to Vercel (3 minutes)

### Step 1: Update API URL
Edit `frontend/.env.production`:
```env
VITE_API_URL=https://citadel-[your-backend].railway.app
VITE_WS_URL=wss://citadel-[your-backend].railway.app
```

### Step 2: Install Vercel CLI
```bash
cd frontend
npm install -g vercel
vercel login
```

### Step 3: Deploy
```bash
vercel --prod
```

Follow prompts:
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No**
- Project name? **citadel-kebbi**

**Your Frontend URL**: `https://citadel-kebbi.vercel.app`

---

## ✅ Post-Deployment Verification

### Test Backend
```bash
curl https://your-backend.railway.app/api/health
# Should return: {"status":"operational"}

curl https://your-backend.railway.app/api/dashboard/overview
# Should return dashboard data with fires, intel, LGAs
```

### Test Frontend
1. Open `https://citadel-kebbi.vercel.app`
2. Login with:
   - Username: `operator`
   - Password: `KebbiOps@2024`
3. Verify dashboard loads with data

---

## 🔧 Troubleshooting

### CORS Errors
Update `backend/main.py`:
```python
allow_origins=[
    "https://citadel-kebbi.vercel.app",  # Your frontend URL
    "https://*.vercel.app",
]
```

### WebSocket Not Connecting
Ensure you're using `wss://` (secure) not `ws://`:
```javascript
const WS_BASE = "wss://your-backend.railway.app";
```

### API Timeouts
Railway free tier has cold starts. First request may take 10-30s.

---

## 📊 Monitoring

### Railway Dashboard
- CPU/Memory usage
- Request logs
- Environment variables

### Vercel Dashboard
- Deployment status
- Analytics
- Error logs

---

## 💰 Cost Estimates

| Service | Free Tier | Paid Tier (Recommended) |
|---------|-----------|-------------------------|
| Railway | $5 credit/mo | $5/mo (512MB RAM) |
| Vercel | 100GB bandwidth | $20/mo (Pro) |
| **Total** | **$0/mo** | **$25/mo** |

---

## 🆘 Emergency Contacts

- **Railway Support**: https://railway.app/help
- **Vercel Support**: https://vercel.com/help
- **CITADEL Docs**: See `CITADEL_KEBBI_TECHNICAL_DOCUMENTATION.md`
