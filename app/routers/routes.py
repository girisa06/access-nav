"""Accessible route options for Chennai.

Mapbox has no step-free data, so options are built from the 44 real CMRL stations
(app/data/cmrl.json, from ungalsoththu/ChennaiGTFS, ODbL) + Mapbox distance/geometry
where available. Metro gets timetable-based updates (live GTFS-RT if configured).
"""
import threading

import requests
from fastapi import APIRouter, HTTPException

from ..cache import cache_get, cache_set
from ..config import settings
from ..gtfs import CMRL, get_realtime_updates
from .reports import _km

router = APIRouter(prefix="/api", tags=["routes"])

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()

METRO_STATIONS = {s["name"]: (s["lat"], s["lon"]) for s in CMRL["stations"]}


def _parse(s: str) -> tuple[float, float]:
    try:
        lat, lon = (float(x) for x in s.split(","))
        return lat, lon
    except ValueError:
        raise HTTPException(400, "Expected lat,lon")


STATION_DISPLAY = {
    "Puratchi Thalaivar Dr. M.G. Ramachandran Central": "Chennai Central",
    "Puratchi Thalaivi Dr. J. Jayalalithaa CMBT": "CMBT, Koyambedu",
    "Arignar Anna Alandur": "Alandur",
    "Chennai International Airport": "Chennai Airport",
}


def _display(name: str) -> str:
    return STATION_DISPLAY.get(name, name)


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


LINES = CMRL.get("lines", {})  # line name -> ordered [lat, lon] station points
STATION_MATCH_KM = 0.15


def _line_index(pts, p):
    i = min(range(len(pts)), key=lambda k: _km(*pts[k], *p))
    return i if _km(*pts[i], *p) <= STATION_MATCH_KM else None


def _slice(pts, i, j):
    return pts[i:j + 1] if i <= j else pts[j:i + 1][::-1]


def _metro_path(s_pt, e_pt) -> list[list[float]]:
    """[lat, lon] points along CMRL lines between two stations (transfers at interchanges)."""
    best = None
    for pts in LINES.values():
        i, j = _line_index(pts, s_pt), _line_index(pts, e_pt)
        if i is not None and j is not None:
            cand = _slice(pts, i, j)
            best = cand if best is None or len(cand) < len(best) else best
    if best:
        return best
    for name_a, pa in LINES.items():
        for name_b, pb in LINES.items():
            if name_a == name_b:
                continue
            i, j = _line_index(pa, s_pt), _line_index(pb, e_pt)
            if i is None or j is None:
                continue
            for x, pt in enumerate(pa):  # interchange = point that is also on line B
                y = _line_index(pb, pt)
                if y is not None:
                    cand = _slice(pa, i, x) + _slice(pb, y, j)[1:]
                    best = cand if best is None or len(cand) < len(best) else best
    return best or [list(s_pt), list(e_pt)]


def _straight(a, b) -> dict:
    return {"type": "LineString", "coordinates": [[a[1], a[0]], [b[1], b[0]]]}


def _walk_leg(a, b) -> list[list[float]]:
    """[lon, lat] coordinates for a walking leg; straight line if Mapbox is unavailable."""
    leg = _mapbox("walking", a, b)
    return leg["geometry"]["coordinates"] if leg else _straight(a, b)["coordinates"]


def _metro_geometry(a, b, s_pt, e_pt) -> dict:
    coords = _walk_leg(a, s_pt)
    coords += [[lon, lat] for lat, lon in _metro_path(s_pt, e_pt)]
    coords += _walk_leg(e_pt, b)
    return {"type": "LineString", "coordinates": coords}


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
        path = _metro_path(METRO_STATIONS[s_name], METRO_STATIONS[e_name])
        routes.append({
            "id": 1, "mode": "Metro", "duration": f"{total} min",
            "distance": f"{metro_km + s_walk + e_walk:.1f} km",
            "accessible": True, "steps": 0, "stops": max(1, len(path) - 1),  # stations along the line path
            "board_at": _display(s_name), "exit_at": _display(e_name),
            "via": f"{_display(s_name)} → {_display(e_name)}",
            "geometry": _metro_geometry(a, b, METRO_STATIONS[s_name], METRO_STATIONS[e_name]),
            "realtime_updates": get_realtime_updates(),
        })

    routes.append({
        "id": 2, "mode": "Accessible Cab", "duration": f"{round(drive_min + 6)} min",
        "distance": f"{km:.1f} km", "accessible": True, "steps": 0, "stops": 0,
        "geometry": drive["geometry"] if drive else _straight(a, b),
        "realtime_updates": {"delay_min": 0, "vehicle_position": None, "next_arrival": "6 min", "source": "estimate"},
    })
    routes.append({
        "id": 3, "mode": "Low-floor Bus", "duration": f"{round(km / 15 * 60 + 8)} min",
        "distance": f"{km:.1f} km", "accessible": disability != "wheelchair", "steps": 2,
        "stops": max(2, round(km / 0.8)),
        "geometry": drive["geometry"] if drive else _straight(a, b),
        "realtime_updates": {"delay_min": 5, "vehicle_position": None, "next_arrival": "12 min", "source": "estimate"},
    })

    if disability == "wheelchair":
        routes = [r for r in routes if r["accessible"]]
    return {"routes": routes}
