import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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


def verifier_user(user: dict = Depends(current_user)) -> dict:
    if user["user_type"] not in ("volunteer", "ngo"):
        raise HTTPException(403, "Only volunteers and NGOs can do this")
    return user
