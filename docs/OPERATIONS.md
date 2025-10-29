# Operations Guide

> **Daily operations, troubleshooting, and maintenance for the AI Newsletter Pipeline.**

**Last Updated:** October 29, 2025

---

## 📋 **Table of Contents**

1. [Daily Operations](#daily-operations)
2. [Managing RSS Sources](#managing-rss-sources)
3. [Running Digests](#running-digests)
4. [Monitoring](#monitoring)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)

---

## 🔄 **Daily Operations**

### **Automated Daily Flow**

**7:00 AM AEST** - GitHub Actions triggers:
1. Scrapes 31 RSS feeds
2. Collects ~180 articles
3. AI filters to top 10 (Stage 1)
4. AI selects final 5 (Stage 2)
5. Posts to Slack #ai-daily-digest
6. Stores in Supabase

**No manual intervention required** - System runs automatically.

### **Daily Checklist**

- [ ] Check Slack for digest post (7:00-7:15 AM AEST)
- [ ] Verify 5 articles were selected
- [ ] Review article quality
- [ ] Click "Add to Pipeline" for interesting articles
- [ ] Check Airtable for new additions

### **What to Monitor**

**Green flags (✅):**
- Digest posted on time
- 5 articles selected
- Diverse sources represented
- Buttons work when clicked

**Red flags (🚨):**
- No digest posted
- Fewer than 5 articles
- All articles from same source
- Buttons don't respond

---

## 📰 **Managing RSS Sources**

### **List All Sources**

```bash
python3 scripts/add_rss_source.py list
```

**Output:**
```
📰 RSS Sources (31 total):
--------------------------------------------------------------------------------
🟢 Active | VentureBeat AI
         URL: https://venturebeat.com/category/ai/feed/
         Last processed: 2025-10-29 07:05:23
         Success/Failure: 245/3

🟢 Active | TechCrunch AI
         URL: https://techcrunch.com/category/artificial-intelligence/feed/
         Last processed: 2025-10-29 07:05:25
         Success/Failure: 238/8
...
```

### **Add New Source**

```bash
python3 scripts/add_rss_source.py add "Source Name" "https://example.com/feed.xml"
```

**Example:**
```bash
python3 scripts/add_rss_source.py add "AI Weekly" "https://aiweekly.co/feed.xml"
```

**Output:**
```
✅ Successfully added RSS source: AI Weekly
   URL: https://aiweekly.co/feed.xml
   Active: True
```

### **Disable Source**

```bash
python3 scripts/add_rss_source.py disable "Source Name"
```

**When to disable:**
- Source consistently returns 404
- Source has paywalled content
- Source quality is poor
- Source is no longer relevant

### **Enable Source**

```bash
python3 scripts/add_rss_source.py enable "Source Name"
```

### **Check Source Health**

**In Supabase SQL Editor:**
```sql
SELECT 
    name,
    active,
    success_count,
    failure_count,
    ROUND(success_count::numeric / NULLIF(success_count + failure_count, 0) * 100, 2) as success_rate,
    last_processed
FROM content_sources
WHERE type = 'rss'
ORDER BY failure_count DESC, success_rate ASC;
```

**Healthy source:** Success rate > 95%  
**Problematic source:** Success rate < 80%

---

## 🚀 **Running Digests**

### **Run Today's Digest Locally**

```bash
python3 scripts/run_ai_digest_pipeline.py
```

**When to use:**
- Testing after code changes
- Debugging issues
- Checking new sources

### **Force Regenerate Today's Digest**

```bash
python3 scripts/run_ai_digest_pipeline.py force
```

**When to use:**
- Digest failed to generate
- Want to regenerate with updated sources
- Testing changes to AI prompts

**⚠️ Warning:** This will overwrite today's existing digest.

### **Run RSS-Only Pipeline**

```bash
python3 scripts/run_rss_pipeline.py
```

**When to use:**
- Testing RSS scraping only
- Debugging source issues
- Checking article collection

**Note:** This doesn't create a digest, just collects articles.

### **Expected Output**

**Successful run:**
```
🎉 AI Daily Digest Created for 2025-10-29
📊 Processing Summary:
  • Total articles collected: 182
    - RSS articles: 182
    - Twitter articles: 0
  • Stage 1 filtering: 182 → 10
  • Stage 2 final selection: 10 → 5
  • Digest ID: abc123...

📰 Selected Articles:
  1. Title of Article 1
     Source: VentureBeat AI (rss)
     ID: xxx
  2. Title of Article 2
     Source: TechCrunch AI (rss)
     ID: xxx
  ...

💡 Key Insights:
  • Insight 1: ...
  • Insight 2: ...
  ...

📱 Posted to Slack: #ai-daily-digest
```

**Failed run:**
```
❌ Error: Failed to scrape RSS feeds
❌ Error: OpenAI API rate limit exceeded
❌ Error: Slack webhook failed
```

---

## 📊 **Monitoring**

### **GitHub Actions**

**URL:** https://github.com/willsupernormal/ai-newsletter-pipeline/actions

**Check:**
- Latest workflow run status
- Execution time (should be 3-5 minutes)
- Error logs if failed

**Common issues:**
- Timeout (increase RSS_REQUEST_TIMEOUT)
- Rate limit (OpenAI API)
- Network errors (transient, retry)

### **Railway (Webhook Server)**

**URL:** https://railway.app/dashboard

**Check:**
- Server status (should be "Running")
- Recent logs for button clicks
- Error rates

**Look for:**
```
✅ [ASYNC] ✓ Added to Airtable: recXXXXXXXXXXXXXX
✅ Successfully processed interaction
❌ [ASYNC] ✗ Failed to add to Airtable: [error]
```

### **Supabase**

**URL:** https://supabase.com/dashboard

**Check:**
- Database size (should grow slowly)
- Query performance
- Table row counts

**Useful queries:**

**Articles per day:**
```sql
SELECT 
    DATE(scraped_at) as date,
    COUNT(*) as articles
FROM articles
WHERE scraped_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(scraped_at)
ORDER BY date DESC;
```

**Source performance:**
```sql
SELECT 
    source_name,
    COUNT(*) as articles,
    COUNT(*) FILTER (WHERE selected_for_digest) as selected
FROM articles
WHERE scraped_at > NOW() - INTERVAL '30 days'
GROUP BY source_name
ORDER BY articles DESC;
```

**Digest history:**
```sql
SELECT 
    digest_date,
    ARRAY_LENGTH(article_ids, 1) as article_count,
    posted_to_slack,
    created_at
FROM daily_digests
ORDER BY digest_date DESC
LIMIT 30;
```

### **Airtable**

**Check:**
- New records appearing
- Fields populated correctly
- No duplicate entries

**Common issues:**
- Empty fields (AI summaries, themes)
- Duplicate records (check URL uniqueness)
- Missing data (check Railway logs)

---

## 🐛 **Troubleshooting**

### **Digest Not Posted to Slack**

**Symptoms:**
- No message in #ai-daily-digest
- GitHub Actions shows success

**Diagnosis:**
```bash
# Check GitHub Actions logs
# Look for: "Posted digest to Slack"

# Check Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```

**Solutions:**
1. Verify SLACK_WEBHOOK_URL in GitHub Secrets
2. Check if webhook is still valid in Slack app settings
3. Verify channel exists and app has access

### **Buttons Not Working**

**Symptoms:**
- Click button, nothing happens
- Button shows error
- No update after clicking

**Diagnosis:**
```bash
# Check Railway logs
# Look for: "Received interaction from Slack"

# Test webhook endpoint
curl -X POST https://your-app.railway.app/health
```

**Solutions:**
1. Verify Railway app is running
2. Check SLACK_SIGNING_SECRET matches
3. Verify Interactivity URL in Slack app
4. Check Railway logs for errors

### **Articles Not in Airtable**

**Symptoms:**
- Button shows "✅ Added"
- No record in Airtable

**Diagnosis:**
```bash
# Check Railway logs for:
# [ASYNC] ✓ Added to Airtable: recXXXXXXXXXXXXXX
# or
# [ASYNC] ✗ Failed to add to Airtable: [error]
```

**Solutions:**
1. Verify AIRTABLE_API_KEY is valid
2. Check AIRTABLE_BASE_ID is correct
3. Verify table name matches exactly
4. Check field names in Airtable match code

### **Low Article Count**

**Symptoms:**
- Fewer than 150 articles collected
- Many sources failing

**Diagnosis:**
```bash
# Run digest locally with verbose logging
python3 scripts/run_ai_digest_pipeline.py force

# Check for errors like:
# ❌ HTTP 403 for https://...
# ❌ HTTP 404 for https://...
# ❌ Timeout fetching https://...
```

**Solutions:**
1. Install brotli: `pip3 install brotli`
2. Disable broken sources
3. Check RSS URLs are still valid
4. Increase RSS_REQUEST_TIMEOUT

### **RSS Source Failing**

**Symptoms:**
- Specific source always fails
- 403, 404, or timeout errors

**Diagnosis:**
```bash
# Test URL directly
curl -I "https://example.com/feed.xml"

# Check if it's a 403 (blocked)
# Check if it's a 404 (not found)
# Check if it times out
```

**Solutions:**

**For 403 (Forbidden):**
- Browser headers already added in code
- Try alternative URL (e.g., Medium endpoint)
- Source may require authentication

**For 404 (Not Found):**
- URL changed, find new URL
- Source discontinued, disable it
- Replace with similar source

**For Timeout:**
- Increase RSS_REQUEST_TIMEOUT
- Source may be slow, increase retries
- Source may be down temporarily

### **OpenAI Rate Limit**

**Symptoms:**
- Error: "Rate limit exceeded"
- Digest generation fails at AI filtering

**Diagnosis:**
```bash
# Check OpenAI usage dashboard
# Look for rate limit errors in logs
```

**Solutions:**
1. Wait a few minutes and retry
2. Reduce STAGE1_TARGET_COUNT
3. Upgrade OpenAI plan
4. Add retry logic with backoff

### **GitHub Actions Timeout**

**Symptoms:**
- Workflow exceeds 6 hours
- Killed by GitHub

**Diagnosis:**
```bash
# Check workflow execution time
# Look for slow operations
```

**Solutions:**
1. Reduce MAX_ARTICLES_PER_SOURCE
2. Increase MAX_CONCURRENT_REQUESTS
3. Disable slow sources
4. Optimize scraping logic

---

## 🔧 **Maintenance**

### **Weekly Tasks**

**Check Source Health:**
```bash
python3 scripts/add_rss_source.py list
```
- Disable sources with high failure rates
- Add new sources if needed

**Review Digest Quality:**
- Are articles relevant?
- Good source diversity?
- AI summaries accurate?

**Check Database Size:**
```sql
SELECT 
    pg_size_pretty(pg_database_size('postgres')) as db_size,
    (SELECT COUNT(*) FROM articles) as article_count,
    (SELECT COUNT(*) FROM daily_digests) as digest_count;
```

### **Monthly Tasks**

**Clean Old Articles:**
```sql
-- Delete articles older than 90 days
DELETE FROM articles 
WHERE scraped_at < NOW() - INTERVAL '90 days'
AND selected_for_digest = FALSE;
```

**Review Source Performance:**
```sql
SELECT 
    source_name,
    COUNT(*) as total_articles,
    COUNT(*) FILTER (WHERE selected_for_digest) as selected,
    ROUND(COUNT(*) FILTER (WHERE selected_for_digest)::numeric / COUNT(*) * 100, 2) as selection_rate
FROM articles
WHERE scraped_at > NOW() - INTERVAL '30 days'
GROUP BY source_name
ORDER BY selection_rate DESC;
```

**Update Dependencies:**
```bash
pip3 install --upgrade -r requirements.txt
```

**Review Costs:**
- OpenAI API usage
- Supabase storage
- Railway hosting
- Airtable records

### **Quarterly Tasks**

**Add New Sources:**
- Research new AI news sources
- Add regional sources (EU, Asia)
- Add niche sources (specific AI topics)

**Review AI Prompts:**
- Are selections high quality?
- Need to adjust filtering criteria?
- Update prompts in `services/prompt_service.py`

**Optimize Performance:**
- Review slow queries
- Add database indexes if needed
- Optimize scraping logic

**Update Documentation:**
- Update this guide
- Update PROJECT_STATUS.md
- Update README.md

---

## 📈 **Performance Benchmarks**

### **Expected Metrics**

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| **Articles collected** | 180-220 | 150-180 | <150 |
| **Source success rate** | >95% | 90-95% | <90% |
| **Execution time** | 3-4 min | 4-6 min | >6 min |
| **Selection diversity** | 5 different sources | 4 different | <4 |
| **Button success rate** | 100% | >95% | <95% |

### **Optimization Tips**

**If article count is low:**
- Add more sources
- Fix broken sources
- Increase MAX_ARTICLES_PER_SOURCE

**If execution time is high:**
- Increase MAX_CONCURRENT_REQUESTS
- Reduce MAX_ARTICLES_PER_SOURCE
- Disable slow sources

**If selection diversity is low:**
- Adjust AI prompts for diversity
- Add more diverse sources
- Check if dominant source is too prolific

---

## 🚨 **Emergency Procedures**

### **System Down**

**If digest fails completely:**

1. **Check GitHub Actions**
   - View latest workflow run
   - Check error logs
   - Manually trigger if needed

2. **Run Locally**
   ```bash
   python3 scripts/run_ai_digest_pipeline.py force
   ```

3. **Post Manual Digest**
   - Copy output from local run
   - Post to Slack manually
   - Note issue for later fix

### **Slack Buttons Broken**

**If buttons stop working:**

1. **Check Railway**
   - Verify app is running
   - Check logs for errors
   - Restart if needed

2. **Verify Slack Config**
   - Check Interactivity URL
   - Verify signing secret
   - Test webhook endpoint

3. **Temporary Workaround**
   - Add articles to Airtable manually
   - Fix buttons later

### **Database Issues**

**If Supabase is down:**

1. **Check Supabase Status**
   - Visit status.supabase.com
   - Check dashboard

2. **Wait for Recovery**
   - Supabase usually recovers quickly
   - Retry digest after recovery

3. **Contact Support**
   - If prolonged outage
   - Check Supabase support

---

## 📞 **Getting Help**

### **Check Logs First**

1. **GitHub Actions:** Workflow execution logs
2. **Railway:** Webhook server logs
3. **Supabase:** Database logs
4. **Browser Console:** For Slack button issues

### **Common Log Locations**

**GitHub Actions:**
```
https://github.com/willsupernormal/ai-newsletter-pipeline/actions
→ Click latest workflow
→ View logs
```

**Railway:**
```
https://railway.app/dashboard
→ Select project
→ View logs
→ Filter by error
```

**Supabase:**
```
https://supabase.com/dashboard
→ Select project
→ Logs
→ Filter by table/function
```

### **Debug Commands**

**Test RSS scraping:**
```bash
python3 scripts/run_rss_pipeline.py
```

**Test Slack webhook:**
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test"}'
```

**Test Railway webhook:**
```bash
curl https://your-app.railway.app/health
```

**Check Supabase connection:**
```bash
python3 -c "from config.settings import Settings; from database.supabase_simple import SimpleSupabaseClient; s = Settings(); c = SimpleSupabaseClient(s); print('✅ Connected' if c.client else '❌ Failed')"
```

---

## 📚 **Additional Resources**

- **[START_HERE.md](../START_HERE.md)** - Project overview
- **[README.md](../README.md)** - Technical architecture
- **[PROJECT_STATUS.md](../PROJECT_STATUS.md)** - Current state
- **[SETUP.md](SETUP.md)** - Initial setup guide
- **[AIRTABLE_DATA_SPEC.md](../AIRTABLE_DATA_SPEC.md)** - Data structure

---

**Questions?** Check [PROJECT_STATUS.md](../PROJECT_STATUS.md) for known issues or review the code in relevant directories.

