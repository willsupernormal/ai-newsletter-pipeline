-- Migration: Remove unused AI fields from digest_articles table
-- Date: October 30, 2025
-- Purpose: Simplify to 5 core AI fields based on actual usage

-- Drop views first (they depend on the columns)
DROP VIEW IF EXISTS current_week_digest CASCADE;
DROP VIEW IF EXISTS pending_airtable_articles CASCADE;

-- Remove unused columns
ALTER TABLE digest_articles DROP COLUMN IF EXISTS strategic_context;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS talking_points;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS newsletter_angles;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS technical_details;

-- Drop associated indexes
DROP INDEX IF EXISTS idx_digest_articles_technical;

-- Recreate views
CREATE OR REPLACE VIEW current_week_digest AS
SELECT *
FROM digest_articles
WHERE digest_date >= DATE_TRUNC('week', CURRENT_DATE)::DATE
ORDER BY digest_date DESC, created_at ASC;

CREATE OR REPLACE VIEW pending_airtable_articles AS
SELECT *
FROM digest_articles
WHERE added_to_airtable = FALSE
ORDER BY digest_date DESC;

-- Update comments
COMMENT ON COLUMN digest_articles.business_impact IS 'AI analysis of business implications and strategic context';
COMMENT ON TABLE digest_articles IS 'Selected articles for daily digest with 5 core AI fields (detailed_summary, business_impact, key_quotes, specific_data, companies_mentioned)';

-- Verify remaining columns
-- Should have: detailed_summary, business_impact, key_quotes, specific_data, companies_mentioned
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'digest_articles' 
  AND column_name IN ('detailed_summary', 'business_impact', 'key_quotes', 'specific_data', 'companies_mentioned')
ORDER BY column_name;
