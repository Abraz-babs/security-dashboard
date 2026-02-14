# CITADEL KEBBI - API Documentation

## Base URL
```
Production: https://divine-daveta-securekebbi-2f64fe25.koyeb.app/api
```

## Authentication
All endpoints require Bearer token authentication except `/auth/login` and `/health`.

```bash
Authorization: Bearer <token>
```

## Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "operational",
  "uptime": "active",
  "timestamp": "2026-02-14T00:00:00"
}
```

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "citadel_admin",
  "password": "KebbiSecure@2024"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "username": "citadel_admin",
    "role": "admin",
    "clearance": "TOP SECRET"
  }
}
```

### Dashboard

#### Get Fire Hotspots
```http
GET /api/dashboard/fires?days=2
```

**Response:**
```json
{
  "hotspots": [
    {
      "latitude": 11.7532,
      "longitude": 4.0821,
      "brightness": 367.5,
      "confidence": "high",
      "acq_date": "2026-02-13",
      "satellite": "VIIRS"
    }
  ],
  "count": 174,
  "region": "Kebbi State",
  "last_updated": "2026-02-13T23:30:00"
}
```

#### Generate SITREP
```http
POST /api/dashboard/sitrep
Content-Type: application/json

{
  "period": "24h"
}
```

### Satellite Tracking

#### Get Tracked Satellites
```http
GET /api/satellite/tracked
```

#### Get Sentinel Passes
```http
GET /api/satellite/sentinel/passes?days=3
```

**Response:**
```json
{
  "sentinels": {
    "SENTINEL-1A": {
      "norad_id": 39634,
      "passes": [...],
      "next_pass": {...}
    }
  },
  "next_pass": {
    "satellite": "SENTINEL-1A",
    "start_utc": 1707830400,
    "seconds_until": 21573
  },
  "upcoming_passes": [...]
}
```

### Intelligence

#### Get Intel Feed
```http
GET /api/intel/feed?query=bandit&max=10
```

**Response:**
```json
{
  "reports": [
    {
      "title": "Bandits attack village in Sokoto",
      "source": "Daily Trust",
      "severity": "critical",
      "category": "criminal",
      "kebbi_relevant": true,
      "published_at": "2026-02-13T18:30:00"
    }
  ],
  "total": 13,
  "source": "multi_source_kebbi_focus"
}
```

### AI Analysis

#### Chat with AI
```http
POST /api/ai/chat
Content-Type: application/json

{
  "message": "When is the next satellite pass over Fakai LGA?"
}
```

**Response:**
```json
{
  "response": "Based on current orbital data, Sentinel-1A will pass over Fakai LGA on...",
  "context": "satellite_timing",
  "sources": ["n2yo", "sentinel"]
}
```

### Admin Configuration

#### Get System Config
```http
GET /api/admin/config/system
Authorization: Bearer <admin_token>
```

#### Update Alert Contacts
```http
POST /api/admin/contacts
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role": "commissioner",
  "name": "CP Security",
  "phone": "+2348012345678",
  "email": "cp@kebbi.gov.ng",
  "priority": "critical"
}
```

#### Get API Status
```http
GET /api/admin/api-status
Authorization: Bearer <admin_token>
```

**Response:**
```json
[
  {
    "name": "NASA FIRMS",
    "status": "operational",
    "last_check": "2026-02-14T00:00:00"
  }
]
```

### Predictive Analytics

#### Get 24-Hour Forecast
```http
GET /api/analytics/forecast/24h
```

**Response:**
```json
{
  "predictions": [
    {
      "time": "2026-02-14T14:00:00",
      "lga": "Fakai",
      "threat_score": 78.5,
      "risk_level": "HIGH",
      "recommended_action": "Deploy patrol teams..."
    }
  ],
  "high_risk_periods": ["14:00-16:00", "20:00-22:00"]
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

## Rate Limits

- Dashboard: 60 requests/minute
- Satellite: 30 requests/minute
- Intel: 60 requests/minute
- AI Chat: 20 requests/minute

## WebSocket (Real-time)

Connect to `/ws/alerts` for real-time push notifications.

```javascript
const ws = new WebSocket('wss://your-backend.koyeb.app/ws/alerts');

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('New alert:', alert);
};
```

## SDK Examples

### Python
```python
import requests

API_BASE = "https://your-backend.koyeb.app/api"
TOKEN = "your_token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Get fires
fires = requests.get(f"{API_BASE}/dashboard/fires", headers=headers).json()

# Get satellite passes
passes = requests.get(f"{API_BASE}/satellite/sentinel/passes", headers=headers).json()
```

### JavaScript
```javascript
const API_BASE = 'https://your-backend.koyeb.app/api';

async function getIntelFeed() {
  const response = await fetch(`${API_BASE}/intel/feed`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}
```

---

**For support contact: technical@citadelkebbi.gov.ng**
