"""Accessible route options for Chennai.

Mapbox has no step-free data, so options are built from curated Chennai Metro
stations (all lift-equipped; coordinates approximate) + Mapbox distance/geometry
where available. Metro gets GTFS-RT updates (mock fallback).
"""
import threading

import requests
from fastapi import APIRouter, HTTPException

from ..cache import cache_get, cache_set
from ..config import settings
from ..gtfs import get_realtime_updates
from .reports import _km

router = APIRouter(prefix="/api", tags=["routes"])

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()

METRO_STATIONS = {
    "Chennai Airport": (12.9908, 80.1690),
    "Meenambakkam": (12.9877, 80.1756),
    "St. Thomas Mount": (13.0003, 80.1985),
    "Alandur": (13.0035, 80.2043),
    "Guindy": (13.0087, 80.2130),
    "Little Mount": (13.0159, 80.2216),
    "Saidapet": (13.0225, 80.2247),
    "Nandanam": (13.0308, 80.2401),
    "Teynampet": (13.0380, 80.2473),
    "AG-DMS": (13.0448, 80.2482),
    "Thousand Lights": (13.0580, 80.2545),
    "LIC": (13.0640, 80.2665),
    "Government Estate": (13.0722, 80.2732),
    "Chennai Central": (13.0827, 80.2757),
    "Egmore": (13.0788, 80.2609),
    "Vadapalani": (13.0505, 80.2122),
    "Ashok Nagar": (13.0364, 80.2123),
    "Koyambedu": (13.0693, 80.1946),
}


def _parse(s: str) -> tuple[float, float]:
    try:
        lat, lon = (float(x) for x in s.split(","))
        return lat, lon
    except ValueError:
        raise HTTPException(400, "Expected lat,lon")


def _nearest(lat, lon) -> tuple[str, float]:
    name = min(METRO_STATIONS, key=lambda n: _km(lat, lon, *METRO_STATIONS[n]))
    return name, _km(lat, lon, *METRO_STATIONS[name])


def _mapbox(profile: str, a, b) -> dict | None:
    if not settings.mapbox_token:
        return None
    try:
        url = f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{a[1]},{a[0]};{b[1]},{b[0]}"
        r = requests.get(url, params={"access_token": settings.mapbox_token, "geometries": "geojson"}, timeout=5)
        r.raise_for_status()
        route = r.json()["routes"][0]
        return {"distance_km": route["distance"] / 1000, "duration_min": route["duration"] / 60,
                "geometry": route["geometry"]}
    except Exception:
        return None


@router.get("/routes")
def get_routes(start: str, end: str, disability: str = "wheelchair"):
    a, b = _parse(start), _parse(end)
    key = f"routes:{a[0]:.3f},{a[1]:.3f}:{b[0]:.3f},{b[1]:.3f}:{disability}"
    cached = cache_get(key)
    if cached:
        return cached
    with _locks_guard:
        lock = _locks.setdefault(key, threading.Lock())
    with lock:  # single-flight: concurrent misses wait for one build
        cached = cache_get(key)
        if cached:
            return cached
        result = _build_routes(a, b, disability)
        cache_set(key, result, ttl=30)  # GTFS-RT refresh window
        return result


def _build_routes(a, b, disability):
    drive =_mapbox("driving", a, b)
    km = drive["distance_km"] if drive else _km(*a, *b) * 1.3
    drive_min = drive["duration_min"] if drive else km / 25 * 60

    routes = []
    s_name, s_walk = _nearest(*a)
    e_name, e_walk = _nearest(*b)
    if s_name != e_name and s_walk < 3 and e_walk < 3:
        metro_km = _km(*METRO_STATIONS[s_name], *METRO_STATIONS[e_name]) * 1.15
        total = round(metro_km / 35 * 60 + (s_walk + e_walk) / 4.5 * 60 + 5)  # ride + walk + wait
        routes.append({
            "id": 1, "mode": "Metro", "duration": f"{total} min",
            "distance": f"{metro_km + s_walk + e_walk:.1f} km",
            "accessible": True, "steps": 0, "stops": max(1, round(metro_km / 1.2)),
            "via": f"{s_name} → {e_name}",
            "realtime_updates": get_realtime_updates(),
        })

    routes.append({
        "id": 2, "mode": "Accessible Cab", "duration": f"{round(drive_min + 6)} min",
        "distance": f"{km:.1f} km", "accessible": True, "steps": 0, "stops": 0,
        "geometry": drive["geometry"] if drive else None,
        "realtime_updates": {"delay_min": 0, "vehicle_position": None, "next_arrival": "6 min"},
    })
    routes.append({
        "id": 3, "mode": "Low-floor Bus", "duration": f"{round(km / 15 * 60 + 8)} min",
        "distance": f"{km:.1f} km", "accessible": disability != "wheelchair", "steps": 2,
        "stops": max(2, round(km / 0.8)),
        "realtime_updates": {"delay_min": 5, "vehicle_position": None, "next_arrival": "12 min"},
    })

    if disability == "wheelchair":
        routes = [r for r in routes if r["accessible"]]
    return {"routes": routes}
