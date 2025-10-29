# Complete Setup Guide

> **Everything you need to set up the AI Newsletter Pipeline from scratch.**

**Last Updated:** October 29, 2025

---

## 📋 **Prerequisites**

- Python 3.11+
- Git
- GitHub account
- Supabase account
- OpenAI API key
- Slack workspace (admin access)
- Airtable account
- Railway account (for webhook server)

---

## 🚀 **Setup Steps**

### **1. Clone Repository**

```bash
git clone https://github.com/willsupernormal/ai-newsletter-pipeline.git
cd ai-newsletter-pipeline
```

### **2. Install Dependencies**

```bash
pip3 install -r requirements.txt
```

**Key dependencies:**
- `supabase` - Database client
- `openai` - AI filtering
- `aiohttp` - Async HTTP
- `feedparser` - RSS parsing
- `pyairtable` - Airtable client
- `fastapi` - Webhook server
- `brotli` - Compression support

### **3. Configure Environment Variables**

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# ============================================
# SUPABASE (Database)
# ============================================
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# ============================================
# OPENAI (AI Filtering)
# ============================================
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4-turbo-preview

# ============================================
# SLACK (Posting & Buttons)
# ============================================
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# ============================================
# AIRTABLE (Content Pipeline)
# ============================================
AIRTABLE_API_KEY=xxx
AIRTABLE_BASE_ID=xxx
AIRTABLE_TABLE_NAME=Content Pipeline

# ============================================
# RSS SETTINGS (Optional)
# ============================================
RSS_REQUEST_TIMEOUT=30
RSS_MAX_RETRIES=3
MAX_ARTICLES_PER_SOURCE=50
MAX_CONCURRENT_REQUESTS=10

# ============================================
# AI SETTINGS (Optional)
# ============================================
STAGE1_TARGET_COUNT=10
STAGE2_TARGET_COUNT=5
CONTENT_EXCERPT_LENGTH=500
```

---

## 🗄️ **Supabase Setup**

### **1. Create Supabase Project**

1. Go to https://supabase.com
2. Create new project
3. Note your project URL and keys

### **2. Create Database Tables**

Run this SQL in Supabase SQL Editor:

```sql
-- ============================================
-- CONTENT SOURCES TABLE
-- ============================================
CREATE TABLE content_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('rss', 'twitter', 'gmail')),
    identifier TEXT NOT NULL, -- URL for RSS, handle for Twitter, etc.
    active BOOLEAN DEFAULT TRUE,
    last_processed TIMESTAMP WITH TIME ZONE,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(type, identifier)
);

-- Index for faster queries
CREATE INDEX idx_content_sources_active ON content_sources(active);
CREATE INDEX idx_content_sources_type ON content_sources(type);

-- ============================================
-- ARTICLES TABLE
-- ============================================
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    content_excerpt TEXT,
    full_content TEXT,
    word_count INTEGER,
    tags TEXT[],
    
    -- AI-generated fields
    ai_summary_short TEXT,
    ai_summary_long TEXT,
    key_themes TEXT[],
    key_metrics JSONB,
    why_it_matters TEXT,
    content_type TEXT,
    
    -- Metadata
    selected_for_digest BOOLEAN DEFAULT FALSE,
    added_to_airtable BOOLEAN DEFAULT FALSE,
    airtable_record_id TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_selected ON articles(selected_for_digest);
CREATE INDEX idx_articles_source ON articles(source_name);

-- ============================================
-- DAILY DIGESTS TABLE
-- ============================================
CREATE TABLE daily_digests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    digest_date DATE NOT NULL UNIQUE,
    article_ids UUID[] NOT NULL,
    summary TEXT,
    key_insights TEXT[],
    posted_to_slack BOOLEAN DEFAULT FALSE,
    slack_message_ts TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for date queries
CREATE INDEX idx_daily_digests_date ON daily_digests(digest_date DESC);

-- ============================================
-- AUTO-UPDATE TIMESTAMPS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_content_sources_updated_at
    BEFORE UPDATE ON content_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_digests_updated_at
    BEFORE UPDATE ON daily_digests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### **3. Add Initial RSS Sources**

```bash
python3 scripts/add_rss_source.py add "VentureBeat AI" "https://venturebeat.com/category/ai/feed/"
python3 scripts/add_rss_source.py add "TechCrunch AI" "https://techcrunch.com/category/artificial-intelligence/feed/"
python3 scripts/add_rss_source.py add "MIT Technology Review" "https://www.technologyreview.com/feed/"
# ... add more sources
```

Or run the bulk import:
```bash
python3 scripts/fix_and_add_sources.py
```

---

## 💬 **Slack Setup**

### **1. Create Slack App**

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "AI Digest Manager"
4. Select your workspace

### **2. Configure OAuth & Permissions**

**Bot Token Scopes:**
- `chat:write` - Post messages
- `chat:write.public` - Post to public channels
- `channels:read` - Read channel info

**Install app to workspace** and copy the Bot Token (`xoxb-...`)

### **3. Configure Interactivity**

1. Enable "Interactivity & Shortcuts"
2. Request URL: `https://your-railway-app.railway.app/slack/interactions`
3. Save changes

### **4. Create Incoming Webhook**

1. Go to "Incoming Webhooks"
2. Activate webhooks
3. Add to channel: `#ai-daily-digest`
4. Copy webhook URL

### **5. Get Signing Secret**

1. Go to "Basic Information"
2. Copy "Signing Secret"

### **6. Update Environment Variables**

```bash
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

---

## 📊 **Airtable Setup**

### **1. Create Airtable Base**

1. Go to https://airtable.com
2. Create new base: "Content Pipeline"
3. Create table: "Content Pipeline"

### **2. Configure Fields**

**Required fields:**
- `Title` (Single line text)
- `URL` (URL)
- `Source` (Single line text)
- `Published Date` (Date)
- `Added Date` (Date)
- `Status` (Single select: Draft, In Progress, Published)
- `Content Excerpt` (Long text)
- `Full Content` (Long text)
- `Word Count` (Number)
- `AI Summary` (Long text)
- `Key Themes` (Multiple select)
- `Why It Matters` (Long text)
- `Content Type` (Single select)
- `Tags` (Multiple select)

### **3. Get API Credentials**

1. Go to https://airtable.com/account
2. Generate API key
3. Get Base ID from base URL: `https://airtable.com/appXXXXXXXXXXXXXX`

### **4. Update Environment Variables**

```bash
AIRTABLE_API_KEY=keyXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME=Content Pipeline
```

---

## 🚂 **Railway Setup (Webhook Server)**

### **1. Create Railway Project**

1. Go to https://railway.app
2. Create new project
3. Deploy from GitHub repo

### **2. Configure Environment Variables**

Add all environment variables from `.env`:
- SUPABASE_URL
- SUPABASE_KEY
- SLACK_BOT_TOKEN
- SLACK_SIGNING_SECRET
- AIRTABLE_API_KEY
- AIRTABLE_BASE_ID
- AIRTABLE_TABLE_NAME

### **3. Configure Start Command**

```bash
uvicorn api.webhook_server:app --host 0.0.0.0 --port $PORT
```

### **4. Get Railway URL**

Copy the generated URL (e.g., `https://your-app.railway.app`)

### **5. Update Slack Interactivity URL**

Go back to Slack app settings:
- Interactivity URL: `https://your-app.railway.app/slack/interactions`

---

## ⚙️ **GitHub Actions Setup**

### **1. Add GitHub Secrets**

Go to repository Settings → Secrets → Actions:

```
SUPABASE_URL
SUPABASE_KEY
SUPABASE_SERVICE_KEY
OPENAI_API_KEY
SLACK_WEBHOOK_URL
SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET
AIRTABLE_API_KEY
AIRTABLE_BASE_ID
AIRTABLE_TABLE_NAME
```

### **2. Verify Workflow**

The workflow file `.github/workflows/daily-scrape.yml` is already configured.

**Schedule:** Daily at 7 AM AEST (9 PM UTC previous day)

**Manual trigger:** Available via GitHub Actions UI

---

## ✅ **Verification**

### **1. Test Locally**

```bash
python3 scripts/run_ai_digest_pipeline.py force
```

**Expected output:**
```
🎉 AI Daily Digest Created for 2025-10-29
📊 Processing Summary:
  • Total articles collected: 180
  • Stage 1 filtering: 180 → 10
  • Stage 2 final selection: 10 → 5
  • Digest ID: xxx

📰 Selected Articles:
  1. [Article title]
  ...

💡 Key Insights:
  • Insight 1
  ...

📱 Posted to Slack: #ai-daily-digest
```

### **2. Test Slack Buttons**

1. Check Slack for digest post
2. Click "Add to Pipeline" button
3. Button should change to "Processing..." then "✅ Added"
4. Check Airtable for new record

### **3. Test GitHub Actions**

1. Go to Actions tab in GitHub
2. Manually trigger workflow
3. Check logs for errors
4. Verify Slack post

---

## 🐛 **Common Setup Issues**

### **"Module not found" errors**
```bash
pip3 install -r requirements.txt
```

### **"Supabase connection failed"**
- Verify SUPABASE_URL and SUPABASE_KEY
- Check if tables exist
- Verify network access

### **"Slack webhook failed"**
- Verify SLACK_WEBHOOK_URL is correct
- Check if channel exists
- Verify app is installed

### **"Airtable API error"**
- Verify AIRTABLE_API_KEY
- Check AIRTABLE_BASE_ID
- Verify table name matches

### **"Railway deployment failed"**
- Check environment variables
- Verify start command
- Check logs for errors

---

## 📚 **Next Steps**

After setup:

1. **Read [OPERATIONS.md](OPERATIONS.md)** - Daily operations guide
2. **Monitor first digest** - Check GitHub Actions logs
3. **Test Slack buttons** - Verify Airtable integration
4. **Add more sources** - Use `add_rss_source.py`

---

## 🔗 **Useful Links**

- **Supabase Dashboard:** https://supabase.com/dashboard
- **Slack API:** https://api.slack.com/apps
- **Airtable API:** https://airtable.com/api
- **Railway Dashboard:** https://railway.app/dashboard
- **GitHub Actions:** https://github.com/[your-repo]/actions

---

**Setup complete! 🎉**

**Next:** Read [OPERATIONS.md](OPERATIONS.md) for daily operations.

