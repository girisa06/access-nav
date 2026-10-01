from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from ..db import get_db
from ..deps import current_user
from ..security import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    user_type: Literal["user", "volunteer", "ngo"]
    name: Optional[str] = None
    organization_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def _auth_response(user: dict) -> dict:
    return {
        "user_id": user["id"],
        "email": user["email"],
        "user_type": user["user_type"],
        "token": create_token(user["id"], user["user_type"]),
    }


@router.post("/register")
def register(body: RegisterRequest):
    db = get_db()
    email = body.email.lower()

    if body.user_type == "volunteer" and not body.name:
        raise HTTPException(400, "name is required for volunteers")
    if body.user_type == "ngo" and not body.organization_name:
        raise HTTPException(400, "organization_name is required for NGOs")

    if db.table("users").select("id").eq("email", email).execute().data:
        raise HTTPException(409, "Email already registered")

    user = (
        db.table("users")
        .insert(
            {
                "email": email,
                "password_hash": hash_password(body.password),
                "user_type": body.user_type,
            }
        )
        .execute()
        .data[0]
    )

    if body.user_type == "volunteer":
        db.table("volunteers").insert({"user_id": user["id"], "name": body.name}).execute()
    elif body.user_type == "ngo":
        db.table("ngos").insert(
            {"user_id": user["id"], "organization_name": body.organization_name}
        ).execute()

    return _auth_response(user)


@router.get("/me")
def me(user: dict = Depends(current_user)):
    """Current account, including whether an organization has been approved."""
    db = get_db()
    row = db.table("users").select("id, email, user_type").eq("id", user["id"]).execute().data
    if not row:
        raise HTTPException(401, "Account no longer exists")
    out = {"user_id": row[0]["id"], "email": row[0]["email"], "user_type": row[0]["user_type"]}
    if row[0]["user_type"] == "ngo":
        ngo = db.table("ngos").select("organization_name, is_verified").eq("user_id", user["id"]).execute().data
        out["organization_name"] = ngo[0]["organization_name"] if ngo else None
        out["organization_verified"] = bool(ngo and ngo[0]["is_verified"])
    return out


@router.post("/login")
def login(body: LoginRequest):
    db = get_db()
    rows = db.table("users").select("*").eq("email", body.email.lower()).execute().data
    if not rows or not verify_password(body.password, rows[0]["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return _auth_response(rows[0])
