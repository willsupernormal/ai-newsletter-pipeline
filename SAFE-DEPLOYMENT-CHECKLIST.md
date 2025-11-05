# Safe Deployment Checklist
## Phase 3: Google Drive Integration

**Date:** November 5, 2025
**Purpose:** Ensure safe deployment with easy rollback

---

## ✅ Backups Created

All modified files have been backed up:

- ✅ `services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py` (27KB)
- ✅ `config/settings_OLD_AIRTABLE_ONLY.py` (7.8KB)
- ✅ `.env.example.OLD_AIRTABLE_ONLY` (2.4KB)

**Location:** Same directories as originals
**Exclusion:** Added to `.gitignore` (won't be committed)

---

## 📁 New Files Added

Phase 3 files (safe to commit):

- ✅ `services/gdocs_markdown_client.py` - Google Drive markdown client
- ✅ `services/content_pipeline.py` - Content routing orchestrator
- ✅ `PHASE3-IMPLEMENTATION-SUMMARY.md` - Implementation guide
- ✅ `ROLLBACK-INSTRUCTIONS.md` - How to revert
- ✅ `SAFE-DEPLOYMENT-CHECKLIST.md` - This file

---

## 🔄 Modified Files

Files that were changed (originals backed up):

- ⚠️ `services/slack_webhook_handler.py`
  - Backup: `slack_webhook_handler_OLD_AIRTABLE_ONLY.py`
  - Change: Routes to ContentPipelineHandler instead of direct Airtable

- ⚠️ `config/settings.py`
  - Backup: `settings_OLD_AIRTABLE_ONLY.py`
  - Change: Added 3 new environment variables

- ⚠️ `.env.example`
  - Backup: `.env.example.OLD_AIRTABLE_ONLY`
  - Change: Documented Google Drive configuration

---

## 📝 Documentation Updated

- ✅ `README.md` - Phase 3 architecture and setup instructions
- ✅ `CHANGELOG.md` - Version 3.0.0 documentation

---

## 🚀 Deployment Options

### Option 1: Safe Deployment (Recommended)

**Deploy Phase 3 code but keep Airtable-only mode:**

1. ✅ Commit and push all files
2. ✅ Railway auto-deploys (2-3 minutes)
3. ✅ System continues using Airtable only (default mode)
4. ✅ Test that Airtable still works
5. ⏭️ When ready: Add Google Drive env vars to enable Phase 3

**Benefits:**
- Code deployed but inactive
- No disruption to current workflow
- Can enable Google Drive when you're ready
- Easy to test

**Commands:**
```bash
cd "/Users/will.bainbridge/CascadeProjects/ai-newsletter-pipeline copy"
git add .
git commit -m "Add Phase 3: Google Drive integration (inactive, Airtable-only mode)"
git push origin main
```

### Option 2: Full Deployment

**Deploy and enable Google Drive immediately:**

1. ✅ Complete Google Drive folder setup (see PHASE3-IMPLEMENTATION-SUMMARY.md)
2. ✅ Add env vars to Railway:
   - `CONTENT_OUTPUT_MODE=both`
   - `GOOGLE_SERVICE_ACCOUNT_KEY={...}`
   - `MARKDOWN_CONTENT_FOLDER_ID={...}`
3. ✅ Commit and push code
4. ✅ Railway deploys with Google Drive enabled
5. ✅ Test both Airtable and Google Drive

**Benefits:**
- Full Phase 3 active immediately
- Save to both destinations
- Complete system operational

---

## 🧪 Testing Plan

### Test 1: Airtable-Only (Baseline)

**Before adding Google Drive env vars:**

1. Go to Slack #ai-daily-digest
2. Click "Add to Pipeline" button
3. Fill modal and submit
4. **Expected:** "✅ Added to Airtable!"
5. **Verify:** Record appears in Airtable
6. **Verify:** No errors in Railway logs

### Test 2: Both Destinations

**After adding Google Drive env vars:**

1. Click "Add to Pipeline" button
2. Fill modal and submit
3. **Expected:** "✅ Added to Airtable & Google Drive!"
4. **Verify:** Record in Airtable
5. **Verify:** Markdown file in Google Drive
6. **Verify:** No errors in Railway logs

### Test 3: Markdown File Format

1. Open markdown file in Google Drive
2. **Verify:** YAML frontmatter at top
3. **Verify:** All fields present (title, theme, etc.)
4. **Verify:** Markdown body formatted correctly
5. **Verify:** Full article text included

### Test 4: Claude Code Querying

```bash
cd "/path/to/Google Drive/AI-Newsletter-Content"
grep -r "theme:" .
```

**Expected:** Should find articles by theme

---

## 🔄 Rollback Plan

### Quick Rollback (No Code Changes)

**If issues occur after deployment:**

1. **Railway Dashboard** → Environment Variables
2. **Set:** `CONTENT_OUTPUT_MODE=airtable`
3. **Save** → Railway redeploys
4. **Result:** Back to Airtable-only mode
5. **Time:** 2-3 minutes

### Full Rollback (Restore Original Code)

**If quick rollback doesn't work:**

```bash
cd "/Users/will.bainbridge/CascadeProjects/ai-newsletter-pipeline copy"

# Restore backups
cp services/slack_webhook_handler_OLD_AIRTABLE_ONLY.py services/slack_webhook_handler.py
cp config/settings_OLD_AIRTABLE_ONLY.py config/settings.py
cp .env.example.OLD_AIRTABLE_ONLY .env.example

# Remove Phase 3 files
rm services/gdocs_markdown_client.py
rm services/content_pipeline.py

# Commit and push
git add .
git commit -m "Rollback: Remove Phase 3, restore Airtable-only"
git push origin main
```

**See:** `ROLLBACK-INSTRUCTIONS.md` for detailed steps

---

## ⚠️ Risk Assessment

### Low Risk
- ✅ Backward compatible (defaults to Airtable-only)
- ✅ Original code backed up
- ✅ Easy rollback (env var change)
- ✅ No breaking changes to existing functionality

### Medium Risk
- ⚠️ New dependencies (googleapis already in requirements.txt)
- ⚠️ Google Drive API quota limits (unlikely to hit)
- ⚠️ Service account permissions (already tested with Context Parser)

### Mitigation
- ✅ Test in Airtable-only mode first
- ✅ Add Google Drive gradually (test with one article)
- ✅ Monitor Railway logs during deployment
- ✅ Keep backups for 1 month

---

## 📊 Deployment Checklist

### Pre-Deployment

- [x] Code written and tested locally (as much as possible)
- [x] Backup files created
- [x] Documentation updated (README, CHANGELOG)
- [x] Rollback instructions written
- [ ] Google Drive folder created (when you have access)
- [ ] Service account permissions granted (when you have access)

### Deployment (Safe Method)

- [ ] Commit Phase 3 code
- [ ] Push to GitHub
- [ ] Wait for Railway deployment (2-3 min)
- [ ] Check Railway logs for errors
- [ ] Test Airtable-only mode works
- [ ] Verify no regression

### Deployment (Full Method)

- [ ] Complete Google Drive setup
- [ ] Add env vars to Railway
- [ ] Push code to GitHub
- [ ] Wait for Railway deployment
- [ ] Test button click
- [ ] Verify both destinations work
- [ ] Check markdown file format

### Post-Deployment

- [ ] Monitor Railway logs for 24 hours
- [ ] Test with multiple articles
- [ ] Verify Claude Code can query files
- [ ] Show demo to boss
- [ ] Decide on final mode (airtable/markdown/both)

---

## 🛠️ Troubleshooting

### Issue: Railway Deployment Fails

**Check:**
- Railway logs for specific error
- Syntax errors in new files
- Import errors

**Fix:**
- Review error message
- Fix syntax if needed
- Re-push

### Issue: Google Drive Files Not Appearing

**Check:**
- `MARKDOWN_CONTENT_FOLDER_ID` is correct
- Service account has Manager permission
- Railway logs for Drive API errors

**Fix:**
- Verify folder ID
- Re-share folder with service account
- Check env var formatting

### Issue: Airtable Stops Working

**Check:**
- Railway logs for Airtable errors
- `AIRTABLE_API_KEY` still set
- Network connectivity

**Fix:**
- Quick rollback: `CONTENT_OUTPUT_MODE=airtable`
- Verify Airtable credentials
- Check Airtable API status

---

## 📞 Support Resources

1. **PHASE3-IMPLEMENTATION-SUMMARY.md** - Complete implementation guide
2. **ROLLBACK-INSTRUCTIONS.md** - How to revert changes
3. **TROUBLESHOOTING.md** - Common issues and fixes
4. **Railway Logs** - Real-time deployment logs
5. **CHANGELOG.md** - Version history and changes

---

## ✅ Final Checklist

Before marking deployment complete:

- [ ] All tests pass
- [ ] No errors in Railway logs
- [ ] Airtable integration confirmed working
- [ ] Google Drive integration confirmed working (if enabled)
- [ ] Boss has seen demo
- [ ] Final mode decision made
- [ ] Backups kept for 1 month
- [ ] Team trained on new system (if applicable)

---

## 🎯 Success Criteria

**Deployment is successful when:**

1. ✅ Railway deploys without errors
2. ✅ Airtable integration still works (baseline)
3. ✅ Google Drive saves work (when enabled)
4. ✅ No regression in existing features
5. ✅ Rollback tested and works
6. ✅ Boss approves final configuration

---

## 📝 Notes

**Recommended Approach:**
1. Deploy code in Airtable-only mode (safe)
2. Test thoroughly
3. Add Google Drive env vars when ready
4. Test both modes
5. Show boss both options
6. Choose final mode

**Timeline:**
- Code deployment: 5 minutes
- Railway deployment: 2-3 minutes
- Testing: 10 minutes
- Google Drive setup (when ready): 10 minutes
- Total: ~30 minutes

---

**Remember:** You can always rollback with a single env var change! 🔄
