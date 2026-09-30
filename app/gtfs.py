"""Transit updates: live GTFS-RT if GTFS_RT_URL is set, else CMRL timetable (headway) based.

No public Chennai GTFS-RT feed is known, so by default `source` is "schedule":
next_arrival is computed from the real CMRL headways (ungalsoththu/ChennaiGTFS, ODbL).
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from google.transit import gtfs_realtime_pb2

from .config import settings

CMRL = json.loads((Path(__file__).parent / "data" / "cmrl.json").read_text(encoding="utf-8"))
IST = timezone(timedelta(hours=5, minutes=30))


def _schedule_updates() -> dict:
    now = datetime.now(IST)
    day = ("weekday", "weekday", "weekday", "weekday", "weekday", "saturday", "sunday")[now.weekday()]
    t = now.hour * 3600 + now.minute * 60 + now.second
    windows = [w for w in CMRL["headways"][day] if w[0] <= t < w[1]]
    if not windows:
        return {"delay_min": 0, "vehicle_position": None, "next_arrival": "Not in service", "source": "schedule"}
    start, _, headway = min(windows, key=lambda w: w[2])
    wait_s = headway - (t - start) % headway
    return {
        "delay_min": 0,
        "vehicle_position": None,
        "next_arrival": f"{max(1, round(wait_s / 60))} min",
        "source": "schedule",
    }


def fetch_feed() -> list[dict]:
    """Return trip updates from the configured feed; raises on failure."""
    resp = requests.get(settings.gtfs_rt_url, timeout=5)
    resp.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)

    updates = []
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            tu = entity.trip_update
            delay = tu.stop_time_update[0].arrival.delay if tu.stop_time_update else 0
            updates.append({"trip_id": tu.trip.trip_id, "delay_min": round(delay / 60)})
    return updates


def get_realtime_updates() -> dict:
    base = _schedule_updates()
    if not settings.gtfs_rt_url:
        return base
    try:
        updates = fetch_feed()
        delay = updates[0]["delay_min"] if updates else 0
        return {**base, "delay_min": delay, "source": "gtfs-rt"}
    except Exception:
        return base
