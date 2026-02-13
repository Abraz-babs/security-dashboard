# CITADEL KEBBI - Deployment Checklist

## ✅ System Status (As of Last Test)

| Feature | Status | Notes |
|---------|--------|-------|
| Dashboard | ✅ Working | LGA risks, threat levels |
| NASA FIRMS | ✅ Working | 38 hotspots detected |
| N2YO Tracking | ✅ Working | 10 satellites |
| GNews | ⚠️ Intermittent | 1 article fetched |
| RSS Feeds | ⚠️ Timeout | Slow response |
| AI (Groq) | ✅ Configured | Key added |
| Analytics | ✅ Working | LGA charts |
| Admin Panel | ✅ Working | System status |

---

## Known Issues

1. **RSS Feed Timeouts** - Nigerian RSS feeds are slow, causing cache warm to fail
2. **GNews Errors** - Intermittent API errors
3. **GDELT Rate Limit** - 429 errors when requesting too fast

**Solution**: System works with on-demand fetching. Cache warming is a "nice to have" not required.

---

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Deployment ready - v2.1.0"
git push origin main
```

### 2. Backend - Render.com

**Create New Web Service:**
- Connect GitHub repo
- Settings:
  - Runtime: Python
  - Build: `pip install -r backend/requirements.txt`
  - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
```
GNEWS_API_KEY=4ff1f67e5dd9e476b094cbe89e6a054e
GROQ_API_KEY=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
NASA_FIRMS_KEY=d6f184f24be054275115eba93b61d360
N2YO_API_KEY=KL63MF-MBRKB3-XR6EX3-5MVD
COPERNICUS_CLIENT_ID=sh-9e94ba4e-fafe-49d8-887d-90b2f3692d74
COPERNICUS_CLIENT_SECRET=hKPle4tbVOKmirZSUZberROjVCV0t6dr
DEBUG=false
```

### 3. Frontend - Vercel

**Create New Project:**
- Import GitHub repo
- Settings:
  - Framework: Vite
  - Root: `frontend`
  - Build: `npm run build`
  - Output: `dist`

**Environment Variables:**
```
VITE_API_URL=https://your-backend.onrender.com
VITE_WS_URL=wss://your-backend.onrender.com
```

---

## Post-Deployment Verification

Test these endpoints:
```bash
# Health check
curl https://your-backend.onrender.com/api/health/detailed

# Should return:
{
  "status": "healthy",
  "external_apis": {
    "nasa_firms": {"status": "configured"},
    "n2yo": {"status": "configured"},
    "gnews": {"status": "configured"}
  }
}

# Test fire data
curl https://your-backend.onrender.com/api/satellite/firms/all?days=2
# Should return 30+ hotspots

# Test LGA data  
curl https://your-backend.onrender.com/api/dashboard/lgas
# Should return 21 LGAs with risk levels
```

---

## Troubleshooting

### If Dashboard Shows 0 Values
1. Wait 30 seconds for first data fetch
2. Check `/api/health/detailed` 
3. Refresh browser

### If AI Features Don't Work
1. Verify `GROQ_API_KEY` in Render environment variables
2. Check Groq console: https://console.groq.com/
3. Ensure key has credit remaining

### If News Shows 0 Reports
1. GNews has 12-hour delay on free plan - this is normal
2. RSS feeds may timeout on first load - refresh page
3. System will accumulate news over time

---

## Cost

| Service | Provider | Cost |
|---------|----------|------|
| Backend | Render | $0 |
| Frontend | Vercel | $0 |
| APIs | Various | $0 |
| **Total** | | **$0/month** |

---

## What's Working Now

- ✅ Dashboard with dynamic LGA risks
- ✅ NASA FIRMS fire detection (38 hotspots)
- ✅ N2YO satellite tracking (10 satellites)
- ✅ AI chatbot and analysis (Groq configured)
- ✅ Admin panel for monitoring
- ✅ Analytics charts

## What's Limited

- ⚠️ News aggregation (GNews 12h delay + RSS timeouts)
- ⚠️ Real-time updates (WebSocket works but may reconnect)

---

**Ready to deploy!** The system is functional and will improve as data accumulates.
