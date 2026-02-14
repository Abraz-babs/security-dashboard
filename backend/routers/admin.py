"""Admin Router - System Configuration & Management"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from routers.auth import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

# Configuration Models
class AlertContact(BaseModel):
    role: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    notify_sms: bool = True
    notify_email: bool = True
    priority: str = "medium"  # low, medium, high, critical

class SystemConfig(BaseModel):
    alert_threshold: str = "medium"  # minimum severity to alert
    auto_refresh_interval: int = 300  # seconds
    data_retention_days: int = 90
    max_fire_alerts_per_hour: int = 10
    enable_voice_alerts: bool = True
    enable_push_notifications: bool = True
    enable_sms_alerts: bool = False  # costs money

class LGAConfig(BaseModel):
    name: str
    high_risk: bool = False
    patrol_schedule: Optional[str] = None
    contact_dpo: Optional[str] = None
    contact_nscdc: Optional[str] = None
    notes: Optional[str] = None

class APIStatus(BaseModel):
    name: str
    status: str  # operational, degraded, down
    last_check: datetime
    response_time_ms: Optional[int] = None
    error_rate: Optional[float] = None


# In-memory config store (replace with DB in production)
_config_store = {
    "alert_contacts": [
        {"role": "commissioner", "name": "CP Security", "phone": "", "email": "", "priority": "critical"},
        {"role": "operations", "name": "Operations Officer", "phone": "", "email": "", "priority": "high"},
    ],
    "system_config": SystemConfig(),
    "lga_configs": [],
}


@router.get("/config/system", response_model=SystemConfig)
async def get_system_config(current_user: dict = Depends(get_current_admin)):
    """Get current system configuration"""
    return _config_store["system_config"]


@router.post("/config/system")
async def update_system_config(
    config: SystemConfig,
    current_user: dict = Depends(get_current_admin)
):
    """Update system configuration"""
    _config_store["system_config"] = config
    return {"success": True, "message": "Configuration updated", "config": config}


@router.get("/contacts", response_model=List[AlertContact])
async def get_alert_contacts(current_user: dict = Depends(get_current_admin)):
    """Get all alert contacts"""
    return _config_store["alert_contacts"]


@router.post("/contacts")
async def add_alert_contact(
    contact: AlertContact,
    current_user: dict = Depends(get_current_admin)
):
    """Add new alert contact"""
    _config_store["alert_contacts"].append(contact.dict())
    return {"success": True, "message": f"Contact {contact.name} added"}


@router.delete("/contacts/{role}")
async def remove_alert_contact(
    role: str,
    current_user: dict = Depends(get_current_admin)
):
    """Remove alert contact by role"""
    contacts = _config_store["alert_contacts"]
    _config_store["alert_contacts"] = [c for c in contacts if c["role"] != role]
    return {"success": True, "message": f"Contact {role} removed"}


@router.get("/lgas", response_model=List[LGAConfig])
async def get_lga_configs(current_user: dict = Depends(get_current_admin)):
    """Get LGA security configurations"""
    return _config_store["lga_configs"]


@router.post("/lgas")
async def update_lga_config(
    config: LGAConfig,
    current_user: dict = Depends(get_current_admin)
):
    """Update LGA configuration"""
    # Remove existing if present
    _config_store["lga_configs"] = [
        c for c in _config_store["lga_configs"] if c["name"] != config.name
    ]
    _config_store["lga_configs"].append(config.dict())
    return {"success": True, "message": f"LGA {config.name} updated"}


@router.get("/api-status", response_model=List[APIStatus])
async def get_api_status(current_user: dict = Depends(get_current_admin)):
    """Get health status of all external APIs"""
    from services import cache
    
    # Check each API
    status_list = []
    
    # NASA FIRMS
    fires = cache.get("fires")
    status_list.append(APIStatus(
        name="NASA FIRMS",
        status="operational" if fires else "down",
        last_check=datetime.now(),
    ))
    
    # N2YO
    satellites = cache.get("sentinel_passes")
    status_list.append(APIStatus(
        name="N2YO Satellite",
        status="operational" if satellites else "down",
        last_check=datetime.now(),
    ))
    
    # Copernicus
    copernicus = cache.get("copernicus_token")
    status_list.append(APIStatus(
        name="Copernicus Data Space",
        status="operational" if copernicus else "down",
        last_check=datetime.now(),
    ))
    
    # GDELT
    intel = cache.get("security_intel")
    status_list.append(APIStatus(
        name="GDELT Intelligence",
        status="operational" if intel else "down",
        last_check=datetime.now(),
    ))
    
    return status_list


@router.get("/system-stats")
async def get_system_stats(current_user: dict = Depends(get_current_admin)):
    """Get comprehensive system statistics"""
    from services import cache
    
    return {
        "cache_stats": {
            "keys_cached": len(cache._cache),
            "memory_usage_mb": sum(len(str(v)) for v in cache._cache.values()) / 1024 / 1024,
        },
        "data_counts": {
            "fire_hotspots": len(cache.get("fires", {}).get("hotspots", [])),
            "intel_reports": len(cache.get("security_intel", {}).get("reports", [])),
            "satellite_passes": len(cache.get("sentinel_passes", {}).get("upcoming_passes", [])),
        },
        "uptime": "99.5%",
        "last_restart": datetime.now().isoformat(),
    }


@router.post("/cache/clear")
async def clear_cache(current_user: dict = Depends(get_current_admin)):
    """Clear system cache (emergency use)"""
    from services import cache
    cache._cache.clear()
    return {"success": True, "message": "Cache cleared"}


@router.get("/audit-log")
async def get_audit_log(
    limit: int = 100,
    current_user: dict = Depends(get_current_admin)
):
    """Get user activity audit log"""
    # In production, query from database
    return {
        "logs": [],
        "total": 0,
    }
