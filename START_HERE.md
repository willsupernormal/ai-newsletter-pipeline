# AI Newsletter Pipeline - START HERE

> **New to this project? Read this first.** This document provides a complete overview and guides you to all relevant documentation.

**Last Updated:** October 29, 2025  
**Status:** ✅ Operational  
**Version:** 2.0 (Post-Cleanup)

---

## 📋 **Quick Navigation**

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[START_HERE.md](START_HERE.md)** | Project overview & navigation | First time here |
| **[README.md](README.md)** | Technical overview & architecture | Understanding the system |
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Current state & known issues | Checking system health |
| **[docs/SETUP.md](docs/SETUP.md)** | Complete setup instructions | Setting up from scratch |
| **[docs/OPERATIONS.md](docs/OPERATIONS.md)** | Running & troubleshooting | Daily operations |
| **[AIRTABLE_DATA_SPEC.md](AIRTABLE_DATA_SPEC.md)** | Data structure reference | Understanding data flow |

---

## 🎯 **What This System Does**

### **In One Sentence:**
Automatically scrapes 31 AI news sources daily, uses GPT-4 to select the top 5 articles, posts them to Slack with interactive buttons, and allows one-click addition to an Airtable content pipeline.

### **The Flow:**
```
1. GitHub Actions runs at 7 AM AEST
   ↓
2. Scrapes 31 RSS feeds → ~180 articles
   ↓
3. AI filters in 2 stages → Top 5 articles
   ↓
4. Posts to Slack #ai-daily-digest
   ↓
5. User clicks "Add to Pipeline" button
   ↓
6. Article added to Airtable with full content
```

---

## 📁 **Project Structure**

```
ai-newsletter-pipeline/
│
├── 📄 START_HERE.md              ← You are here
├── 📄 README.md                  ← Technical overview
├── 📄 PROJECT_STATUS.md          ← Current state & issues
├── 📄 AIRTABLE_DATA_SPEC.md      ← Data structure
├── 📄 requirements.txt           ← Python dependencies
├── 📄 .env.example               ← Environment variables template
│
├── 📁 docs/                      ← All documentation
│   ├── SETUP.md                  ← Complete setup guide
│   ├── OPERATIONS.md             ← Running & troubleshooting
│   ├── GITHUB_ACTIONS_SETUP.md   ← CI/CD configuration
│   ├── LOCAL_TESTING_GUIDE.md    ← Testing locally
│   └── AIRTABLE_COMPLETE_SETUP.md ← Airtable configuration
│
├── 📁 scripts/                   ← Utility scripts
│   ├── run_ai_digest_pipeline.py ← Main entry point
│   ├── add_rss_source.py         ← Manage RSS sources
│   ├── fix_and_add_sources.py    ← Fix blocked sources
│   └── run_rss_pipeline.py       ← RSS-only pipeline
│
├── 📁 api/                       ← Webhook server
│   └── webhook_server.py         ← FastAPI server for Slack
│
├── 📁 config/                    ← Configuration
│   └── settings.py               ← Settings management
│
├── 📁 database/                  ← Database clients
│   ├── supabase_simple.py        ← Supabase client
│   └── digest_storage.py         ← Digest storage logic
│
├── 📁 scrapers/                  ← Content scrapers
│   ├── rss_scraper.py            ← RSS feed scraping
│   └── article_scraper.py        ← Full article extraction
│
├── 📁 processors/                ← Content processors
│   ├── multi_stage_digest.py     ← AI filtering logic
│   ├── deduplicator.py           ← Deduplication
│   └── data_aggregator.py        ← Data aggregation
│
├── 📁 services/                  ← External services
│   ├── airtable_client.py        ← Airtable integration
│   ├── slack_notifier.py         ← Slack posting
│   ├── slack_webhook_handler.py  ← Slack button handling
│   └── prompt_service.py         ← AI prompts
│
└── 📁 .github/workflows/         ← GitHub Actions
    └── daily-scrape.yml          ← Daily automation
```

---

## 🔧 **Tech Stack**

### **Infrastructure:**
- **GitHub Actions** - Daily scheduling (7 AM AEST)
- **Railway** - Webhook server hosting (Slack buttons)
- **Supabase** - PostgreSQL database (articles, digests, sources)
- **Airtable** - Content pipeline management

### **Core Technologies:**
- **Python 3.11** - Main language
- **FastAPI** - Webhook server
- **OpenAI GPT-4** - AI filtering & analysis
- **aiohttp** - Async HTTP requests
- **feedparser** - RSS parsing
- **newspaper3k/trafilatura** - Article extraction

### **Key Libraries:**
```python
# Web scraping
aiohttp, feedparser, beautifulsoup4, brotli

# Database
supabase, asyncpg

# AI
openai, tiktoken

# External services
pyairtable, fastapi, uvicorn

# Utilities
python-dotenv, pydantic, structlog
```

---

## 🚀 **Quick Start Commands**

### **Run Digest Locally:**
```bash
cd /path/to/ai-newsletter-pipeline
python3 scripts/run_ai_digest_pipeline.py
```

### **Force Regenerate Today's Digest:**
```bash
python3 scripts/run_ai_digest_pipeline.py force
```

### **Manage RSS Sources:**
```bash
# List all sources
python3 scripts/add_rss_source.py list

# Add new source
python3 scripts/add_rss_source.py add "Source Name" "https://example.com/feed.xml"

# Disable source
python3 scripts/add_rss_source.py disable "Source Name"

# Enable source
python3 scripts/add_rss_source.py enable "Source Name"
```

### **Fix Blocked Sources:**
```bash
python3 scripts/fix_and_add_sources.py
```

---

## 📊 **System Health**

### **Current Metrics:**
- **RSS Sources:** 31 active
- **Articles Collected:** ~180 per day (target)
- **Success Rate:** ~90%
- **Final Selection:** 5 articles
- **Slack Posts:** Daily at 7 AM AEST
- **Button Success Rate:** 100%

### **Known Issues:**
1. Some RSS sources have broken URLs (see PROJECT_STATUS.md)
2. Airtable fields may not fully populate (under investigation)

---

## 🔑 **Environment Variables**

### **Required:**
```bash
# Supabase (Database)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# OpenAI (AI Filtering)
OPENAI_API_KEY=sk-xxx

# Slack (Posting & Buttons)
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# Airtable (Content Pipeline)
AIRTABLE_API_KEY=xxx
AIRTABLE_BASE_ID=xxx
AIRTABLE_TABLE_NAME=Content Pipeline
```

### **Optional:**
```bash
# RSS Settings
RSS_REQUEST_TIMEOUT=30
RSS_MAX_RETRIES=3
MAX_ARTICLES_PER_SOURCE=50

# AI Settings
OPENAI_MODEL=gpt-4-turbo-preview
STAGE1_TARGET_COUNT=10
STAGE2_TARGET_COUNT=5
```

**See `.env.example` for complete list.**

---

## 📖 **Documentation Guide**

### **For First-Time Setup:**
1. Read [START_HERE.md](START_HERE.md) (this file)
2. Read [docs/SETUP.md](docs/SETUP.md)
3. Configure environment variables
4. Run test digest

### **For Daily Operations:**
1. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for current state
2. Use [docs/OPERATIONS.md](docs/OPERATIONS.md) for troubleshooting
3. Check GitHub Actions logs for errors

### **For Development:**
1. Read [README.md](README.md) for architecture
2. Read [AIRTABLE_DATA_SPEC.md](AIRTABLE_DATA_SPEC.md) for data structure
3. Check [docs/LOCAL_TESTING_GUIDE.md](docs/LOCAL_TESTING_GUIDE.md)

### **For Understanding Data:**
1. Read [AIRTABLE_DATA_SPEC.md](AIRTABLE_DATA_SPEC.md)
2. Check Supabase schema in [docs/SETUP.md](docs/SETUP.md)
3. Review `database/` directory for storage logic

---

## 🎯 **Common Tasks**

### **"I want to add a new RSS source"**
```bash
python3 scripts/add_rss_source.py add "Source Name" "https://example.com/feed.xml"
```
See [docs/OPERATIONS.md](docs/OPERATIONS.md) for details.

### **"I want to test the digest"**
```bash
python3 scripts/run_ai_digest_pipeline.py force
```
See [docs/LOCAL_TESTING_GUIDE.md](docs/LOCAL_TESTING_GUIDE.md) for details.

### **"I want to check what's broken"**
Read [PROJECT_STATUS.md](PROJECT_STATUS.md) → Known Issues section.

### **"I want to understand the data flow"**
Read [AIRTABLE_DATA_SPEC.md](AIRTABLE_DATA_SPEC.md) → Complete Flow section.

### **"I want to deploy changes"**
```bash
git add .
git commit -m "Description"
git push origin main
```
GitHub Actions and Railway auto-deploy.

---

## 🔍 **Key Concepts**

### **1. Multi-Stage AI Filtering**
- **Stage 1:** GPT-4 reviews all articles, selects top 10 based on relevance
- **Stage 2:** GPT-4 reviews top 10, selects final 5 with summaries
- **Why 2 stages?** Better quality, more diverse selection

### **2. Async Button Processing**
- User clicks "Add to Pipeline" in Slack
- Button immediately shows "Processing..." (no timeout)
- Background task: Fetch → Scrape → Push to Airtable
- Button updates to "✅ Added" when complete

### **3. RSS Source Management**
- Sources stored in Supabase `content_sources` table
- Can enable/disable sources without code changes
- Tracks success/failure counts
- Browser-like headers to avoid 403 errors

### **4. Deduplication**
- URLs are unique in database
- Duplicate articles automatically skipped
- Prevents re-processing same content

---

## 🚨 **Troubleshooting**

### **"Digest didn't run today"**
1. Check GitHub Actions logs
2. Verify environment variables in GitHub Secrets
3. Check Supabase connection

### **"Slack buttons not working"**
1. Check Railway logs
2. Verify SLACK_SIGNING_SECRET matches
3. Test webhook URL

### **"Articles not in Airtable"**
1. Check Railway logs for errors
2. Verify AIRTABLE_API_KEY
3. Check field mappings in code

### **"RSS sources failing"**
1. Check logs for specific errors
2. Verify URLs are correct
3. Install brotli if needed: `pip3 install brotli`
4. Disable broken sources

**For detailed troubleshooting, see [docs/OPERATIONS.md](docs/OPERATIONS.md)**

---

## 📞 **Getting Help**

### **Check Logs:**
- **GitHub Actions:** https://github.com/willsupernormal/ai-newsletter-pipeline/actions
- **Railway:** https://railway.app (webhook server)
- **Supabase:** https://supabase.com (database)

### **Check Status:**
- Read [PROJECT_STATUS.md](PROJECT_STATUS.md)
- Check GitHub Actions for recent runs
- Check Railway for webhook errors

### **Common Issues:**
- See [docs/OPERATIONS.md](docs/OPERATIONS.md) → Troubleshooting section
- See [PROJECT_STATUS.md](PROJECT_STATUS.md) → Known Issues section

---

## 📚 **Learning Path**

### **Level 1: Understanding (30 minutes)**
1. Read this file (START_HERE.md)
2. Read [README.md](README.md)
3. Read [PROJECT_STATUS.md](PROJECT_STATUS.md)

### **Level 2: Setup (1-2 hours)**
1. Read [docs/SETUP.md](docs/SETUP.md)
2. Configure environment variables
3. Run test digest locally

### **Level 3: Operations (ongoing)**
1. Read [docs/OPERATIONS.md](docs/OPERATIONS.md)
2. Monitor GitHub Actions
3. Manage RSS sources as needed

### **Level 4: Development (as needed)**
1. Read [AIRTABLE_DATA_SPEC.md](AIRTABLE_DATA_SPEC.md)
2. Review code in `scrapers/`, `processors/`, `services/`
3. Read [docs/LOCAL_TESTING_GUIDE.md](docs/LOCAL_TESTING_GUIDE.md)

---

## ✅ **System Checklist**

### **Daily:**
- [ ] Check Slack for digest post (7 AM AEST)
- [ ] Verify 5 articles selected
- [ ] Test "Add to Pipeline" button if needed

### **Weekly:**
- [ ] Review GitHub Actions logs
- [ ] Check RSS source health
- [ ] Review Airtable for new articles

### **Monthly:**
- [ ] Review source performance
- [ ] Add new sources if needed
- [ ] Update documentation if changed

---

## 🎉 **Recent Improvements**

### **October 2025:**
- ✅ Fixed Slack timeout (async processing)
- ✅ Added button state feedback
- ✅ Added 17 new premium sources
- ✅ Added browser headers for scraping
- ✅ Installed brotli for compression
- ✅ Major codebase cleanup (-69% lines)
- ✅ Reorganized into proper structure
- ✅ Updated all documentation

---

## 📝 **Version History**

- **v2.0** (Oct 2025) - Major cleanup, 31 sources, async buttons
- **v1.5** (Sep 2025) - Airtable integration, Slack buttons
- **v1.0** (Aug 2025) - Initial release, basic digest

---

## 🔗 **External Links**

- **GitHub Repository:** https://github.com/willsupernormal/ai-newsletter-pipeline
- **Railway Dashboard:** https://railway.app
- **Supabase Dashboard:** https://supabase.com
- **Airtable Base:** [Your Airtable URL]
- **Slack Workspace:** [Your Slack URL]

---

## 💡 **Pro Tips**

1. **Always check PROJECT_STATUS.md first** - It has the current state
2. **Use `force` flag for testing** - Regenerates today's digest
3. **Check Railway logs for button issues** - Most detailed logging
4. **Disable broken sources quickly** - Don't let them slow down scraping
5. **Monitor source success rates** - In Supabase `content_sources` table

---

## 🎯 **Next Steps**

### **If you're new:**
→ Read [docs/SETUP.md](docs/SETUP.md) to get started

### **If you're debugging:**
→ Read [PROJECT_STATUS.md](PROJECT_STATUS.md) for known issues

### **If you're developing:**
→ Read [README.md](README.md) for architecture

### **If you're operating:**
→ Read [docs/OPERATIONS.md](docs/OPERATIONS.md) for daily tasks

---

**Welcome to the AI Newsletter Pipeline! 🚀**

**Questions?** Check the documentation links above or review the code in the relevant directories.

