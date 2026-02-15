"""CITADEL KEBBI - Main FastAPI Application (V2.1)"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from config import APP_NAME, APP_VERSION, DEBUG
from routers import auth, dashboard, satellite, intel, ai, intelligence
from services import cache
from services.data_warmer import warm_all_caches, background_refresh
import asyncio
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter: 100 requests per minute per IP
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Security Intelligence Command Center for Kebbi State",
    debug=False,  # SECURITY: Disable debug in production
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - allow frontend (dev + production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://*.vercel.app",
        "https://*.netlify.app",
        "https://security-ai-fushion-dashboard-kb.netlify.app",
        "https://divine-daveta-securekebbi-2f64fe25.koyeb.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(satellite.router)
app.include_router(intel.router)
app.include_router(ai.router)
app.include_router(intelligence.router)


@app.get("/")
async def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "OPERATIONAL",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health")
async def health():
    return {"status": "operational", "uptime": "active", "timestamp": datetime.now().isoformat()}


@app.get("/api/health/detailed")
async def health_detailed():
    """Detailed health check with external API status."""
    import httpx
    from config import GNEWS_API_KEY, NASA_FIRMS_KEY, N2YO_API_KEY, COPERNICUS_CLIENT_ID
    
    checks = {
        "backend": {"status": "healthy", "timestamp": datetime.now().isoformat()},
        "external_apis": {},
        "cache_status": {}
    }
    
    # Check cache status
    checks["cache_status"] = {
        "intel_data": "warm" if cache.get("intel_data") else "cold",
        "fire_data": "warm" if cache.get("fire_data") else "cold",
        "sentinel_passes": "warm" if cache.get("sentinel_passes") else "cold",
        "dashboard_overview": "warm" if cache.get("dashboard_overview") else "cold",
    }
    
    # Check NASA FIRMS (lightweight - just check config)
    checks["external_apis"]["nasa_firms"] = {
        "status": "configured" if NASA_FIRMS_KEY else "missing_key",
        "type": "fire_thermal_data"
    }
    
    # Check N2YO
    checks["external_apis"]["n2yo"] = {
        "status": "configured" if N2YO_API_KEY else "missing_key",
        "type": "satellite_tracking"
    }
    
    # Check Copernicus
    checks["external_apis"]["copernicus"] = {
        "status": "configured" if COPERNICUS_CLIENT_ID else "missing_key",
        "type": "satellite_imagery"
    }
    
    # Check GNews
    checks["external_apis"]["gnews"] = {
        "status": "configured" if GNEWS_API_KEY else "missing_key",
        "type": "news_api"
    }
    
    # Test RSS feeds (lightweight HEAD request)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.head("https://www.premiumtimesng.com/category/news/top-news/feed")
            checks["external_apis"]["rss_feeds"] = {
                "status": "reachable" if resp.status_code == 200 else "degraded",
                "sample": "premium_times"
            }
    except Exception as e:
        checks["external_apis"]["rss_feeds"] = {"status": "unreachable", "error": str(e)}
    
    # Overall status
    all_healthy = all(
        api["status"] in ["configured", "reachable"]
        for api in checks["external_apis"].values()
    )
    checks["status"] = "healthy" if all_healthy else "degraded"
    
    return checks


# ──── WebSocket for Real-time Updates ────
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for c in disconnected:
            self.disconnect(c)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data) if data else {}
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            elif msg.get("type") == "subscribe":
                await websocket.send_json({"type": "subscribed", "channel": msg.get("channel", "all")})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ──── Background Intel Broadcast (Uses Cache) ────
async def auto_intel_broadcast():
    """Periodically broadcast LIVE intel + fire data. Uses cached data for speed."""
    while True:
        try:
            await asyncio.sleep(120)  # Every 2 minutes

            # Fetch LIVE data (will cache automatically via dashboard router helper)
            from services.newsdata import fetch_security_intel
            from services.firms import fetch_all_sensors

            # Use cached data if available, else fetch with timeout
            intel = cache.get("intel_data")
            fires = cache.get("fire_data")

            if not intel or not fires:
                try:
                    intel_task = fetch_security_intel()
                    fire_task = fetch_all_sensors(days=1)
                    intel, fires = await asyncio.wait_for(
                        asyncio.gather(intel_task, fire_task),
                        timeout=15.0
                    )
                    cache.set("intel_data", intel, ttl=90)
                    cache.set("fire_data", fires, ttl=90)
                except asyncio.TimeoutError:
                    intel = intel or {"reports": [], "total": 0}
                    fires = fires or {"hotspots": [], "total": 0}

            # Get sentinel data from cache too
            sentinel_data = cache.get("sentinel_passes") or {}
            next_pass = sentinel_data.get("next_pass")

            # Broadcast REAL data counts to voice system
            await manager.broadcast({
                "type": "intel_update",
                "timestamp": datetime.now().isoformat(),
                "intel_count": intel.get("total", 0),
                "fire_count": fires.get("total", 0),
                "latest_reports": intel.get("reports", [])[:5],
                "latest_hotspots": fires.get("hotspots", [])[:3],
                "sentinel_next_pass": next_pass,
            })
        except Exception as e:
            print(f"[BROADCAST ERROR] {e}")


# ──── Sentinel Orbit Alert (Uses Cache) ────
async def sentinel_orbit_alert():
    """Check Sentinel pass proximity and broadcast alerts — cached."""
    while True:
        try:
            await asyncio.sleep(60)

            # Use cached sentinel data (refreshed by OrbitTracker frontend)
            data = cache.get("sentinel_passes")
            if not data:
                from services.sentinel_timer import get_sentinel_passes
                try:
                    data = await asyncio.wait_for(get_sentinel_passes(days=1), timeout=15.0)
                except asyncio.TimeoutError:
                    continue

            next_pass = data.get("next_pass")
            if next_pass:
                # Recalculate seconds_until
                now_ts = datetime.now().timestamp()
                seconds_until = int(next_pass.get("start_utc", 0) - now_ts)
                satellite_name = next_pass.get("satellite", "SENTINEL")

                if 280 <= seconds_until <= 320:
                    await manager.broadcast({
                        "type": "sentinel_alert",
                        "alert": "approaching",
                        "satellite": satellite_name,
                        "seconds_until": seconds_until,
                        "message": f"{satellite_name} will be overhead in approximately 5 minutes",
                        "timestamp": datetime.now().isoformat(),
                    })
                elif 0 < seconds_until <= 30:
                    await manager.broadcast({
                        "type": "sentinel_alert",
                        "alert": "overhead",
                        "satellite": satellite_name,
                        "message": f"{satellite_name} is now overhead. Imagery acquisition in progress.",
                        "timestamp": datetime.now().isoformat(),
                    })
        except Exception:
            pass


@app.on_event("startup")
async def startup_event():
    """Startup: pre-warm cache synchronously + start background tasks."""
    print(f"\n{'='*60}")
    print(f"  {APP_NAME} v{APP_VERSION}")
    print(f"  Security Intelligence Command Center")
    print(f"  Status: INITIALIZING...")
    print(f"{'='*60}\n")
    
    # CRITICAL: Warm cache synchronously before accepting requests
    # This ensures the first request has data
    await warm_all_caches()
    
    # Start background refresh tasks
    asyncio.create_task(background_refresh())
    asyncio.create_task(auto_intel_broadcast())
    asyncio.create_task(sentinel_orbit_alert())
    
    print(f"\n{'='*60}")
    print(f"  {APP_NAME} v{APP_VERSION}")
    print(f"  Security Intelligence Command Center")
    print(f"  Status: OPERATIONAL")
    print(f"  Time: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
