# Backend → Frontend Handover (AccessiNav)

**Backend status: Phases 1–4 done and live.** You can build against real data now, no mocks needed.
Live API: `https://web-production-c199d.up.railway.app` | Interactive docs (try every endpoint): `/docs`

## 1. Env vars for your `.env`
```
VITE_API_URL=https://web-production-c199d.up.railway.app/api
VITE_SUPABASE_URL=https://aevofjrzgjrsljnevqrq.supabase.co
VITE_SUPABASE_ANON_KEY=<Giri will send this. Anon key ONLY, never service_role>
VITE_MAPBOX_TOKEN=<Giri will send this>
```
**Giri needs from you:** your Vercel URL, to add to CORS. Until then only `http://localhost:5173` works, and a deployed site will hit CORS errors.

## 2. Auth
- `POST /auth/register` `{email, password, user_type: "user"|"volunteer"|"ngo", name?, organization_name?}`
  volunteers must send `name`, NGOs must send `organization_name` (else 400).
- `POST /auth/login` `{email, password}`
- Both return `{user_id, email, user_type, token}`. Token lasts 72h.
- **Every write needs the header** `Authorization: Bearer <token>`. Reads (routes, reports, leaderboard) are public.
- Errors: 401 missing/invalid token, 403 wrong role, 404 not found, 409 email already registered, 422 bad body.
  Body is `{"detail": "..."}` (500s are `{"error": "..."}`).
- No test accounts exist. Register your own (one per role) to test the volunteer and NGO flows.

## 3. Endpoints
| Method | Path | Who | Body / params → response |
|---|---|---|---|
| GET | /routes | public | `?start=lat,lon&end=lat,lon&disability=wheelchair` → `{routes:[...]}` |
| GET | /reports | public | `?lat&lon&radius` (km, default 5; lat/lon optional = all) → `{reports:[...]}` |
| POST | /reports | any user | `{description, photo_url?, latitude, longitude}` → `{id, created_at}` |
| POST | /reports/{id}/upvote | any user | → `{upvotes}` (one vote per user; repeat returns the same count) |
| POST | /reports/{id}/verify | volunteer/ngo | `{verification_status: "verified"\|"false"}` → `{verified_by_type}` |
| POST | /reports/bulk-verify | ngo only | `{report_ids: [...], verification_status}` → `{verified_by_type, count}` |
| GET | /dashboard/pending-reports | volunteer/ngo | → `{reports, count}` (unverified only) |
| GET | /dashboard/verified | volunteer/ngo | → reports this verifier handled |
| GET | /dashboard/leaderboard | public | → `{leaderboard:[{name, type, total_verified, level}]}` |
| POST | /sos | any user | `{latitude, longitude}` → `{alert_id, status}` |
| GET | /sos | any user | → `{alerts:[...]}` active alerts (NGO dashboard) |
| POST | /sos/{id}/resolve | volunteer/ngo | → `{alert_id, status:"resolved"}` |
| GET | /health | public | → `{status:"ok"}` |

`user_id` in bodies is ignored; identity comes from the token.

## 4. Data shapes
**Route:** `{id, mode, duration:"34 min", distance:"12.1 km", accessible, steps, stops, via?, geometry?, realtime_updates:{delay_min, vehicle_position, next_arrival, source}}`
- `geometry` is a GeoJSON LineString (`[lon, lat]` order, Mapbox-ready), present on the cab route only.
- `vehicle_position` is **always null**. Don't build a live vehicle marker.
- `source` is `"schedule"` (Metro, from the real timetable) or `"estimate"` (cab/bus). Label it honestly in the UI.
- A wheelchair search never returns the bus. Metro only appears when start/end are near two different stations.

**Report:** `{id, description, photo_url, latitude, longitude, upvotes, report_source, verification_status, verified_by_name, verified_by_type, created_at}`
Badge logic:
- `verified_by_type === "ngo"` → green
- `"volunteer"` → blue
- otherwise → gray, plus an "upvoted" hint when `upvotes >= 3`
- `verification_status === "false"` means rejected. Hide it or show it struck out.

## 5. Realtime (Supabase JS)
Subscribe with the anon key to `postgres_changes` on tables **`reports`** and **`sos_alerts`** (INSERT and UPDATE).
- A volunteer verifying a report arrives as an UPDATE on `reports`, so the badge can change live.
- The anon key is read-only (RLS). All writes go through the API above.
- **Not yet confirmed by Giri:** that the tables are enabled in the Supabase realtime publication. If you get no events, tell him.
- Photos: upload to Cloudinary from the frontend and send the resulting URL as `photo_url`.

## 6. Good to know
- The first request after idle can be slow (cold cache). Show a loading state.
- Reports are cached 5s but refresh instantly after any write. Routes are cached 30s.
- 6 demo reports are seeded around Chennai (St. Thomas Mount, Central, Guindy, Egmore, Vadapalani, Alandur). Good test coords: start `13.0003,80.1985`, end `13.0827,80.2757`.
- Metro data: 44 real CMRL stations from the open ChennaiGTFS repo (ODbL).

## 7. Still pending on the backend side
- Two-phone realtime test (needs your frontend hooked up).
- Upstash Redis (caching works without it).
- Your Vercel URL in CORS.
