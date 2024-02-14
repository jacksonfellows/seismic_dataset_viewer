ALTER TABLE picks ADD user_id TEXT;
UPDATE picks SET user_id = 'jf787'; -- Assume I did all the existing picks.
