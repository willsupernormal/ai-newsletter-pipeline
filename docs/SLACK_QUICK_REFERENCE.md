# 📱 Slack Integration - Quick Reference Card

**One-page guide for Slack webhook setup**

---

## 🎯 What You Need

1. **Slack workspace access**
2. **Permission to create webhooks**
3. **GitHub repository access**
4. **5 minutes**

---

## ⚡ Quick Setup (5 Steps)

### **1. Create Slack Webhooks**

```
Slack → Settings & administration → Manage apps
→ Search "Incoming Webhooks" → Add to Slack
→ Select channel: #ai-daily-digest → Add
→ Copy webhook URL
```

**Create 2 webhooks:**
- **Main**: `#ai-daily-digest` channel
- **Error**: Your personal DM or `#ai-pipeline-errors`

### **2. Add to GitHub Secrets**

```bash
gh secret set SLACK_WEBHOOK_URL
# Paste main webhook URL

gh secret set SLACK_ERROR_WEBHOOK_URL  
# Paste error webhook URL
```

### **3. Add to Local `.env`**

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/MAIN/WEBHOOK
SLACK_ERROR_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ERROR/WEBHOOK
SLACK_ENABLED=true
```

### **4. Test Locally**

```bash
python3 run_ai_digest_pipeline.py
```

Check Slack for message!

### **5. Deploy**

```bash
git add .
git commit -m "Add Slack integration"
git push origin main
```

Done! ✅

---

## 🧪 Quick Tests

### **Test Webhook**
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-type: application/json' \
  -d '{"text":"Test"}'
```

### **Test Error Notification**
```python
python3 -c "
from services.slack_notifier import SlackNotifier
from config.settings import Settings
s = Settings()
SlackNotifier(s.SLACK_WEBHOOK_URL, s.SLACK_ERROR_WEBHOOK_URL).post_error_notification('Test error')
"
```

---

## 🔧 Common Issues

| Problem | Solution |
|---------|----------|
| No message in Slack | Check `SLACK_ENABLED=true` |
| "Webhook not found" | Verify webhook URL is correct |
| GitHub Actions fails | Check secrets are set: `gh secret list` |
| Wrong channel | Create new webhook for correct channel |

---

## 📊 What You'll See

**Daily at 7 AM AEST:**
```
🤖 AI Daily Digest - [Date]
📊 Summary: [AI-generated summary]
💡 Key Insights: [3 bullet points]
📰 Top 5 Articles: [With links]
📈 Stats: [Articles processed]
```

**On Errors:**
```
⚠️ AI Pipeline Error
Error: [Error message]
Stage: [Pipeline stage]
Details: [Error details]
```

---

## 🔐 Security Reminders

- ✅ Webhook URLs are secrets - never commit to git
- ✅ Store in GitHub secrets and `.env` only
- ✅ Regenerate if accidentally exposed
- ✅ Use separate webhooks for main/error channels

---

## 📞 Need Help?

1. Check `docs/SLACK_SETUP_GUIDE.md` for detailed instructions
2. Check `docs/SLACK_INTEGRATION_PLAN.md` for technical details
3. Test locally first before deploying to GitHub Actions

---

**Setup Time**: ~5 minutes  
**Status**: Production ready ✅
