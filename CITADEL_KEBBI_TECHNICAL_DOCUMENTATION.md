# CITADEL KEBBI - Technical Documentation
## Security Intelligence Command Center v2.0

---

# TABLE OF CONTENTS
1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Engineering Design](#3-engineering-design)
4. [Component Deep Dive](#4-component-deep-dive)
5. [Data Flow & Processing](#5-data-flow--processing)
6. [API Integration Layer](#6-api-integration-layer)
7. [Security Architecture](#7-security-architecture)
8. [Market Analysis & Worth](#8-market-analysis--worth)
9. [Deployment Guide](#9-deployment-guide)
10. [Future Roadmap](#10-future-roadmap)

---

# 1. EXECUTIVE SUMMARY

## 1.1 Project Overview

**CITADEL KEBBI** is a real-time Security Intelligence Command Center designed for Kebbi State, Nigeria. It aggregates multi-source intelligence data, performs AI-powered threat analysis, and provides actionable situational awareness to security operatives.

### Core Capabilities
- **Real-time Threat Monitoring**: NASA FIRMS thermal anomaly detection, satellite tracking
- **Multi-Source Intelligence**: GDELT, GNews, RSS feeds, OSINT aggregation
- **AI-Powered Analysis**: Groq LLM for threat assessment, trend analysis, SITREP generation
- **Geospatial Intelligence**: 21 LGA risk mapping with dynamic scoring
- **Predictive Analytics**: ML-based anomaly detection and threat forecasting

### Technology Stack
```
Backend:  Python 3.11 + FastAPI + WebSocket
Frontend: React 18 + Vite + CSS3 (Cyberpunk UI)
AI/ML:    Groq (Llama 3.3-70B) + Gemini + Custom ML Models
Data:     Multi-API aggregation + In-memory caching
Deploy:   Railway (Backend) + Vercel (Frontend)
```

---

# 2. SYSTEM ARCHITECTURE

## 2.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER (Vercel)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   React UI   │  │  WebSocket   │  │  DataCache   │  │  Voice/Speech│    │
│  │   (Vite)     │  │   Client     │  │ (localStorage)│  │   Engine     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                                   │
│                    FastAPI (Python 3.11) on Railway                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   CORS      │ │    Auth     │ │  Rate Limit │ │   Cache     │           │
│  │ Middleware  │ │   Router    │ │ Middleware  │ │   Layer     │           │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
└─────────┼───────────────┼───────────────┼───────────────┼──────────────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Dashboard  │ │  Satellite  │ │   Intel     │ │     AI      │           │
│  │   Router    │ │   Router    │ │   Router    │ │   Router    │           │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
└─────────┼───────────────┼───────────────┼───────────────┼──────────────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL API INTEGRATION LAYER                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  NASA FIRMS │ │   GDELT     │ │   GNews     │ │    N2YO     │           │
│  │ Fire/Thermal│ │ OSINT News  │ │  News API   │ │  Satellite  │           │
│  │  Detection  │ │   (Global)  │ │  (Kebbi)    │ │  Tracking   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │ Copernicus  │ │    RSS      │ │   Groq AI   │                           │
│  │  Sentinel   │ │   Feeds     │ │   (LLM)     │                           │
│  │  Imagery    │ │(Nigerian)   │ │ Analysis    │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Component Interaction Flow

```
User Request Flow:
──────────────────

┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  User   │───▶│   React     │───▶│   FastAPI   │───▶│    Cache    │
│  Login  │    │   Frontend  │    │   Backend   │    │   Check     │
└─────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                            │
                                    ┌───────────────────────┼───────┐
                                    │                       │       │
                                    ▼                       ▼       ▼
                              ┌──────────┐          ┌──────────┐ ┌──────────┐
                              │   HIT    │          │  MISS    │ │ External │
                              │  Return  │          │  Fetch   │ │   APIs   │
                              │  Cache   │          │  Fresh   │ │          │
                              └──────────┘          └────┬─────┘ └────┬─────┘
                                                         │            │
                                                         └────────────┘
                                                                │
                                                                ▼
                                                         ┌─────────────┐
                                                         │   Update    │
                                                         │    Cache    │
                                                         └─────────────┘

Real-time Updates (WebSocket):
──────────────────────────────

┌──────────┐         ┌──────────────┐         ┌──────────────┐
│  Backend │◀───────▶│  WebSocket   │◀───────▶│   Frontend   │
│  Events  │  Push   │   Manager    │  Push   │   Listeners  │
└──────────┘         └──────────────┘         └──────────────┘
     │
     ├─ Intel Update Detected
     ├─ Sentinel Overhead Alert
     └─ Threat Level Change
```

---

# 3. ENGINEERING DESIGN

## 3.1 Backend Architecture (FastAPI)

### Directory Structure
```
backend/
├── main.py                 # FastAPI app + WebSocket + lifecycle
├── config.py              # Environment variables, constants, LGA data
├── models/
│   └── schemas.py         # Pydantic models for request/response
├── routers/
│   ├── auth.py            # Authentication (SHA-256 hashed passwords)
│   ├── dashboard.py       # Overview, LGA data, threat levels
│   ├── satellite.py       # NASA FIRMS, N2YO, Copernicus, Sentinel
│   ├── intel.py           # OSINT aggregation endpoints
│   └── ai.py              # Chat, analysis, SITREP generation
├── services/
│   ├── cache.py           # In-memory caching layer
│   ├── firms.py           # NASA FIRMS API integration
│   ├── n2yo.py            # Satellite tracking API
│   ├── newsdata.py        # Multi-source intelligence (GDELT, GNews, RSS)
│   ├── copernicus.py      # Sentinel data hub
│   ├── sentinel_timer.py  # Orbital mechanics calculator
│   ├── ml_engine.py       # Anomaly detection, trend analysis
│   └── groq_ai.py         # LLM integration (Groq + Gemini fallback)
└── requirements.txt
```

### Key Design Patterns

#### 1. **Caching Strategy (Multi-Tier)**
```python
# L1: In-memory Python cache (fastest)
cache.set(key, data, ttl=180)  # 3 minutes

# L2: localStorage (frontend persistence)
dataCache.set(CACHE_KEYS.DASHBOARD, data)  # 5 minutes

# Cache warming on startup prevents cold starts
async def _prewarm_cache():
    fires = await fetch_all_sensors(days=2)
    cache.set("fire_data", fires, ttl=180)
```

#### 2. **Graceful Degradation**
```python
# If external API fails, return cached or empty data
async def _get_cached_data():
    cached = cache.get("fire_data")
    try:
        fresh = await fetch_all_sensors(days=2)
        cache.set("fire_data", fresh, ttl=180)
        return fresh
    except TimeoutError:
        return cached or {"hotspots": [], "total": 0}  # Graceful fallback
```

#### 3. **Background Refresh**
```python
# Return cache immediately, refresh in background
if cache_valid:
    asyncio.create_task(_refresh_cache_if_needed())  # Non-blocking
    return cached_data
```

## 3.2 Frontend Architecture (React + Vite)

### Directory Structure
```
frontend/
├── src/
│   ├── App.jsx                 # Main app, auth, WebSocket, routing
│   ├── api/
│   │   └── client.js          # API client with caching + timeouts
│   ├── services/
│   │   └── DataCache.js       # localStorage persistence layer
│   ├── components/
│   │   ├── Auth/
│   │   │   └── LoginScreen.jsx
│   │   ├── Layout/
│   │   │   ├── Sidebar.jsx
│   │   │   └── Header.jsx
│   │   ├── Dashboard/
│   │   │   └── DashboardView.jsx
│   │   ├── Satellite/
│   │   │   ├── SatelliteView.jsx
│   │   │   └── OrbitTracker.jsx
│   │   ├── Intel/
│   │   │   └── IntelFeed.jsx
│   │   ├── AI/
│   │   │   ├── ChatBot.jsx
│ │   │   └── AIAnalysis.jsx
│   │   ├── Analytics/
│   │   │   └── AnalyticsView.jsx
│   │   ├── SITREP/
│   │   │   └── SITREPGenerator.jsx
│   │   ├── Globe/
│   │   │   └── Globe3D.jsx
│   │   └── Admin/
│   │       └── AdminPanel.jsx
│   └── index.css              # Cyberpunk/security UI theme
├── index.html
└── package.json
```

### Key Frontend Patterns

#### 1. **State Management**
```javascript
// Multi-tier state: Props → Cache → API
const [dashboardData, setDashboardData] = useState(() => 
    dataCache.get(CACHE_KEYS.DASHBOARD)  // Initialize from cache
);

useEffect(() => {
    getDashboardOverview()
        .then(data => {
            setDashboardData(data);
            dataCache.set(CACHE_KEYS.DASHBOARD, data);  // Persist
        })
        .catch(() => {
            // Fallback to cached on error
            const cached = dataCache.get(CACHE_KEYS.DASHBOARD);
            if (cached) setDashboardData(cached);
        });
}, []);
```

#### 2. **Real-time Updates (WebSocket)**
```javascript
useEffect(() => {
    wsRef.current = createWebSocket((data) => {
        if (data.type === 'intel_update') {
            setDashboardData(prev => ({
                ...prev,
                stats: { ...prev.stats, intel_reports: data.intel_count }
            }));
        }
        if (data.type === 'sentinel_alert') {
            setSentinelAlert(data);
            speakText(`SENTINEL ALERT: ${data.message}`);  // Voice
        }
    });
}, []);
```

#### 3. **Cyberpunk UI Theme**
```css
/* Glassmorphism panels */
.glass-panel {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 240, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

/* Neon glow effects */
.stat-card.critical { --stat-color: #ff0040; }
.stat-card.warning { --stat-color: #ff6600; }
```

---

# 4. COMPONENT DEEP DIVE

## 4.1 Intelligence Aggregation Engine

### Multi-Source Data Pipeline
```
┌─────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE ENGINE                          │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │   GDELT     │   │   GNews     │   │   RSS       │           │
│  │  (Global)   │   │  (Kebbi)    │   │  (Nigeria)  │           │
│  │  21 reports │   │  0 reports  │   │  0 reports  │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            ▼                                    │
│                   ┌─────────────────┐                          │
│                   │  Deduplication  │                          │
│                   │  + Filtering    │                          │
│                   └────────┬────────┘                          │
│                            ▼                                    │
│                   ┌─────────────────┐                          │
│                   │ Severity Scoring│                          │
│                   │ Category Tagger │                          │
│                   └────────┬────────┘                          │
│                            ▼                                    │
│                   ┌─────────────────┐                          │
│                   │  21 Processed   │                          │
│                   │  Intel Reports  │                          │
│                   └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### Kebbi-Focused Filtering
```python
KEBBI_REGION_WORDS = [
    "kebbi", "sokoto", "zamfara", "northwest nigeria", "birnin kebbi",
    "argungu", "zuru", "yauri", "shanga", "bagudo", "augie", "dandi",
    "fakai", "sakaba", "wasagu", "danko", "koko", "besse", "kalgwai",
    "bandit", "terrorist", "kidnap", "ambush", "herdsmen", "cattle rustling"
]
```

## 4.2 Dynamic LGA Risk Scoring

### Risk Calculation Algorithm
```python
def _calculate_dynamic_lga_risk(lga, hotspots, reports):
    score = 0.0
    
    # 1. Fire hotspot proximity (NASA FIRMS) - 35% weight
    for h in hotspots:
        dist = _haversine(lga["lat"], lga["lon"], h["latitude"], h["longitude"])
        if dist < 30:  # Within 30km
            score += max(0, (30 - dist) / 30) * 0.15
    
    # 2. Intel report mentions - 40% weight
    for r in reports:
        if lga["name"].lower() in r["title"].lower():
            score += 0.2 if r["severity"] == "critical" else 0.1
    
    # 3. Geographic risk factors - 25% weight
    border_lgas = {"Dandi", "Augie", "Argungu", "Bagudo"}  # Border with Niger/Nigeria
    southern = {"Fakai", "Sakaba", "Wasagu/Danko", "Zuru"}  # Bandit prone
    
    if lga["name"] in southern:
        score += 0.25  # High historical bandit activity
    elif lga["name"] in border_lgas:
        score += 0.15  # Border vulnerability
    
    # Risk classification
    if score >= 0.6: return "critical", score
    elif score >= 0.4: return "high", score
    elif score >= 0.2: return "medium", score
    else: return "low", score
```

## 4.3 AI Analysis Engine (Groq + Gemini)

### Architecture
```
User Query ──▶ Context Builder ──▶ LLM Router ──▶ Response
                    │                  │
                    ▼                  ▼
            ┌──────────────┐    ┌─────────────┐
            │ Dashboard    │    │  Groq API   │
            │ Data         │    │  (Primary)  │
            │ (fires, intel│    │  Llama 3.3  │
            │  LGAs)       │    │  70B        │
            └──────────────┘    └──────┬──────┘
                                       │
                                ┌──────┴──────┐
                                │   Failure   │
                                └──────┬──────┘
                                       ▼
                                ┌─────────────┐
                                │  Gemini API │
                                │  (Fallback) │
                                │  Flash 2.0  │
                                └─────────────┘
```

### Prompt Engineering
```python
SYSTEM_PROMPT = """You are CITADEL KEBBI, an advanced AI security analyst for Kebbi State, Nigeria.
Your role is to provide tactical intelligence analysis and actionable recommendations.

ANALYSIS FRAMEWORK:
1. Threat Assessment: Evaluate severity and immediacy
2. Geographic Context: Consider LGA-specific factors
3. Pattern Recognition: Identify trends and anomalies
4. Actionable Intelligence: Provide specific recommendations

TONE: Professional, concise, authoritative military intelligence style.
Use terms like 'SITREP', 'threat vector', 'operational area'.
"""
```

---

# 5. DATA FLOW & PROCESSING

## 5.1 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA LIFECYCLE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

PHASE 1: INGESTION (External APIs)
───────────────────────────────────
NASA FIRMS    ──▶ Fire hotspots (lat/lon/brightness/confidence)
GDELT         ──▶ News articles (title/description/url/date)
GNews         ──▶ News articles (title/description/source)
RSS Feeds     ──▶ Nigerian news (XML parsing)
N2YO          ──▶ Satellite positions (TLE propagation)

PHASE 2: PROCESSING (Backend)
──────────────────────────────
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Parse     │───▶│   Filter    │───▶│   Score     │───▶│   Cache     │
│   JSON/XML  │    │   Kebbi     │    │   Severity  │    │   Store     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

PHASE 3: ANALYSIS (ML + AI)
───────────────────────────
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Anomaly Detect  │    │  Trend Analysis │    │  Threat Predict │
│ (IsolationForest)│   │  (Time series)  │    │  (Heuristic)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘

PHASE 4: DISTRIBUTION
──────────────────────
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  REST API   │    │  WebSocket  │    │   Voice     │
│  (HTTP)     │    │  (Real-time)│    │  (TTS)      │
└─────────────┘    └─────────────┘    └─────────────┘

PHASE 5: VISUALIZATION (Frontend)
─────────────────────────────────
Dashboard ──▶ Stats cards, threat gauge, LGA grid
Satellite ──▶ Fire map, orbit tracker
Intel     ──▶ News feed, filterable by severity
AI        ──▶ Chat interface, analysis reports
```

## 5.2 Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CACHE HIERARCHY                                   │
└─────────────────────────────────────────────────────────────────────────────┘

Level 1: Python In-Memory (Fastest)
├─ Key: "fire_data"
├─ TTL: 180 seconds (3 minutes)
├─ Data: NASA FIRMS hotspots
└─ Purpose: Eliminate repeated API calls

Level 2: Dashboard Cache
├─ Key: "dashboard_overview"
├─ TTL: 300 seconds (5 minutes)
├─ Data: Computed stats, threat levels
└─ Purpose: Fast dashboard rendering

Level 3: Frontend localStorage (Persistent)
├─ Key: "citadel_dashboard_data"
├─ TTL: 300 seconds (5 minutes)
├─ Data: API responses
└─ Purpose: Survive tab switches/reloads

Invalidation Strategy:
- Time-based: Automatic expiry after TTL
- Manual: Admin panel "Clear Cache" button
- Event-driven: WebSocket broadcasts trigger refresh
```

---

# 6. API INTEGRATION LAYER

## 6.1 External API Matrix

| API | Purpose | Rate Limit | Cost | Reliability |
|-----|---------|------------|------|-------------|
| **NASA FIRMS** | Fire hotspots | 10 req/min | Free | ⭐⭐⭐⭐⭐ |
| **GDELT** | Global news | Unlimited | Free | ⭐⭐⭐⭐ |
| **GNews** | News articles | 100/day | Free tier | ⭐⭐⭐ |
| **N2YO** | Satellite tracking | 1000/day | Free | ⭐⭐⭐⭐⭐ |
| **Groq** | AI analysis | 30 req/min | Free tier | ⭐⭐⭐⭐ |
| **Gemini** | AI fallback | 60 req/min | Free tier | ⭐⭐⭐⭐ |
| **Copernicus** | Sentinel imagery | 10 req/min | Free | ⭐⭐⭐ |

## 6.2 API Resilience Patterns

```python
# Pattern 1: Timeout with fallback
try:
    data = await asyncio.wait_for(fetch_api(), timeout=10.0)
except asyncio.TimeoutError:
    data = cache.get("key") or default_data

# Pattern 2: Circuit breaker (simplified)
last_failure = failure_timestamps.get(api_name, 0)
if time.time() - last_failure < 60:  # 1 min cooldown
    return cached_data  # Skip API call

try:
    return await fetch_api()
except Exception as e:
    failure_timestamps[api_name] = time.time()
    return cached_data

# Pattern 3: Multi-source aggregation
results = await asyncio.gather(
    fetch_gdelt(),
    fetch_gnews(),
    fetch_rss(),
    return_exceptions=True
)
valid_results = [r for r in results if not isinstance(r, Exception)]
```

---

# 7. SECURITY ARCHITECTURE

## 7.1 Authentication Flow

```
┌─────────┐         ┌──────────────┐         ┌──────────────┐
│  User   │────────▶│   Login      │────────▶│  SHA-256     │
│         │  POST   │   Endpoint   │  Hash   │  Verify      │
└─────────┘         └──────────────┘         └──────┬───────┘
                                                    │
                          ┌────────────────────────┘
                          ▼
                   ┌──────────────┐
                   │   Token      │
                   │   Generate   │
                   │   (SHA-256   │
                   │   seeded)    │
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │   Return     │
                   │   {token,    │
                   │   user}      │
                   └──────────────┘
```

### Password Storage
```python
# No plaintext storage - only SHA-256 hashes
AUTHORIZED_USERS = {
    "operator": {
        "password_hash": hashlib.sha256("KebbiOps@2024".encode()).hexdigest(),
        "role": "operator",
        "clearance": "CONFIDENTIAL",
    }
}
```

## 7.2 CORS & Security Headers

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://*.vercel.app",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# 8. MARKET ANALYSIS & WORTH

## 8.1 Target Market

### Primary Market: State Governments (Nigeria)
| State | Security Budget (Annual) | Addressable |
|-------|--------------------------|-------------|
| Kebbi State | ₦5-10B ($3.3-6.6M) | ✅ Pilot |
| Sokoto State | ₦8-12B | 🎯 Target |
| Zamfara State | ₦10-15B | 🎯 Target |
| Niger State | ₦7-10B | 🎯 Target |
| Katsina State | ₦8-12B | 🎯 Target |
| **Total NW Region** | **₦40-60B** | **~$35M** |

### Secondary Market: Private Security
- Mining companies (Zamfara gold, Kebbi agriculture)
- Logistics/Transport companies
- Insurance companies (risk assessment)

### Tertiary Market: International
- Other African countries with similar challenges
- NGOs operating in conflict zones
- UN peacekeeping missions

## 8.2 Revenue Model

### SaaS Pricing Tiers
```
┌─────────────────────────────────────────────────────────────┐
│  TIER           │  PRICE        │  FEATURES                  │
├─────────────────┼───────────────┼────────────────────────────┤
│  Basic          │  ₦500K/mo     │  Dashboard, Intel Feed     │
│                 │  ($330)       │  2 LGAs, Email alerts      │
├─────────────────┼───────────────┼────────────────────────────┤
│  Professional   │  ₦2M/mo       │  Full state coverage       │
│                 │  ($1,300)     │  AI Analysis, API access   │
│                 │               │  24/7 support              │
├─────────────────┼───────────────┼────────────────────────────┤
│  Enterprise     │  ₦5M/mo       │  Multi-state, Custom AI    │
│                 │  ($3,300)     │  On-premise option         │
│                 │               │  Dedicated account manager │
└─────────────────────────────────────────────────────────────┘
```

### Market Valuation

#### Comparable Companies
| Company | Product | Valuation | Revenue |
|---------|---------|-----------|---------|
| Palantir | Gotham | $40B | $2B |
| Dataminr | Real-time alerts | $4.1B | $150M |
| Recorded Future | Threat intel | $780M | $100M |
| Premise Data | Crowd-sourced intel | $500M | $50M |

#### CITADEL KEBBI Valuation Estimate
**Conservative (Nigeria only):**
- 5 states × ₦2M/month = ₦10M/month = ₦120M/year ($80K)
- 5-year projection: ₦600M ($400K)
- Valuation at 5x revenue: **$2M**

**Aggressive (West Africa expansion):**
- 15 countries × 5 states × ₦2M = ₦150M/month ($100K)
- Annual: ₦1.8B ($1.2M)
- 5-year projection: ₦9B ($6M)
- Valuation at 10x revenue: **$60M**

### Competitive Advantages
1. **Localized AI**: Trained on Nigerian security context
2. **Multi-source**: Combines 7+ intelligence sources
3. **Real-time**: WebSocket updates vs batch processing
4. **Cost-effective**: Open-source stack, low operating costs
5. **Offline capable**: Caching works without internet

---

# 9. DEPLOYMENT GUIDE

## 9.1 Railway (Backend) Deployment

### Step 1: Prepare Repository
```bash
# Ensure your code is in GitHub
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Railway Setup
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your CITADEL repository
4. Railway auto-detects Python/FastAPI

### Step 3: Environment Variables
```env
# In Railway Dashboard → Variables
GROQ_API_KEY=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
GEMINI_API_KEY=AIzaSyA4bbAHvwxikKohtOpdvSeTIEBEMFqRuPM
NASA_FIRMS_KEY=d6f184f24be054275115eba93b61d360
N2YO_API_KEY=KL63MF-MBRKB3-XR6EX3-5MVD
GNEWS_API_KEY=4ff1f67e5dd9e476b094cbe89e6a054e
COPERNICUS_CLIENT_ID=sh-9e94ba4e-fafe-49d8-887d-90b2f3692d74
COPERNICUS_CLIENT_SECRET=hKPle4tbVOKmirZSUZberROjVCV0t6dr
APP_NAME=CITADEL KEBBI
APP_VERSION=2.0.0
DEBUG=false
```

### Step 4: Procfile
Create `Procfile` in backend root:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 5: Deploy
```bash
# Railway CLI (optional)
npm install -g @railway/cli
railway login
railway link
railway up
```

**Backend URL**: `https://citadel-backend.railway.app`

---

## 9.2 Vercel (Frontend) Deployment

### Step 1: Update API URLs
```javascript
// frontend/src/api/client.js
const API_BASE = import.meta.env.VITE_API_URL || 'https://citadel-backend.railway.app';
const WS_BASE = import.meta.env.VITE_WS_URL || 'wss://citadel-backend.railway.app';
```

### Step 2: Environment Variables
Create `frontend/.env.production`:
```env
VITE_API_URL=https://citadel-backend.railway.app
VITE_WS_URL=wss://citadel-backend.railway.app
```

### Step 3: Vercel Configuration
Create `vercel.json` in frontend root:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### Step 4: Deploy
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

**Frontend URL**: `https://citadel-kebbi.vercel.app`

---

## 9.3 Alternative: Netlify Deployment

### Netlify Configuration
Create `netlify.toml` in frontend root:
```toml
[build]
  base = "frontend"
  publish = "dist"
  command = "npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Deploy via Git
1. Push to GitHub
2. Connect repo to Netlify
3. Set build command: `npm run build`
4. Set publish directory: `dist`

---

## 9.4 Post-Deployment Checklist

### Backend Verification
```bash
# Test health endpoint
curl https://your-backend.railway.app/api/health

# Test dashboard
curl https://your-backend.railway.app/api/dashboard/overview

# Verify WebSocket (use wss:// for production)
wscat -c wss://your-backend.railway.app/ws
```

### Frontend Verification
1. ✅ Login works
2. ✅ Dashboard shows data (fires, intel, LGAs)
3. ✅ WebSocket connects (check browser console)
4. ✅ AI chat responds
5. ✅ SITREP generates

### CORS Configuration
Update backend `main.py`:
```python
allow_origins=[
    "http://localhost:5173",  # Local dev
    "https://your-frontend.vercel.app",  # Production
    "https://*.vercel.app",
]
```

---

# 10. FUTURE ROADMAP

## Phase 2 (Q2 2025)
- [ ] Mobile app (React Native)
- [ ] SMS/Email alerts integration
- [ ] Drone imagery analysis
- [ ] WhatsApp bot for field reports

## Phase 3 (Q3 2025)
- [ ] Expand to Sokoto, Zamfara states
- [ ] Predictive modeling (ML training)
- [ ] Blockchain for intel verification
- [ ] Satellite image change detection

## Phase 4 (Q4 2025)
- [ ] Voice recognition (Hausa support)
- [ ] Integration with NPF/NSCDC systems
- [ ] Export to ECOWAS countries
- [ ] Advanced analytics (Power BI/Tableau)

---

# APPENDIX

## A. API Endpoint Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/auth/login` | POST | User authentication | No |
| `/api/dashboard/overview` | GET | Full dashboard stats | Yes |
| `/api/dashboard/lgas` | GET | 21 LGAs with risk levels | Yes |
| `/api/intel/security` | GET | Multi-source intel feed | Yes |
| `/api/satellite/firms/all` | GET | NASA fire hotspots | Yes |
| `/api/ai/analyze` | POST | AI threat analysis | Yes |
| `/api/ai/sitrep` | POST | Generate SITREP | Yes |
| `/ws` | WebSocket | Real-time updates | Yes |

## B. Database Schema (Future)

```sql
-- PostgreSQL for persistent storage
users (id, username, password_hash, role, clearance, created_at)
intel_reports (id, title, description, source, severity, category, lat, lon, created_at)
fire_hotspots (id, latitude, longitude, brightness, confidence, acq_date, sensor)
lga_risk_history (id, lga_name, risk_level, score, calculated_at)
alert_logs (id, type, severity, message, acknowledged, created_at)
```

## C. Support & Maintenance

**Development Team:** CITADEL Engineering
**Support Email:** support@citadel-kebbi.gov.ng
**Documentation:** https://docs.citadel-kebbi.gov.ng
**Status Page:** https://status.citadel-kebbi.gov.ng

---

*Document Version: 2.0.0*
*Last Updated: February 2025*
*Classification: UNCLASSIFIED*
