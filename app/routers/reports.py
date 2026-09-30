import math
import time
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..cache import cache_get, cache_set
from ..db import get_db
from ..deps import current_user, verifier_user

router = APIRouter(prefix="/api", tags=["reports"])

REPORT_COLS = (
    "id, description, photo_url, latitude, longitude, upvotes, report_source, "
    "verification_status, verified_by_name, verified_by_type, created_at"
)


def _km(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin((p2 - p1) / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    )
    return 6371 * 2 * math.asin(math.sqrt(a))


class ReportCreate(BaseModel):
    description: str
    photo_url: Optional[str] = None
    latitude: float
    longitude: float
    user_id: Optional[str] = None  # ignored; identity comes from the JWT


class VerifyRequest(BaseModel):
    verifier_id: Optional[str] = None
    verification_status: Literal["verified", "false", "rejected"]


def _bump_reports() -> None:
    """Invalidate cached report lists after any write."""
    cache_set("reports:version", time.time(), ttl=3600)


@router.get("/reports")
def list_reports(lat: Optional[float] = None, lon: Optional[float] = None, radius: float = 5):
    key = f"reports:{cache_get('reports:version')}:{lat and round(lat, 3)}:{lon and round(lon, 3)}:{radius}"
    cached = cache_get(key)
    if cached:
        return cached
    result = _query_reports(lat, lon, radius)
    cache_set(key, result, ttl=5)
    return result


def _query_reports(lat, lon, radius):
    q =get_db().table("reports").select(REPORT_COLS).order("created_at", desc=True).limit(200)
    if lat is not None and lon is not None:
        dlat = radius / 111
        dlon = radius / (111 * max(math.cos(math.radians(lat)), 0.01))
        q = (
            q.gte("latitude", lat - dlat).lte("latitude", lat + dlat)
            .gte("longitude", lon - dlon).lte("longitude", lon + dlon)
        )
    rows = q.execute().data
    if lat is not None and lon is not None:
        rows = [r for r in rows if _km(lat, lon, r["latitude"], r["longitude"]) <= radius]
    return {"reports": rows}


@router.post("/reports")
def create_report(body: ReportCreate, user: dict = Depends(current_user)):
    row = (
        get_db().table("reports")
        .insert(
            {
                "reported_by": user["id"],
                "report_source": user["user_type"],
                "description": body.description,
                "photo_url": body.photo_url,
                "latitude": body.latitude,
                "longitude": body.longitude,
            }
        )
        .execute().data[0]
    )
    _bump_reports()
    return {"id": row["id"], "created_at": row["created_at"]}


@router.post("/reports/{report_id}/upvote")
def upvote(report_id: str, user: dict = Depends(current_user)):
    db = get_db()
    if not db.table("reports").select("id").eq("id", report_id).execute().data:
        raise HTTPException(404, "Report not found")
    n = db.rpc("upvote_report", {"p_report_id": report_id, "p_user_id": user["id"]}).execute().data
    _bump_reports()
    return {"upvotes": n}


def _apply_verification(user: dict, ids: list[str], verification_status: str) -> str:
    """Mark reports verified/false as this volunteer or NGO; returns the verifier type."""
    db = get_db()
    found = db.table("reports").select("id").in_("id", ids).execute().data
    if not found:
        raise HTTPException(404, "Report not found")
    ids = [r["id"] for r in found]

    vtype = user["user_type"]
    if vtype == "volunteer":
        prof = db.table("volunteers").select("id, name, total_verified").eq("user_id", user["id"]).execute().data
        name_key = "name"
    else:
        prof = db.table("ngos").select("id, organization_name, total_verified").eq("user_id", user["id"]).execute().data
        name_key = "organization_name"
    if not prof:
        raise HTTPException(403, "Verifier profile not found")

    status = "false" if verification_status in ("false", "rejected") else "verified"
    db.table("reports").update(
        {
            "verification_status": status,
            "verified_by": user["id"],
            "verified_by_name": prof[0][name_key],
            "verified_by_type": vtype,
        }
    ).in_("id", ids).execute()

    table = "volunteers" if vtype == "volunteer" else "ngos"
    db.table(table).update({"total_verified": (prof[0]["total_verified"] or 0) + len(ids)}).eq("id", prof[0]["id"]).execute()
    _bump_reports()
    return vtype


@router.post("/reports/{report_id}/verify")
def verify(report_id: str, body: VerifyRequest, user: dict = Depends(verifier_user)):
    if body.verifier_id and body.verifier_id != user["id"]:
        raise HTTPException(403, "verifier_id does not match token")
    return {"verified_by_type": _apply_verification(user, [report_id], body.verification_status)}


class BulkVerifyRequest(BaseModel):
    report_ids: list[str]
    verification_status: Literal["verified", "false", "rejected"]


@router.post("/reports/bulk-verify")
def bulk_verify(body: BulkVerifyRequest, user: dict = Depends(verifier_user)):
    """NGO dashboard bulk verification (extra, not in the locked contract)."""
    if user["user_type"] != "ngo":
        raise HTTPException(403, "Only NGOs can bulk verify")
    if not body.report_ids:
        raise HTTPException(400, "report_ids is empty")
    vtype = _apply_verification(user, body.report_ids, body.verification_status)
    return {"verified_by_type": vtype, "count": len(body.report_ids)}


@router.get("/dashboard/verified")
def my_verified(user: dict = Depends(verifier_user)):
    rows = (
        get_db().table("reports").select(REPORT_COLS)
        .eq("verified_by", user["id"]).order("created_at", desc=True).limit(100)
        .execute().data
    )
    return {"reports": rows, "count": len(rows)}


@router.get("/dashboard/leaderboard")
def leaderboard():
    db = get_db()
    vols = db.table("volunteers").select("name, total_verified, verification_level").order("total_verified", desc=True).limit(10).execute().data
    ngos = db.table("ngos").select("organization_name, total_verified, verification_level").order("total_verified", desc=True).limit(10).execute().data
    board = [{"name": v["name"], "type": "volunteer", "total_verified": v["total_verified"], "level": v["verification_level"]} for v in vols]
    board += [{"name": n["organization_name"], "type": "ngo", "total_verified": n["total_verified"], "level": n["verification_level"]} for n in ngos]
    board.sort(key=lambda x: x["total_verified"] or 0, reverse=True)
    return {"leaderboard": board[:10]}


@router.get("/dashboard/pending-reports")
def pending_reports(verifier_id: Optional[str] = None, user: dict = Depends(verifier_user)):
    rows = (
        get_db().table("reports").select(REPORT_COLS)
        .eq("verification_status", "unverified")
        .order("created_at", desc=True).limit(100)
        .execute().data
    )
    return {"reports": rows, "count": len(rows)}
