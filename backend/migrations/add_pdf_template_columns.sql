-- DISC-028: Add PDF template columns to contractors table
-- Migration: Add pdf_template and pdf_accent_color columns

-- Add pdf_template column with default 'modern'
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS pdf_template VARCHAR(50) DEFAULT 'modern';

-- Add pdf_accent_color column (nullable)
ALTER TABLE contractors
ADD COLUMN IF NOT EXISTS pdf_accent_color VARCHAR(50);

-- Create index for faster lookups (optional, but good practice)
CREATE INDEX IF NOT EXISTS idx_contractors_pdf_template ON contractors(pdf_template);

-- Set existing contractors to 'modern' template if null
UPDATE contractors
SET pdf_template = 'modern'
WHERE pdf_template IS NULL;
