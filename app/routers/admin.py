from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException

from ..db import get_db
from ..deps import admin_only

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(admin_only)])


@router.get("/organizations")
def list_organizations(status: Literal["pending", "approved", "all"] = "pending"):
    """Organizations awaiting approval (default), approved ones, or all."""
    db = get_db()
    q = db.table("ngos").select("id, user_id, organization_name, website, is_verified, verified_at, total_verified, created_at").order("created_at", desc=True)
    if status != "all":
        q = q.eq("is_verified", status == "approved")
    orgs = q.execute().data
    emails = {u["id"]: u["email"] for u in db.table("users").select("id, email").in_("id", [o["user_id"] for o in orgs]).execute().data} if orgs else {}
    return {"organizations": [{**o, "email": emails.get(o["user_id"])} for o in orgs], "count": len(orgs)}


def _set_approval(ngo_id: str, approved: bool) -> dict:
    rows = get_db().table("ngos").update({
        "is_verified": approved,
        "verified_at": datetime.now(timezone.utc).isoformat() if approved else None,
        "verification_level": "gold" if approved else "bronze",
    }).eq("id", ngo_id).execute().data
    if not rows:
        raise HTTPException(404, "Organization not found")
    return {"id": ngo_id, "organization_name": rows[0]["organization_name"], "is_verified": approved}


@router.post("/organizations/{ngo_id}/approve")
def approve(ngo_id: str):
    return _set_approval(ngo_id, True)


@router.post("/organizations/{ngo_id}/revoke")
def revoke(ngo_id: str):
    return _set_approval(ngo_id, False)
