"""NASA FIRMS - Fire Information for Resource Management System"""
import httpx
from datetime import datetime
from config import NASA_FIRMS_KEY, KEBBI_BBOX

FIRMS_BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"


async def fetch_fire_hotspots(source="VIIRS_SNPP_NRT", days=2):
    """Fetch active fire/thermal anomaly data for Kebbi State from NASA FIRMS."""
    try:
        bbox = KEBBI_BBOX
        area = f"{bbox['min_lon']},{bbox['min_lat']},{bbox['max_lon']},{bbox['max_lat']}"
        url = f"{FIRMS_BASE}/{NASA_FIRMS_KEY}/{source}/{area}/{days}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        lines = resp.text.strip().split("\n")
        if len(lines) < 2:
            return {"hotspots": [], "total": 0, "source": "firms_live", "note": "No active fires detected"}

        headers = lines[0].split(",")
        hotspots = []

        for line in lines[1:]:
            values = line.split(",")
            if len(values) < len(headers):
                continue
            row = dict(zip(headers, values))
            try:
                hotspot = {
                    "latitude": float(row.get("latitude", 0)),
                    "longitude": float(row.get("longitude", 0)),
                    "brightness": float(row.get("bright_ti4", row.get("brightness", 0))),
                    "confidence": row.get("confidence", "nominal"),
                    "acq_date": row.get("acq_date", ""),
                    "acq_time": row.get("acq_time", ""),
                    "satellite": row.get("satellite", source),
                    "frp": float(row.get("frp", 0)) if row.get("frp") else None,
                    "daynight": row.get("daynight", ""),
                    "scan": float(row.get("scan", 0)) if row.get("scan") else None,
                    "track": float(row.get("track", 0)) if row.get("track") else None,
                }
                # Only include points within Kebbi State bounds
                if (bbox["min_lat"] <= hotspot["latitude"] <= bbox["max_lat"] and
                    bbox["min_lon"] <= hotspot["longitude"] <= bbox["max_lon"]):
                    hotspots.append(hotspot)
            except (ValueError, TypeError):
                continue

        return {
            "hotspots": hotspots,
            "total": len(hotspots),
            "source": "firms_live",
            "query": {"area": area, "days": days, "sensor": source}
        }

    except Exception as e:
        return {"hotspots": [], "total": 0, "source": "firms_error", "error": str(e)}


async def fetch_all_sensors(days=2):
    """Fetch fire data from multiple FIRMS sensors."""
    sensors = ["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "MODIS_NRT"]
    all_hotspots = []
    errors = []

    for sensor in sensors:
        result = await fetch_fire_hotspots(source=sensor, days=days)
        if result.get("hotspots"):
            all_hotspots.extend(result["hotspots"])
        if result.get("error"):
            errors.append(f"{sensor}: {result['error']}")

    # Deduplicate by proximity (within ~0.01 degree)
    unique = []
    for h in all_hotspots:
        is_dup = False
        for u in unique:
            if abs(h["latitude"] - u["latitude"]) < 0.01 and abs(h["longitude"] - u["longitude"]) < 0.01:
                if h["brightness"] > u["brightness"]:
                    unique.remove(u)
                    unique.append(h)
                is_dup = True
                break
        if not is_dup:
            unique.append(h)

    return {
        "hotspots": unique,
        "total": len(unique),
        "sensors_queried": len(sensors),
        "source": "firms_multi_live",
        "errors": errors if errors else None
    }
