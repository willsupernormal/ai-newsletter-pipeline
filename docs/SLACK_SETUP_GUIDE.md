# 📱 Slack Integration Setup Guide

**Quick Start Guide for Daily Digest Slack Posting**

---

## 🎯 Overview

Your AI newsletter pipeline will now post daily digests directly to Slack:
- **Channel**: `#ai-daily-digest`
- **Time**: 7 AM AEST (after GitHub Actions completes)
- **Format**: Beautiful formatted message with 5 articles + AI summary
- **Errors**: Personal notifications for pipeline failures

---

## 📋 Setup Checklist

- [ ] Create `#ai-daily-digest` Slack channel
- [ ] Create main webhook for daily digests
- [ ] Create error webhook for personal notifications
- [ ] Add webhooks to GitHub secrets
- [ ] Add webhooks to local `.env` (for testing)
- [ ] Test locally
- [ ] Deploy to GitHub Actions

---

## 🔧 Step 1: Create Slack Webhooks

### **A. Create Main Digest Webhook**

1. **Open Slack in browser**: `https://[your-workspace].slack.com`

2. **Access App Directory**:
   - Click workspace name (top left)
   - Select **Settings & administration** → **Manage apps**
   - OR go to: `https://[your-workspace].slack.com/apps`

3. **Find Incoming Webhooks**:
   - Search for "Incoming Webhooks"
   - Click on the app
   - Click **Add to Slack** (or **Add Configuration**)

4. **Configure Webhook**:
   - **Channel**: Select `#ai-daily-digest`
   - Click **Add Incoming WebHooks integration**

5. **Customize (Optional)**:
   - **Descriptive Label**: "AI Newsletter Pipeline - Daily Digest"
   - **Customize Name**: "AI Digest Bot"
   - **Customize Icon**: Upload a robot/AI icon (optional)

6. **Copy Webhook URL**:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```
   
   ⚠️ **IMPORTANT**: Save this URL securely - it's a secret!

### **B. Create Error Notification Webhook**

**Option 1: Direct Message (Recommended)**

1. Go back to **Incoming Webhooks** in App Directory
2. Click **Add Configuration** again
3. This time select: **"Privately to @[your-name]"** or **"Privately to you"**
4. Click **Add Incoming WebHooks integration**
5. Copy this second webhook URL

**Option 2: Private Error Channel**

1. Create a private channel: `#ai-pipeline-errors` (just you as member)
2. Create webhook for this channel
3. Copy the webhook URL

**Why separate webhooks?**
- Main webhook → Team channel (`#ai-daily-digest`)
- Error webhook → Personal DM or private channel
- You get immediate personal notifications for failures

---

## 🔐 Step 2: Add Webhooks to GitHub Secrets

### **Using GitHub CLI (Recommended)**

```bash
# Navigate to your project
cd "/Users/will.bainbridge/CascadeProjects/ai-newsletter-pipeline copy"

# Add main webhook
gh secret set SLACK_WEBHOOK_URL
# Paste your main webhook URL when prompted, press Enter

# Add error webhook
gh secret set SLACK_ERROR_WEBHOOK_URL
# Paste your error webhook URL when prompted, press Enter
```

### **Using GitHub Web UI**

1. Go to: `https://github.com/willsupernormal/ai-newsletter-pipeline`
2. Click **Settings** tab
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**

**Add First Secret:**
- Name: `SLACK_WEBHOOK_URL`
- Value: [Paste your main webhook URL]
- Click **Add secret**

**Add Second Secret:**
- Name: `SLACK_ERROR_WEBHOOK_URL`
- Value: [Paste your error webhook URL]
- Click **Add secret**

---

## 💻 Step 3: Add Webhooks to Local Environment

For local testing, add to your `.env` file:

```bash
# Add to .env file
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/MAIN/WEBHOOK" >> .env
echo "SLACK_ERROR_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ERROR/WEBHOOK" >> .env
echo "SLACK_ENABLED=true" >> .env
```

**Or manually edit `.env`:**

```bash
# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
SLACK_ERROR_WEBHOOK_URL=https://hooks.slack.com/services/T11111111/B11111111/YYYYYYYYYYYYYYYYYYYY
SLACK_ENABLED=true
SLACK_CHANNEL_NAME=ai-daily-digest
```

---

## 🧪 Step 4: Test Locally

### **Test 1: Verify Webhook Works**

```bash
# Quick webhook test
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🤖 Test message from AI Newsletter Pipeline"}' \
  YOUR_WEBHOOK_URL
```

You should see the message appear in your Slack channel immediately.

### **Test 2: Test Slack Notifier**

```python
# Create test file: test_slack.py
python3 -c "
import asyncio
from services.slack_notifier import SlackNotifier
from config.settings import Settings
from datetime import date

async def test():
    settings = Settings()
    slack = SlackNotifier(
        webhook_url=settings.SLACK_WEBHOOK_URL,
        error_webhook_url=settings.SLACK_ERROR_WEBHOOK_URL,
        enabled=True
    )
    
    # Test digest message
    test_articles = [
        {
            'title': 'Test Article: AI Governance Framework',
            'source_name': 'Test Source',
            'summary': 'This is a test summary for the Slack integration.',
            'url': 'https://example.com/test'
        }
    ]
    
    success = slack.post_digest(
        digest_date=date.today(),
        summary_text='This is a test digest to verify Slack integration is working correctly.',
        key_insights=['Test insight 1', 'Test insight 2'],
        selected_articles=test_articles,
        total_processed=50,
        rss_count=30,
        twitter_count=20
    )
    
    print(f'Slack post success: {success}')

asyncio.run(test())
"
```

### **Test 3: Test Error Notification**

```python
python3 -c "
from services.slack_notifier import SlackNotifier
from config.settings import Settings

settings = Settings()
slack = SlackNotifier(
    webhook_url=settings.SLACK_WEBHOOK_URL,
    error_webhook_url=settings.SLACK_ERROR_WEBHOOK_URL,
    enabled=True
)

slack.post_error_notification(
    error_message='Test error notification',
    error_details='This is a test to verify error notifications work',
    pipeline_stage='Testing'
)

print('Error notification sent!')
"
```

### **Test 4: Run Full Pipeline**

```bash
# Run the full pipeline locally
python3 run_ai_digest_pipeline.py
```

Check your Slack channel - you should see the digest posted!

---

## 🚀 Step 5: Deploy to GitHub Actions

### **Verify Secrets Are Set**

```bash
# List secrets (won't show values, just names)
gh secret list
```

You should see:
- `SLACK_WEBHOOK_URL`
- `SLACK_ERROR_WEBHOOK_URL`

### **Trigger Manual Test Run**

```bash
# Trigger workflow manually
gh workflow run daily-scrape.yml

# Wait a moment, then check status
gh run list

# View logs of latest run
gh run view --log
```

### **Check Slack**

After the workflow completes (~5-10 minutes):
- Check `#ai-daily-digest` for the digest message
- If there's an error, check your personal DM/error channel

---

## 📊 What You'll See in Slack

### **Daily Digest Message**

```
🤖 AI Daily Digest - October 23, 2025

📊 Summary
Today's AI landscape focuses on enterprise adoption challenges, with 
major developments in model governance and data infrastructure strategies.

💡 Key Insights
• Enterprise AI governance frameworks gaining traction
• Data preparation remains critical bottleneck
• Vendor-agnostic approaches showing ROI benefits

────────────────────────────────────────

📰 Top 5 Articles

1️⃣ Enterprise AI Governance: New Framework Released
Harvard Business Review

Major consulting firms release comprehensive governance framework 
addressing compliance, ethics, and operational risks in AI deployment.

🔗 Read Article

────────────────────────────────────────

[Articles 2-5 follow same format]

────────────────────────────────────────

📈 Today's Stats • Articles Processed: 87 (50 RSS + 37 Twitter) • Selected: 5
```

### **Error Notification (if pipeline fails)**

```
⚠️ AI Pipeline Error

Error: Daily digest pipeline failed for 2025-10-23

Stage: AI Digest Pipeline

Details:
OpenAI API rate limit exceeded

🕐 2025-10-23 07:15:32
```

---

## 🔧 Troubleshooting

### **Issue: "Slack posting failed"**

**Check:**
1. Webhook URL is correct in `.env` or GitHub secrets
2. Webhook hasn't been revoked in Slack
3. Network connectivity (firewall blocking?)
4. Check logs for specific error message

**Solution:**
```bash
# Test webhook directly
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-type: application/json' \
  -d '{"text":"Test"}'
```

### **Issue: "No message appears in Slack"**

**Check:**
1. `SLACK_ENABLED=true` in environment
2. Webhook URL is set
3. Correct channel selected when creating webhook
4. You're looking at the right channel

**Solution:**
```bash
# Check environment variables
python3 -c "from config.settings import Settings; s = Settings(); print(f'Enabled: {s.SLACK_ENABLED}'); print(f'Webhook: {s.SLACK_WEBHOOK_URL[:50]}...')"
```

### **Issue: "Message format looks broken"**

**Check:**
1. Article summaries might be too long
2. Special characters in text

**Solution:**
- Summaries are auto-truncated to 300 chars
- Check `slack_notifier.py` formatting logic

### **Issue: "GitHub Actions fails with Slack error"**

**Check:**
1. Secrets are set in GitHub (not just local `.env`)
2. Secret names match exactly: `SLACK_WEBHOOK_URL`
3. Workflow file has correct environment variables

**Solution:**
```bash
# Re-add secrets
gh secret set SLACK_WEBHOOK_URL
gh secret set SLACK_ERROR_WEBHOOK_URL
```

---

## 🔒 Security Best Practices

### **Webhook URL Security**

✅ **DO:**
- Store in GitHub secrets
- Store in `.env` (which is gitignored)
- Regenerate if accidentally exposed
- Use separate webhooks for different purposes

❌ **DON'T:**
- Commit webhook URLs to git
- Share webhook URLs publicly
- Log webhook URLs in code
- Use same webhook for testing and production

### **Regenerating Webhooks**

If a webhook is compromised:

1. Go to Slack → **Settings & administration** → **Manage apps**
2. Find **Incoming Webhooks**
3. Click **Configure**
4. Find the compromised webhook
5. Click **Remove** or **Regenerate**
6. Create new webhook
7. Update GitHub secrets and `.env`

---

## 📝 Configuration Options

### **Disable Slack Posting**

Temporarily disable without removing webhooks:

```bash
# In .env
SLACK_ENABLED=false
```

Or in GitHub secrets:
```bash
gh secret set SLACK_ENABLED --body "false"
```

### **Change Channel**

To post to a different channel:

1. Create new webhook for new channel
2. Update `SLACK_WEBHOOK_URL` secret
3. Update `SLACK_CHANNEL_NAME` in `.env` (documentation only)

### **Customize Message Format**

Edit `services/slack_notifier.py`:
- `format_digest_message()` - Main digest formatting
- `post_error_notification()` - Error message formatting

---

## 🎯 Next Steps

After setup is complete:

1. ✅ **Monitor first few runs** - Check Slack messages look good
2. ✅ **Test error notifications** - Verify you get personal alerts
3. ✅ **Adjust formatting** - Tweak message format if needed
4. ✅ **Team feedback** - Get team input on digest usefulness

---

## 📚 Resources

- [Slack Incoming Webhooks Docs](https://api.slack.com/messaging/webhooks)
- [Slack Block Kit Builder](https://app.slack.com/block-kit-builder) - Visual message designer
- [Slack Message Formatting](https://api.slack.com/reference/surfaces/formatting)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## ✅ Setup Complete Checklist

- [ ] `#ai-daily-digest` channel created
- [ ] Main webhook created and tested
- [ ] Error webhook created and tested
- [ ] Both webhooks added to GitHub secrets
- [ ] Both webhooks added to local `.env`
- [ ] Local test successful
- [ ] GitHub Actions test successful
- [ ] Team can see messages in Slack
- [ ] Error notifications working
- [ ] Documentation reviewed

---

**Status**: Ready to go live! 🚀

Your daily AI digest will now automatically post to Slack every morning at 7 AM AEST.
