"""GTFS-RT reader with mock fallback (so the demo never depends on a live feed)."""
import random

import requests
from google.transit import gtfs_realtime_pb2

from .config import settings


def _mock_updates() -> dict:
    return {
        "delay_min": random.choice([0, 0, 2, 4]),
        "vehicle_position": {"lat": 13.0827, "lon": 80.2707},
        "next_arrival": f"{random.randint(2, 9)} min",
        "source": "mock",
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
    if not settings.gtfs_rt_url:
        return _mock_updates()
    try:
        updates = fetch_feed()
        delay = updates[0]["delay_min"] if updates else 0
        return {**_mock_updates(), "delay_min": delay, "source": "gtfs-rt"}
    except Exception:
        return _mock_updates()
