"""N2YO - Satellite Orbit Tracking Service"""
import httpx
from config import N2YO_API_KEY, KEBBI_CENTER

N2YO_BASE = "https://api.n2yo.com/rest/v1/satellite"

# Key reconnaissance/observation satellites
TRACKED_SATELLITES = [
    {"norad_id": 25544, "name": "ISS (ZARYA)"},
    {"norad_id": 40069, "name": "SENTINEL-2A"},
    {"norad_id": 42063, "name": "SENTINEL-2B"},
    {"norad_id": 33591, "name": "NOAA-19"},
    {"norad_id": 43013, "name": "NOAA-20 (JPSS-1)"},
    {"norad_id": 27424, "name": "TERRA (EOS AM-1)"},
    {"norad_id": 27386, "name": "AQUA (EOS PM-1)"},
    {"norad_id": 49260, "name": "LANDSAT 9"},
    {"norad_id": 39084, "name": "LANDSAT 8"},
    {"norad_id": 43602, "name": "ICESAT-2"},
]


async def get_satellite_positions(norad_id=25544):
    """Get current position of a satellite by NORAD ID."""
    try:
        url = (
            f"{N2YO_BASE}/positions/{norad_id}/"
            f"{KEBBI_CENTER['lat']}/{KEBBI_CENTER['lon']}/0/1"
            f"&apiKey={N2YO_API_KEY}"
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        info = data.get("info", {})
        positions = data.get("positions", [])

        return {
            "satellite": {
                "name": info.get("satname", "Unknown"),
                "norad_id": info.get("satid", norad_id),
                "intl_designator": info.get("transactionscount", ""),
            },
            "positions": [{
                "latitude": p.get("satlatitude"),
                "longitude": p.get("satlongitude"),
                "altitude_km": p.get("sataltitude"),
                "azimuth": p.get("azimuth"),
                "elevation": p.get("elevation"),
                "ra": p.get("ra"),
                "dec": p.get("dec"),
                "timestamp": p.get("timestamp"),
            } for p in positions],
            "source": "n2yo_live"
        }
    except Exception as e:
        return {"satellite": {"name": "Unknown", "norad_id": norad_id}, "positions": [], "source": "n2yo_error", "error": str(e)}


async def get_visual_passes(norad_id=25544, days=5, min_visibility=60):
    """Get upcoming visual passes for a satellite over Kebbi State."""
    try:
        url = (
            f"{N2YO_BASE}/visualpasses/{norad_id}/"
            f"{KEBBI_CENTER['lat']}/{KEBBI_CENTER['lon']}/0/{days}/{min_visibility}"
            f"&apiKey={N2YO_API_KEY}"
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        info = data.get("info", {})
        passes = data.get("passes", [])

        return {
            "satellite": info.get("satname", "Unknown"),
            "norad_id": info.get("satid", norad_id),
            "passes_count": info.get("passescount", 0),
            "passes": [{
                "start_utc": p.get("startUTC"),
                "start_azimuth": p.get("startAz"),
                "start_azimuth_compass": p.get("startAzCompass"),
                "start_elevation": p.get("startEl"),
                "max_utc": p.get("maxUTC"),
                "max_azimuth": p.get("maxAz"),
                "max_elevation": p.get("maxEl"),
                "end_utc": p.get("endUTC"),
                "end_azimuth": p.get("endAz"),
                "end_elevation": p.get("endEl"),
                "magnitude": p.get("mag"),
                "duration_seconds": p.get("duration"),
            } for p in passes],
            "source": "n2yo_live"
        }
    except Exception as e:
        return {"satellite": "Unknown", "norad_id": norad_id, "passes_count": 0, "passes": [], "source": "n2yo_error", "error": str(e)}


async def get_above_kebbi(category=0, search_radius=70):
    """Get all satellites currently above Kebbi State region."""
    try:
        url = (
            f"{N2YO_BASE}/above/"
            f"{KEBBI_CENTER['lat']}/{KEBBI_CENTER['lon']}/0/{search_radius}/{category}"
            f"&apiKey={N2YO_API_KEY}"
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        info = data.get("info", {})
        above = data.get("above", [])

        return {
            "category": info.get("category", "All"),
            "satellites_count": info.get("satcount", 0),
            "satellites": [{
                "name": s.get("satname"),
                "norad_id": s.get("satid"),
                "intl_designator": s.get("intDesignator"),
                "launch_date": s.get("launchDate"),
                "latitude": s.get("satlat"),
                "longitude": s.get("satlng"),
                "altitude_km": s.get("satalt"),
            } for s in above[:50]],  # Cap at 50 for performance
            "source": "n2yo_live"
        }
    except Exception as e:
        return {"category": "All", "satellites_count": 0, "satellites": [], "source": "n2yo_error", "error": str(e)}


async def get_all_tracked_positions():
    """Get positions of all tracked reconnaissance satellites."""
    results = []
    for sat in TRACKED_SATELLITES:
        pos = await get_satellite_positions(sat["norad_id"])
        if pos.get("positions"):
            results.append({
                "name": sat["name"],
                "norad_id": sat["norad_id"],
                "position": pos["positions"][0] if pos["positions"] else None,
                "source": pos["source"]
            })
    return {"tracked_satellites": results, "total": len(results), "source": "n2yo_live"}
