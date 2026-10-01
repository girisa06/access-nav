# AccessiNav Backend

FastAPI backend for AccessiNav, an accessible transit app for people with disabilities (Chennai).
Data: Supabase (Postgres + Realtime). Cache: Upstash Redis (in-memory fallback). Deployed on Railway.

**Live:** https://web-production-c199d.up.railway.app | **Docs:** `/docs`

## Run locally
```
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # fill in values
uvicorn app.main:app --reload
```

## Database setup (Supabase SQL Editor, in order)
1. `sql/schema.sql`
2. `sql/phase3.sql` (upvote dedupe, indexes)
3. Optional demo data: `python -m scripts.seed`

## Auth
`POST /api/auth/register|login` return `{user_id, email, user_type, token}`.
Send `Authorization: Bearer <token>` on every write. Reads (routes, reports, leaderboard) are public.

## Endpoints
| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | /api/health | - | |
| POST | /api/auth/register, /login | - | |
| GET | /api/routes?start=lat,lon&end=lat,lon&disability= | - | cached 30s |
| GET | /api/reports?lat&lon&radius(km) | - | |
| POST | /api/reports | any | user id taken from token |
| POST | /api/reports/{id}/upvote | any | one vote per user |
| POST | /api/reports/{id}/verify | volunteer/ngo | body `verification_status`: verified / false |
| POST | /api/reports/bulk-verify | ngo | `{report_ids, verification_status}` |
| GET | /api/dashboard/pending-reports | volunteer/ngo | |
| GET | /api/dashboard/verified | volunteer/ngo | reports this verifier handled |
| GET | /api/dashboard/leaderboard | - | |
| POST | /api/sos | any | `{latitude, longitude}` |
| GET | /api/sos | volunteer / approved org | active alerts with live locations |
| POST | /api/sos/{id}/location | alert owner | live position update; returns `status` so the client knows when to stop |
| POST | /api/sos/{id}/cancel | alert owner | stop the alert |
| POST | /api/sos/{id}/resolve | volunteer / approved org | |
| GET | /api/auth/me | any | account + `organization_verified` for organizations |
| GET | /api/admin/organizations?status=pending\|approved\|all | `X-Admin-Key` | |
| POST | /api/admin/organizations/{id}/approve, /revoke | `X-Admin-Key` | organizations must be approved before they can verify reports or see SOS alerts |

Verifiers can never verify their own reports: a single verify returns 403, bulk verify skips them
(`skipped_own` in the response), and they are hidden from the pending queue.

Bulk verify, verified, leaderboard and the SOS list/resolve are additions beyond the original contract.

## Realtime
The frontend subscribes directly to Supabase Realtime on `reports` and `sos_alerts`
using the **anon** key (read-only via RLS). The backend writes with the service key.

## Environment
See `.env.example`. Never commit `.env`.

## Transit data
Metro stations and timetable headways come from [ungalsoththu/ChennaiGTFS](https://github.com/ungalsoththu/ChennaiGTFS)
(CMRL, unofficial, ODbL, attribution: UngalSoththu / Ithu Ungal Soththu), stored in `app/data/cmrl.json`
(rebuild with `python -m scripts.build_cmrl <dir>`). It is static GTFS, so Metro "next arrival" is
timetable-based (`source: "schedule"`). Set `GTFS_RT_URL` to use a live GTFS-RT feed if one becomes available.
Bus and cab times are estimates (`source: "estimate"`).

## Load test
`python -m scripts.loadtest https://<host> 100`
