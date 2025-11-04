# Troubleshooting Guide

Complete debugging guide for the AI Newsletter Pipeline.

---

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Common Issues](#common-issues)
- [Component-Specific Issues](#component-specific-issues)
- [Error Messages](#error-messages)
- [Debugging Tools](#debugging-tools)
- [Emergency Procedures](#emergency-procedures)

---

## Quick Diagnostics

### System Health Check

**1. Check Railway Status**
```
URL: https://railway.app
Status: Should show "Deployed" with green checkmark
Logs: Look for "✓ Server running on port 8000"
```

**2. Check Supabase Connection**
```sql
-- Run in Supabase SQL Editor
SELECT COUNT(*) FROM digest_articles WHERE digest_date = CURRENT_DATE;
-- Should return 5 (today's articles)
```

**3. Check Slack App**
```
URL: https://api.slack.com/apps
Interactivity: Should be enabled
Request URL: Should point to Railway app
Bot Token: Should start with xoxb-
```

**4. Check Airtable**
```
Base ID: appwmAiF24deDVqFw
Table: Content Pipeline
Fields: Should have 5 AI fields + 3 user fields
```

### Quick Test

**End-to-end test:**
1. Go to Slack #ai-daily-digest
2. Click "Add to Pipeline" on any article
3. Fill modal (optional) and submit
4. Check Airtable for new record
5. Verify all fields populated

**Expected time:** 3-5 seconds from click to Airtable

---

## Common Issues

### Issue 1: Button Click Does Nothing

**Symptoms:**
- Click "Add to Pipeline" button
- Nothing happens
- No modal opens

**Causes:**
1. Railway not deployed
2. Slack app not configured
3. Wrong Request URL

**Solutions:**

```bash
# 1. Check Railway deployment
# Go to https://railway.app
# Verify status is "Deployed"
# Check logs for errors

# 2. Check Slack app configuration
# Go to https://api.slack.com/apps
# Features → Interactivity & Shortcuts
# Verify Request URL: https://your-app.up.railway.app/slack/interactions

# 3. Check Railway logs
# Look for: "Received action: add_to_pipeline from user: <username>"
# If missing, Slack isn't sending webhooks
```

**Fix:**
1. Redeploy Railway: `git push origin main`
2. Update Slack Request URL
3. Verify `SLACK_SIGNING_SECRET` in Railway

---

### Issue 2: Modal Opens But Submit Fails

**Symptoms:**
- Modal opens successfully
- Fill fields and click Submit
- Modal shows error or doesn't close

**Causes:**
1. Article not found in Supabase
2. Railway processing error
3. Airtable field mismatch

**Solutions:**

```bash
# 1. Check Railway logs
# Look for: "[ASYNC] Processing article: <article_id>"
# Look for errors after this line

# 2. Verify article exists in Supabase
```

```sql
SELECT * FROM digest_articles 
WHERE id = '<article_id_from_logs>';
```

```bash
# 3. Check Airtable fields
# Verify these fields exist with exact names:
# - Detailed Summary
# - Business Impact
# - Key Quotes
# - Specific Data
# - Companies Mentioned
# - Theme
# - Content Type
# - Your Angle
```

**Fix:**
1. Check Railway logs for specific error
2. Verify article in Supabase
3. Create missing Airtable fields

---

### Issue 3: Article Not in Airtable

**Symptoms:**
- Modal submits successfully
- Success message in Slack
- Article NOT in Airtable

**Causes:**
1. Airtable API key invalid
2. Base ID wrong
3. Field names don't match
4. Field types incorrect

**Solutions:**

```bash
# 1. Check Railway logs
# Look for: "Failed to create Airtable record"
# Look for: "Unknown field name: '<field_name>'"

# 2. Verify environment variables in Railway
AIRTABLE_API_KEY=key...
AIRTABLE_BASE_ID=app...

# 3. Verify field names match exactly (case-sensitive)
# Code → Airtable
# 'Detailed Summary' → 'Detailed Summary'
# 'Business Impact' → 'Business Impact'
# etc.

# 4. Verify field types
# Long text: Detailed Summary, Business Impact, Key Quotes, Specific Data, Your Angle
# Single line text: Companies Mentioned, Theme, Content Type
```

**Fix:**
1. Update Railway environment variables
2. Fix field names in Airtable
3. Change field types if needed

---

### Issue 4: Digest Generation Fails

**Symptoms:**
- Run `run_ai_digest_pipeline.py force`
- Script fails with error
- No articles in Supabase

**Causes:**
1. OpenAI API key invalid
2. Supabase connection failed
3. RSS feeds inaccessible
4. Slack webhook invalid

**Solutions:**

```bash
# 1. Check OpenAI API key
# Verify key is valid at https://platform.openai.com/api-keys

# 2. Check Supabase connection
# Verify SUPABASE_URL and SUPABASE_KEY in .env

# 3. Test RSS scraping
python -m scrapers.rss_scraper

# 4. Check Slack webhook
# Verify SLACK_WEBHOOK_URL in .env
```

**Fix:**
1. Update `.env` with correct API keys
2. Test individual components
3. Check script output for specific errors

---

### Issue 5: Railway Deployment Fails

**Symptoms:**
- Push to GitHub
- Railway shows "Failed" status
- Red X in deployment logs

**Causes:**
1. Syntax error in code
2. Missing dependency
3. Environment variable missing
4. Port configuration wrong

**Solutions:**

```bash
# 1. Check Railway logs for error
# Look for Python traceback
# Look for "ModuleNotFoundError"

# 2. Verify requirements.txt
# All dependencies listed
# Correct versions

# 3. Check environment variables
# All required vars set in Railway dashboard

# 4. Verify port configuration
# webhook_server.py should use PORT env var
# Railway sets this automatically
```

**Fix:**
1. Fix syntax errors in code
2. Add missing dependencies to `requirements.txt`
3. Set missing environment variables
4. Test locally before pushing

---

## Component-Specific Issues

### Supabase Issues

**Connection Timeout:**
```python
# Error: "Connection timeout"
# Fix: Check SUPABASE_URL and SUPABASE_KEY
# Verify network connection
# Check Supabase project status
```

**Column Not Found:**
```sql
-- Error: "column 'xxx' does not exist"
-- Fix: Run migration to add column
-- Or remove column reference from code
```

**View Dependency Error:**
```sql
-- Error: "cannot drop column because other objects depend on it"
-- Fix: Drop views first
DROP VIEW IF EXISTS current_week_digest CASCADE;
DROP VIEW IF EXISTS pending_airtable_articles CASCADE;
-- Then drop column
ALTER TABLE digest_articles DROP COLUMN xxx;
-- Then recreate views
```

### Railway Issues

**Server Won't Start:**
```bash
# Check logs for:
# - Import errors
# - Missing environment variables
# - Port binding errors

# Fix:
# 1. Verify all imports exist
# 2. Set all required env vars
# 3. Use PORT env var (Railway sets this)
```

**Webhook Not Receiving Requests:**
```bash
# Check:
# 1. Slack Request URL points to Railway
# 2. Railway app is deployed
# 3. SLACK_SIGNING_SECRET is correct

# Test:
curl -X POST https://your-app.up.railway.app/health
# Should return: {"status": "healthy"}
```

### Slack Issues

**Modal Doesn't Open:**
```python
# Error: "trigger_id expired"
# Fix: trigger_id expires in 3 seconds
# Must call views.open immediately after receiving action

# Error: "invalid_auth"
# Fix: Check SLACK_BOT_TOKEN is correct
# Must start with xoxb-
```

**Button Doesn't Update:**
```python
# Error: Button stays as "Add to Pipeline"
# Fix: Check response_url is being used
# Verify button block_id matches
```

### Airtable Issues

**Unknown Field Name:**
```python
# Error: "Unknown field name: 'Detailed Summary'"
# Fix: Create field in Airtable with exact name
# Case-sensitive: 'Detailed Summary' not 'detailed summary'
```

**Invalid Field Type:**
```python
# Error: "Field type mismatch"
# Fix: Change field type in Airtable
# Long text for: Summary, Impact, Quotes, Data, Angle
# Single line text for: Companies, Theme, Content Type
```

---

## Error Messages

### Python Errors

**`'str' object has no attribute 'get'`**
```python
# Cause: Trying to call .get() on a string
# Fix: Check if object is dict before calling .get()
if isinstance(obj, dict):
    value = obj.get('key')
```

**`name 'xxx' is not defined`**
```python
# Cause: Variable not defined or not passed to function
# Fix: Define variable or add to function parameters
def my_function(param1, param2, xxx):
    # Now xxx is defined
```

**`'NoneType' object has no attribute 'xxx'`**
```python
# Cause: Object is None
# Fix: Check for None before accessing attributes
if obj is not None:
    value = obj.xxx
```

### Slack Errors

**`channel_not_found`**
```python
# Cause: Channel ID is wrong
# Fix: Use correct channel ID
# #ai-daily-digest = C09NLCBCMCZ
```

**`invalid_auth`**
```python
# Cause: Bot token is invalid
# Fix: Check SLACK_BOT_TOKEN
# Must start with xoxb-
# Must be from correct Slack app
```

**`trigger_id_expired`**
```python
# Cause: Waited too long to open modal
# Fix: Call views.open immediately after receiving action
# trigger_id expires in 3 seconds
```

### Airtable Errors

**`INVALID_REQUEST_UNKNOWN`**
```python
# Cause: Field name doesn't exist
# Fix: Create field in Airtable
# Verify exact name match (case-sensitive)
```

**`INVALID_VALUE_FOR_COLUMN`**
```python
# Cause: Value doesn't match field type
# Fix: Change field type or format value
# Long text for long strings
# Single line text for short strings
```

### Supabase Errors

**`relation "xxx" does not exist`**
```sql
-- Cause: Table or view doesn't exist
-- Fix: Run migration to create table/view
-- Or check table name spelling
```

**`column "xxx" does not exist`**
```sql
-- Cause: Column doesn't exist in table
-- Fix: Run migration to add column
-- Or remove column reference from code
```

---

## Debugging Tools

### Railway Logs

```bash
# View logs in Railway dashboard
# Look for:
# - "✓ Server running on port 8000" (success)
# - Python tracebacks (errors)
# - "Received action: xxx" (webhook received)
# - "[ASYNC] Processing article: xxx" (processing started)
# - "✓ Added to Airtable: xxx" (success)
```

### Supabase SQL Editor

```sql
-- Check today's articles
SELECT * FROM digest_articles 
WHERE digest_date = CURRENT_DATE;

-- Check article by ID
SELECT * FROM digest_articles 
WHERE id = '<article_id>';

-- Check Airtable tracking
SELECT title, added_to_airtable, airtable_record_id 
FROM digest_articles 
WHERE digest_date = CURRENT_DATE;

-- Check views
SELECT * FROM current_week_digest;
SELECT * FROM pending_airtable_articles;
```

### Local Testing

```bash
# Test digest generation
PYTHONPATH=/path/to/project python3 scripts/run_ai_digest_pipeline.py force

# Test RSS scraping
python -m scrapers.rss_scraper

# Test article scraping
python -m scrapers.article_scraper

# Check Python imports
python -c "import services.slack_webhook_handler"
python -c "import services.airtable_client"
```

### Curl Testing

```bash
# Test Railway health
curl https://your-app.up.railway.app/health

# Test Slack webhook (requires signature)
curl -X POST https://your-app.up.railway.app/slack/interactions \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "payload={...}"
```

---

## Emergency Procedures

### Rollback Deployment

```bash
# Find last working commit
git log --oneline -10

# Rollback to that commit
git reset --hard <commit-hash>

# Force push to Railway
git push -f origin main

# Wait 2-3 minutes for deployment
```

### Restore Database

```sql
-- If you dropped columns by mistake
-- You'll need to restore from backup
-- Contact Supabase support

-- If you just need to recreate views
CREATE OR REPLACE VIEW current_week_digest AS
SELECT * FROM digest_articles
WHERE digest_date >= DATE_TRUNC('week', CURRENT_DATE)::DATE
ORDER BY digest_date DESC, created_at ASC;

CREATE OR REPLACE VIEW pending_airtable_articles AS
SELECT * FROM digest_articles
WHERE added_to_airtable = FALSE
ORDER BY digest_date DESC;
```

### Reset Slack App

```bash
# If Slack app is completely broken:
# 1. Go to https://api.slack.com/apps
# 2. Delete old app
# 3. Create new app
# 4. Enable Interactivity
# 5. Set Request URL
# 6. Add Bot Token Scopes
# 7. Install to workspace
# 8. Update tokens in Railway
```

### Clear Airtable

```bash
# If you need to start fresh:
# 1. Delete all records in Airtable
# 2. Reset added_to_airtable in Supabase
```

```sql
UPDATE digest_articles 
SET added_to_airtable = FALSE, 
    airtable_record_id = NULL;
```

---

## Getting Help

### Check These First
1. Railway logs
2. Supabase logs  
3. Slack API logs
4. This troubleshooting guide

### Information to Gather
- Error message (full text)
- Railway logs (last 50 lines)
- Steps to reproduce
- Expected vs actual behavior
- Environment (local vs Railway)

### Useful Commands

```bash
# Get Railway logs
# Go to https://railway.app → Your Project → Deployments → View Logs

# Get Supabase logs
# Go to https://supabase.com → Your Project → Logs

# Get Slack API logs
# Go to https://api.slack.com/apps → Your App → Event Subscriptions → View Logs

# Test local environment
python -c "from config.settings import Settings; s = Settings(); print('OK')"

# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "(openai|supabase|fastapi|slack|airtable)"
```

---

## Prevention

### Before Making Changes

1. ✅ Read the code you're changing
2. ✅ Check for dependencies
3. ✅ Review deployment checklist
4. ✅ Test locally if possible
5. ✅ Make small, incremental changes

### After Making Changes

1. ✅ Commit with descriptive message
2. ✅ Push to GitHub
3. ✅ Wait for Railway deployment
4. ✅ Check Railway logs
5. ✅ Test end-to-end
6. ✅ Verify Airtable data

### Regular Maintenance

1. ✅ Check Railway logs weekly
2. ✅ Verify Supabase storage usage
3. ✅ Test button clicks monthly
4. ✅ Review Airtable data quality
5. ✅ Update dependencies quarterly

---

## Success Indicators

### System is Working When:
- ✅ Railway shows "Deployed" status
- ✅ Supabase has 5 articles daily
- ✅ Slack digest posts daily
- ✅ Button clicks open modal
- ✅ Modal submissions succeed
- ✅ Articles appear in Airtable
- ✅ All fields populated correctly
- ✅ No errors in Railway logs

### System Needs Attention When:
- ❌ Railway shows "Failed" status
- ❌ No articles in Supabase
- ❌ No Slack digest posted
- ❌ Button clicks fail
- ❌ Modal doesn't open
- ❌ Articles missing from Airtable
- ❌ Fields not populated
- ❌ Errors in Railway logs

---

## Contact

For persistent issues:
1. Check all sections of this guide
2. Review [README.md](README.md) for setup
3. Review [CHANGELOG.md](CHANGELOG.md) for recent changes
4. Check Railway, Supabase, and Slack logs
5. Test each component individually
