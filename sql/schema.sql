-- AccessiNav schema. Paste into Supabase > SQL Editor > Run.

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('user', 'volunteer', 'ngo')),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS volunteers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  verification_level VARCHAR(20) DEFAULT 'bronze',
  total_verified INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ngos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  organization_name TEXT NOT NULL,
  website TEXT,
  verification_level VARCHAR(20) DEFAULT 'gold',
  total_verified INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reported_by UUID REFERENCES users(id),
  report_source VARCHAR(20),
  description TEXT NOT NULL,
  photo_url TEXT,
  latitude FLOAT,
  longitude FLOAT,
  upvotes INT DEFAULT 0,
  verified_by UUID,
  verified_by_name TEXT,
  verified_by_type VARCHAR(20),
  verification_status VARCHAR(20) DEFAULT 'unverified',  -- 'unverified', 'verified', 'false'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sos_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  latitude FLOAT,
  longitude FLOAT,
  status VARCHAR(20) DEFAULT 'active',  -- 'active', 'resolved'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_geo ON reports (latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports (verification_status);

-- Row Level Security: backend uses the service_role key (bypasses RLS).
-- The frontend anon key may only READ reports and sos_alerts (for realtime).
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE volunteers ENABLE ROW LEVEL SECURITY;
ALTER TABLE ngos ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE sos_alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon read reports" ON reports FOR SELECT TO anon USING (true);
CREATE POLICY "anon read sos_alerts" ON sos_alerts FOR SELECT TO anon USING (true);

-- Table privileges (new Supabase projects don't grant these automatically).
GRANT ALL ON users, volunteers, ngos, reports, sos_alerts TO service_role;
GRANT SELECT ON reports, sos_alerts TO anon;

-- Realtime only on tables with no secrets (NOT users: it holds password_hash).
ALTER PUBLICATION supabase_realtime ADD TABLE reports, sos_alerts;
