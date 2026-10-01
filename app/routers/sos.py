from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..db import get_db
from ..deps import current_user, responder_user

router = APIRouter(prefix="/api/sos", tags=["sos"])


class SosRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    user_id: Optional[str] = None  # ignored; identity comes from the JWT


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


def _own_alert(alert_id: str, user: dict) -> dict:
    """The caller's own alert; 404 for anyone else's so alert ids can't be probed."""
    rows = get_db().table("sos_alerts").select("id, user_id, status").eq("id", alert_id).execute().data
    if not rows or rows[0]["user_id"] != user["id"]:
        raise HTTPException(404, "Alert not found")
    return rows[0]


@router.post("")
def create_sos(body: SosRequest, user: dict = Depends(current_user)):
    row = (
        get_db().table("sos_alerts")
        .insert({"user_id": user["id"], "latitude": body.latitude, "longitude": body.longitude})
        .execute().data[0]
    )
    return {"alert_id": row["id"], "status": row["status"]}


@router.post("/{alert_id}/location")
def update_location(alert_id: str, body: LocationUpdate, user: dict = Depends(current_user)):
    """Live location update from the person who raised the alert. Tells the client when to stop."""
    alert = _own_alert(alert_id, user)
    if alert["status"] != "active":
        return {"alert_id": alert_id, "status": alert["status"]}
    get_db().table("sos_alerts").update({"latitude": body.latitude, "longitude": body.longitude}).eq("id", alert_id).execute()
    return {"alert_id": alert_id, "status": "active"}


@router.post("/{alert_id}/cancel")
def cancel(alert_id: str, user: dict = Depends(current_user)):
    """The person who raised the alert stops it (and stops sharing their location)."""
    _own_alert(alert_id, user)
    get_db().table("sos_alerts").update({"status": "cancelled"}).eq("id", alert_id).eq("status", "active").execute()
    return {"alert_id": alert_id, "status": "cancelled"}


@router.post("/{alert_id}/resolve")
def resolve(alert_id: str, user: dict = Depends(responder_user)):
    rows = get_db().table("sos_alerts").update({"status": "resolved"}).eq("id", alert_id).execute().data
    if not rows:
        raise HTTPException(404, "Alert not found")
    return {"alert_id": alert_id, "status": "resolved"}


@router.get("")
def active_alerts(user: dict = Depends(responder_user)):
    """Active SOS alerts with live locations (volunteers and approved organizations only)."""
    rows = (
        get_db().table("sos_alerts").select("*")
        .eq("status", "active").order("created_at", desc=True).limit(50)
        .execute().data
    )
    return {"alerts": rows}
