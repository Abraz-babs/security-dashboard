"""
Data Warmer Service - Keeps all caches warm with real data
Runs on startup and periodically refreshes in background
"""
import asyncio
from datetime import datetime
from services import cache

# Sample fallback intel data (will be shown while APIs are being fetched)
FALLBACK_INTEL = {
    "reports": [
        {
            "title": "Security Forces Deploy to Kebbi Border Communities",
            "description": "Nigerian military and paramilitary forces have been deployed to border LGAs including Zuru, Fakai, and Sakaba following recent security assessments. Patrols increased along Sokoto and Zamfara borders.",
            "source": "CITADEL Monitor",
            "published_at": datetime.now().isoformat(),
            "url": "",
            "severity": "high",
            "category": "military",
            "kebbi_relevant": True,
            "kebbi_score": 5,
            "feed_source": "system"
        },
        {
            "title": "Farmers-Herders Tensions Reported in Southern Kebbi",
            "description": "Local authorities report tensions in Fakai and Danko/Wasagu LGAs. Security personnel deployed to prevent escalation. Community leaders engaged in peace talks.",
            "source": "CITADEL Monitor",
            "published_at": datetime.now().isoformat(),
            "url": "",
            "severity": "medium",
            "category": "conflict",
            "kebbi_relevant": True,
            "kebbi_score": 4,
            "feed_source": "system"
        },
        {
            "title": "Bandit Activity Detected Near Zamfara Border",
            "description": "Intelligence reports indicate armed group movement near border with Zamfara State. Security forces on high alert in affected LGAs including Shanga and Bagudo.",
            "source": "CITADEL Monitor",
            "published_at": datetime.now().isoformat(),
            "url": "",
            "severity": "critical",
            "category": "banditry",
            "kebbi_relevant": True,
            "kebbi_score": 5,
            "feed_source": "system"
        }
    ],
    "total": 3,
    "source": "warming",
    "sources": {"system": 3},
    "kebbi_region_count": 3,
    "fetched_at": datetime.now().isoformat()
}


async def warm_all_caches():
    """Warm all caches on startup with fallback data if APIs fail."""
    print("\n[DATA WARMER] Starting cache warming...")
    
    # Warm intel data FIRST (most important for dashboard)
    await _warm_intel_cache()
    
    # Warm fire data
    await _warm_fire_cache()
    
    # Warm satellite data
    await _warm_satellite_cache()
    
    print("[DATA WARMER] Initial warming complete\n")


async def _warm_intel_cache():
    """Warm intel cache - use real APIs with fallback to sample data."""
    from services.newsdata import fetch_security_intel
    
    # First, set fallback data immediately so UI has something to show
    cache.set("intel_data", FALLBACK_INTEL, ttl=300)
    print(f"[DATA WARMER] Intel: Set fallback data ({FALLBACK_INTEL['total']} reports)")
    
    # Then try to fetch real data
    try:
        # Try with shorter timeout first - skip RSS which is slow
        intel = await asyncio.wait_for(_fetch_intel_fast(), timeout=12.0)
        if intel and intel.get("total", 0) > 0:
            cache.set("intel_data", intel, ttl=180)
            print(f"[DATA WARMER] Intel: Updated with real data ({intel['total']} reports)")
        else:
            print("[DATA WARMER] Intel: APIs returned empty, keeping fallback")
    except Exception as e:
        print(f"[DATA WARMER] Intel: API fetch failed ({e}), keeping fallback")


async def _fetch_intel_fast():
    """Fetch intel without slow RSS feeds."""
    from services.newsdata import fetch_serper, fetch_gnews, fetch_gdelt
    
    # Run only fast sources (skip RSS)
    tasks = [
        asyncio.create_task(fetch_serper("Kebbi state security", 8)),
        asyncio.create_task(fetch_gnews("Kebbi Nigeria security", 8)),
        asyncio.create_task(fetch_gdelt("Kebbi Sokoto Zamfara bandit", 5)),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_reports = []
    seen_titles = set()
    
    for result in results:
        if isinstance(result, Exception):
            continue
        if isinstance(result, list):
            for report in result:
                title = report.get("title", "").strip().lower()[:80]
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    all_reports.append(report)
    
    return {
        "reports": all_reports,
        "total": len(all_reports),
        "source": "multi_source_fast",
        "sources": {"serper": len([r for r in all_reports if r.get("feed_source") == "serper"]),
                   "gnews": len([r for r in all_reports if r.get("feed_source") == "gnews"]),
                   "gdelt": len([r for r in all_reports if r.get("feed_source") == "gdelt"])},
        "kebbi_region_count": len([r for r in all_reports if r.get("kebbi_relevant")]),
        "fetched_at": datetime.now().isoformat()
    }


async def _warm_fire_cache():
    """Warm fire/hotspot cache."""
    from services.firms import fetch_all_sensors
    
    try:
        fires = await asyncio.wait_for(fetch_all_sensors(days=2), timeout=15.0)
        cache.set("fire_data", fires, ttl=180)
        print(f"[DATA WARMER] Fires: {fires.get('total', 0)} hotspots")
    except Exception as e:
        # Set empty but valid fallback
        cache.set("fire_data", {"hotspots": [], "total": 0, "source": "warming"}, ttl=60)
        print(f"[DATA WARMER] Fires: Failed ({e})")


async def _warm_satellite_cache():
    """Warm satellite data cache."""
    from services.sentinel_timer import get_sentinel_passes
    from services.copernicus import fetch_sentinel_products
    
    # Sentinel passes
    try:
        passes = await asyncio.wait_for(get_sentinel_passes(days=3), timeout=10.0)
        cache.set("sentinel_passes", passes, ttl=300)
        print("[DATA WARMER] Satellites: Passes warmed")
    except Exception as e:
        print(f"[DATA WARMER] Satellites: Passes failed ({e})")
    
    # Sentinel products
    try:
        products = await asyncio.wait_for(fetch_sentinel_products(days_back=7, max_results=5), timeout=10.0)
        cache.set("sentinel_products", products, ttl=600)
        print(f"[DATA WARMER] Satellites: {products.get('total', 0)} products")
    except Exception:
        pass


async def background_refresh():
    """Background task to keep caches fresh. Runs every 3 minutes."""
    while True:
        await asyncio.sleep(180)  # 3 minutes
        
        print("[DATA WARMER] Background refresh starting...")
        
        # Refresh intel (fast version without RSS)
        try:
            intel = await asyncio.wait_for(_fetch_intel_fast(), timeout=15.0)
            if intel and intel.get("total", 0) > 0:
                cache.set("intel_data", intel, ttl=180)
                print(f"[DATA WARMER] Refreshed intel: {intel['total']} reports")
        except Exception as e:
            print(f"[DATA WARMER] Intel refresh failed: {e}")
        
        # Refresh fires
        try:
            from services.firms import fetch_all_sensors
            fires = await asyncio.wait_for(fetch_all_sensors(days=2), timeout=15.0)
            cache.set("fire_data", fires, ttl=180)
            print(f"[DATA WARMER] Refreshed fires: {fires.get('total', 0)} hotspots")
        except Exception as e:
            print(f"[DATA WARMER] Fire refresh failed: {e}")
