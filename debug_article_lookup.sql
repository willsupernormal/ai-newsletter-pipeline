-- Debug: Check if article exists in digest_articles
SELECT 
    id,
    title,
    digest_date,
    posted_to_slack,
    added_to_airtable,
    created_at
FROM digest_articles
WHERE id = '72b09af6-a655-42de-b0d8-d2c1840665eb';

-- Check all articles from today
SELECT 
    id,
    title,
    digest_date
FROM digest_articles
WHERE digest_date = '2025-10-30'
ORDER BY created_at;

-- Check if article exists in OLD articles table
SELECT 
    id,
    title,
    scraped_at
FROM articles
WHERE id = '72b09af6-a655-42de-b0d8-d2c1840665eb';
