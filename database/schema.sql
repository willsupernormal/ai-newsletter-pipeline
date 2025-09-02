-- AI Newsletter Pipeline Database Schema
-- Execute this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Articles table - main content storage
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  url TEXT UNIQUE,
  content_excerpt TEXT,
  source_type TEXT NOT NULL CHECK (source_type IN ('rss', 'twitter', 'gmail_newsletter')),
  source_name TEXT NOT NULL,
  published_at TIMESTAMP,
  scraped_at TIMESTAMP DEFAULT NOW(),
  week_start_date DATE NOT NULL,
  relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 100),
  business_impact_score FLOAT CHECK (business_impact_score >= 0 AND business_impact_score <= 100),
  tags TEXT[],
  twitter_metrics JSONB,
  selected_for_newsletter BOOLEAN DEFAULT FALSE,
  curator_notes TEXT,
  newsletter_priority INTEGER CHECK (newsletter_priority >= 1 AND newsletter_priority <= 5),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Content sources tracking
CREATE TABLE content_sources (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('rss', 'twitter', 'gmail_newsletter')),
  identifier TEXT NOT NULL, -- URL for RSS, handle for Twitter, email for Gmail
  active BOOLEAN DEFAULT TRUE,
  last_processed TIMESTAMP,
  success_count INTEGER DEFAULT 0,
  failure_count INTEGER DEFAULT 0,
  average_relevance_score FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Weekly cycles tracking
CREATE TABLE weekly_cycles (
  id SERIAL PRIMARY KEY,
  week_start_date DATE UNIQUE NOT NULL,
  articles_collected INTEGER DEFAULT 0,
  articles_curated INTEGER DEFAULT 0,
  average_relevance_score FLOAT,
  top_themes TEXT[],
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Content processing logs
CREATE TABLE processing_logs (
  id SERIAL PRIMARY KEY,
  process_type TEXT NOT NULL,
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  status TEXT CHECK (status IN ('running', 'completed', 'failed')),
  articles_processed INTEGER DEFAULT 0,
  error_message TEXT,
  details JSONB
);

-- Performance indexes
CREATE INDEX idx_articles_week_relevance ON articles(week_start_date DESC, relevance_score DESC);
CREATE INDEX idx_articles_source_type ON articles(source_type, scraped_at DESC);
CREATE INDEX idx_articles_tags ON articles USING gin(tags);
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_selected ON articles(selected_for_newsletter, newsletter_priority);
CREATE INDEX idx_articles_published ON articles(published_at DESC);

-- Content sources indexes
CREATE INDEX idx_sources_type_active ON content_sources(type, active);
CREATE INDEX idx_sources_last_processed ON content_sources(last_processed);

-- Weekly cycles indexes
CREATE INDEX idx_weekly_cycles_date ON weekly_cycles(week_start_date DESC);

-- Useful views for MCP integration
CREATE VIEW current_week_articles AS 
SELECT *, 
       CASE WHEN relevance_score >= 80 THEN 'high'
            WHEN relevance_score >= 60 THEN 'medium' 
            ELSE 'low' END as priority_level
FROM articles 
WHERE week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
ORDER BY relevance_score DESC, scraped_at DESC;

-- Selected articles for newsletter
CREATE VIEW newsletter_articles AS
SELECT *
FROM articles
WHERE selected_for_newsletter = TRUE
  AND week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
ORDER BY newsletter_priority ASC, relevance_score DESC;

-- Source performance view
CREATE VIEW source_performance AS
SELECT 
  cs.name,
  cs.type,
  cs.identifier,
  cs.success_count,
  cs.failure_count,
  CASE 
    WHEN cs.success_count + cs.failure_count > 0 
    THEN ROUND((cs.success_count::float / (cs.success_count + cs.failure_count) * 100), 2)
    ELSE 0 
  END as success_rate,
  cs.average_relevance_score,
  COUNT(a.id) as articles_this_week,
  AVG(a.relevance_score) as avg_relevance_this_week
FROM content_sources cs
LEFT JOIN articles a ON a.source_name = cs.name 
  AND a.week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
WHERE cs.active = TRUE
GROUP BY cs.id, cs.name, cs.type, cs.identifier, cs.success_count, 
         cs.failure_count, cs.average_relevance_score
ORDER BY success_rate DESC, avg_relevance_this_week DESC NULLS LAST;

-- Weekly trends view
CREATE VIEW weekly_trends AS
SELECT 
  wc.week_start_date,
  wc.articles_collected,
  wc.articles_curated,
  wc.average_relevance_score,
  CASE 
    WHEN wc.articles_collected > 0 
    THEN ROUND((wc.articles_curated::float / wc.articles_collected * 100), 2)
    ELSE 0 
  END as curation_rate
FROM weekly_cycles wc
ORDER BY wc.week_start_date DESC;

-- Function to get current week start (Monday)
CREATE OR REPLACE FUNCTION get_current_week_start()
RETURNS DATE AS $$
BEGIN
  RETURN DATE_TRUNC('week', CURRENT_DATE)::DATE;
END;
$$ LANGUAGE plpgsql;

-- Function to update article timestamps
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to update timestamps
CREATE TRIGGER update_articles_modtime 
  BEFORE UPDATE ON articles 
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_content_sources_modtime 
  BEFORE UPDATE ON content_sources 
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_weekly_cycles_modtime 
  BEFORE UPDATE ON weekly_cycles 
  FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Insert default RSS content sources
INSERT INTO content_sources (name, type, identifier) VALUES
('VentureBeat AI', 'rss', 'https://venturebeat.com/category/ai/feed/'),
('AI Business', 'rss', 'https://aibusiness.com/rss.xml'),
('MIT Technology Review', 'rss', 'https://www.technologyreview.com/feed/'),
('TechCrunch AI', 'rss', 'https://techcrunch.com/category/artificial-intelligence/feed/'),
('The Register AI/ML', 'rss', 'https://www.theregister.com/software/ai_ml/headlines.atom'),
('Analytics India Magazine', 'rss', 'https://analyticsindiamag.com/feed/'),
('Harvard Business Review', 'rss', 'https://feeds.hbr.org/harvardbusiness');

-- Insert default Twitter accounts
INSERT INTO content_sources (name, type, identifier) VALUES
('Andrew Ng', 'twitter', 'AndrewYNg'),
('Andrej Karpathy', 'twitter', 'karpathy'),
('Yann LeCun', 'twitter', 'ylecun'),
('Sam Altman', 'twitter', 'sama'),
('OpenAI', 'twitter', 'OpenAI'),
('Google AI', 'twitter', 'GoogleAI');

-- Create RLS policies for security (optional, for production)
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_cycles ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_logs ENABLE ROW LEVEL SECURITY;

-- Allow all operations for service role (used by pipeline)
CREATE POLICY "Allow all for service role" ON articles FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service role" ON content_sources FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service role" ON weekly_cycles FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service role" ON processing_logs FOR ALL USING (auth.role() = 'service_role');

-- Allow read access for authenticated users (boss access via MCP)
CREATE POLICY "Allow read for authenticated users" ON articles FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Allow read for authenticated users" ON content_sources FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Allow read for authenticated users" ON weekly_cycles FOR SELECT USING (auth.role() = 'authenticated');

-- Allow update for newsletter curation
CREATE POLICY "Allow newsletter updates for authenticated users" ON articles 
  FOR UPDATE USING (auth.role() = 'authenticated')
  WITH CHECK (auth.role() = 'authenticated');

COMMIT;