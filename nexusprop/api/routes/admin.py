"""Admin authentication and operations routes.

Simple password-gate for the admin dashboard.
Token is base64(admin:{timestamp}:{secret_key}) stored in sessionStorage.
"""

from __future__ import annotations

import base64
import time

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from nexusprop.config.settings import get_settings

router = APIRouter()
settings = get_settings()


class AdminLoginRequest(BaseModel):
    key: str


class AdminLoginResponse(BaseModel):
    valid: bool
    token: str | None = None


class AdminVerifyResponse(BaseModel):
    valid: bool


def _make_token() -> str:
    """Create a simple admin session token."""
    raw = f"admin:{int(time.time())}:{settings.secret_key}"
    return base64.b64encode(raw.encode()).decode()


def _verify_token(token: str) -> bool:
    """Verify an admin session token."""
    try:
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.split(":")
        if len(parts) < 3:
            return False
        if parts[0] != "admin":
            return False
        if parts[2] != settings.secret_key:
            return False
        # Token valid for 24 hours
        issued = int(parts[1])
        if time.time() - issued > 86400:
            return False
        return True
    except Exception:
        return False


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(body: AdminLoginRequest):
    """Authenticate with the admin key and receive a session token."""
    if body.key != settings.admin_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return AdminLoginResponse(valid=True, token=_make_token())


@router.get("/verify", response_model=AdminVerifyResponse)
async def admin_verify(authorization: str = Header(default="")):
    """Verify an existing admin session token."""
    token = authorization.replace("Bearer ", "").strip()
    if not token or not _verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return AdminVerifyResponse(valid=True)
