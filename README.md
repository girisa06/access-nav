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
| GET | /api/sos | any | active alerts (NGO dashboard) |
| POST | /api/sos/{id}/resolve | volunteer/ngo | |

Bulk verify, verified, leaderboard and the SOS list/resolve are additions beyond the original contract.

## Realtime
The frontend subscribes directly to Supabase Realtime on `reports` and `sos_alerts`
using the **anon** key (read-only via RLS). The backend writes with the service key.

## Environment
See `.env.example`. Never commit `.env`.

## Load test
`python -m scripts.loadtest https://<host> 100`
