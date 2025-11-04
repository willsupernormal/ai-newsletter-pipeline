# AI Newsletter Pipeline

> **Automated daily AI news digest with intelligent filtering, Slack integration, and Airtable content pipeline**

**Status:** ✅ Production | **Last Updated:** November 4, 2025

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)

---

## Overview

This system automatically:
1. **Scrapes** 180+ AI articles daily from 31 RSS feeds
2. **Filters** to top 5 articles using GPT-4 multi-stage selection
3. **Posts** digest to Slack with interactive buttons
4. **Enables** one-click article addition to Airtable content pipeline

### Key Features

- ✅ **Multi-stage AI filtering** - GPT-4 selects best 5 from 180+ articles
- ✅ **5 AI-generated fields** - Summary, business impact, quotes, data, companies
- ✅ **Interactive Slack modal** - Select theme, content type, and angle
- ✅ **Airtable integration** - One-click article addition with full metadata
- ✅ **Railway webhook server** - Handles Slack button clicks in production
- ✅ **Supabase storage** - Central database for articles and AI data

---

## System Architecture

### Components

```
┌──────────────────────────────────────────────────────────────┐
│                    1. LOCAL MACHINE                          │
│                  (Digest Generation)                         │
├──────────────────────────────────────────────────────────────┤
│  • Scrapes 180 articles from 31 RSS feeds                   │
│  • AI Stage 1: Filter to 18 articles                        │
│  • AI Stage 2: Select 5 + generate AI fields                │
│  • Store in Supabase digest_articles table                  │
│  • Post to Slack with "Add to Pipeline" buttons             │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                      2. SLACK                                │
│                  (User Interface)                            │
├──────────────────────────────────────────────────────────────┤
│  • User sees 5 articles with buttons                        │
│  • Clicks "Add to Pipeline"                                 │
│  • Modal opens with 3 optional fields:                      │
│    - Theme (10 options)                                     │
│    - Content Type (6 options)                               │
│    - Your Angle (free text)                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                     3. RAILWAY                               │
│              (Webhook Server - Production)                   │
├──────────────────────────────────────────────────────────────┤
│  • Receives button click webhook                            │
│  • Opens modal for user input                               │
│  • On submit: Fetches article from Supabase                 │
│  • Scrapes full article text                                │
│  • Pushes to Airtable with all fields                       │
│  • Posts success message to Slack                           │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                    4. AIRTABLE                               │
│              (Content Management System)                     │
├──────────────────────────────────────────────────────────────┤
│  Article stored with:                                        │
│  • Basic: Title, URL, Source, Date, Word Count              │
│  • AI Fields (5): Summary, Impact, Quotes, Data, Companies  │
│  • User Fields (3): Theme, Content Type, Your Angle         │
│  • Full Article Text (scraped)                              │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Language:** Python 3.11+
- **AI:** OpenAI GPT-4
- **Database:** Supabase (PostgreSQL)
- **Webhook Server:** Railway (FastAPI)
- **Messaging:** Slack API
- **CMS:** Airtable
- **Scraping:** newspaper3k, BeautifulSoup4

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Supabase account
- Slack workspace with bot
- Airtable account
- Railway account (for production)

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd ai-newsletter-pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Setup

Create `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Airtable
AIRTABLE_API_KEY=key...
AIRTABLE_BASE_ID=app...

# Railway (production only)
WEBHOOK_PORT=8000
```

### 3. Database Setup

1. Create Supabase project at https://supabase.com
2. Run migration in Supabase SQL Editor:

```bash
# Copy contents of database/migrations/create_digest_articles_table.sql
# Paste into Supabase SQL Editor and run
```

### 4. Airtable Setup

Create "Content Pipeline" table with these fields:

**Basic Fields:**
- Title (Single line text)
- URL (URL)
- Source (Single line text)
- Date (Date)
- Stage (Single select: 📥 Saved, 📝 Writing, ✅ Published)
- Priority (Single select: 🔴 High, 🟡 Medium, 🟢 Low)

**AI-Generated Fields (5):**
- Detailed Summary (Long text)
- Business Impact (Long text)
- Key Quotes (Long text)
- Specific Data (Long text)
- Companies Mentioned (Single line text)

**User-Selected Fields (3):**
- Theme (Single select: AI Governance, Vendor Lock-in, Data Strategy, etc.)
- Content Type (Single select: News, Research, Opinion, Analysis, Case Study, Tutorial)
- Your Angle (Long text)

**Scraped Fields:**
- Full Article Text (Long text)
- Word Count (Number)

**Metadata:**
- Supabase ID (Single line text)
- Airtable Record ID (Single line text)

### 5. Slack App Setup

1. Create Slack app at https://api.slack.com/apps
2. Enable **Interactivity**:
   - Request URL: `https://your-railway-app.up.railway.app/slack/interactions`
3. Add **Bot Token Scopes**:
   - `chat:write`
   - `channels:read`
   - `im:write`
4. Install app to workspace
5. Copy tokens to `.env`

### 6. Railway Deployment

1. Create Railway project at https://railway.app
2. Connect GitHub repo
3. Add environment variables (same as `.env`)
4. Deploy automatically on push to `main`

---

## How It Works

### Daily Digest Generation (Local)

Run manually:

```bash
# Generate and post digest
PYTHONPATH=/path/to/project python3 scripts/run_ai_digest_pipeline.py force

# Show recent digests
PYTHONPATH=/path/to/project python3 scripts/run_ai_digest_pipeline.py show
```

**Process:**
1. Scrapes 31 RSS feeds → ~180 articles
2. **Stage 1 AI Filter:** GPT-4 selects top 18 articles
3. **Stage 2 AI Filter:** GPT-4 selects final 5 + generates:
   - Detailed summary (400-450 chars)
   - Business impact (120-170 chars)
   - Key quotes (JSONB array)
   - Specific data/metrics (JSONB array)
   - Companies mentioned (text array)
4. Stores in Supabase `digest_articles` table
5. Posts to Slack #ai-daily-digest with buttons

### Button Click Flow (Railway)

**User clicks "Add to Pipeline":**
1. Railway receives webhook
2. Opens Slack modal with 3 optional fields:
   - **Theme:** AI Governance, Vendor Lock-in, Data Strategy, Enterprise Adoption, Model Performance, Regulatory Compliance, Technical Innovation, Business Strategy, Ethics & Safety, Market Trends
   - **Content Type:** News, Research, Opinion, Analysis, Case Study, Tutorial
   - **Your Angle:** Free-form text input
3. User fills fields (all optional) and clicks Submit
4. Modal closes, processing starts in background
5. Railway:
   - Fetches article from Supabase `digest_articles`
   - Scrapes full article text from original URL
   - Prepares Airtable data with all fields
   - Creates Airtable record
   - Updates Supabase (`added_to_airtable = true`)
   - Posts success message to Slack channel

**Result:** Article appears in Airtable with:
- 5 AI-generated fields
- 3 user-selected fields
- Full article text
- All metadata

---

## Deployment

### Local Development

No deployment needed. Run scripts manually:

```bash
# Generate digest
PYTHONPATH=/path/to/project python3 scripts/run_ai_digest_pipeline.py force
```

### Railway Production

**Automatic deployment on git push:**

```bash
git add .
git commit -m "your message"
git push origin main
```

**Railway auto-deploys in 2-3 minutes.**

### Deployment Checklist

**Before ANY code change:**
1. ✅ Identify which components affected (local vs Railway)
2. ✅ Check if Supabase schema changes needed
3. ✅ Check if Airtable fields need updating
4. ✅ Review all files that import/use changed code

**After code changes:**
1. ✅ Commit and push to GitHub
2. ✅ Wait 2-3 minutes for Railway deployment
3. ✅ Check Railway logs for successful startup
4. ✅ Test Slack button click end-to-end
5. ✅ Verify Airtable data populates correctly

**Files that require Railway deployment:**
- `services/slack_webhook_handler.py`
- `services/airtable_client.py`
- `database/digest_storage.py`
- `api/webhook_server.py`
- Any file imported by the above

### Verifying Deployment

**Check Railway logs:**
```
✓ Server running on port 8000
✓ digest_storage.py loaded
✓ SlackWebhookHandler initialized
```

**Test button click:**
1. Go to Slack #ai-daily-digest
2. Click "Add to Pipeline"
3. Fill modal and submit
4. Check Airtable for new record

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed debugging guide.

### Common Issues

**Button click fails:**
- Check Railway logs for errors
- Verify article exists in Supabase `digest_articles`
- Verify Airtable fields exist with exact names
- Check Railway environment variables

**Modal doesn't open:**
- Verify Slack app has correct Request URL
- Check Railway deployment is live
- Verify `SLACK_BOT_TOKEN` is correct

**Article not in Airtable:**
- Check Railway logs for "Failed to create Airtable record"
- Verify field names match exactly (case-sensitive)
- Check field types in Airtable
- Verify `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID`

**Digest generation fails:**
- Check OpenAI API key
- Verify Supabase connection
- Check RSS feeds are accessible
- Verify Slack webhook URL

---

## File Structure

```
ai-newsletter-pipeline/
├── README.md                          # This file
├── CHANGELOG.md                       # Version history and changes
├── TROUBLESHOOTING.md                 # Detailed debugging guide
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables (not in git)
├── .env.example                      # Environment template
│
├── api/
│   └── webhook_server.py             # Railway FastAPI server
│
├── config/
│   └── settings.py                   # Configuration management
│
├── database/
│   ├── digest_storage.py             # Digest CRUD operations
│   ├── supabase_simple.py            # Simplified Supabase client
│   └── migrations/
│       ├── create_digest_articles_table.sql
│       └── update_digest_articles_remove_fields.sql
│
├── processors/
│   ├── multi_stage_digest.py         # Two-stage AI filtering
│   ├── data_aggregator.py            # Multi-source aggregation
│   └── theme_extractor.py            # Topic analysis
│
├── scrapers/
│   ├── rss_scraper.py                # RSS feed processing
│   └── article_scraper.py            # Full article scraping
│
├── services/
│   ├── slack_webhook_handler.py      # Slack interaction handler
│   ├── airtable_client.py            # Airtable integration
│   └── slack_poster.py               # Slack message posting
│
├── scripts/
│   └── run_ai_digest_pipeline.py     # Main digest generation script
│
└── utils/
    ├── logger.py                     # Logging configuration
    └── helpers.py                    # Utility functions
```

---

## Key Concepts

### AI Fields (5)

Generated by GPT-4 during digest creation:

1. **Detailed Summary** (400-450 chars) - Comprehensive article summary
2. **Business Impact** (120-170 chars) - Business implications and strategic context
3. **Key Quotes** (JSONB) - Important quotes from article
4. **Specific Data** (JSONB) - Metrics, numbers, statistics
5. **Companies Mentioned** (Array) - Company names referenced

### User Fields (3)

Selected by user in Slack modal:

1. **Theme** - Strategic category (AI Governance, Vendor Lock-in, etc.)
2. **Content Type** - Article format (News, Research, Opinion, etc.)
3. **Your Angle** - Custom perspective or notes

### Data Flow

**Local → Supabase → Slack → Railway → Airtable**

1. **Local:** Generate digest, store in Supabase, post to Slack
2. **Slack:** User clicks button, modal opens
3. **Railway:** Process modal submission, scrape article, push to Airtable
4. **Airtable:** Final content repository with all fields

### Critical Dependencies

**Supabase ↔ Code ↔ Airtable**

When changing AI fields, you MUST update all 3:
1. Supabase schema (database columns)
2. Code (field mappings)
3. Airtable (field definitions)

---

## Support

For issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or check:
- Railway logs: https://railway.app
- Supabase logs: https://supabase.com
- Slack API logs: https://api.slack.com/apps

---

## License

MIT License - see LICENSE file for details
