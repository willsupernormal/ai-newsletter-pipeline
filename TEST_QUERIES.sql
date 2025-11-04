-- ============================================
-- TEST QUERIES FOR SUPABASE
-- ============================================
-- Run these AFTER the migration to verify everything works
-- ============================================

-- ============================================
-- TEST 1: Verify Table Structure (5 AI fields should remain)
-- ============================================
-- Expected: 5 rows returned with the core AI fields
SELECT 
    column_name, 
    data_type,
    is_nullable
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

-- Expected Result:
-- business_impact    | text  | YES
-- companies_mentioned| ARRAY | YES
-- detailed_summary   | text  | YES
-- key_quotes         | jsonb | YES
-- specific_data      | jsonb | YES


-- ============================================
-- TEST 2: Verify Removed Columns Are Gone
-- ============================================
-- Expected: 0 rows (columns should be deleted)
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'digest_articles' 
  AND column_name IN (
    'strategic_context',
    'talking_points',
    'newsletter_angles',
    'technical_details'
  );

-- Expected Result: (empty - no rows)


-- ============================================
-- TEST 3: Verify Views Were Recreated
-- ============================================
-- Expected: 2 rows (both views should exist)
SELECT 
    table_name,
    view_definition
FROM information_schema.views 
WHERE table_name IN ('current_week_digest', 'pending_airtable_articles')
ORDER BY table_name;

-- Expected Result:
-- current_week_digest       | SELECT * FROM digest_articles WHERE...
-- pending_airtable_articles | SELECT * FROM digest_articles WHERE...


-- ============================================
-- TEST 4: Check Today's Articles (Data Integrity)
-- ============================================
-- Expected: 5 rows with populated AI fields
SELECT 
    id,
    title,
    digest_date,
    LENGTH(detailed_summary) as summary_length,
    LENGTH(business_impact) as impact_length,
    CASE 
        WHEN key_quotes IS NULL THEN 'NULL'
        WHEN jsonb_typeof(key_quotes) = 'array' THEN 'ARRAY (' || jsonb_array_length(key_quotes)::text || ' items)'
        ELSE 'OTHER'
    END as quotes_status,
    CASE 
        WHEN specific_data IS NULL THEN 'NULL'
        WHEN jsonb_typeof(specific_data) = 'array' THEN 'ARRAY (' || jsonb_array_length(specific_data)::text || ' items)'
        ELSE 'OTHER'
    END as data_status,
    ARRAY_LENGTH(companies_mentioned, 1) as companies_count,
    posted_to_slack,
    added_to_airtable
FROM digest_articles
WHERE digest_date = CURRENT_DATE
ORDER BY created_at;

-- Expected Result: 5 rows like:
-- id | title | digest_date | summary_length | impact_length | quotes_status | data_status | companies_count | posted_to_slack | added_to_airtable
-- ... | Mem0 raises $24M... | 2025-10-30 | 419 | 169 | ARRAY (2 items) | ARRAY (1 items) | 4 | true | false


-- ============================================
-- TEST 5: View Actual AI Content (Sample)
-- ============================================
-- Expected: Full AI-generated content for first article
SELECT 
    title,
    detailed_summary,
    business_impact,
    key_quotes,
    specific_data,
    companies_mentioned
FROM digest_articles
WHERE digest_date = CURRENT_DATE
ORDER BY created_at
LIMIT 1;

-- Expected Result: Full text in all fields


-- ============================================
-- TEST 6: Check All Columns in Table
-- ============================================
-- Expected: Should see all remaining columns (no removed ones)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'digest_articles'
ORDER BY ordinal_position;

-- Expected Result: Should include:
-- id, title, url, source_name, source_type, published_at, scraped_at, 
-- digest_date, posted_to_slack, slack_message_ts, added_to_airtable, 
-- airtable_record_id, detailed_summary, business_impact, key_quotes, 
-- specific_data, companies_mentioned, created_at, updated_at
-- 
-- Should NOT include:
-- strategic_context, talking_points, newsletter_angles, technical_details


-- ============================================
-- TEST 7: Check Indexes
-- ============================================
-- Expected: Should NOT see idx_digest_articles_technical
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'digest_articles'
ORDER BY indexname;

-- Expected Result: Should see:
-- idx_digest_articles_companies (GIN index)
-- idx_digest_articles_date
-- idx_digest_articles_slack
-- idx_digest_articles_url
-- idx_digest_articles_url_date
--
-- Should NOT see:
-- idx_digest_articles_technical


-- ============================================
-- TEST 8: Test View Functionality
-- ============================================
-- Expected: Articles from current week
SELECT 
    digest_date,
    COUNT(*) as article_count
FROM current_week_digest
GROUP BY digest_date
ORDER BY digest_date DESC;

-- Expected Result: Should show today's date with 5 articles


-- ============================================
-- TEST 9: Test Pending Airtable View
-- ============================================
-- Expected: Articles not yet added to Airtable
SELECT 
    digest_date,
    title,
    posted_to_slack,
    added_to_airtable
FROM pending_airtable_articles
WHERE digest_date = CURRENT_DATE
ORDER BY created_at;

-- Expected Result: 5 articles with added_to_airtable = false


-- ============================================
-- TEST 10: Comprehensive Data Quality Check
-- ============================================
-- Expected: All 5 articles should pass quality checks
SELECT 
    title,
    -- Check all required fields are populated
    CASE WHEN detailed_summary IS NOT NULL AND LENGTH(detailed_summary) > 100 
         THEN '✓' ELSE '✗' END as has_summary,
    CASE WHEN business_impact IS NOT NULL AND LENGTH(business_impact) > 50 
         THEN '✓' ELSE '✗' END as has_impact,
    CASE WHEN key_quotes IS NOT NULL 
         THEN '✓' ELSE '✗' END as has_quotes,
    CASE WHEN specific_data IS NOT NULL 
         THEN '✓' ELSE '✗' END as has_data,
    CASE WHEN companies_mentioned IS NOT NULL AND ARRAY_LENGTH(companies_mentioned, 1) > 0 
         THEN '✓' ELSE '✗' END as has_companies,
    -- Overall status
    CASE 
        WHEN detailed_summary IS NOT NULL 
         AND business_impact IS NOT NULL 
         AND key_quotes IS NOT NULL 
         AND specific_data IS NOT NULL 
         AND companies_mentioned IS NOT NULL 
        THEN '✅ PASS' 
        ELSE '❌ FAIL' 
    END as overall_status
FROM digest_articles
WHERE digest_date = CURRENT_DATE
ORDER BY created_at;

-- Expected Result: All 5 articles should show ✅ PASS


-- ============================================
-- QUICK SUCCESS CHECK (Run this first!)
-- ============================================
-- This single query tells you if everything is working
SELECT 
    '1. Table Structure' as test_name,
    CASE WHEN COUNT(*) = 5 THEN '✅ PASS' ELSE '❌ FAIL' END as status
FROM information_schema.columns 
WHERE table_name = 'digest_articles' 
  AND column_name IN ('detailed_summary', 'business_impact', 'key_quotes', 'specific_data', 'companies_mentioned')

UNION ALL

SELECT 
    '2. Removed Columns',
    CASE WHEN COUNT(*) = 0 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM information_schema.columns 
WHERE table_name = 'digest_articles' 
  AND column_name IN ('strategic_context', 'talking_points', 'newsletter_angles', 'technical_details')

UNION ALL

SELECT 
    '3. Views Exist',
    CASE WHEN COUNT(*) = 2 THEN '✅ PASS' ELSE '❌ FAIL' END
FROM information_schema.views 
WHERE table_name IN ('current_week_digest', 'pending_airtable_articles')

UNION ALL

SELECT 
    '4. Today Articles',
    CASE WHEN COUNT(*) = 5 THEN '✅ PASS' ELSE '❌ FAIL (' || COUNT(*)::text || ' articles)' END
FROM digest_articles
WHERE digest_date = CURRENT_DATE

UNION ALL

SELECT 
    '5. AI Fields Populated',
    CASE WHEN COUNT(*) = 5 THEN '✅ PASS' ELSE '❌ FAIL (' || COUNT(*)::text || ' with data)' END
FROM digest_articles
WHERE digest_date = CURRENT_DATE
  AND detailed_summary IS NOT NULL
  AND business_impact IS NOT NULL;

-- Expected Result:
-- 1. Table Structure    | ✅ PASS
-- 2. Removed Columns    | ✅ PASS
-- 3. Views Exist        | ✅ PASS
-- 4. Today Articles     | ✅ PASS
-- 5. AI Fields Populated| ✅ PASS


-- ============================================
-- If all tests pass, you're ready to test the button click!
-- ============================================
