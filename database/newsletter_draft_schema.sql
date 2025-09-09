-- Newsletter Draft Schema
-- Execute this in Supabase SQL Editor

-- Newsletter drafts table - stores weekly newsletter drafts
CREATE TABLE newsletter_drafts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start_date DATE NOT NULL UNIQUE,
  draft_date TIMESTAMP DEFAULT NOW(),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published')),
  
  -- Newsletter sections as structured data
  top_headlines JSONB, -- Array of headline objects with title, summary, source_article_id
  deep_dive JSONB, -- Single deep dive object with expanded content
  operators_lens JSONB, -- Array of takeaway bullet points
  quick_hits JSONB, -- Optional array of short notes
  
  -- Metadata
  total_articles_considered INTEGER,
  selection_criteria JSONB, -- Criteria used for filtering
  ai_reasoning TEXT, -- AI's reasoning for selections
  
  -- Boss interaction
  boss_notes TEXT,
  boss_edits JSONB, -- Track boss modifications
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Newsletter sections breakdown for easier querying
CREATE TABLE newsletter_sections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  newsletter_draft_id UUID REFERENCES newsletter_drafts(id) ON DELETE CASCADE,
  section_type TEXT NOT NULL CHECK (section_type IN ('headline', 'deep_dive', 'operators_lens', 'quick_hit')),
  section_order INTEGER, -- Order within section type
  
  -- Content fields
  title TEXT,
  summary TEXT,
  content TEXT, -- Full content for deep dive
  source_article_id UUID REFERENCES articles(id),
  
  -- Metadata
  word_count INTEGER,
  tone_analysis JSONB,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Weekly article performance for newsletter selection
CREATE TABLE weekly_article_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  week_start_date DATE NOT NULL,
  
  -- Filtering criteria scores (0-100)
  relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 100),
  timeliness_score FLOAT CHECK (timeliness_score >= 0 AND timeliness_score <= 100),
  evidence_quality_score FLOAT CHECK (evidence_quality_score >= 0 AND evidence_quality_score <= 100),
  innovation_score FLOAT CHECK (innovation_score >= 0 AND innovation_score <= 100),
  
  -- Combined scores
  headline_potential_score FLOAT CHECK (headline_potential_score >= 0 AND headline_potential_score <= 100),
  deep_dive_potential_score FLOAT CHECK (deep_dive_potential_score >= 0 AND deep_dive_potential_score <= 100),
  
  -- Selection status
  selected_for_newsletter BOOLEAN DEFAULT FALSE,
  newsletter_section TEXT CHECK (newsletter_section IN ('headline', 'deep_dive', 'operators_lens', 'quick_hit')),
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_newsletter_drafts_week ON newsletter_drafts(week_start_date);
CREATE INDEX idx_newsletter_drafts_status ON newsletter_drafts(status);
CREATE INDEX idx_newsletter_sections_draft ON newsletter_sections(newsletter_draft_id);
CREATE INDEX idx_newsletter_sections_type ON newsletter_sections(section_type);
CREATE INDEX idx_weekly_scores_week ON weekly_article_scores(week_start_date);
CREATE INDEX idx_weekly_scores_article ON weekly_article_scores(article_id);
CREATE INDEX idx_weekly_scores_selected ON weekly_article_scores(selected_for_newsletter);

-- Views for easier querying
CREATE VIEW current_newsletter_draft AS
SELECT * FROM newsletter_drafts 
WHERE week_start_date = (
  SELECT MAX(week_start_date) FROM newsletter_drafts
);

CREATE VIEW newsletter_ready_articles AS
SELECT 
  a.*,
  was.relevance_score,
  was.timeliness_score,
  was.evidence_quality_score,
  was.innovation_score,
  was.headline_potential_score,
  was.deep_dive_potential_score
FROM articles a
JOIN weekly_article_scores was ON a.id = was.article_id
WHERE was.week_start_date = (
  SELECT DATE_TRUNC('week', CURRENT_DATE)::DATE
)
ORDER BY was.headline_potential_score DESC;

-- Comments
COMMENT ON TABLE newsletter_drafts IS 'Weekly newsletter drafts with structured sections';
COMMENT ON TABLE newsletter_sections IS 'Individual sections within newsletter drafts';
COMMENT ON TABLE weekly_article_scores IS 'Article scoring for newsletter selection criteria';
COMMENT ON VIEW newsletter_ready_articles IS 'Articles scored and ready for newsletter selection';
