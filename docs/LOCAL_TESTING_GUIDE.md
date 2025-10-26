# 🧪 Local Testing Guide - Phase 2

**Goal**: Test webhook server locally before deploying  
**Time**: 15 minutes

---

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Test Components

### Test Airtable:
```bash
python test_airtable.py
```

Should see: `✅ Connected successfully!`

---

## 3. Start Webhook Server

```bash
python -m uvicorn api.webhook_server:app --reload --port 8000
```

Test health:
```bash
curl http://localhost:8000/health
```

---

## 4. Expose with ngrok

Install ngrok:
```bash
brew install ngrok
```

Run:
```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

---

## 5. Configure Slack

1. Go to https://api.slack.com/apps
2. Your app → "Interactivity & Shortcuts"
3. Request URL: `https://abc123.ngrok.io/slack/interactions`
4. Save

---

## 6. Test

1. Run pipeline: `python run_ai_digest_pipeline.py force`
2. Check Slack for buttons
3. Click "Add to Pipeline"
4. Check Airtable for new record

---

**Done! Ready to deploy.** 🚀
