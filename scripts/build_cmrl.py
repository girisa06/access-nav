"""Build app/data/cmrl.json from the ChennaiGTFS CMRL feed.
Usage: python -m scripts.build_cmrl <dir with stops.txt and frequencies.txt>
Data: https://github.com/ungalsoththu/ChennaiGTFS (ODbL, unofficial)."""
import csv
import json
import sys

d = sys.argv[1]


def rd(f):
    return list(csv.DictReader(open(f"{d}/{f}", encoding="utf-8-sig")))


def sec(t):
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s


stations = [
    {"name": s["stop_name"], "lat": float(s["stop_lat"]), "lon": float(s["stop_lon"])}
    for s in rd("stops.txt")
]
hw = {"weekday": set(), "saturday": set(), "sunday": set()}
for f in rd("frequencies.txt"):
    day = f["trip_id"].split("_")[2]
    hw[day].add((sec(f["start_time"]), sec(f["end_time"]), int(f["headway_secs"])))

out = {
    "source": "ungalsoththu/ChennaiGTFS (CMRL), ODbL - attribution: UngalSoththu / Ithu Ungal Soththu",
    "stations": stations,
    "headways": {k: [list(x) for x in sorted(v)] for k, v in hw.items()},
}
json.dump(out, open("app/data/cmrl.json", "w"), indent=1)
print(len(stations), "stations;", {k: len(v) for k, v in hw.items()}, "headway windows")
