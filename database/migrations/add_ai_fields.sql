-- Migration: Add AI-generated fields to articles table
-- Date: October 30, 2025
-- Purpose: Add columns for AI-generated content analysis

-- Add AI summary fields
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS ai_summary TEXT,
ADD COLUMN IF NOT EXISTS ai_summary_short TEXT,
ADD COLUMN IF NOT EXISTS key_quotes JSONB,
ADD COLUMN IF NOT EXISTS key_metrics JSONB,
ADD COLUMN IF NOT EXISTS why_it_matters TEXT,
ADD COLUMN IF NOT EXISTS primary_theme TEXT,
ADD COLUMN IF NOT EXISTS content_type TEXT DEFAULT 'news',
ADD COLUMN IF NOT EXISTS selected_for_digest BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS key_themes TEXT[];

-- Add index for digest selection
CREATE INDEX IF NOT EXISTS idx_articles_selected_digest 
ON articles(selected_for_digest, scraped_at DESC);

-- Add index for content type
CREATE INDEX IF NOT EXISTS idx_articles_content_type 
ON articles(content_type);

-- Add index for primary theme
CREATE INDEX IF NOT EXISTS idx_articles_primary_theme 
ON articles(primary_theme);

-- Add comment for documentation
COMMENT ON COLUMN articles.ai_summary IS 'Full AI-generated summary of the article';
COMMENT ON COLUMN articles.ai_summary_short IS 'Short AI-generated summary (1-2 sentences)';
COMMENT ON COLUMN articles.key_quotes IS 'Important quotes extracted by AI (JSONB array)';
COMMENT ON COLUMN articles.key_metrics IS 'Key metrics and numbers mentioned (JSONB array)';
COMMENT ON COLUMN articles.why_it_matters IS 'AI-generated explanation of business impact';
COMMENT ON COLUMN articles.primary_theme IS 'Main theme/category identified by AI';
COMMENT ON COLUMN articles.content_type IS 'Type of content: news, analysis, research, opinion';
COMMENT ON COLUMN articles.selected_for_digest IS 'Whether article was selected for daily digest';
COMMENT ON COLUMN articles.key_themes IS 'Array of themes/topics identified by AI';

COMMIT;
