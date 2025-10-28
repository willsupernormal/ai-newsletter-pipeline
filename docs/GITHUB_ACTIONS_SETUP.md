# GitHub Actions Setup for Daily Digest

This guide explains how to set up automated daily digest generation using GitHub Actions.

---

## Why GitHub Actions?

**Instead of:**
- ❌ Cron job on local machine (unreliable, must be always on)
- ❌ Railway cron (expensive, overkill for scheduled task)

**Use GitHub Actions:**
- ✅ Free (2,000 minutes/month)
- ✅ Reliable (GitHub's infrastructure)
- ✅ Easy to configure
- ✅ Built-in secrets management
- ✅ Can trigger manually
- ✅ Email notifications on failure

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  GitHub Actions (Scheduled Job)                          │
│  • Runs daily at 8 AM                                    │
│  • Generates digest                                      │
│  • Posts to Slack                                        │
│  • Shuts down after completion                           │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Railway (Always-On Webhook Server)                      │
│  • Listens for button clicks                             │
│  • Handles Slack interactions                            │
│  • Scrapes articles                                      │
│  • Pushes to Airtable                                    │
└──────────────────────────────────────────────────────────┘
```

**Two separate services:**
1. **GitHub Actions** - Digest generation (scheduled)
2. **Railway** - Webhook server (always running)

---

## Setup Instructions

### Step 1: Add Secrets to GitHub

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of these secrets:

| Secret Name | Value | Where to Find |
|-------------|-------|---------------|
| `OPENAI_API_KEY` | `sk-...` | OpenAI dashboard |
| `SUPABASE_URL` | `https://xpxrbgttnjjcfwmnosyc.supabase.co` | Supabase project settings |
| `SUPABASE_KEY` | `eyJhbGc...` | Supabase project settings → API |
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/...` | Slack app → Incoming Webhooks |
| `SLACK_BOT_TOKEN` | `xoxb-...` | Slack app → OAuth & Permissions |

**Important:** Copy these from your `.env` file!

---

### Step 2: Verify Workflow File

The workflow file is already created at:
```
.github/workflows/daily-digest.yml
```

**What it does:**
- Runs daily at 8 AM UTC (9 AM UK time)
- Checks out code
- Installs Python 3.11
- Installs dependencies
- Runs digest generation
- Sends Slack notification if it fails

---

### Step 3: Test Manual Run

Before waiting for the scheduled run, test it manually:

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **Daily AI Digest** workflow
4. Click **Run workflow** button
5. Select `main` branch
6. Click **Run workflow**

**Watch the logs:**
- Should complete in 2-3 minutes
- Check Slack for the digest
- Verify 5 articles with buttons

---

### Step 4: Verify Schedule

After manual test succeeds:

1. The workflow will now run automatically every day at 8 AM UTC
2. You'll receive an email if it fails
3. Check GitHub Actions tab to see run history

---

## Customizing the Schedule

Edit `.github/workflows/daily-digest.yml`:

```yaml
schedule:
  - cron: '0 8 * * *'  # 8 AM UTC
```

**Common schedules:**
- `0 8 * * *` - 8 AM UTC daily
- `0 9 * * *` - 9 AM UTC daily
- `0 8 * * 1-5` - 8 AM UTC weekdays only
- `0 8,14 * * *` - 8 AM and 2 PM UTC daily

**Cron syntax:**
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

---

## Monitoring

### View Run History

1. Go to **Actions** tab in GitHub
2. Click **Daily AI Digest** workflow
3. See all past runs with status

### Check Logs

1. Click on any run
2. Click **generate-digest** job
3. Expand steps to see detailed logs

### Email Notifications

GitHub automatically emails you if:
- Workflow fails
- Workflow succeeds after previous failure

---

## Troubleshooting

### Workflow Doesn't Run

**Check:**
1. Is the workflow file in `.github/workflows/` folder?
2. Is the file named with `.yml` extension?
3. Is the syntax valid? (GitHub will show errors)
4. Are you on the `main` branch?

### Workflow Fails

**Common issues:**

#### 1. Missing Secrets
```
Error: OPENAI_API_KEY not found
```
**Fix:** Add the secret in GitHub Settings → Secrets

#### 2. Dependency Installation Fails
```
Error: Could not find a version that satisfies...
```
**Fix:** Check `requirements.txt` for invalid versions

#### 3. API Rate Limits
```
Error: Rate limit exceeded
```
**Fix:** OpenAI rate limit reached. Wait or upgrade plan.

#### 4. Supabase Connection Fails
```
Error: Could not connect to Supabase
```
**Fix:** Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct

---

## Cost Analysis

### GitHub Actions (Free Tier)

**Limits:**
- 2,000 minutes/month
- 500 MB storage

**Usage per run:**
- ~3 minutes per digest
- ~30 runs/month (daily)
- **Total: 90 minutes/month**

**Conclusion:** Well within free tier! ✅

### Comparison to Alternatives

| Option | Cost | Reliability | Ease of Use |
|--------|------|-------------|-------------|
| **GitHub Actions** | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Railway Cron | $5-10/mo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Local Cron | Free | ⭐⭐ | ⭐⭐⭐ |
| AWS Lambda | ~$1/mo | ⭐⭐⭐⭐ | ⭐⭐ |

---

## Advanced: Multiple Schedules

Want different digests at different times?

**Example: Morning & Afternoon Digests**

```yaml
name: Daily AI Digest

on:
  schedule:
    # Morning digest at 8 AM
    - cron: '0 8 * * *'
    # Afternoon digest at 2 PM
    - cron: '0 14 * * *'
  workflow_dispatch:

jobs:
  generate-digest:
    runs-on: ubuntu-latest
    steps:
      # ... same as before
```

---

## Advanced: Conditional Runs

**Only run on weekdays:**

```yaml
on:
  schedule:
    - cron: '0 8 * * 1-5'  # Monday-Friday only
```

**Skip holidays:**

```yaml
jobs:
  generate-digest:
    runs-on: ubuntu-latest
    steps:
      - name: Check if holiday
        id: check_holiday
        run: |
          # Add logic to check if today is a holiday
          # Set output: is_holiday=true/false
      
      - name: Generate digest
        if: steps.check_holiday.outputs.is_holiday != 'true'
        run: python3 run_ai_digest_pipeline.py force
```

---

## What Stays on Railway?

**Railway continues to run:**
- Webhook server (always listening)
- Handles button clicks
- Scrapes articles on-demand
- Pushes to Airtable

**Railway does NOT:**
- Generate daily digests (GitHub Actions does this)
- Run scheduled tasks
- Call GPT-4 for analysis

**Why this split?**
- GitHub Actions: Free for scheduled tasks
- Railway: Cheap for always-on webhook ($5/mo)
- Best of both worlds!

---

## Summary

✅ **GitHub Actions** generates digest daily (free, reliable)  
✅ **Railway** handles button clicks (always available)  
✅ **No local machine** needed (everything in cloud)  
✅ **Easy to monitor** (GitHub UI + Slack notifications)  
✅ **Cost effective** (free + $5/mo)

---

## Next Steps

1. ✅ Add secrets to GitHub
2. ✅ Test manual workflow run
3. ✅ Verify digest appears in Slack
4. ✅ Wait for first scheduled run tomorrow
5. ✅ Monitor for a week to ensure reliability

---

**Questions?**

Check the logs in GitHub Actions or Railway for detailed error messages.

---

*End of Guide*
