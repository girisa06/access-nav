"""Seed demo reports around Chennai. Run once: python -m scripts.seed"""
from app.db import get_db

REPORTS = [
    ("Lift out of order at St. Thomas Mount station", 13.0003, 80.1985, 5, "unverified", None, None),
    ("Ramp too steep at Central Station entrance", 13.0827, 80.2757, 4, "verified", "Priya S", "volunteer"),
    ("Accessible toilet locked at Guindy", 13.0087, 80.2130, 2, "verified", "Access India Trust", "ngo"),
    ("Footpath broken near Egmore metro exit", 13.0788, 80.2609, 3, "unverified", None, None),
    ("Tactile paving missing at Vadapalani", 13.0505, 80.2122, 1, "unverified", None, None),
    ("Wide gate open and staffed at Alandur", 13.0035, 80.2043, 6, "verified", "Arun K", "volunteer"),
]

if __name__ == "__main__":
    db = get_db()
    for desc, lat, lon, up, status, by, btype in REPORTS:
        db.table("reports").insert({
            "description": desc, "latitude": lat, "longitude": lon, "upvotes": up,
            "report_source": "user", "verification_status": status,
            "verified_by_name": by, "verified_by_type": btype,
        }).execute()
    print(f"seeded {len(REPORTS)} reports")
