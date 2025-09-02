# AI Newsletter Pipeline - Setup Guide

Complete step-by-step setup instructions for the AI newsletter pipeline.

## Prerequisites

- Python 3.11+
- Git
- GitHub account
- Supabase account
- OpenAI API access
- Apify account
- Gmail account with app password

## 1. Environment Setup

### Clone and Setup Project

```bash
cd ~/Documents/Projects
git clone <your-repo-url> ai-newsletter-pipeline
cd ai-newsletter-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

## 2. Service Account Setup

### Supabase Setup

1. **Create Project:**
   - Go to https://supabase.com
   - Create new project
   - Note your project URL and keys

2. **Setup Database:**
   - Go to SQL Editor in Supabase dashboard
   - Copy and paste contents of `database/schema.sql`
   - Execute the SQL to create tables and views

3. **Get API Keys:**
   - Go to Settings > API
   - Copy `anon public` key and `service_role secret` key
   - Add to `.env` file

### OpenAI Setup

1. **Get API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create new API key
   - Add to `.env` as `OPENAI_API_KEY`

2. **Set Usage Limits:**
   - Go to Settings > Billing
   - Set usage limits to control costs
   - Recommended: $20-50/month for moderate usage

### Apify Setup

1. **Create Account:**
   - Go to https://apify.com
   - Create free account (1000 free actors runs/month)

2. **Get API Token:**
   - Go to Settings > Integrations
   - Create new API token
   - Add to `.env` as `APIFY_API_TOKEN`

3. **Test Twitter Actor:**
   - Go to Apify Store
   - Find "Twitter Scraper" actor
   - Test with a few accounts to ensure it works

### Gmail Setup

1. **Enable 2FA:**
   - Go to your Google Account settings
   - Enable 2-factor authentication

2. **Create App Password:**
   - Go to Security > 2-Step Verification > App passwords
   - Create password for "Mail"
   - Add to `.env` as `GMAIL_APP_PASSWORD`

3. **Create Newsletter Label:**
   - In Gmail, create label called "newsletter"
   - Apply to existing newsletter emails
   - Set up filters to auto-label future newsletters

## 3. Local Testing

### Test Individual Components

```bash
# Test RSS scraping
python -m scrapers.rss_scraper

# Test Twitter scraping (requires Apify token)
python -m scrapers.twitter_scraper

# Test Gmail scraping (requires Gmail credentials)
python -m scrapers.gmail_scraper

# Test full pipeline (dry run)
python main.py --dry-run --log-level DEBUG
```

### Test Database Connection

```bash
# Test database operations
python -c "
from config.settings import Settings
from database.supabase_client import SupabaseClient
import asyncio

async def test_db():
    settings = Settings()
    db = SupabaseClient(settings)
    await db.init_connection_pool()
    result = await db.execute_query('SELECT 1 as test')
    print('Database connection successful:', result)
    await db.close_pool()

asyncio.run(test_db())
"
```

## 4. GitHub Repository Setup

### Initialize Repository

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial AI newsletter pipeline setup"

# Create GitHub repository
gh repo create ai-newsletter-pipeline --public --push
# Or manually create on GitHub and add remote:
# git remote add origin https://github.com/yourusername/ai-newsletter-pipeline.git
# git branch -M main
# git push -u origin main
```

### Setup GitHub Secrets

```bash
# Set required secrets for GitHub Actions
gh secret set SUPABASE_URL --body "https://your-project.supabase.co"
gh secret set SUPABASE_KEY --body "your_supabase_anon_key"
gh secret set SUPABASE_SERVICE_KEY --body "your_supabase_service_key"
gh secret set OPENAI_API_KEY --body "sk-your_openai_key"
gh secret set APIFY_API_TOKEN --body "your_apify_token"
gh secret set GMAIL_EMAIL --body "your_gmail_address"
gh secret set GMAIL_APP_PASSWORD --body "your_gmail_app_password"

# Verify secrets are set
gh secret list
```

## 5. Production Deployment

### Test GitHub Actions

1. **Manual Trigger:**
   - Go to GitHub > Actions
   - Run "Daily AI Newsletter Scraping" manually
   - Check logs for any issues

2. **Dry Run Test:**
   - Trigger workflow with dry_run = true
   - Verify no database writes occur
   - Check all components work

### Monitor First Runs

1. **Check Logs:**
   - Monitor GitHub Actions logs
   - Look for rate limiting or API issues
   - Verify content is being collected

2. **Verify Database:**
   - Check Supabase dashboard
   - Verify articles are being stored
   - Check weekly cycles are created

## 6. Boss MCP Integration

### Claude Desktop Configuration

Add to your Claude Desktop MCP settings (`~/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-supabase"],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your_service_role_key"
      }
    }
  }
}
```

### Test MCP Integration

In Claude Desktop, test these queries:

```sql
-- Get this week's articles
SELECT title, source_name, relevance_score, url 
FROM current_week_articles 
LIMIT 10;

-- Get weekly summary
SELECT * FROM weekly_trends LIMIT 4;

-- Select articles for newsletter
UPDATE articles 
SET selected_for_newsletter = TRUE, newsletter_priority = 1 
WHERE id = 'article-uuid-here';
```

## 7. Monitoring and Maintenance

### Performance Monitoring

1. **Daily Checks:**
   - GitHub Actions status
   - Error notifications
   - Article collection counts

2. **Weekly Reviews:**
   - Source performance
   - Content quality
   - Database cleanup

### Cost Monitoring

1. **OpenAI Usage:**
   - Monitor API usage in OpenAI dashboard
   - Set usage alerts
   - Adjust MAX_ARTICLES_PER_SOURCE if needed

2. **Apify Usage:**
   - Monitor actor run usage
   - Free tier: 1000 runs/month
   - Optimize Twitter account list if needed

3. **Supabase Usage:**
   - Monitor database size
   - Free tier: 500MB
   - Set up cleanup if approaching limits

## 8. Troubleshooting

### Common Issues

**Pipeline Fails with Rate Limiting:**
```bash
# Increase delays in .env
REQUEST_DELAY_SECONDS=2.0
MAX_CONCURRENT_REQUESTS=3
```

**Gmail Authentication Fails:**
```bash
# Verify app password is correct
# Check GMAIL_EMAIL format
# Ensure IMAP is enabled in Gmail settings
```

**Supabase Connection Issues:**
```bash
# Check URL format (should include https://)
# Verify service key has correct permissions
# Test connection with psql if needed
```

**OpenAI API Errors:**
```bash
# Check API key validity
# Monitor usage limits
# Reduce batch sizes if rate limited
```

### Debug Commands

```bash
# Debug with verbose logging
python main.py --dry-run --log-level DEBUG

# Test specific components
python -c "
import asyncio
from scrapers.rss_scraper import RSScraper
from config.settings import Settings

async def debug():
    settings = Settings()
    async with RSScraper(settings) as scraper:
        articles = await scraper.scrape_single_feed({
            'name': 'Test',
            'url': 'https://feeds.hbr.org/harvardbusiness'
        })
        print(f'Got {len(articles)} articles')

asyncio.run(debug())
"

# Check database content
python -c "
import asyncio
from database.weekly_manager import WeeklyManager
from config.settings import Settings

async def check_db():
    settings = Settings()
    manager = WeeklyManager(settings)
    summary = await manager.get_current_week_summary()
    print('Week summary:', summary)

asyncio.run(check_db())
"
```

### Getting Help

1. **Check logs:** GitHub Actions > Workflow runs > Logs
2. **Check issues:** Review any created GitHub issues
3. **Test locally:** Run with `--dry-run --log-level DEBUG`
4. **Database queries:** Use Supabase SQL editor for investigation

## 9. Customization

### Adding New RSS Sources

Edit `config/settings.py`:

```python
@property
def rss_feeds(self) -> List[dict]:
    return [
        # ... existing feeds ...
        {"name": "Your New Source", "url": "https://example.com/feed.xml"},
    ]
```

### Adjusting AI Evaluation

Edit the scoring prompt in `config/settings.py`:

```python
@property
def ai_scoring_prompt(self) -> str:
    # Modify the prompt to adjust evaluation criteria
```

### Changing Schedule

Edit `.github/workflows/daily-scrape.yml`:

```yaml
on:
  schedule:
    # Change to desired schedule (cron format)
    - cron: '0 7 * * *'  # 7 AM UTC daily
```

## Success Checklist

- [ ] All services configured with valid credentials
- [ ] Database schema created successfully
- [ ] Local testing passes for all components
- [ ] GitHub Actions runs successfully
- [ ] MCP integration works with Claude
- [ ] Content is being collected and scored
- [ ] Weekly cycles are organizing content properly
- [ ] Boss can query and curate content via Claude

Your AI newsletter pipeline is now ready for automated daily operation! 🎉