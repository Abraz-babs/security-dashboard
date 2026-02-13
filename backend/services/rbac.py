"""Role-Based Access Control (RBAC) for CITADEL KEBBI
Defines permissions for Admin, Analyst, and Operator roles.
"""
from enum import Enum
from functools import wraps
from fastapi import HTTPException, Request

class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    OPERATOR = "operator"

# Permission definitions
PERMISSIONS = {
    Role.ADMIN: {
        "can_view_dashboard",
        "can_view_satellite",
        "can_view_intel",
        "can_view_analytics",
        "can_view_sitrep",
        "can_view_admin",
        "can_manage_users",
        "can_manage_settings",
        "can_view_logs",
        "can_export_data",
        "can_trigger_analysis",
        "can_send_alerts",
    },
    Role.ANALYST: {
        "can_view_dashboard",
        "can_view_satellite",
        "can_view_intel",
        "can_view_analytics",
        "can_view_sitrep",
        "can_export_data",
        "can_trigger_analysis",
    },
    Role.OPERATOR: {
        "can_view_dashboard",
        "can_view_satellite",
        "can_view_intel",
        "can_view_sitrep",
    },
}

# Menu access by role
MENU_ACCESS = {
    Role.ADMIN: [
        "dashboard", "satellite", "orbit", "intel", "chat", 
        "analysis", "sitrep", "analytics", "globe", "admin"
    ],
    Role.ANALYST: [
        "dashboard", "satellite", "orbit", "intel", "chat",
        "analysis", "sitrep", "analytics", "globe"
    ],
    Role.OPERATOR: [
        "dashboard", "satellite", "orbit", "intel", "sitrep", "globe"
    ],
}

# Feature access by role
FEATURE_ACCESS = {
    Role.ADMIN: {
        "satellite_tabs": ["imagery", "sar", "thermal"],
        "can_download_sitrep": True,
        "can_run_ai_analysis": True,
        "can_access_chatbot": True,
        "can_view_fire_correlation": True,
        "can_refresh_data": True,
    },
    Role.ANALYST: {
        "satellite_tabs": ["imagery", "sar", "thermal"],
        "can_download_sitrep": True,
        "can_run_ai_analysis": True,
        "can_access_chatbot": True,
        "can_view_fire_correlation": True,
        "can_refresh_data": True,
    },
    Role.OPERATOR: {
        "satellite_tabs": ["imagery", "thermal"],  # No SAR (too technical)
        "can_download_sitrep": False,
        "can_run_ai_analysis": False,
        "can_access_chatbot": True,
        "can_view_fire_correlation": True,
        "can_refresh_data": False,  # View only
    },
}


def has_permission(role: Role, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in PERMISSIONS.get(role, set())


def get_menu_items(role: Role) -> list:
    """Get accessible menu items for a role."""
    return MENU_ACCESS.get(role, ["dashboard"])


def get_feature_access(role: Role) -> dict:
    """Get feature access config for a role."""
    return FEATURE_ACCESS.get(role, {})


def require_permission(permission: str):
    """Decorator to require a specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get user role from request state (set by auth middleware)
            user_role = getattr(request.state, "user_role", None)
            if not user_role:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if not has_permission(Role(user_role), permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_permissions_summary(role: Role) -> dict:
    """Get a summary of user permissions for frontend."""
    return {
        "role": role.value,
        "menu_items": get_menu_items(role),
        "features": get_feature_access(role),
        "permissions": list(PERMISSIONS.get(role, set())),
    }
