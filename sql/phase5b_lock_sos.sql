-- Phase 5b: stop the public anon key from reading SOS alerts directly.
-- schema.sql let the anon key SELECT sos_alerts (for realtime). The anon key ships in the frontend,
-- so anyone could read every live SOS location through Supabase's REST API and bypass the backend's
-- volunteer / approved-organization check. The frontend reads SOS alerts through the API, not Supabase.
-- Paste into Supabase > SQL Editor > Run.

DROP POLICY IF EXISTS "anon read sos_alerts" ON sos_alerts;
REVOKE SELECT ON sos_alerts FROM anon;
