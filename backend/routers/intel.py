"""Intel Router - OSINT Intelligence Feed (Cached with Fallback)"""
from fastapi import APIRouter
from services.newsdata import fetch_intel_feed
from services import cache
from services.data_warmer import FALLBACK_INTEL, _fetch_intel_fast
import asyncio

router = APIRouter(prefix="/api/intel", tags=["intel"])


@router.get("/feed")
async def get_intel_feed(query: str = "Kebbi Nigeria security", limit: int = 10):
    """Get OSINT intelligence feed - uses cache if available."""
    cached = cache.get("intel_data")
    if cached and cached.get("total", 0) > 0:
        reports = cached.get("reports", [])
        # Filter by query if provided
        if query and query != "Kebbi Nigeria security":
            query_lower = query.lower()
            reports = [r for r in reports if query_lower in r.get("title", "").lower() 
                      or query_lower in r.get("description", "").lower()]
        return {
            "reports": reports[:limit],
            "total": len(reports),
            "query": query,
            "source": cached.get("source", "cache"),
            "fetched_at": cached.get("fetched_at")
        }
    
    # No cache - return fallback immediately
    return {
        "reports": FALLBACK_INTEL["reports"][:limit],
        "total": len(FALLBACK_INTEL["reports"]),
        "query": query,
        "source": "fallback",
        "fetched_at": FALLBACK_INTEL["fetched_at"]
    }


@router.get("/security")
async def get_security_intel():
    """Get comprehensive security intel - ALWAYS returns data from cache or fallback."""
    # Try cache first
    cached = cache.get("intel_data")
    if cached and cached.get("total", 0) > 0:
        return cached
    
    # Return fallback data immediately - don't wait for APIs
    print("[Intel] Returning fallback data (cache empty)")
    return FALLBACK_INTEL


@router.post("/refresh")
async def refresh_intel():
    """Force refresh intel data from APIs."""
    try:
        intel = await asyncio.wait_for(_fetch_intel_fast(), timeout=15.0)
        if intel and intel.get("total", 0) > 0:
            cache.set("intel_data", intel, ttl=180)
            return {"success": True, "message": f"Refreshed {intel['total']} reports", "data": intel}
        return {"success": False, "message": "APIs returned empty data"}
    except Exception as e:
        return {"success": False, "message": f"Refresh failed: {str(e)}"}
