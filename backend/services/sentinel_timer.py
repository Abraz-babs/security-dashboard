"""Sentinel Orbit Timer — Cached, Fast (V2.1)
Predicts Sentinel satellite passes over Kebbi State.
Uses backend cache to avoid repeated N2YO API calls.
"""
import httpx
from datetime import datetime
from config import N2YO_API_KEY, KEBBI_CENTER
from services import cache

N2YO_BASE = "https://api.n2yo.com/rest/v1/satellite"

SENTINEL_SATS = {
    "SENTINEL-2A": 40697,
    "SENTINEL-2B": 42063,
    "SENTINEL-1A": 39634,
    "SENTINEL-1B": 41456,
}


async def get_sentinel_passes(days=5):
    """Get predicted passes for Sentinel satellites — CACHED for 5 minutes."""
    # Check cache first (sentinel data doesn't change fast)
    cached = cache.get("sentinel_passes")
    if cached:
        # Recalculate seconds_until for accuracy
        now_ts = datetime.now().timestamp()
        if cached.get("next_pass"):
            cached["next_pass"]["seconds_until"] = int(cached["next_pass"]["start_utc"] - now_ts)
        for p in cached.get("upcoming_passes", []):
            p["seconds_until"] = int(p["start_utc"] - now_ts)
        return cached

    lat, lon = KEBBI_CENTER["lat"], KEBBI_CENTER["lon"]
    results = {}

    async with httpx.AsyncClient(timeout=12.0) as client:
        for name, norad_id in SENTINEL_SATS.items():
            try:
                # Get visual passes
                url = f"{N2YO_BASE}/visualpasses/{norad_id}/{lat}/{lon}/0/{days}/300"
                resp = await client.get(url, params={"apiKey": N2YO_API_KEY})
                resp.raise_for_status()
                data = resp.json()

                passes = []
                for p in data.get("passes", []):
                    start_utc = p.get("startUTC", 0)
                    end_utc = p.get("endUTC", 0)
                    passes.append({
                        "start_utc": start_utc,
                        "end_utc": end_utc,
                        "start_time": datetime.fromtimestamp(start_utc).isoformat() if start_utc else None,
                        "end_time": datetime.fromtimestamp(end_utc).isoformat() if end_utc else None,
                        "max_elevation": p.get("maxEl", 0),
                        "duration_seconds": end_utc - start_utc if end_utc and start_utc else 0,
                        "start_azimuth": p.get("startAz", 0),
                        "start_azimuth_compass": p.get("startAzCompass", ""),
                    })

                # Get current position (single call, no batch)
                position = None
                try:
                    pos_url = f"{N2YO_BASE}/positions/{norad_id}/{lat}/{lon}/0/1"
                    pos_resp = await client.get(pos_url, params={"apiKey": N2YO_API_KEY})
                    pos_data = pos_resp.json()
                    if pos_data.get("positions"):
                        pos = pos_data["positions"][0]
                        position = {
                            "latitude": pos.get("satlatitude"),
                            "longitude": pos.get("satlongitude"),
                            "altitude_km": pos.get("sataltitude"),
                        }
                except Exception:
                    pass

                results[name] = {
                    "norad_id": norad_id,
                    "name": name,
                    "passes": passes,
                    "pass_count": len(passes),
                    "position": position,
                    "next_pass": passes[0] if passes else None,
                    "active": True,
                }
            except Exception as e:
                results[name] = {
                    "norad_id": norad_id,
                    "name": name,
                    "passes": [],
                    "pass_count": 0,
                    "position": None,
                    "next_pass": None,
                    "active": True,
                    "error": str(e),
                }

    # Calculate time to next pass
    now_ts = datetime.now().timestamp()
    upcoming = []
    for name, sat in results.items():
        for p in sat["passes"]:
            if p["start_utc"] > now_ts:
                upcoming.append({
                    "satellite": name,
                    "norad_id": sat["norad_id"],
                    "start_utc": p["start_utc"],
                    "seconds_until": int(p["start_utc"] - now_ts),
                    "start_time": p["start_time"],
                    "max_elevation": p["max_elevation"],
                })
                break

    upcoming.sort(key=lambda x: x["seconds_until"])

    result = {
        "sentinels": results,
        "next_pass": upcoming[0] if upcoming else None,
        "upcoming_passes": upcoming,
        "timestamp": datetime.now().isoformat(),
    }

    # Cache for 5 minutes (satellite orbits are predictable)
    cache.set("sentinel_passes", result, ttl=300)
    return result
