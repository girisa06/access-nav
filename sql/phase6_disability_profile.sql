-- Phase 6: per-account accessibility profile. Paste into Supabase > SQL Editor > Run.
-- NULL means "not chosen yet" (new accounts are asked on first sign-in), so there is deliberately no DEFAULT.

ALTER TABLE users ADD COLUMN IF NOT EXISTS disability_profile VARCHAR(30);

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_disability_profile_check;
ALTER TABLE users ADD CONSTRAINT users_disability_profile_check
  CHECK (disability_profile IS NULL OR disability_profile IN ('wheelchair', 'cognitive', 'hearing_impaired', 'visually_impaired'));
