"""AI Router - Chat, Analysis, SITREP (V2.1 - Cached + Timeout-Safe)"""
from fastapi import APIRouter
from models.schemas import ChatMessage, AnalysisRequest, SITREPRequest
from services.groq_ai import chat, analyze_dashboard, generate_sitrep
from services import cache
from config import KEBBI_LGAS
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/ai", tags=["ai"])

# In-memory chat history (per session - simple approach)
_chat_histories = {}


@router.post("/chat")
async def ai_chat(msg: ChatMessage):
    """Send a message to CITADEL AI chatbot."""
    session_id = "default"

    if session_id not in _chat_histories:
        _chat_histories[session_id] = []

    history = _chat_histories[session_id]
    response = chat(msg.message, history=history, context=msg.context)

    # Update history
    history.append({"role": "user", "content": msg.message})
    history.append({"role": "assistant", "content": response})

    # Keep history manageable
    if len(history) > 20:
        _chat_histories[session_id] = history[-20:]

    return {
        "response": response,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/analyze")
async def ai_analyze(req: AnalysisRequest):
    """Run AI analysis on current dashboard data — uses cached intel/fire data."""
    dashboard_data = req.dashboard_data or {}

    # Use cached data instead of live fetching (avoids 30s+ timeout)
    if not dashboard_data.get("fire_hotspots"):
        cached_fires = cache.get("fire_data")
        if cached_fires:
            dashboard_data["fire_hotspots"] = cached_fires.get("hotspots", [])
        else:
            # Quick fetch with timeout
            try:
                from services.firms import fetch_all_sensors
                fire = await asyncio.wait_for(fetch_all_sensors(days=2), timeout=10.0)
                dashboard_data["fire_hotspots"] = fire.get("hotspots", [])
                cache.set("fire_data", fire, ttl=180)
            except (asyncio.TimeoutError, Exception):
                dashboard_data["fire_hotspots"] = []

    if not dashboard_data.get("intel_reports"):
        cached_intel = cache.get("intel_data")
        if cached_intel:
            dashboard_data["intel_reports"] = cached_intel.get("reports", [])
        else:
            try:
                from services.newsdata import fetch_security_intel
                intel = await asyncio.wait_for(fetch_security_intel(), timeout=10.0)
                dashboard_data["intel_reports"] = intel.get("reports", [])
                cache.set("intel_data", intel, ttl=180)
            except (asyncio.TimeoutError, Exception):
                dashboard_data["intel_reports"] = []

    if not dashboard_data.get("lga_data"):
        dashboard_data["lga_data"] = KEBBI_LGAS

    analysis = analyze_dashboard(dashboard_data, focus_area=req.focus_area)

    return {
        "analysis": analysis,
        "timestamp": datetime.utcnow().isoformat(),
        "data_sources": ["NASA FIRMS", "Multi-Source OSINT", "LGA Intelligence"],
    }


@router.post("/sitrep")
async def ai_sitrep(req: SITREPRequest):
    """Generate a SITREP from current intelligence — uses cached data."""
    # Use cached data first (fast), fallback to live fetch with timeout
    fire_data = cache.get("fire_data")
    intel_data = cache.get("intel_data")

    if not fire_data or not intel_data:
        try:
            from services.firms import fetch_all_sensors
            from services.newsdata import fetch_security_intel

            tasks = []
            if not fire_data:
                tasks.append(fetch_all_sensors(days=2))
            else:
                tasks.append(asyncio.sleep(0))  # placeholder
            if not intel_data:
                tasks.append(fetch_security_intel())
            else:
                tasks.append(asyncio.sleep(0))  # placeholder

            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=12.0
            )

            if not fire_data and not isinstance(results[0], (Exception, type(None))):
                fire_data = results[0] if isinstance(results[0], dict) else {"hotspots": [], "total": 0}
                cache.set("fire_data", fire_data, ttl=180)
            if not intel_data and not isinstance(results[1], (Exception, type(None))):
                intel_data = results[1] if isinstance(results[1], dict) else {"reports": [], "total": 0}
                cache.set("intel_data", intel_data, ttl=180)
        except (asyncio.TimeoutError, Exception):
            pass

    fire_data = fire_data or {"hotspots": [], "total": 0}
    intel_data = intel_data or {"reports": [], "total": 0}

    intel_context = {
        "fire_hotspots": fire_data.get("hotspots", []),
        "intel_reports": intel_data.get("reports", []),
        "lga_data": KEBBI_LGAS,
        "active_threats": fire_data.get("total", 0) + sum(
            1 for r in intel_data.get("reports", []) if r.get("severity") in ["critical", "high"]
        ),
        "threat_level": "ELEVATED",
    }

    sitrep = generate_sitrep(intel_context, period=req.period)

    return {
        "sitrep": sitrep,
        "timestamp": datetime.utcnow().isoformat(),
        "period": req.period,
    }


@router.post("/clear-history")
async def clear_chat_history():
    """Clear chat history."""
    _chat_histories.clear()
    return {"status": "cleared"}
