# CITADEL KEBBI - Free API Keys Setup Guide

This guide shows you how to obtain **free API keys** for all external data sources used by CITADEL KEBBI.

---

## 📰 NEWS API KEYS (For Security Intel)

### 1. **GNews API** (Recommended - 100 requests/day FREE)
**Purpose**: News articles about Kebbi, Sokoto, Zamfara security

**Signup**:
1. Go to https://gnews.io/
2. Click "Get API Key"
3. Create free account
4. Copy your API key

**Cost**: FREE tier - 100 requests/day
**Upgrade**: $4.99/month for 10,000 requests

**Add to `.env`**:
```
GNEWS_API_KEY=your_gnews_api_key_here
```

---

### 2. **NewsData.io** (Alternative - 200 requests/day FREE)
**Purpose**: Alternative news source

**Signup**:
1. Go to https://newsdata.io/
2. Click "Get API Key"
3. Create free account
4. Copy your API key

**Cost**: FREE tier - 200 requests/day

**Add to `.env`**:
```
NEWSDATA_API_KEY=your_newsdata_api_key_here
```

---

### 3. **GDELT Project** (FREE - No API key needed)
**Purpose**: Global news monitoring

**Status**: ✅ Already working - No signup required
**Limitations**: May have intermittent availability

---

### 4. **RSS Feeds** (FREE - No API key needed)
**Purpose**: Nigerian news from Premium Times, Daily Trust, Sahara Reporters, etc.

**Status**: ✅ Already working - No signup required

---

## 🛰️ SATELLITE API KEYS

### 5. **NASA FIRMS** (FREE - API key recommended)
**Purpose**: Fire and thermal hotspot detection

**Signup**:
1. Go to https://firms.modaps.eosdis.nasa.gov/api/
2. Click "Sign Up" to get API key
3. Or use the existing key (rate-limited but functional)

**Cost**: Completely FREE

**Add to `.env`** (optional but recommended):
```
NASA_FIRMS_KEY=your_nasa_firms_key_here
```

---

### 6. **N2YO Satellite Tracking** (FREE - API key required)
**Purpose**: Real-time satellite positions and passes

**Signup**:
1. Go to https://www.n2yo.com/api/
2. Click "Request API Key"
3. Fill in your email and purpose
4. Wait for email with API key (usually instant)

**Cost**: FREE tier - 1000 requests/hour

**Add to `.env`**:
```
N2YO_API_KEY=your_n2yo_api_key_here
```

---

### 7. **Copernicus Sentinel Hub** (FREE - Account required)
**Purpose**: Satellite imagery products over Kebbi State

**Signup**:
1. Go to https://dataspace.copernicus.eu/
2. Click "Register" and create account
3. After login, go to "User Settings" > "Dashboard"
4. Navigate to "Copernicus Services" to get Client ID and Secret

**Cost**: Completely FREE for research/non-commercial use

**Add to `.env`**:
```
COPERNICUS_CLIENT_ID=your_client_id
COPERNICUS_CLIENT_SECRET=your_client_secret
```

---

## 🤖 AI API KEYS (For Analysis)

### 8. **Groq AI** (FREE - $200 credit)
**Purpose**: LLM for AI analysis and chatbot

**Signup**:
1. Go to https://console.groq.com/
2. Sign up with GitHub or email
3. Get $200 free credit automatically
4. Go to "API Keys" and create new key

**Cost**: FREE ($200 credit) → Pay-as-you-go after
**Rate Limit**: Free tier - 20 requests/minute

**Add to `.env`**:
```
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

### 9. **Google Gemini** (FREE - 1,500 requests/day)
**Purpose**: Fallback AI when Groq is unavailable

**Signup**:
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your API key

**Cost**: FREE tier - 1,500 requests/day

**Add to `.env`**:
```
GEMINI_API_KEY=AIzaYourGeminiKeyHere
GEMINI_MODEL=gemini-2.0-flash
```

---

## 📋 Complete `.env` Template

Create a file named `.env` in the project root with this content:

```bash
# === NEWS APIS ===
GNEWS_API_KEY=                         # Get from gnews.io (FREE 100/day)
NEWSDATA_API_KEY=                      # Get from newsdata.io (FREE 200/day)
GNEWS_API_KEY=                         # Optional backup

# === SATELLITE APIS ===
NASA_FIRMS_KEY=d6f184f24be054275115eba93b61d360  # Or get your own
N2YO_API_KEY=                          # Get from n2yo.com (FREE)
COPERNICUS_CLIENT_ID=                  # Get from dataspace.copernicus.eu
COPERNICUS_CLIENT_SECRET=              # Get from dataspace.copernicus.eu

# === AI APIS ===
GROQ_API_KEY=                          # Get from console.groq.com (FREE $200)
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_API_KEY=                        # Get from aistudio.google.com (FREE 1500/day)
GEMINI_MODEL=gemini-2.0-flash

# === APP SETTINGS ===
DEBUG=false
APP_NAME=CITADEL KEBBI
APP_VERSION=2.1.0
DATABASE_URL=postgresql://citadel:KebbiSecure2024_Database_X9m2@localhost:5432/citadel_db

# === FRONTEND ===
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

---

## ⚡ Quick Start (Minimal Setup)

For basic functionality, you only need these **3 FREE APIs**:

| Priority | Service | Get Key From | Cost |
|----------|---------|--------------|------|
| 🔴 High | **N2YO** | n2yo.com | FREE |
| 🟡 Medium | **Groq** | console.groq.com | FREE ($200 credit) |
| 🟢 Low | **GNews** | gnews.io | FREE (100/day) |

With just N2YO + Groq, the system works with:
- ✅ Live satellite tracking
- ✅ AI analysis and chatbot
- ✅ RSS news feeds (no API key needed)
- ✅ NASA FIRMS (fallback key included)

---

## 🔧 Testing Your API Keys

After adding keys to `.env`, restart the backend:

```bash
cd backend
python -m uvicorn main:app --reload
```

Then test each API:

```bash
# Test health endpoint (shows API status)
curl http://localhost:8000/api/health/detailed

# Test satellite tracking
curl http://localhost:8000/api/satellite/n2yo/tracked

# Test intel feeds
curl http://localhost:8000/api/intel/security
```

---

## 📞 Support

If an API stops working:
1. Check rate limits (most free tiers reset daily)
2. Verify API key hasn't expired
3. Check service status page (some services have maintenance)
4. The system automatically falls back to RSS feeds if APIs fail

---

## 💡 Pro Tips

1. **Rotate API keys** monthly if you hit rate limits
2. **Use multiple news APIs** for redundancy (already configured)
3. **Cache reduces API calls** - data is cached for 3-5 minutes
4. **Groq $200 credit** lasts ~3-6 months for typical usage
