# 📱 Slack Integration Plan - Daily AI Digest Delivery

**Created**: October 23, 2025  
**Status**: Planning Phase  
**Goal**: Replace Sunday newsletter with daily Slack digest delivery

---

## 🎯 Overview

Transform the AI newsletter pipeline from weekly newsletter generation to **daily Slack digest delivery**:

- **Pause**: Sunday newsletter draft generation (`run_newsletter_draft.py`)
- **Add**: Daily Slack message posting after digest creation
- **Format**: Single formatted message with 5 articles + AI summary
- **Automation**: Integrated into existing GitHub Actions workflow

---

## 🔧 Slack Integration Options

### **Option 1: Incoming Webhooks (RECOMMENDED)**

**Pros:**
- ✅ Simplest setup (1 webhook URL)
- ✅ No OAuth flow required
- ✅ Perfect for one-way posting
- ✅ Works seamlessly with GitHub Actions
- ✅ No token management needed

**Cons:**
- ⚠️ Can only post to one channel
- ⚠️ No interactive features (buttons, reactions)
- ⚠️ Can't read messages or respond

**Best For:** Phase 1 - Simple daily digest posting

### **Option 2: Slack Bot with API Token**

**Pros:**
- ✅ Can post to multiple channels
- ✅ Can add interactive buttons (for Phase 2)
- ✅ Can read reactions and respond
- ✅ More flexible for future features

**Cons:**
- ⚠️ Requires OAuth setup
- ⚠️ Need to manage bot token securely
- ⚠️ More complex initial setup

**Best For:** Phase 2 - Interactive features (buttons, reactions)

### **Recommendation: Start with Webhooks, Migrate to Bot Later**

**Phase 1**: Use Incoming Webhooks for simple posting  
**Phase 2**: Upgrade to Bot API when adding interactive features

---

## 📋 Implementation Plan

### **Phase 1: Basic Slack Posting (Week 1)**

#### **What We'll Build:**
1. Slack webhook integration in daily pipeline
2. Formatted message with digest summary
3. 5 articles with titles, summaries, and links
4. GitHub Actions secret management
5. Error handling and logging

#### **Changes Required:**

**1. New Module: `services/slack_notifier.py`**
```python
# Handles Slack webhook posting
- Format digest as Slack Block Kit message
- Post to webhook URL
- Handle errors gracefully
```

**2. Update: `run_ai_digest_pipeline.py`**
```python
# Add Slack posting after digest creation
- Import SlackNotifier
- Post digest to Slack
- Log success/failure
```

**3. Update: `.github/workflows/daily-scrape.yml`**
```python
# Add Slack webhook URL to secrets
- SLACK_WEBHOOK_URL environment variable
```

**4. Update: `config/settings.py`**
```python
# Add Slack configuration
- SLACK_WEBHOOK_URL setting
- SLACK_ENABLED flag (for testing)
```

---

## 🎨 Slack Message Format Design

### **Message Structure (Slack Block Kit)**

```
┌─────────────────────────────────────────────────────────┐
│  🤖 AI Daily Digest - October 23, 2025                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Summary                                              │
│  Today's AI landscape focuses on enterprise adoption    │
│  challenges, with major developments in model           │
│  governance and data infrastructure strategies.         │
│                                                          │
│  💡 Key Insights                                         │
│  • Enterprise AI governance frameworks gaining traction │
│  • Data preparation remains critical bottleneck         │
│  • Vendor-agnostic approaches showing ROI benefits      │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  📰 Top 5 Articles                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1️⃣ Enterprise AI Governance: New Framework Released    │
│     Harvard Business Review                             │
│                                                          │
│     Major consulting firms release comprehensive        │
│     governance framework addressing compliance,         │
│     ethics, and operational risks in AI deployment.     │
│                                                          │
│     🔗 Read Article                                      │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  2️⃣ Data Infrastructure Strategies for AI Scale         │
│     MIT Technology Review                               │
│                                                          │
│     Analysis of successful enterprise data strategies   │
│     that enable vendor-agnostic AI implementations.     │
│                                                          │
│     🔗 Read Article                                      │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  [Articles 3-5 follow same format]                      │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  📈 Today's Stats                                        │
│  • Articles Processed: 87                               │
│  • Sources Checked: 14                                  │
│  • Average Relevance: 73/100                            │
└─────────────────────────────────────────────────────────┘
```

### **Technical Implementation (Slack Block Kit JSON)**

```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🤖 AI Daily Digest - October 23, 2025"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*📊 Summary*\nToday's AI landscape focuses on..."
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*💡 Key Insights*\n• Enterprise AI governance...\n• Data preparation...\n• Vendor-agnostic..."
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*📰 Top 5 Articles*"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*1️⃣ Enterprise AI Governance: New Framework Released*\n_Harvard Business Review_\n\nMajor consulting firms release comprehensive governance framework...\n\n<https://example.com/article|🔗 Read Article>"
      }
    },
    {
      "type": "divider"
    },
    // Repeat for articles 2-5
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "📈 *Today's Stats* • Articles Processed: 87 • Sources: 14 • Avg Relevance: 73/100"
        }
      ]
    }
  ]
}
```

---

## 🔐 GitHub Actions + Slack Authentication

### **How It Works**

```
GitHub Actions Workflow
    ↓
Environment Variables (Secrets)
    ↓
Python Script Reads SLACK_WEBHOOK_URL
    ↓
HTTP POST to Slack Webhook
    ↓
Message Appears in Slack Channel
```

### **Setup Steps**

#### **1. Create Slack Incoming Webhook**

1. Go to your Slack workspace
2. Navigate to: **Settings & Administration** → **Manage Apps**
3. Search for "Incoming Webhooks" and install
4. Click **Add to Slack**
5. Select the channel (e.g., `#ai-daily-digest`)
6. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)

#### **2. Add Webhook to GitHub Secrets**

```bash
# In your GitHub repository
gh secret set SLACK_WEBHOOK_URL

# Or via GitHub UI:
# Settings → Secrets and variables → Actions → New repository secret
# Name: SLACK_WEBHOOK_URL
# Value: https://hooks.slack.com/services/...
```

#### **3. Update GitHub Actions Workflow**

```yaml
# .github/workflows/daily-scrape.yml
env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  SLACK_ENABLED: "true"
```

### **Security Considerations**

✅ **Webhook URL is secret** - Never commit to code  
✅ **GitHub encrypts secrets** - Secure storage  
✅ **Webhook only posts** - Can't read channel history  
✅ **Can revoke webhook** - Regenerate if compromised  
⚠️ **Anyone with URL can post** - Keep it secret  

---

## 📝 Code Implementation Details

### **New File: `services/slack_notifier.py`**

```python
"""
Slack notification service for daily digest delivery
"""
import requests
import logging
from typing import Dict, List, Optional
from datetime import date

logger = logging.getLogger(__name__)

class SlackNotifier:
    """Handles posting daily digests to Slack via webhook"""
    
    def __init__(self, webhook_url: str, enabled: bool = True):
        self.webhook_url = webhook_url
        self.enabled = enabled
    
    def format_digest_message(self, digest: Dict) -> Dict:
        """
        Format daily digest as Slack Block Kit message
        
        Args:
            digest: Daily digest data from database
            
        Returns:
            Slack Block Kit JSON structure
        """
        blocks = []
        
        # Header
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🤖 AI Daily Digest - {digest['digest_date']}"
            }
        })
        
        # Summary section
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 Summary*\n{digest['summary_text']}"
            }
        })
        
        # Key insights
        if digest.get('key_insights'):
            insights_text = "*💡 Key Insights*\n" + "\n".join(
                f"• {insight}" for insight in digest['key_insights']
            )
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": insights_text
                }
            })
        
        # Divider
        blocks.append({"type": "divider"})
        
        # Articles header
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📰 Top 5 Articles*"
            }
        })
        
        # Individual articles
        for idx, article in enumerate(digest['selected_articles'], 1):
            article_text = (
                f"*{idx}️⃣ {article['title']}*\n"
                f"_{article['source_name']}_\n\n"
                f"{article['summary']}\n\n"
                f"<{article['url']}|🔗 Read Article>"
            )
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article_text
                }
            })
            
            # Add divider between articles (except after last one)
            if idx < len(digest['selected_articles']):
                blocks.append({"type": "divider"})
        
        # Stats footer
        stats_text = (
            f"📈 *Today's Stats* • "
            f"Articles Processed: {digest.get('total_articles_processed', 0)} • "
            f"Sources: {digest.get('sources_checked', 0)} • "
            f"Avg Relevance: {digest.get('avg_relevance_score', 0):.0f}/100"
        )
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": stats_text
            }]
        })
        
        return {"blocks": blocks}
    
    def post_digest(self, digest: Dict) -> bool:
        """
        Post digest to Slack channel
        
        Args:
            digest: Daily digest data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("Slack notifications disabled, skipping post")
            return True
        
        if not self.webhook_url:
            logger.error("Slack webhook URL not configured")
            return False
        
        try:
            # Format message
            message = self.format_digest_message(digest)
            
            # Post to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Posted digest to Slack: {digest['digest_date']}")
                return True
            else:
                logger.error(
                    f"❌ Slack post failed: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting to Slack: {e}")
            return False
    
    def post_error_notification(self, error_message: str) -> bool:
        """Post error notification to Slack"""
        if not self.enabled or not self.webhook_url:
            return False
        
        try:
            message = {
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ *AI Pipeline Error*\n{error_message}"
                    }
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Failed to post error to Slack: {e}")
            return False
```

### **Update: `config/settings.py`**

```python
# Add to Settings class

# Slack Configuration
SLACK_WEBHOOK_URL: Optional[str] = Field(
    default=None, 
    description="Slack webhook URL for daily digest posting"
)
SLACK_ENABLED: bool = Field(
    default=True, 
    description="Enable/disable Slack notifications"
)
SLACK_CHANNEL_NAME: str = Field(
    default="ai-daily-digest",
    description="Slack channel name (for documentation)"
)
```

### **Update: `run_ai_digest_pipeline.py`**

```python
# Add after digest creation

from services.slack_notifier import SlackNotifier

async def run_ai_digest_pipeline(target_date: date = None):
    # ... existing code ...
    
    # After digest is created and stored
    if digest_id:
        logger.info("✅ Daily digest created successfully")
        
        # Post to Slack
        if settings.SLACK_WEBHOOK_URL:
            slack = SlackNotifier(
                webhook_url=settings.SLACK_WEBHOOK_URL,
                enabled=settings.SLACK_ENABLED
            )
            
            # Fetch full digest with articles for Slack formatting
            full_digest = await digest_storage.get_digest_with_articles(digest_id)
            
            slack_success = slack.post_digest(full_digest)
            if slack_success:
                logger.info("📱 Posted digest to Slack")
            else:
                logger.warning("⚠️ Failed to post to Slack")
        
        return True
```

### **Update: `.github/workflows/daily-scrape.yml`**

```yaml
- name: Run content scraping pipeline
  env:
    # ... existing env vars ...
    
    # Slack Configuration
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    SLACK_ENABLED: "true"
```

---

## 🧪 Testing Plan

### **Local Testing**

```bash
# 1. Set webhook URL in .env
echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/..." >> .env
echo "SLACK_ENABLED=true" >> .env

# 2. Test Slack notifier directly
python3 -c "
from services.slack_notifier import SlackNotifier
from config.settings import Settings

settings = Settings()
slack = SlackNotifier(settings.SLACK_WEBHOOK_URL)

# Test message
test_digest = {
    'digest_date': '2025-10-23',
    'summary_text': 'Test summary',
    'key_insights': ['Insight 1', 'Insight 2'],
    'selected_articles': [
        {
            'title': 'Test Article',
            'source_name': 'Test Source',
            'summary': 'Test summary',
            'url': 'https://example.com'
        }
    ],
    'total_articles_processed': 50
}

slack.post_digest(test_digest)
"

# 3. Run full pipeline with Slack posting
python3 run_ai_digest_pipeline.py
```

### **GitHub Actions Testing**

```bash
# 1. Add secret to GitHub
gh secret set SLACK_WEBHOOK_URL

# 2. Trigger manual workflow run
gh workflow run daily-scrape.yml

# 3. Check logs
gh run list
gh run view <run-id> --log
```

---

## 📅 Implementation Timeline

### **Week 1: Phase 1 - Basic Slack Integration**

**Day 1-2: Setup & Development**
- [ ] Create Slack webhook in workspace
- [ ] Add webhook to GitHub secrets
- [ ] Create `services/slack_notifier.py`
- [ ] Update `config/settings.py`
- [ ] Update `run_ai_digest_pipeline.py`

**Day 3: Testing**
- [ ] Test locally with test digest
- [ ] Test message formatting
- [ ] Verify links work correctly
- [ ] Test error handling

**Day 4: Integration**
- [ ] Update GitHub Actions workflow
- [ ] Test via manual workflow trigger
- [ ] Verify Slack message appears correctly
- [ ] Check logs for errors

**Day 5: Documentation & Cleanup**
- [ ] Update README.md
- [ ] Document Slack setup process
- [ ] Add troubleshooting guide
- [ ] Pause newsletter draft generation

### **Future: Phase 2 - Interactive Features**

**When Ready:**
- [ ] Migrate to Slack Bot API
- [ ] Add interactive buttons per article
- [ ] Implement "Deep Dive" button → triggers AI analysis
- [ ] Add reaction-based feedback
- [ ] Track which articles get most engagement
- [ ] Use engagement data to tune AI selection

---

## 🚀 Phase 2: Future Enhancements (Optional)

### **Interactive Buttons**

```
┌─────────────────────────────────────────────┐
│  1️⃣ Enterprise AI Governance Framework      │
│     Harvard Business Review                 │
│                                             │
│     Major consulting firms release...       │
│                                             │
│  [🔗 Read] [🔍 Deep Dive] [💾 Save]        │
└─────────────────────────────────────────────┘
```

**Button Actions:**
- **Read**: Opens article in browser
- **Deep Dive**: Triggers AI to generate 500-word analysis
- **Save**: Marks article for newsletter consideration

### **Reaction-Based Feedback**

```
User adds 👍 → Increases article relevance score
User adds 🔥 → Marks as high priority
User adds 📌 → Saves for newsletter
```

### **Slash Commands**

```
/ai-digest today          → Show today's digest
/ai-digest search [topic] → Find articles on topic
/ai-digest stats          → Show weekly stats
```

### **Technical Requirements for Phase 2**

1. **Slack App Creation**
   - Create Slack app in workspace
   - Enable Bot Token Scopes
   - Install app to workspace

2. **OAuth & Permissions**
   - `chat:write` - Post messages
   - `reactions:read` - Read reactions
   - `commands` - Slash commands
   - `interactive-messages` - Button clicks

3. **Webhook Endpoint**
   - Need server to receive button clicks
   - Options: AWS Lambda, Vercel, Railway
   - Handle Slack event verification

4. **Database Updates**
   - Track user interactions
   - Store engagement metrics
   - Use for AI tuning

---

## 📊 Success Metrics

### **Phase 1 Metrics**

- ✅ Daily digest posted successfully to Slack
- ✅ Message formatting is clean and readable
- ✅ All article links work correctly
- ✅ No GitHub Actions failures
- ✅ Team finds digest useful

### **Phase 2 Metrics (Future)**

- Button click-through rate
- Most engaged article types
- Time saved vs manual curation
- User satisfaction scores

---

## ⚠️ Potential Issues & Solutions

### **Issue 1: Webhook URL Exposed**

**Problem**: Webhook URL in logs or code  
**Solution**: 
- Never log webhook URL
- Use GitHub secrets only
- Regenerate if compromised

### **Issue 2: Message Too Long**

**Problem**: Slack has 3000 char limit per block  
**Solution**:
- Truncate summaries if needed
- Split into multiple messages if necessary
- Keep summaries concise (150-200 chars)

### **Issue 3: Rate Limiting**

**Problem**: Slack rate limits webhook posts  
**Solution**:
- Only post once per day
- Add retry logic with backoff
- Monitor for 429 errors

### **Issue 4: GitHub Actions Timeout**

**Problem**: Slack post delays pipeline  
**Solution**:
- Set 10-second timeout on requests
- Make Slack posting non-blocking
- Continue even if Slack fails

---

## 📚 Resources

### **Slack Documentation**
- [Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [Block Kit Builder](https://app.slack.com/block-kit-builder)
- [Message Formatting](https://api.slack.com/reference/surfaces/formatting)
- [Slack API](https://api.slack.com/)

### **Testing Tools**
- [Block Kit Builder](https://app.slack.com/block-kit-builder) - Visual message designer
- [Webhook Tester](https://webhook.site/) - Test webhook posts
- [Slack API Tester](https://api.slack.com/methods) - Test API calls

---

## ✅ Pre-Implementation Checklist

Before starting implementation:

- [ ] Slack workspace access confirmed
- [ ] Channel created (`#ai-daily-digest` or similar)
- [ ] Webhook URL generated
- [ ] GitHub secrets access confirmed
- [ ] Team agrees on message format
- [ ] Backup plan if Slack fails (email? log only?)
- [ ] Newsletter draft generation paused
- [ ] Documentation updated

---

## 🎯 Next Steps

1. **Review this plan** - Confirm approach and format
2. **Create Slack webhook** - Get webhook URL
3. **Add to GitHub secrets** - Secure storage
4. **Implement Phase 1** - Basic posting
5. **Test thoroughly** - Local and GitHub Actions
6. **Monitor for 1 week** - Ensure stability
7. **Plan Phase 2** - If interactive features desired

---

**Questions to Answer Before Implementation:**

1. ✅ Which Slack channel should receive the digest?
2. ✅ What time should it post? (Currently 7 AM AEST)
3. ✅ Should we keep newsletter draft generation code for future?
4. ✅ Do you want error notifications in Slack too?
5. ✅ Any specific formatting preferences for the message?

---

**Status**: ⏸️ Awaiting approval to proceed with implementation
