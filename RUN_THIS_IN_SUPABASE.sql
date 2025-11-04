-- ============================================
-- RUN THIS IN SUPABASE SQL EDITOR
-- ============================================
-- Purpose: Remove 4 unused AI fields from digest_articles table
-- Date: October 30, 2025
-- ============================================

-- Step 1: Drop views first (they depend on the columns)
DROP VIEW IF EXISTS current_week_digest CASCADE;
DROP VIEW IF EXISTS pending_airtable_articles CASCADE;

-- Step 2: Remove unused columns
ALTER TABLE digest_articles DROP COLUMN IF EXISTS strategic_context;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS talking_points;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS newsletter_angles;
ALTER TABLE digest_articles DROP COLUMN IF EXISTS technical_details;

-- Step 3: Drop unused index
DROP INDEX IF EXISTS idx_digest_articles_technical;

-- Step 4: Recreate views with only the 5 core AI fields
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

-- Step 5: Update table comment
COMMENT ON TABLE digest_articles IS 'Selected articles for daily digest with 5 core AI fields (detailed_summary, business_impact, key_quotes, specific_data, companies_mentioned)';

-- Step 6: Update business_impact column comment
COMMENT ON COLUMN digest_articles.business_impact IS 'AI analysis of business implications and strategic context (combined field)';

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify remaining AI columns (should return 5 rows)
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'digest_articles' 
  AND column_name IN (
    'detailed_summary', 
    'business_impact', 
    'key_quotes', 
    'specific_data', 
    'companies_mentioned'
  )
ORDER BY column_name;

-- Verify removed columns are gone (should return 0 rows)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'digest_articles' 
  AND column_name IN (
    'strategic_context',
    'talking_points',
    'newsletter_angles',
    'technical_details'
  );

-- Check current data (should show 5 articles from today)
SELECT 
    title,
    LENGTH(detailed_summary) as summary_len,
    LENGTH(business_impact) as impact_len,
    ARRAY_LENGTH(companies_mentioned, 1) as companies_count,
    digest_date
FROM digest_articles
WHERE digest_date = CURRENT_DATE
ORDER BY created_at;

-- ============================================
-- SUCCESS!
-- ============================================
-- If all queries run without errors, you're done!
-- Next: Create 5 fields in Airtable (see SIMPLIFIED_AI_FIELDS.md)
-- ============================================
