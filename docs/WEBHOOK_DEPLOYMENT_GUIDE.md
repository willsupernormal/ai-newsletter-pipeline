# 🚀 Webhook Server Deployment Guide

**Goal**: Deploy the webhook server so Slack can send button clicks to it  
**Time**: 30-45 minutes  
**Platform**: Railway (recommended) or Render

---

## 📋 **Prerequisites**

Before deploying, ensure you have:
- ✅ Airtable set up and credentials in `.env`
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ Webhook server tested locally (optional but recommended)
- ✅ GitHub repository with latest code pushed

---

## 🎯 **Option 1: Deploy to Railway (Recommended)**

Railway is the easiest option with a generous free tier.

### **Step 1: Create Railway Account**

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended for easy deployment)
4. Verify your email

### **Step 2: Create New Project**

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub
4. Select your repository: `ai-newsletter-pipeline`
5. Click **"Deploy Now"**

### **Step 3: Configure Build Settings**

1. Railway will auto-detect Python
2. Click on your deployment
3. Go to **"Settings"** tab
4. Set **Start Command**:
   ```
   python -m uvicorn api.webhook_server:app --host 0.0.0.0 --port $PORT
   ```
5. Set **Root Directory**: `/` (leave as default)

### **Step 4: Add Environment Variables**

1. Go to **"Variables"** tab
2. Click **"Add Variable"** for each:

```bash
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# OpenAI
OPENAI_API_KEY=your-openai-key

# Slack
SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_SIGNING_SECRET=your-slack-signing-secret
SLACK_WEBHOOK_URL=your-slack-webhook-url

# Airtable
AIRTABLE_API_KEY=your-airtable-api-key
AIRTABLE_BASE_ID=your-airtable-base-id
AIRTABLE_TABLE_NAME=Content Pipeline

# Webhook
WEBHOOK_PORT=8000
```

3. Click **"Add"** for each variable

### **Step 5: Get Public URL**

1. Go to **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. Copy the generated URL (e.g., `https://your-app.up.railway.app`)
5. Save this URL - you'll need it for Slack configuration

### **Step 6: Verify Deployment**

1. Go to **"Deployments"** tab
2. Wait for deployment to complete (green checkmark)
3. Click on the deployment
4. Check logs for: `Starting webhook server on port 8000`
5. Visit your URL: `https://your-app.up.railway.app/health`
6. You should see: `{"status": "healthy"}`

---

## 🎯 **Option 2: Deploy to Render**

Render is another good option with a free tier.

### **Step 1: Create Render Account**

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub
4. Verify your email

### **Step 2: Create New Web Service**

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select `ai-newsletter-pipeline`
4. Click **"Connect"**

### **Step 3: Configure Service**

1. **Name**: `ai-digest-webhook`
2. **Region**: Choose closest to you
3. **Branch**: `main`
4. **Root Directory**: Leave empty
5. **Runtime**: Python 3
6. **Build Command**:
   ```
   pip install -r requirements.txt
   ```
7. **Start Command**:
   ```
   python -m uvicorn api.webhook_server:app --host 0.0.0.0 --port $PORT
   ```
8. **Instance Type**: Free

### **Step 4: Add Environment Variables**

1. Scroll to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add all variables from Railway Step 4 above

### **Step 5: Deploy**

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Once deployed, copy the URL (e.g., `https://ai-digest-webhook.onrender.com`)

### **Step 6: Verify Deployment**

1. Visit: `https://your-app.onrender.com/health`
2. Should see: `{"status": "healthy"}`

---

## 🔧 **Configure Slack App**

Now that your webhook is deployed, configure Slack to send button clicks to it.

### **Step 1: Go to Slack App Settings**

1. Go to https://api.slack.com/apps
2. Click on your app (AI Digest Manager)

### **Step 2: Enable Interactivity**

1. Click **"Interactivity & Shortcuts"** in the left sidebar
2. Toggle **"Interactivity"** to **ON**

### **Step 3: Set Request URL**

1. **Request URL**: Enter your webhook URL + `/slack/interactions`
   - Railway example: `https://your-app.up.railway.app/slack/interactions`
   - Render example: `https://ai-digest-webhook.onrender.com/slack/interactions`
2. Click **"Save Changes"**
3. Slack will verify the URL (you should see a green checkmark)

### **Step 4: Verify Configuration**

1. If you see ✅ next to the Request URL, you're good!
2. If you see ❌, check:
   - Webhook server is running
   - URL is correct (including `/slack/interactions`)
   - No typos in the URL
   - Server logs for errors

---

## ✅ **Test End-to-End**

Now let's test the complete flow!

### **Step 1: Run the Pipeline**

```bash
python run_ai_digest_pipeline.py force
```

This will:
1. Fetch articles
2. Generate digest
3. Post to Slack with buttons

### **Step 2: Check Slack**

1. Go to `#ai-daily-digest` channel
2. You should see the digest with "🔖 Add to Pipeline" buttons

### **Step 3: Click a Button**

1. Click **"🔖 Add to Pipeline"** on any article
2. Wait 2-5 seconds
3. You should see a response:
   ```
   ✅ Added to Pipeline!
   
   [Article Title]
   
   📊 Scraped: 1,234 words
   🔗 View Original
   📋 Check Airtable: Content Pipeline
   ```

### **Step 4: Verify in Airtable**

1. Go to your Airtable "Content Pipeline" base
2. You should see a new record in the "📥 Saved" column
3. Check that all fields are populated:
   - Title, URL, Source
   - AI Summary, Metrics, Quotes
   - Full Article Text
   - Word Count

### **Step 5: Check Logs**

1. Go to Railway/Render dashboard
2. Check deployment logs
3. You should see:
   ```
   Received action: add_to_pipeline from user: your-username
   Processing 'Add to Pipeline' for article: [article-id]
   Scraping full article: [url]
   ✓ Scraped with newspaper3k: 1234 words
   ✓ Added to Airtable: [record-id] - [title]
   ```

---

## 🐛 **Troubleshooting**

### **Problem: Slack shows "URL verification failed"**

**Solution:**
1. Check webhook server is running
2. Visit `https://your-url/health` - should return `{"status": "healthy"}`
3. Check server logs for errors
4. Verify SLACK_SIGNING_SECRET is correct in environment variables
5. Try redeploying

### **Problem: Button click shows "❌ Error"**

**Solution:**
1. Check webhook server logs
2. Common issues:
   - Airtable credentials incorrect
   - Supabase credentials incorrect
   - Article not found in database
3. Test locally first (see LOCAL_TESTING_GUIDE.md)

### **Problem: Article not appearing in Airtable**

**Solution:**
1. Check Airtable credentials in environment variables
2. Verify table name is exactly "Content Pipeline"
3. Check all required fields exist in Airtable
4. Look at webhook server logs for specific error

### **Problem: "Already in pipeline" message**

**Solution:**
- This is expected if you click the button twice
- The article was already added to Airtable
- Check Airtable to verify it's there

### **Problem: Scraping fails**

**Solution:**
1. Some sites block scrapers
2. Check webhook logs for scraping errors
3. Article will still be added to Airtable, just without full text
4. You can manually add full text later

---

## 📊 **Monitoring**

### **Check Deployment Health**

**Railway:**
1. Go to project dashboard
2. Click on deployment
3. View **"Metrics"** tab for CPU/Memory usage
4. View **"Logs"** tab for real-time logs

**Render:**
1. Go to service dashboard
2. View **"Logs"** tab
3. View **"Metrics"** tab

### **Set Up Alerts (Optional)**

**Railway:**
1. Go to **"Settings"** → **"Notifications"**
2. Add email for deployment failures

**Render:**
1. Go to **"Settings"** → **"Notifications"**
2. Add email for service down alerts

---

## 💰 **Costs**

### **Railway Free Tier:**
- $5 credit per month
- Enough for ~500 button clicks/month
- No credit card required

### **Render Free Tier:**
- 750 hours/month (enough for 24/7)
- Spins down after 15 min inactivity
- Takes 30-60 seconds to wake up

### **Recommendation:**
- Start with Railway (no spin-down delay)
- If you exceed free tier, upgrade or switch to Render

---

## 🎯 **Next Steps**

Once deployed and tested:

1. ✅ Webhook server deployed
2. ✅ Slack app configured
3. ✅ End-to-end test successful
4. ✅ Monitoring set up

**You're done! 🎉**

Now you can:
- Run daily pipeline
- Click buttons to add articles to Airtable
- Manage your content pipeline in Airtable
- Move articles through stages (Saved → Research → Writing → Ready → Published)

---

## 📝 **Maintenance**

### **Updating Code:**

1. Push changes to GitHub
2. Railway/Render will auto-deploy
3. Check logs to verify deployment

### **Checking Logs:**

- Railway: Dashboard → Deployment → Logs
- Render: Dashboard → Logs tab

### **Restarting Server:**

- Railway: Dashboard → Deployment → "Restart"
- Render: Dashboard → "Manual Deploy" → "Deploy latest commit"

---

**Questions? Issues? Check the logs first, then reach out!** 🚀
