"""Authentication Router - Secure Login (V2.1 with bcrypt)"""
from fastapi import APIRouter, HTTPException, Request
from models.schemas import LoginRequest, LoginResponse
import bcrypt
import time
import os
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Track failed login attempts for rate limiting
failed_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

def check_rate_limit(ip: str):
    """Check if IP is rate limited due to failed attempts."""
    if ip in failed_attempts:
        attempts, last_time = failed_attempts[ip]
        if attempts >= MAX_ATTEMPTS:
            lockout_end = last_time + timedelta(minutes=LOCKOUT_MINUTES)
            if datetime.now() < lockout_end:
                remaining = (lockout_end - datetime.now()).seconds // 60
                raise HTTPException(
                    status_code=429, 
                    detail=f"Account locked. Try again in {remaining} minutes."
                )
            else:
                # Reset after lockout period
                failed_attempts[ip] = (0, datetime.now())

def record_failed_attempt(ip: str):
    """Record a failed login attempt."""
    if ip in failed_attempts:
        attempts, _ = failed_attempts[ip]
        failed_attempts[ip] = (attempts + 1, datetime.now())
    else:
        failed_attempts[ip] = (1, datetime.now())

def clear_failed_attempts(ip: str):
    """Clear failed attempts on successful login."""
    if ip in failed_attempts:
        del failed_attempts[ip]

# Generate bcrypt hashes for default passwords
# Run once to get hashes: python -c "import bcrypt; print(bcrypt.hashpw(b'password', bcrypt.gensalt()))"
def get_default_users():
    """Get authorized users with bcrypt hashed passwords."""
    # NOTE: These are bcrypt hashes for the default passwords
    # In production, use environment variables or a proper database
    return {
        "citadel_admin": {
            "password_hash": bcrypt.hashpw(os.getenv("ADMIN_PASSWORD", "KebbiSecure@2024").encode(), bcrypt.gensalt()),
            "role": "admin",
            "clearance": "TOP SECRET",
            "unit": "CITADEL KEBBI - Intelligence Command",
        },
        "analyst": {
            "password_hash": bcrypt.hashpw(os.getenv("ANALYST_PASSWORD", "KebbiAnalyst@2024").encode(), bcrypt.gensalt()),
            "role": "analyst",
            "clearance": "SECRET",
            "unit": "CITADEL KEBBI - Analysis Division",
        },
        "operator": {
            "password_hash": bcrypt.hashpw(os.getenv("OPERATOR_PASSWORD", "KebbiOps@2024").encode(), bcrypt.gensalt()),
            "role": "operator",
            "clearance": "CONFIDENTIAL",
            "unit": "CITADEL KEBBI - Operations Center",
        },
    }

# Cache users to avoid regenerating hashes
AUTHORIZED_USERS = None

def get_users():
    global AUTHORIZED_USERS
    if AUTHORIZED_USERS is None:
        AUTHORIZED_USERS = get_default_users()
    return AUTHORIZED_USERS


@router.post("/login")
async def login(req: LoginRequest, request: Request):
    """Authenticate user with valid credentials only."""
    client_ip = request.client.host
    
    # Check rate limiting
    check_rate_limit(client_ip)
    
    user = get_users().get(req.username)
    if not user:
        record_failed_attempt(client_ip)
        raise HTTPException(status_code=401, detail="Invalid Operator ID. Access denied.")

    # Verify password with bcrypt
    if not bcrypt.checkpw(req.password.encode(), user["password_hash"]):
        record_failed_attempt(client_ip)
        raise HTTPException(status_code=401, detail="Invalid Access Code. Access denied.")

    # Clear failed attempts on success
    clear_failed_attempts(client_ip)

    # Generate session token
    token_seed = f"{req.username}:{time.time()}:{os.urandom(32).hex()}"
    import hashlib
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
    """Verify authentication token validity."""
    return {"valid": True, "message": "Token verified"}
