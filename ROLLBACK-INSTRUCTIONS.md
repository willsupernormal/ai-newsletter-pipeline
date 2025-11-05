# Rollback Instructions
## How to Revert to Airtable-Only System

**Created:** November 5, 2025
**Purpose:** Safe rollback from Phase 3 (Google Drive integration) to Phase 2 (Airtable only)

---

## Quick Rollback (Recommended)

**Fastest way - No code changes needed:**

1. **Go to Railway Dashboard**
2. **Set environment variable:**
   ```bash
   CONTENT_OUTPUT_MODE=airtable
   ```
3. **Save** - Railway will redeploy
4. **Done** - System reverts to Airtable-only

**This method:**
- ✅ Keeps new code in place (doesn't break anything)
- ✅ Just switches mode back to Airtable
- ✅ Takes 2-3 minutes (Railway redeploy)
- ✅ Can switch back to "both" anytime

---

## Full Rollback (If Quick Rollback Fails)

**If you want to completely remove Phase 3 code:**

### Step 1: Restore Backup Files

```bash
cd "/Users/will.bainbridge/CascadeProjects/ai-newsletter-pipeline copy"

# Restore original files
cp services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py services/slack_webhook_handler.py
cp config/settings_OLD_AIRTABLE_ONLY.py config/settings.py
cp .env.example.OLD_AIRTABLE_ONLY .env.example
```

### Step 2: Delete Phase 3 Files

```bash
# Remove new files (Phase 3)
rm services/gdocs_markdown_client.py
rm services/content_pipeline.py
```

### Step 3: Commit and Push

```bash
git add .
git commit -m "Rollback: Remove Phase 3 Google Drive integration, restore Airtable-only"
git push origin main
```

### Step 4: Railway Auto-Deploys

Wait 2-3 minutes for Railway to redeploy with old code.

### Step 5: Remove Railway Env Vars (Optional)

In Railway dashboard, remove:
- `CONTENT_OUTPUT_MODE`
- `GOOGLE_SERVICE_ACCOUNT_KEY`
- `MARKDOWN_CONTENT_FOLDER_ID`

---

## Backup File Reference

### Original Files (Backed Up)

1. **`services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py`**
   - Original webhook handler
   - Direct Airtable integration
   - No content pipeline

2. **`config/settings_OLD_AIRTABLE_ONLY.py`**
   - Original settings
   - No Google Drive env vars
   - No CONTENT_OUTPUT_MODE

3. **`.env.example.OLD_AIRTABLE_ONLY`**
   - Original env example
   - Only Airtable configuration

### Phase 3 Files (Can Be Deleted)

1. **`services/gdocs_markdown_client.py`** (NEW)
2. **`services/content_pipeline.py`** (NEW)
3. **`PHASE3-IMPLEMENTATION-SUMMARY.md`** (NEW)
4. **`ROLLBACK-INSTRUCTIONS.md`** (NEW - this file)

---

## What Each Rollback Method Does

### Quick Rollback (Env Var Change)
```
Current State:
- Phase 3 code exists
- CONTENT_OUTPUT_MODE=both
- Saves to Airtable & Drive

After Quick Rollback:
- Phase 3 code still exists (inactive)
- CONTENT_OUTPUT_MODE=airtable
- Saves to Airtable only
- Can switch back anytime
```

### Full Rollback (File Restore)
```
Current State:
- Phase 3 code exists
- Phase 3 files in repo

After Full Rollback:
- Phase 3 code deleted
- Original code restored
- Back to Phase 2 state
- Need to re-implement Phase 3 if wanted later
```

---

## Testing After Rollback

1. **Go to Slack** #ai-daily-digest
2. **Click** "Add to Pipeline" button
3. **Expected result:**
   - Article saves to Airtable only
   - Success message: "✅ Added to Airtable!"
   - No mention of Google Drive
4. **Check Airtable** - Record should exist
5. **Check Google Drive** - No new files (if using quick rollback, that's fine)

---

## Troubleshooting

### Issue: Railway Won't Deploy After Rollback

**Solution:**
1. Check Railway logs for errors
2. Verify restored files have no syntax errors
3. Try: Remove `GOOGLE_SERVICE_ACCOUNT_KEY` from Railway (might be causing JSON parse errors)

### Issue: "ContentPipelineHandler not found"

**Solution:**
1. You did full rollback but Railway still has old code cached
2. In Railway: Settings → Redeploy
3. Or: Make small change to code, commit, push (forces rebuild)

### Issue: Airtable Integration Broken

**Solution:**
1. Verify `AIRTABLE_API_KEY` and `AIRTABLE_BASE_ID` still set in Railway
2. Check Railway logs for Airtable errors
3. Test Airtable API connection

---

## Recovery Plan

### If Rollback Causes Issues

**Option 1: Roll forward (fix Phase 3)**
- Keep Phase 3 code
- Debug specific issue
- Stay on latest version

**Option 2: Full rollback (remove Phase 3)**
- Restore backup files
- Remove Phase 3 files
- Push to Railway

**Option 3: Emergency revert**
- Use Railway's deployment history
- Rollback to last working deployment
- Investigate offline

---

## Prevention for Future Updates

### Best Practices

1. **Always create backups before modifying:**
   ```bash
   cp file.py file_BACKUP_$(date +%Y%m%d).py
   ```

2. **Test locally first:**
   - Run server locally
   - Test button clicks
   - Verify both modes work

3. **Use feature flags:**
   - Already implemented: `CONTENT_OUTPUT_MODE`
   - Can switch modes without code changes

4. **Git branches:**
   - Create feature branch: `git checkout -b feature/google-drive`
   - Test in separate Railway environment
   - Merge to main when stable

5. **Railway staging environment:**
   - Create separate Railway project for testing
   - Test changes there first
   - Deploy to production when verified

---

## Backup Verification

To verify backups are intact:

```bash
cd "/Users/will.bainbridge/CascadeProjects/ai-newsletter-pipeline copy"

# Check backups exist
ls -lh services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py
ls -lh config/settings_OLD_AIRTABLE_ONLY.py
ls -lh .env.example.OLD_AIRTABLE_ONLY

# Check file sizes (should be similar to originals)
wc -l services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py
wc -l config/settings_OLD_AIRTABLE_ONLY.py
```

---

## Summary

**Recommended Approach:**
- ✅ Start with **Quick Rollback** (just change env var)
- ✅ Only do **Full Rollback** if quick rollback fails
- ✅ Keep backups for at least 1 month
- ✅ Document any issues encountered

**Quick Rollback Command:**
```bash
# In Railway Dashboard:
CONTENT_OUTPUT_MODE=airtable
```

**Full Rollback Commands:**
```bash
cp services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py services/slack_webhook_handler.py
cp config/settings_OLD_AIRTABLE_ONLY.py config/settings.py
rm services/gdocs_markdown_client.py services/content_pipeline.py
git add . && git commit -m "Rollback Phase 3" && git push
```

---

**Questions?** Check TROUBLESHOOTING.md or Railway logs.
