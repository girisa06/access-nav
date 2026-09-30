"""Seed demo reports. Run: python -m scripts.seed   (safe to re-run)

Each description uses the format the frontend parses:
    [Issue type · Severity · Category]
    Place: <name>
    <details>
Coordinates come from the real CMRL station data, so every place name matches its pin.
Only reports with no author (reported_by IS NULL, i.e. earlier seed data) are replaced;
reports submitted by real users are never touched.
"""
import json
from pathlib import Path

from app.db import get_db

STATIONS = {s["name"]: (s["lat"], s["lon"]) for s in json.loads(
    (Path(__file__).parent.parent / "app" / "data" / "cmrl.json").read_text(encoding="utf-8"))["stations"]}

CENTRAL = "Puratchi Thalaivar Dr. M.G. Ramachandran Central"
ALANDUR = "Arignar Anna Alandur"

# (cmrl station, place shown to users, issue type, severity, category, details, upvotes, status, verifier name, verifier type)
REPORTS = [
    ("Guindy", "Guindy Metro Station", "Broken elevator or escalator", "High", "Wheelchair",
     "The lift between the concourse and the platform has been out of service for two days. Wheelchair users have no step-free way down.",
     5, "unverified", None, None),
    (CENTRAL, "Chennai Central Metro Station", "Missing or broken ramp", "Medium", "Wheelchair",
     "The ramp at the main entrance is very steep and has no handrail, which makes it unsafe to use without help.",
     4, "verified", "Priya S", "volunteer"),
    ("Vadapalani", "Vadapalani Metro Station", "Missing tactile paving (guide blocks)", "Medium", "Visual impairment",
     "There are no guide blocks between the entrance gate and the ticket counter, so there is nothing to follow by cane.",
     3, "verified", "Access India Trust", "ngo"),
    ("Egmore", "Egmore Metro Station", "No audio announcements", "Medium", "Visual impairment",
     "Train arrivals are only shown on the display board. There are no spoken announcements on the platform.",
     2, "unverified", None, None),
    ("Teynampet", "Teynampet Metro Station", "No visual announcements", "Low", "Hearing impairment",
     "Delay and platform-change messages are only announced by speaker. Nothing is shown on the screens.",
     1, "verified", "Meera R", "volunteer"),
    (ALANDUR, "Alandur Metro Station", "Broken or missing accessible toilet", "Medium", "Wheelchair",
     "The accessible toilet on the concourse is locked and staff were unable to find the key when asked.",
     6, "verified", "Arun K", "volunteer"),
    ("Koyambedu", "Koyambedu Metro Station", "Narrow/blocked passage", "High", "Mobility assistance",
     "Vendor stalls and parked trolleys leave less than a metre of clear space in the walkway to the exit.",
     3, "unverified", None, None),
    ("St. Thomas Mount", "St. Thomas Mount Metro Station", "✅ Accessible feature (working well!)", "Low", "Wheelchair",
     "The wide gate is open and staffed, the lift works, and there is a clear level path from the street to the platform.",
     7, "verified", "Access India Trust", "ngo"),
    ("Thousand Lights", "Thousand Lights Metro Station", "Broken ticket machine", "Low", "General accessibility",
     "The ticket machine nearest the entrance shows an error, and the next one is too high to reach from a wheelchair.",
     2, "unverified", None, None),
    ("Meenambakkam", "Meenambakkam Metro Station", "Steps/stairs with no alternative", "High", "Wheelchair",
     "The exit toward the bus stop has only a flight of stairs. No ramp or lift is signposted.",
     4, "unverified", None, None),
]

if __name__ == "__main__":
    db = get_db()
    removed = db.table("reports").delete().is_("reported_by", "null").execute().data
    for station, place, issue, severity, category, details, upvotes, status, by, btype in REPORTS:
        lat, lon = STATIONS[station]
        db.table("reports").insert({
            "description": f"[{issue} · {severity} · {category}]\nPlace: {place}\n{details}",
            "latitude": lat, "longitude": lon, "upvotes": upvotes,
            "report_source": "user", "verification_status": status,
            "verified_by_name": by, "verified_by_type": btype,
        }).execute()
    print(f"replaced {len(removed)} old seed reports with {len(REPORTS)} new ones")
