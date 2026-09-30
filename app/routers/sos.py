from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..db import get_db
from ..deps import current_user

router = APIRouter(prefix="/api/sos", tags=["sos"])


class SosRequest(BaseModel):
    latitude: float
    longitude: float
    user_id: Optional[str] = None  # ignored; identity comes from the JWT


@router.post("")
def create_sos(body: SosRequest, user: dict = Depends(current_user)):
    row = (
        get_db().table("sos_alerts")
        .insert({"user_id": user["id"], "latitude": body.latitude, "longitude": body.longitude})
        .execute().data[0]
    )
    return {"alert_id": row["id"], "status": row["status"]}


@router.post("/{alert_id}/resolve")
def resolve(alert_id: str, user: dict = Depends(current_user)):
    if user["user_type"] not in ("ngo", "volunteer"):
        raise HTTPException(403, "Only NGOs and volunteers can resolve alerts")
    rows = get_db().table("sos_alerts").update({"status": "resolved"}).eq("id", alert_id).execute().data
    if not rows:
        raise HTTPException(404, "Alert not found")
    return {"alert_id": alert_id, "status": "resolved"}


@router.get("")
def active_alerts(user: dict = Depends(current_user)):
    """Active SOS alerts for the NGO dashboard (extra, not in the locked contract)."""
    rows = (
        get_db().table("sos_alerts").select("*")
        .eq("status", "active").order("created_at", desc=True).limit(50)
        .execute().data
    )
    return {"alerts": rows}
