-- Migration: Create digest_articles table for selected daily articles
-- Date: October 30, 2025
-- Purpose: Store only the 5 selected articles per day with full AI enrichment

-- Create new table for digest articles
CREATE TABLE IF NOT EXISTS digest_articles (
  -- Primary identification
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('rss', 'twitter', 'gmail_newsletter')),
  
  -- Timing
  published_at TIMESTAMP,
  scraped_at TIMESTAMP DEFAULT NOW(),
  digest_date DATE NOT NULL,
  
  -- Slack metadata
  posted_to_slack BOOLEAN DEFAULT FALSE,
  slack_message_ts TEXT,
  added_to_airtable BOOLEAN DEFAULT FALSE,
  airtable_record_id TEXT,
  
  -- AI-generated analysis (from your JSON structure)
  detailed_summary TEXT,
  business_impact TEXT,
  strategic_context TEXT,
  
  -- Structured data (JSONB for flexibility)
  key_quotes JSONB,           -- [{quote: "", speaker: "", context: ""}]
  specific_data JSONB,         -- [{metric: "", value: "", context: ""}]
  
  -- Arrays for easy querying
  talking_points TEXT[],
  newsletter_angles TEXT[],
  technical_details TEXT[],
  companies_mentioned TEXT[],
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_digest_articles_date ON digest_articles(digest_date DESC);
CREATE INDEX idx_digest_articles_companies ON digest_articles USING gin(companies_mentioned);
CREATE INDEX idx_digest_articles_technical ON digest_articles USING gin(technical_details);
CREATE INDEX idx_digest_articles_url ON digest_articles(url);
CREATE INDEX idx_digest_articles_slack ON digest_articles(posted_to_slack, digest_date DESC);

-- Unique constraint: same URL can't be in digest twice on same date
CREATE UNIQUE INDEX idx_digest_articles_url_date ON digest_articles(url, digest_date);

-- Auto-update timestamp trigger
CREATE TRIGGER update_digest_articles_updated_at
  BEFORE UPDATE ON digest_articles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE digest_articles IS 'Selected articles for daily digest with full AI enrichment (5 per day)';
COMMENT ON COLUMN digest_articles.detailed_summary IS 'Full AI-generated summary of the article';
COMMENT ON COLUMN digest_articles.business_impact IS 'AI analysis of business implications';
COMMENT ON COLUMN digest_articles.strategic_context IS 'Strategic context and industry relevance';
COMMENT ON COLUMN digest_articles.key_quotes IS 'Important quotes extracted by AI (JSONB array)';
COMMENT ON COLUMN digest_articles.specific_data IS 'Key metrics, numbers, and data points (JSONB array)';
COMMENT ON COLUMN digest_articles.talking_points IS 'Discussion points for the article';
COMMENT ON COLUMN digest_articles.newsletter_angles IS 'Potential angles for newsletter coverage';
COMMENT ON COLUMN digest_articles.technical_details IS 'Technical concepts and details mentioned';
COMMENT ON COLUMN digest_articles.companies_mentioned IS 'Companies and organizations mentioned';

-- View for current week's digest
CREATE OR REPLACE VIEW current_week_digest AS
SELECT *
FROM digest_articles
WHERE digest_date >= DATE_TRUNC('week', CURRENT_DATE)::DATE
ORDER BY digest_date DESC, created_at ASC;

-- View for articles ready to add to Airtable
CREATE OR REPLACE VIEW pending_airtable_articles AS
SELECT *
FROM digest_articles
WHERE added_to_airtable = FALSE
ORDER BY digest_date DESC;

COMMIT;
