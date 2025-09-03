-- Twitter User ID to Username Mapping
-- Execute this in Supabase SQL Editor

-- Create Twitter user mapping table
CREATE TABLE IF NOT EXISTS twitter_users (
  id SERIAL PRIMARY KEY,
  user_id TEXT UNIQUE NOT NULL,
  username TEXT NOT NULL,
  display_name TEXT,
  followers_count INTEGER,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert the user mappings you provided
INSERT INTO twitter_users (user_id, username, display_name) VALUES
  ('216939636', 'AndrewYNg', 'Andrew Ng'),
  ('33836629', 'karpathy', 'Andrej Karpathy'),
  ('48008938', 'ylecun', 'Yann LeCun'),
  ('1605', 'sama', 'Sam Altman'),
  ('4398626122', 'OpenAI', 'OpenAI'),
  ('33838201', 'GoogleAI', 'Google AI')
ON CONFLICT (user_id) DO UPDATE SET
  username = EXCLUDED.username,
  display_name = EXCLUDED.display_name,
  updated_at = NOW();

-- Add twitter_username column to articles table if it doesn't exist
ALTER TABLE articles ADD COLUMN IF NOT EXISTS twitter_username TEXT;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_twitter_users_user_id ON twitter_users(user_id);
CREATE INDEX IF NOT EXISTS idx_articles_twitter_username ON articles(twitter_username);
