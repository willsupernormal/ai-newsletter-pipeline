# 🤖 AI Newsletter Pipeline - Complete System Overview

**Last Updated**: October 23, 2025  
**Status**: ✅ Production Ready & Running Daily

---

## 📋 Executive Summary

This is an **automated AI newsletter pipeline** that:
1. **Scrapes** 50+ sources daily (RSS, Twitter, Gmail newsletters)
2. **Processes** content with AI filtering (2-stage OpenAI evaluation)
3. **Generates** daily digests with top 5 articles + AI summaries
4. **Creates** weekly newsletter drafts every Sunday
5. **Enables** boss interaction via Claude MCP for curation

**Current State**: System is live on GitHub Actions, running daily at 7 AM Melbourne time (9 PM UTC previous day).

---

## 🏗️ System Architecture

### Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY AUTOMATED PIPELINE                  │
│                  (GitHub Actions @ 7 AM AEST)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: CONTENT COLLECTION (Multi-Source Scraping)        │
├─────────────────────────────────────────────────────────────┤
│  → RSS Feeds (8 sources)                                     │
│    • VentureBeat AI, TechCrunch AI, MIT Tech Review         │
│    • Harvard Business Review, Analytics India Mag           │
│    • AI Business, The Register, Ars Technica                │
│                                                              │
│  → Twitter Accounts (6 influencers)                          │
│    • @AndrewYNg, @karpathy, @ylecun                         │
│    • @sama, @OpenAI, @GoogleAI                              │
│                                                              │
│  → Gmail Newsletters (tagged "newsletter")                   │
│    • Last 24 hours, parsed for content                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: CONTENT PROCESSING                                │
├─────────────────────────────────────────────────────────────┤
│  → Deduplication (cross-source duplicate detection)         │
│  → Content Cleaning (extract text, format)                  │
│  → Store in Supabase (articles table)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: AI FILTERING (Two-Stage OpenAI Processing)        │
├─────────────────────────────────────────────────────────────┤
│  Stage 1: Relevance Filtering                               │
│    • Score all articles 0-100                               │
│    • Select top 15 most relevant                            │
│    • Philosophy: "Don't panic. Prepare data. Stay agnostic" │
│                                                              │
│  Stage 2: Final Selection                                   │
│    • Deep analysis of top 15                                │
│    • Select final 5 articles                                │
│    • Generate detailed summaries                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STAGE 4: DAILY DIGEST CREATION                             │
├─────────────────────────────────────────────────────────────┤
│  → AI generates comprehensive summary                        │
│  → Identifies key insights & themes                         │
│  → Stores in daily_digests table                            │
│  → Links to selected article IDs                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  WEEKLY PROCESS (Sundays)                                   │
├─────────────────────────────────────────────────────────────┤
│  → Newsletter Draft Generation                              │
│    • Scores week's articles on 4 criteria                   │
│    • Selects 3-5 headlines                                  │
│    • Creates 600-800 word deep dive                         │
│    • Generates 3 operator takeaways                         │
│  → Stores in newsletter_drafts table                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  BOSS INTERACTION (Anytime via Claude MCP)                  │
├─────────────────────────────────────────────────────────────┤
│  → Review daily digests                                     │
│  → Search by themes/topics                                  │
│  → Mark articles for newsletter                             │
│  → Edit newsletter drafts                                   │
│  → Track source performance                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema (Supabase)

### Core Tables

| Table | Purpose | Row Count (Typical) | Status |
|-------|---------|---------------------|--------|
| **articles** | All scraped content | 300-500/week | ✅ Active |
| **daily_digests** | Daily AI summaries | 7/week | ✅ Active |
| **newsletter_drafts** | Weekly newsletter drafts | 1/week | ✅ Active |
| **content_sources** | RSS/Gmail source management | 8-10 | ✅ Active |
| **twitter_users** | Twitter account tracking | 6 | ✅ Active |
| **weekly_article_scores** | Newsletter scoring data | 100-200/week | ✅ Active |
| **newsletter_sections** | Section breakdown (optional) | 0 | ⚠️ Unused |
| **weekly_cycles** | Week tracking metadata | 1/week | ✅ Active |

### Helper Views

- **current_newsletter_draft**: Latest newsletter draft
- **current_week_articles**: This week's articles with priority levels
- **newsletter_ready_articles**: Scored articles for selection

---

## 📁 File Structure

```
ai-newsletter-pipeline/
├── 🎯 ENTRY POINTS (Run Scripts)
│   ├── run_ai_digest_pipeline.py      # Daily digest generation (MAIN)
│   ├── run_newsletter_draft.py        # Weekly newsletter creation
│   ├── run_rss_pipeline.py            # RSS-only testing
│   └── run_simple_pipeline.py         # Simple pipeline (no AI)
│
├── 🔧 CORE MODULES
│   ├── config/
│   │   └── settings.py                # All configuration & prompts
│   │
│   ├── scrapers/
│   │   ├── rss_scraper.py            # RSS feed processing
│   │   ├── twitter_scraper.py        # Twitter via RapidAPI
│   │   ├── gmail_scraper.py          # Newsletter email parsing
│   │   └── twitter_rapidapi.py       # Twitter API wrapper
│   │
│   ├── processors/
│   │   ├── multi_stage_digest.py     # 2-stage AI filtering (MAIN)
│   │   ├── newsletter_draft_processor.py  # Weekly newsletter generation
│   │   ├── content_processor.py      # Text cleaning & formatting
│   │   ├── deduplicator.py          # Duplicate detection
│   │   ├── ai_evaluator.py          # Legacy AI scoring
│   │   ├── data_aggregator.py       # Multi-source aggregation
│   │   └── theme_extractor.py       # Topic analysis
│   │
│   ├── database/
│   │   ├── supabase_client.py       # Main database client
│   │   ├── digest_storage.py        # Daily digest operations
│   │   ├── weekly_manager.py        # Week cycling logic
│   │   ├── schema.sql               # Database schema
│   │   └── newsletter_draft_schema.sql  # Newsletter tables
│   │
│   └── utils/
│       ├── logger.py                # Logging setup
│       └── helpers.py               # Utility functions
│
├── 🧪 TESTS
│   ├── test_basic_functionality.py   # Core component tests
│   ├── test_multi_stage_digest.py   # Digest pipeline tests
│   ├── test_newsletter_draft.py     # Newsletter tests
│   └── test_rss.py                  # RSS scraper tests
│
├── 🤖 AUTOMATION
│   └── .github/workflows/
│       └── daily-scrape.yml         # GitHub Actions (7 AM AEST)
│
└── 📚 DOCUMENTATION
    ├── README.md                    # Main documentation
    ├── BOSS_MCP_PROMPT.md          # Claude MCP setup guide
    ├── SUPABASE_SETUP_INSTRUCTIONS.md  # Database setup
    └── SYSTEM_OVERVIEW.md          # This file
```

---

## 🎯 Key Components Explained

### 1. Daily Digest Pipeline (`run_ai_digest_pipeline.py`)

**What it does:**
- Scrapes all sources (RSS, Twitter, Gmail)
- Deduplicates content
- AI filters to top 15 articles (Stage 1)
- AI selects final 5 with summaries (Stage 2)
- Creates daily digest with AI-generated overview

**AI Prompts:**
- **Stage 1** (Line 156 in `multi_stage_digest.py`): Filters for business relevance
- **Stage 2** (Line 240 in `multi_stage_digest.py`): Detailed summaries with quotes/data

**Runs:** Daily at 7 AM AEST via GitHub Actions

### 2. Newsletter Draft Generator (`run_newsletter_draft.py`)

**What it does:**
- Analyzes week's articles (Sunday)
- Scores on 4 criteria: Relevance, Timeliness, Evidence Quality, Innovation
- Selects 3-5 headlines
- Creates 600-800 word deep dive with multiple perspectives
- Generates 3 operator takeaways
- Stores structured draft in database

**AI Prompts:**
- **Scoring** (Line 81 in `newsletter_draft_processor.py`): Rates articles 0-100
- **Selection** (Line 217 in `newsletter_draft_processor.py`): Creates newsletter structure

**Runs:** Manually or scheduled for Sundays

### 3. Content Scrapers

**RSS Scraper** (`rss_scraper.py`):
- Fetches 8 RSS feeds
- Parses articles with feedparser
- Extracts title, content, published date
- Stores in Supabase

**Twitter Scraper** (`twitter_scraper.py`):
- Uses RapidAPI Twitter service
- Monitors 6 key accounts
- Fetches recent tweets
- Extracts engagement metrics

**Gmail Scraper** (`gmail_scraper.py`):
- Connects via IMAP
- Finds emails tagged "newsletter"
- Parses HTML content
- Extracts articles from newsletters

### 4. AI Processing

**Philosophy**: "Don't panic. Prepare your data. Stay agnostic."

**Scoring Criteria** (from `settings.py` line 102):
1. Business relevance for tech executives (30 pts)
2. Data strategy/vendor independence (25 pts)
3. Actionable insights vs research (20 pts)
4. Enterprise decision-making impact (15 pts)
5. Recency and relevance (10 pts)

**Newsletter Criteria** (4 dimensions):
1. **Relevance**: Alignment with philosophy
2. **Timeliness**: Current and urgent
3. **Evidence Quality**: Data-backed insights
4. **Innovation**: Novel approaches/perspectives

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Twitter
RAPIDAPI_KEY=your_rapidapi_key

# Gmail
GMAIL_EMAIL=your@email.com
GMAIL_APP_PASSWORD=your_app_password

# Pipeline Settings
LOG_LEVEL=INFO
MIN_RELEVANCE_SCORE=50
MAX_ARTICLES_PER_SOURCE=50
```

### Content Sources

**RSS Feeds** (managed in `content_sources` table):
- VentureBeat AI
- TechCrunch AI
- MIT Technology Review
- Harvard Business Review
- Analytics India Magazine
- AI Business
- The Register AI/ML
- Ars Technica

**Twitter Accounts** (managed in `twitter_users` table):
- Andrew Ng (@AndrewYNg)
- Andrej Karpathy (@karpathy)
- Yann LeCun (@ylecun)
- Sam Altman (@sama)
- OpenAI (@OpenAI)
- Google AI (@GoogleAI)

---

## 🚀 How to Use

### Daily Workflow (Automated)

1. **7 AM AEST**: GitHub Actions runs daily pipeline
2. **Pipeline executes**:
   - Scrapes all sources
   - Processes content
   - Creates daily digest
   - Stores in database
3. **Boss reviews** via Claude MCP anytime

### Weekly Workflow (Manual/Scheduled)

1. **Sunday**: Run newsletter draft generator
   ```bash
   python3 run_newsletter_draft.py
   ```
2. **System generates**:
   - Scores all week's articles
   - Selects best content
   - Creates structured draft
3. **Boss reviews/edits** via Claude MCP
4. **Publish** when ready

### Boss Interaction (Claude MCP)

**Setup**: Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-supabase"],
      "env": {
        "SUPABASE_URL": "your_url",
        "SUPABASE_SERVICE_ROLE_KEY": "your_key"
      }
    }
  }
}
```

**Common Queries**:
- "Show me today's digest"
- "Find vendor lock-in articles from this week"
- "What are the top themes this week?"
- "Show me the current newsletter draft"
- "Mark articles X, Y, Z for newsletter"

---

## 🧪 Testing

### Run All Tests
```bash
python3 test_basic_functionality.py  # Core components
python3 test_multi_stage_digest.py   # Digest pipeline
python3 test_newsletter_draft.py     # Newsletter generation
python3 test_rss.py                  # RSS scraper
```

### Test Individual Components
```bash
# Test RSS scraping
python3 run_rss_pipeline.py

# Test newsletter draft
python3 run_newsletter_draft.py

# Show recent digests
python3 -c "import asyncio; from run_ai_digest_pipeline import show_recent_digests; asyncio.run(show_recent_digests(3))"
```

---

## ⚠️ Known Issues & Limitations

### Current Status

✅ **Working Well:**
- Daily scraping from all sources
- AI filtering and digest generation
- Database storage and retrieval
- Newsletter draft generation
- GitHub Actions automation
- Basic functionality tests passing

⚠️ **Potential Issues:**

1. **Twitter API Rate Limits**
   - Using RapidAPI (limited free tier)
   - May hit rate limits with frequent runs
   - **Solution**: Monitor usage, upgrade plan if needed

2. **Gmail IMAP Connection**
   - Requires app password (2FA)
   - May timeout on slow connections
   - **Solution**: Verify credentials, check firewall

3. **OpenAI API Costs**
   - Daily digest uses ~5-10 API calls
   - Newsletter draft uses ~10-15 calls
   - **Estimate**: $5-10/month at current volume
   - **Solution**: Monitor usage, adjust batch sizes

4. **Unused Table**
   - `newsletter_sections` table has 0 rows
   - Currently using JSONB in `newsletter_drafts`
   - **Status**: Kept for potential future granular editing

5. **Database Migration**
   - No automated migration system
   - Schema changes require manual SQL execution
   - **Solution**: Document all changes in SQL files

### Missing Features

🔜 **Not Yet Implemented:**
- Automated newsletter publishing
- Email delivery integration
- Analytics dashboard
- A/B testing for content selection
- Historical trend analysis
- Source performance auto-tuning

---

## 🔒 Security Considerations

### Secrets Management
- ✅ All API keys in `.env` (gitignored)
- ✅ GitHub Actions uses encrypted secrets
- ✅ Supabase service key for admin operations
- ⚠️ No secret rotation implemented

### Database Access
- ✅ Row Level Security (RLS) on Supabase
- ✅ Service key only for pipeline
- ✅ Anon key for read-only MCP access
- ⚠️ No audit logging for boss edits

### API Security
- ✅ HTTPS for all external calls
- ✅ Rate limiting on scrapers
- ⚠️ No retry backoff for failed requests

---

## 📊 Performance Metrics

### Typical Daily Run
- **Duration**: 5-10 minutes
- **Articles Scraped**: 50-100
- **Articles Stored**: 30-60 (after dedup)
- **AI API Calls**: 5-10
- **Final Digest**: 5 articles

### Weekly Newsletter Generation
- **Duration**: 8-12 minutes
- **Articles Analyzed**: 150-300
- **AI API Calls**: 10-15
- **Output**: 3-5 headlines, 1 deep dive, 3 takeaways

### Database Size
- **Articles**: ~300-500 per week
- **Digests**: 7 per week
- **Newsletter Drafts**: 1 per week
- **Total Storage**: ~50-100 MB/month

---

## 🛠️ Maintenance Tasks

### Daily
- ✅ Automated via GitHub Actions
- Check logs for failures
- Monitor API usage

### Weekly
- Review newsletter draft quality
- Check source performance
- Verify database health

### Monthly
- Clean old articles (4+ weeks)
- Review API costs
- Update content sources if needed
- Check for dependency updates

### As Needed
- Add/remove RSS feeds via `add_rss_source.py`
- Update Twitter accounts in database
- Adjust AI prompts in `settings.py` or processor files
- Tune scoring thresholds

---

## 🎓 Learning Resources

### Key Files to Understand
1. **`run_ai_digest_pipeline.py`**: Main daily workflow
2. **`processors/multi_stage_digest.py`**: AI filtering logic
3. **`processors/newsletter_draft_processor.py`**: Newsletter generation
4. **`config/settings.py`**: All prompts and configuration

### AI Prompt Locations
- **Daily digest Stage 1**: `multi_stage_digest.py` line 156
- **Daily digest Stage 2**: `multi_stage_digest.py` line 240
- **Newsletter scoring**: `newsletter_draft_processor.py` line 81
- **Newsletter selection**: `newsletter_draft_processor.py` line 217
- **Legacy scoring**: `settings.py` line 102

### Database Query Examples
See `BOSS_MCP_PROMPT.md` for comprehensive query examples.

---

## 🚨 Troubleshooting

### Pipeline Fails on GitHub Actions
1. Check workflow logs in GitHub Actions tab
2. Verify all secrets are set correctly
3. Test locally with same environment variables
4. Check API rate limits (Twitter, OpenAI)

### No Articles Being Scraped
1. Test individual scrapers:
   ```bash
   python3 -m scrapers.rss_scraper
   python3 -m scrapers.twitter_scraper
   ```
2. Check RSS feed URLs are still valid
3. Verify Twitter API credentials
4. Check Gmail app password

### AI Filtering Not Working
1. Verify OpenAI API key is valid
2. Check API usage limits
3. Review prompts in processor files
4. Test with smaller batch size

### Database Connection Issues
1. Verify Supabase URL and keys
2. Check network connectivity
3. Review Supabase dashboard for errors
4. Test with `test_basic_functionality.py`

---

## 📞 Support & Contact

### Documentation
- **README.md**: Quick start and overview
- **BOSS_MCP_PROMPT.md**: Claude MCP setup
- **SUPABASE_SETUP_INSTRUCTIONS.md**: Database setup
- **This file**: Complete system reference

### GitHub Repository
- **URL**: https://github.com/willsupernormal/ai-newsletter-pipeline
- **Issues**: Report bugs or request features
- **Actions**: View automated run history

---

## ✅ System Health Checklist

Run this checklist periodically to ensure system health:

- [ ] GitHub Actions running successfully daily
- [ ] Daily digests being created in database
- [ ] Articles being scraped from all sources
- [ ] No API rate limit errors
- [ ] Database storage within limits
- [ ] Newsletter drafts generating on Sundays
- [ ] Boss can access via Claude MCP
- [ ] All tests passing locally
- [ ] API costs within budget
- [ ] No security vulnerabilities in dependencies

---

**System Status**: ✅ **OPERATIONAL**  
**Last Verified**: October 23, 2025  
**Next Review**: Weekly
