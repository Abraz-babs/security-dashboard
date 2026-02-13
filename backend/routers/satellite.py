"""Satellite Router - Copernicus, FIRMS, N2YO, Sentinel Timer (V2)"""
from fastapi import APIRouter
from services.copernicus import (
    fetch_sentinel_products, get_satellite_passes,
    fetch_sentinel1_products, correlate_fires_to_satellites
)
from services.firms import fetch_fire_hotspots, fetch_all_sensors
from services.n2yo import (
    get_satellite_positions, get_visual_passes,
    get_above_kebbi, get_all_tracked_positions
)
from services.sentinel_timer import get_sentinel_passes

router = APIRouter(prefix="/api/satellite", tags=["satellite"])


# ──── Copernicus Endpoints ────
@router.get("/copernicus/products")
async def copernicus_products(days: int = 7, limit: int = 10):
    """Get recent Sentinel-2 products over Kebbi State."""
    return await fetch_sentinel_products(days_back=days, max_results=limit)


@router.get("/copernicus/passes")
async def copernicus_passes():
    """Get Sentinel satellite pass schedule."""
    return await get_satellite_passes()


# ──── NASA FIRMS Endpoints ────
@router.get("/firms/hotspots")
async def firms_hotspots(sensor: str = "VIIRS_SNPP_NRT", days: int = 2):
    """Get fire/thermal hotspot data for Kebbi State."""
    return await fetch_fire_hotspots(source=sensor, days=days)


@router.get("/firms/all")
async def firms_all_sensors(days: int = 2):
    """Get combined fire data from all FIRMS sensors."""
    return await fetch_all_sensors(days=days)


# ──── N2YO Endpoints ────
@router.get("/n2yo/position/{norad_id}")
async def satellite_position(norad_id: int):
    """Get current position of a satellite by NORAD ID."""
    return await get_satellite_positions(norad_id)


@router.get("/n2yo/passes/{norad_id}")
async def satellite_passes(norad_id: int, days: int = 5):
    """Get visual passes for a satellite over Kebbi."""
    return await get_visual_passes(norad_id, days=days)


@router.get("/n2yo/above")
async def satellites_above(category: int = 0, radius: int = 70):
    """Get satellites currently above Kebbi State."""
    return await get_above_kebbi(category=category, search_radius=radius)


@router.get("/n2yo/tracked")
async def tracked_satellites():
    """Get positions of all tracked reconnaissance satellites."""
    return await get_all_tracked_positions()


# ──── Sentinel Timer ────
@router.get("/sentinel/passes")
async def sentinel_pass_schedule(days: int = 5):
    """Get next pass predictions for all Sentinel satellites over Kebbi State."""
    return await get_sentinel_passes(days=days)


# ──── NEW: SAR (Rainy Season) Endpoints ────
@router.get("/copernicus/sar")
async def sentinel1_sar_products(days: int = 7, limit: int = 10):
    """Get Sentinel-1 SAR products - works through clouds and at night.
    Use this during rainy season when optical imagery is blocked."""
    return await fetch_sentinel1_products(days_back=days, max_results=limit)


@router.get("/correlate/fires")
async def fire_satellite_correlation(days: int = 3):
    """For each detected fire, find the next satellite pass that can image it.
    Returns imaging recommendations with priority levels."""
    from services.firms import fetch_all_sensors
    fires = await fetch_all_sensors(days=2)
    hotspots = fires.get("hotspots", [])
    return await correlate_fires_to_satellites(hotspots, days_ahead=days)
