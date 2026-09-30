"""Simulate concurrent users. Usage: python -m scripts.loadtest [base_url] [users]"""
import asyncio
import statistics
import sys
import time

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
USERS = int(sys.argv[2]) if len(sys.argv) > 2 else 100
PATHS = [
    "/api/health",
    "/api/reports?lat=13.05&lon=80.25&radius=5",
    "/api/routes?start=13.0003,80.1985&end=13.0827,80.2757&disability=wheelchair",
]


async def user(client: httpx.AsyncClient, lat: list[float], fails: list[str]):
    for path in PATHS:
        t = time.perf_counter()
        try:
            r = await client.get(BASE + path)
            if r.status_code != 200:
                fails.append(f"{path} {r.status_code}")
        except Exception as e:
            fails.append(f"{path} {type(e).__name__}")
        lat.append((time.perf_counter() - t) * 1000)


async def main():
    lat: list[float] = []
    fails: list[str] = []
    async with httpx.AsyncClient(timeout=30) as client:
        t = time.perf_counter()
        await asyncio.gather(*(user(client, lat, fails) for _ in range(USERS)))
        total = time.perf_counter() - t
    lat.sort()
    print(f"{USERS} users, {len(lat)} requests in {total:.1f}s, failures: {len(fails)}")
    print(f"median {statistics.median(lat):.0f}ms  p95 {lat[int(len(lat) * .95)]:.0f}ms  max {lat[-1]:.0f}ms")
    if fails:
        print("sample failures:", fails[:5])


asyncio.run(main())
