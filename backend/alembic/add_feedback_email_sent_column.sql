-- Migration: Add feedback_email_sent column to contractors table
-- DISC-147: Feedback Drip Tracking
-- This column tracks which feedback email has been sent (day 3, day 7, etc.)

-- Add the column if it doesn't exist
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS feedback_email_sent INTEGER;

-- Verify the column was added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'contractors'
AND column_name = 'feedback_email_sent';
