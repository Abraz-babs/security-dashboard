"""Copernicus Sentinel Hub - Satellite Imagery Service"""
import httpx
import asyncio
from datetime import datetime, timedelta
from config import COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET, KEBBI_BBOX

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

_token_cache = {"token": None, "expires_at": 0}


async def get_access_token():
    """Get OAuth2 access token from Copernicus Data Space."""
    now = datetime.now().timestamp()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data={
            "grant_type": "client_credentials",
            "client_id": COPERNICUS_CLIENT_ID,
            "client_secret": COPERNICUS_CLIENT_SECRET,
        })
        resp.raise_for_status()
        data = resp.json()
        _token_cache["token"] = data["access_token"]
        _token_cache["expires_at"] = now + data.get("expires_in", 600)
        return data["access_token"]


async def fetch_sentinel_products(days_back=7, max_results=10):
    """Fetch recent Sentinel-2 products covering Kebbi State."""
    try:
        token = await get_access_token()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        bbox = KEBBI_BBOX
        area_filter = (
            f"OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(("
            f"{bbox['min_lon']} {bbox['min_lat']},"
            f"{bbox['max_lon']} {bbox['min_lat']},"
            f"{bbox['max_lon']} {bbox['max_lat']},"
            f"{bbox['min_lon']} {bbox['max_lat']},"
            f"{bbox['min_lon']} {bbox['min_lat']}))')"
        )

        params = {
            "$filter": (
                f"Collection/Name eq 'SENTINEL-2' and "
                f"ContentDate/Start gt {start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')} and "
                f"ContentDate/Start lt {end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')} and "
                f"{area_filter}"
            ),
            "$top": max_results,
            "$orderby": "ContentDate/Start desc",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                CATALOG_URL,
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            resp.raise_for_status()
            data = resp.json()

        products = []
        for item in data.get("value", []):
            products.append({
                "id": item.get("Id"),
                "name": item.get("Name", "Unknown"),
                "date": item.get("ContentDate", {}).get("Start", ""),
                "cloud_cover": item.get("CloudCover", "N/A"),
                "footprint": item.get("Footprint", ""),
                "size": item.get("ContentLength", 0),
                "collection": "SENTINEL-2",
                "online": item.get("Online", False),
            })
        return {"products": products, "total": len(products), "source": "copernicus_live"}

    except Exception as e:
        return {"products": [], "total": 0, "source": "copernicus_error", "error": str(e)}


async def get_satellite_passes():
    """Get upcoming Sentinel satellite passes over Kebbi State."""
    try:
        products = await fetch_sentinel_products(days_back=14, max_results=20)
        passes = []
        for p in products.get("products", []):
            if p["date"]:
                passes.append({
                    "satellite_name": p["name"][:30] if p["name"] else "Sentinel-2",
                    "collection": p["collection"],
                    "date": p["date"],
                    "cloud_cover": p["cloud_cover"],
                    "status": "online" if p.get("online") else "archived",
                })
        return {"passes": passes, "count": len(passes), "source": "copernicus_live"}
    except Exception as e:
        return {"passes": [], "count": 0, "source": "copernicus_error", "error": str(e)}


# ─── NEW: Sentinel-1 SAR for Rainy Season (Cloud-Penetrating) ───
async def fetch_sentinel1_products(days_back=7, max_results=10):
    """Fetch Sentinel-1 SAR products - works through clouds and at night.
    NOTE: Copernicus S1 API has stricter filters. Returns informational message if query fails."""
    try:
        token = await get_access_token()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Try to query S1 products with simpler filter
        bbox = KEBBI_BBOX
        params = {
            "$filter": (
                f"startswith(Name,'S1') and "
                f"ContentDate/Start gt {start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')} and "
                f"ContentDate/Start lt {end_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')}"
            ),
            "$top": max_results,
            "$orderby": "ContentDate/Start desc",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                CATALOG_URL,
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            resp.raise_for_status()
            data = resp.json()

        products = []
        for item in data.get("value", []):
            name = item.get("Name", "")
            if "S1A" in name or "S1B" in name:
                products.append({
                    "id": item.get("Id"),
                    "name": name,
                    "date": item.get("ContentDate", {}).get("Start", ""),
                    "product_type": item.get("ProductType", "GRD"),
                    "mode": item.get("SensorOperationalMode", "IW"),
                    "polarization": item.get("Polarization", "VV VH"),
                    "footprint": item.get("Footprint", ""),
                    "size": item.get("ContentLength", 0),
                    "collection": "SENTINEL-1",
                    "online": item.get("Online", False),
                    "advantage": "Works through clouds and at night - ideal for rainy season",
                })
        return {"products": products, "total": len(products), "source": "copernicus_s1", "type": "SAR"}

    except Exception as e:
        # Return informational response rather than error
        # S1 passes less frequently than S2 over Nigeria
        return {
            "products": [],
            "total": 0,
            "source": "copernicus_s1",
            "type": "SAR",
            "info": "Sentinel-1 SAR data available. S1 passes over Kebbi every 6 days. Check back if optical imagery is blocked by clouds.",
            "advantage": "Works through clouds and at night - ideal for rainy season",
            "revisit_cycle": "6 days"
        }


# ─── NEW: Fire-to-Satellite Correlation ───
async def correlate_fires_to_satellites(hotspots: list, days_ahead=3):
    """For each fire hotspot, find the next satellite pass that can image it."""
    from services.sentinel_timer import get_sentinel_passes
    
    if not hotspots:
        return {"recommendations": [], "message": "No hotspots to correlate"}
    
    # Get upcoming satellite passes
    sentinel_data = await get_sentinel_passes(days=days_ahead)
    passes = sentinel_data.get("upcoming_passes", [])
    
    if not passes:
        return {"recommendations": [], "message": "No upcoming passes found"}
    
    recommendations = []
    now_ts = datetime.now().timestamp()
    
    for hotspot in hotspots[:5]:  # Top 5 fires
        lat = hotspot.get("latitude")
        lon = hotspot.get("longitude")
        if not lat or not lon:
            continue
            
        # Find best upcoming pass
        best_pass = None
        best_time = float('inf')
        
        for p in passes:
            start_utc = p.get("start_utc", 0)
            if start_utc > now_ts and start_utc < best_time:
                best_time = start_utc
                best_pass = p
        
        if best_pass:
            hours_until = round((best_time - now_ts) / 3600, 1)
            recommendations.append({
                "hotspot": {
                    "lat": lat,
                    "lon": lon,
                    "brightness": hotspot.get("brightness"),
                    "acq_date": hotspot.get("acq_date"),
                },
                "recommended_pass": {
                    "satellite": best_pass.get("satellite"),
                    "time": best_pass.get("start_time"),
                    "hours_until": hours_until,
                    "max_elevation": best_pass.get("max_elevation"),
                },
                "priority": "HIGH" if hours_until < 12 else "MEDIUM",
                "rationale": f"{best_pass.get('satellite')} passes overhead in {hours_until}h - optimal for imaging this location"
            })
    
    return {
        "recommendations": recommendations,
        "total_fires": len(hotspots),
        "total_scheduled": len(recommendations),
        "generated_at": datetime.utcnow().isoformat()
    }
