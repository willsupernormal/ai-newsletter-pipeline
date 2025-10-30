-- Migration: Remove unused AI fields from digest_articles table
-- Date: October 30, 2025
-- Purpose: Simplify to 5 core AI fields based on actual usage

-- Remove unused columns
ALTER TABLE digest_articles DROP COLUMN IF EXISTS strategic_context;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS talking_points;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS newsletter_angles;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS technical_details;

-- Drop associated indexes
DROP INDEX IF EXISTS idx_digest_articles_technical;

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
