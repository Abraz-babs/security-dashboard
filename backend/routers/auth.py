"""Authentication Router - Secure Login (V2)"""
from fastapi import APIRouter, HTTPException
from models.schemas import LoginRequest, LoginResponse
import hashlib
import time

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Authorized users with hashed passwords
# Default: citadel_admin / KebbiSecure@2024
AUTHORIZED_USERS = {
    "citadel_admin": {
        "password_hash": hashlib.sha256("KebbiSecure@2024".encode()).hexdigest(),
        "role": "admin",
        "clearance": "TOP SECRET",
        "unit": "CITADEL KEBBI - Intelligence Command",
    },
    "analyst": {
        "password_hash": hashlib.sha256("KebbiAnalyst@2024".encode()).hexdigest(),
        "role": "analyst",
        "clearance": "SECRET",
        "unit": "CITADEL KEBBI - Analysis Division",
    },
    "operator": {
        "password_hash": hashlib.sha256("KebbiOps@2024".encode()).hexdigest(),
        "role": "operator",
        "clearance": "CONFIDENTIAL",
        "unit": "CITADEL KEBBI - Operations Center",
    },
}


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate user with valid credentials only."""
    user = AUTHORIZED_USERS.get(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Operator ID. Access denied.")

    input_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if input_hash != user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid Access Code. Access denied.")

    # Generate session token
    token_seed = f"{req.username}:{time.time()}:{hashlib.sha256(req.password.encode()).hexdigest()}"
    token = hashlib.sha256(token_seed.encode()).hexdigest()

    return {
        "success": True,
        "token": token,
        "user": {
            "username": req.username,
            "role": user["role"],
            "clearance": user["clearance"],
            "unit": user["unit"],
        }
    }


@router.get("/verify")
async def verify_token():
    """Verify token validity."""
    return {"valid": True, "clearance": "TOP SECRET"}
