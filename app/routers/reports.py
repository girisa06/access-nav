import math
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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


@router.get("/reports")
def list_reports(lat: Optional[float] = None, lon: Optional[float] = None, radius: float = 5):
    q = get_db().table("reports").select(REPORT_COLS).order("created_at", desc=True).limit(200)
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
    return {"id": row["id"], "created_at": row["created_at"]}


@router.post("/reports/{report_id}/upvote")
def upvote(report_id: str, user: dict = Depends(current_user)):
    db = get_db()
    rows = db.table("reports").select("upvotes").eq("id", report_id).execute().data
    if not rows:
        raise HTTPException(404, "Report not found")
    n = (rows[0]["upvotes"] or 0) + 1
    db.table("reports").update({"upvotes": n}).eq("id", report_id).execute()
    return {"upvotes": n}


@router.post("/reports/{report_id}/verify")
def verify(report_id: str, body: VerifyRequest, user: dict = Depends(verifier_user)):
    if body.verifier_id and body.verifier_id != user["id"]:
        raise HTTPException(403, "verifier_id does not match token")
    db = get_db()
    if not db.table("reports").select("id").eq("id", report_id).execute().data:
        raise HTTPException(404, "Report not found")

    vtype = user["user_type"]
    if vtype == "volunteer":
        prof = db.table("volunteers").select("id, name, total_verified").eq("user_id", user["id"]).execute().data
        name_key = "name"
    else:
        prof = db.table("ngos").select("id, organization_name, total_verified").eq("user_id", user["id"]).execute().data
        name_key = "organization_name"
    if not prof:
        raise HTTPException(403, "Verifier profile not found")

    status = "false" if body.verification_status in ("false", "rejected") else "verified"
    db.table("reports").update(
        {
            "verification_status": status,
            "verified_by": user["id"],
            "verified_by_name": prof[0][name_key],
            "verified_by_type": vtype,
        }
    ).eq("id", report_id).execute()

    table = "volunteers" if vtype == "volunteer" else "ngos"
    db.table(table).update({"total_verified": (prof[0]["total_verified"] or 0) + 1}).eq("id", prof[0]["id"]).execute()
    return {"verified_by_type": vtype}


@router.get("/dashboard/pending-reports")
def pending_reports(verifier_id: Optional[str] = None, user: dict = Depends(verifier_user)):
    rows = (
        get_db().table("reports").select(REPORT_COLS)
        .eq("verification_status", "unverified")
        .order("created_at", desc=True).limit(100)
        .execute().data
    )
    return {"reports": rows, "count": len(rows)}
