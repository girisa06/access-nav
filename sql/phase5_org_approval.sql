-- Organization approval. Paste into Supabase > SQL Editor > Run.
-- Organizations can sign up as before but cannot verify reports until an admin approves them.

ALTER TABLE ngos ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE ngos ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_ngos_is_verified ON ngos (is_verified);
