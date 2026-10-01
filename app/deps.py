import secrets

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .db import get_db
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(401, "Missing bearer token")
    try:
        payload = decode_token(creds.credentials)
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    return {"id": payload["sub"], "user_type": payload["user_type"]}


def admin_only(x_admin_key: str = Header(default="")) -> None:
    """Admin endpoints are protected by a shared secret (ADMIN_API_KEY) sent as X-Admin-Key."""
    if not settings.admin_api_key:
        raise HTTPException(503, "Admin API is not configured")
    if not secrets.compare_digest(x_admin_key.encode(), settings.admin_api_key.encode()):
        raise HTTPException(403, "Invalid admin key")


def verifier_user(user: dict = Depends(current_user)) -> dict:
    if user["user_type"] not in ("volunteer", "ngo"):
        raise HTTPException(403, "Only volunteers and NGOs can do this")
    return user


def responder_user(user: dict = Depends(current_user)) -> dict:
    """Who may see and handle SOS alerts: volunteers and approved organizations only."""
    if user["user_type"] == "volunteer":
        return user
    if user["user_type"] == "ngo":
        ngo = get_db().table("ngos").select("is_verified").eq("user_id", user["id"]).execute().data
        if ngo and ngo[0]["is_verified"]:
            return user
        raise HTTPException(403, "Your organization must be approved before it can see SOS alerts")
    raise HTTPException(403, "Only volunteers and approved organizations can see SOS alerts")
