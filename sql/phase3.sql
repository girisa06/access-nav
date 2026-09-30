-- Phase 3 migration. Paste into Supabase > SQL Editor > Run.

-- One upvote per user per report
CREATE TABLE IF NOT EXISTS report_upvotes (
  report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP DEFAULT NOW(),
  PRIMARY KEY (report_id, user_id)
);
ALTER TABLE report_upvotes ENABLE ROW LEVEL SECURITY;
GRANT ALL ON report_upvotes TO service_role;

-- Atomic upvote: returns the new count (unchanged if this user already upvoted)
CREATE OR REPLACE FUNCTION upvote_report(p_report_id UUID, p_user_id UUID)
RETURNS INT LANGUAGE plpgsql AS $$
DECLARE n INT;
BEGIN
  INSERT INTO report_upvotes (report_id, user_id) VALUES (p_report_id, p_user_id)
  ON CONFLICT DO NOTHING;
  IF FOUND THEN
    UPDATE reports SET upvotes = COALESCE(upvotes, 0) + 1 WHERE id = p_report_id;
  END IF;
  SELECT upvotes INTO n FROM reports WHERE id = p_report_id;
  RETURN n;
END $$;
GRANT EXECUTE ON FUNCTION upvote_report(UUID, UUID) TO service_role;

CREATE INDEX IF NOT EXISTS idx_reports_verified_by ON reports (verified_by);
CREATE INDEX IF NOT EXISTS idx_reports_created ON reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sos_status ON sos_alerts (status);
