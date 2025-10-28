# AI Newsletter Pipeline - Current Status

**Last Updated:** October 27, 2025, 11:00 PM  
**Status:** ✅ OPERATIONAL (with improvements needed)

---

## 🎯 **What This System Does**

Automatically generates a daily AI news digest by:
1. **Scraping** 31 RSS feeds for AI news
2. **Filtering** with AI (141 articles → 10 → 5 best)
3. **Posting** to Slack with interactive "Add to Pipeline" buttons
4. **Adding** selected articles to Airtable for content planning

---

## ✅ **What's Working**

### **Core Functionality:**
- ✅ Daily digest runs at 7 AM AEST via GitHub Actions
- ✅ AI filtering selects top 5 articles
- ✅ Posts to Slack #ai-daily-digest channel
- ✅ Interactive buttons work (add articles to Airtable)
- ✅ Button shows visual feedback (Processing → Added)
- ✅ Articles stored in Supabase database
- ✅ Webhook server running on Railway

### **Recent Improvements:**
- ✅ Fixed Slack timeout issue (async processing)
- ✅ Added button state changes (UX improvement)
- ✅ Fixed blocked RSS sources (3 sources)
- ✅ Added 17 new premium sources (Enterprise + Open Source)
- ✅ Added browser headers to avoid 403 errors

---

## ⚠️ **Current Issues**

### **1. Reduced Article Count**
- **Before:** 141 articles collected
- **After upgrade:** 88 articles collected
- **Cause:** Many new sources have broken URLs or need brotli
- **Priority:** HIGH

### **2. Broken RSS Sources**
```
❌ Microsoft DevBlogs - 404
❌ McKinsey - 404
❌ Deloitte - 404
❌ IBM Watson - 404
❌ Accenture - 404
❌ Protocol - 404
❌ Google Cloud AI - Parse error
❌ TechCrunch - Needs brotli
❌ VentureBeat - Needs brotli
❌ Gartner - Needs brotli
```
- **Priority:** HIGH

### **3. Missing Brotli Dependency**
- **Issue:** Some feeds use brotli compression
- **Fix:** `pip install brotli`
- **Priority:** HIGH

### **4. Airtable Fields Not Populating**
- **Issue:** Theme, Content Type, AI summaries not in Airtable
- **Cause:** Unknown (needs investigation with logs)
- **Priority:** MEDIUM

### **5. Messy Codebase**
- **Issue:** 45 markdown files (mostly obsolete)
- **Issue:** 12 test files (mostly one-time tests)
- **Issue:** Flat structure (no organization)
- **Priority:** MEDIUM

---

## 📊 **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY DIGEST FLOW                        │
└─────────────────────────────────────────────────────────────┘

1. GitHub Actions (7 AM AEST)
   ↓
2. Scrape 31 RSS Feeds → ~180 articles
   ↓
3. Stage 1 AI Filter → Top 10 articles
   ↓
4. Stage 2 AI Filter → Top 5 articles
   ↓
5. Post to Slack with buttons
   ↓
6. Store in Supabase

┌─────────────────────────────────────────────────────────────┐
│                  BUTTON CLICK FLOW                          │
└─────────────────────────────────────────────────────────────┘

1. User clicks "Add to Pipeline" in Slack
   ↓
2. Slack → Railway Webhook Server
   ↓
3. Button changes to "Processing..." (instant)
   ↓
4. Background: Fetch from Supabase → Scrape full article → Push to Airtable
   ↓
5. Button changes to "✅ Added" (3-4 seconds)
   ↓
6. Article appears in Airtable
```

---

## 🔧 **Tech Stack**

### **Infrastructure:**
- **GitHub Actions** - Daily digest scheduling
- **Railway** - Webhook server hosting
- **Supabase** - Database (articles, digests, sources)
- **Airtable** - Content pipeline management

### **Languages & Frameworks:**
- **Python 3.11** - Main language
- **FastAPI** - Webhook server
- **OpenAI GPT-4** - AI filtering & analysis

### **Key Libraries:**
- `feedparser` - RSS parsing
- `aiohttp` - Async HTTP requests
- `newspaper3k` / `trafilatura` - Article scraping
- `pyairtable` - Airtable integration
- `supabase-py` - Supabase client

---

## 📁 **Key Files**

### **Entry Points:**
- `run_ai_digest_pipeline.py` - Main digest generation
- `api/webhook_server.py` - Slack webhook handler

### **Core Logic:**
- `processors/multi_stage_digest.py` - AI filtering
- `scrapers/rss_scraper.py` - RSS scraping
- `scrapers/article_scraper.py` - Full article scraping
- `services/slack_webhook_handler.py` - Button click handling
- `services/airtable_client.py` - Airtable integration

### **Utilities:**
- `add_rss_source.py` - Manage RSS sources
- `fix_and_add_sources.py` - Fix blocked sources

### **Configuration:**
- `.env` - Environment variables
- `config/settings.py` - Settings management
- `.github/workflows/daily-scrape.yml` - GitHub Actions

---

## 🎯 **Next Steps**

### **Immediate (This Week):**

1. **Fix Broken Sources** (Priority: HIGH)
   ```bash
   # Install brotli
   pip install brotli
   
   # Fix broken URLs manually in Supabase
   # Or disable non-working sources
   python add_rss_source.py disable "Source Name"
   ```

2. **Investigate Airtable Fields** (Priority: MEDIUM)
   - Click button in Slack
   - Check Railway logs for `[ASYNC]` messages
   - Verify what data exists in Supabase
   - Fix field mapping if needed

3. **Clean Up Codebase** (Priority: MEDIUM)
   - Delete 28 obsolete markdown files
   - Delete 10 obsolete test files
   - Create 3 essential docs (README, SETUP, OPERATIONS)
   - See `CODEBASE_CLEANUP_TODO.md` for full plan

### **Short-term (This Month):**

4. **Improve Source Quality**
   - Get article count back to 180-220
   - Ensure all 31 sources working
   - Monitor source health

5. **Organize Codebase**
   - Create proper directory structure
   - Move scripts to `scripts/`
   - Update import paths

6. **Add Monitoring**
   - Track source success rates
   - Alert on failures
   - Dashboard for metrics

### **Long-term (Next Quarter):**

7. **Add More Sources**
   - Regional coverage (EU, Asia)
   - Niche AI topics
   - Academic sources

8. **Improve AI Filtering**
   - Better diversity scoring
   - User feedback integration
   - Personalization

9. **Enhanced Airtable Integration**
   - Auto-categorization
   - Content scheduling
   - Performance tracking

---

## 📈 **Metrics**

### **Current Performance:**
- **RSS Sources:** 31 active (17 added today)
- **Articles Collected:** 88 (target: 180-220)
- **Success Rate:** ~60% (target: 97%+)
- **Final Selection:** 5 articles
- **Slack Posts:** Daily at 7 AM AEST
- **Button Success Rate:** 100%

### **Quality Metrics:**
- **Source Diversity:** Good (AWS, LangChain, AI Business, The Register)
- **Content Types:** Mixed (enterprise, technical, business, research)
- **Freshness:** Last 7 days only
- **AI Filtering:** Working well (141 → 10 → 5)

---

## 🔐 **Environment Variables**

### **Required:**
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# OpenAI
OPENAI_API_KEY=sk-xxx

# Slack
SLACK_BOT_TOKEN=xoxb-xxx
SLACK_SIGNING_SECRET=xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# Airtable
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

---

## 🐛 **Known Bugs**

1. **Airtable fields not populating** - Under investigation
2. **Some RSS sources broken** - Need URL fixes
3. **Brotli compression not supported** - Need to install brotli
4. **Article count dropped** - Due to broken sources

---

## 📚 **Documentation**

### **Current Docs:**
- `README.md` - Project overview
- `CODEBASE_CLEANUP_TODO.md` - Cleanup plan (NEW)
- `PROJECT_STATUS.md` - This file (NEW)
- `AIRTABLE_DATA_SPEC.md` - Data structure
- `SUPABASE_SETUP_INSTRUCTIONS.md` - Database setup
- `docs/SETUP_GUIDE.md` - Initial setup
- `docs/GITHUB_ACTIONS_SETUP.md` - CI/CD setup

### **Planned Docs:**
- `docs/SETUP.md` - Consolidated setup guide
- `docs/OPERATIONS.md` - Running & troubleshooting

---

## 🎓 **How to Use**

### **Run Digest Locally:**
```bash
python run_ai_digest_pipeline.py
```

### **Force Regenerate:**
```bash
python run_ai_digest_pipeline.py force
```

### **Manage RSS Sources:**
```bash
# List all sources
python add_rss_source.py list

# Add source
python add_rss_source.py add "Name" "URL"

# Disable source
python add_rss_source.py disable "Name"
```

### **Fix Blocked Sources:**
```bash
python fix_and_add_sources.py
```

---

## 🚨 **Troubleshooting**

### **Digest Not Running:**
1. Check GitHub Actions logs
2. Verify environment variables
3. Check Supabase connection

### **Slack Buttons Not Working:**
1. Check Railway logs
2. Verify webhook URL in Slack app
3. Check SLACK_SIGNING_SECRET

### **Airtable Not Updating:**
1. Check Railway logs for errors
2. Verify AIRTABLE_API_KEY
3. Check field mappings

### **RSS Sources Failing:**
1. Check logs for specific errors
2. Install brotli if needed
3. Verify URLs are correct
4. Disable broken sources

---

## 📞 **Support**

### **Logs:**
- **GitHub Actions:** https://github.com/willsupernormal/ai-newsletter-pipeline/actions
- **Railway:** https://railway.app (webhook server logs)
- **Supabase:** https://supabase.com (database logs)

### **Configuration:**
- **Slack App:** https://api.slack.com/apps
- **Airtable:** https://airtable.com
- **GitHub Secrets:** Repository Settings → Secrets

---

## ✅ **Summary**

**System Status:** ✅ Operational but needs improvements

**What's Working:**
- Daily digest generation
- Slack posting with buttons
- Button interactions
- Airtable integration (mostly)

**What Needs Fixing:**
- Broken RSS sources (10+ sources)
- Missing brotli dependency
- Airtable field population
- Codebase organization

**Next Action:** Fix broken RSS sources to restore article count

---

**For detailed cleanup plan, see:** `CODEBASE_CLEANUP_TODO.md`

