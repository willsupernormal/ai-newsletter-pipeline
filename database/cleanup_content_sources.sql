-- Clean up content_sources table to remove Twitter entries
-- Twitter sources should be managed via twitter_users table instead

-- Remove Twitter entries from content_sources table
DELETE FROM content_sources WHERE type = 'twitter';

-- Add some sample RSS feeds to content_sources table
INSERT INTO content_sources (name, type, identifier, active) VALUES
  ('TechCrunch', 'rss', 'https://techcrunch.com/feed/', true),
  ('VentureBeat', 'rss', 'https://venturebeat.com/feed/', true),
  ('MIT Technology Review', 'rss', 'https://www.technologyreview.com/feed/', true),
  ('Harvard Business Review - AI', 'rss', 'https://hbr.org/topic/artificial-intelligence/feed', true),
  ('Analytics India Magazine', 'rss', 'https://analyticsindiamag.com/feed/', true),
  ('AI Business', 'rss', 'https://aibusiness.com/rss.xml', true),
  ('The Information - AI', 'rss', 'https://www.theinformation.com/articles/artificial-intelligence?format=rss', true),
  ('Reuters Technology', 'rss', 'https://www.reuters.com/technology/feed/', true),
  ('Ars Technica', 'rss', 'https://feeds.arstechnica.com/arstechnica/index', true),
  ('Wired AI', 'rss', 'https://www.wired.com/feed/category/artificial-intelligence/latest/rss', true)
ON CONFLICT (name, type, identifier) DO NOTHING;

-- Update the schema comment to clarify Twitter vs RSS separation
COMMENT ON TABLE content_sources IS 'RSS and Gmail newsletter sources. Twitter sources are managed via twitter_users table.';

-- Add constraint to prevent Twitter entries in content_sources
ALTER TABLE content_sources ADD CONSTRAINT no_twitter_in_content_sources 
  CHECK (type != 'twitter');
