# AI Newsletter Pipeline

Automated content collection and weekly curation system for business AI newsletters. Built with async Python, Supabase, and Claude MCP integration.

## Features

- **Daily Automated Scraping**: RSS feeds, Twitter accounts, and Gmail newsletters
- **AI-Powered Content Scoring**: OpenAI-based relevance evaluation
- **Weekly Content Organization**: Boss only sees current week's content
- **Claude MCP Integration**: Natural language curation workflow
- **Duplicate Detection**: Smart deduplication across sources
- **GitHub Actions Automation**: Runs daily at 7 AM UTC
- **Source Performance Analytics**: Track which sources deliver best content

## Architecture

```
Daily Scraping (GitHub Actions 7 AM UTC)
├── RSS Feeds → Business AI sources
├── Twitter Accounts → Key influencers  
├── Gmail Newsletter Tag → Parse "newsletter" tagged emails
└── Weekly Content Organization → Boss sees current week only

Boss Curation (Weekend via Claude MCP)
├── "Show me this week's top vendor lock-in stories"
├── "What are the best data strategy articles from this week?"
└── "Mark articles 1,3,5 as newsletter-ready"
```

## Quick Start

### 1. Environment Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd ai-newsletter-pipeline
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. Database Setup

1. Create a new Supabase project at https://supabase.com
2. Copy your project URL and keys to `.env`
3. Run the SQL schema in Supabase SQL Editor (see `database/schema.sql`)

### 3. Service Account Setup

**OpenAI**: Get API key from https://platform.openai.com/api-keys

**Twitter Scraping** (choose one):
- **Apify**: Sign up at https://apify.com, get API token
- **RapidAPI**: Sign up at https://rapidapi.com, find Twitter API service

**Gmail**: 
- Enable 2-factor authentication
- Generate app password for the pipeline
- Tag newsletters with "newsletter" label

### 4. GitHub Actions Setup

```bash
# Add secrets to your GitHub repository
gh secret set SUPABASE_URL
gh secret set SUPABASE_KEY
gh secret set SUPABASE_SERVICE_KEY
gh secret set OPENAI_API_KEY
gh secret set TWITTER_SERVICE  # "apify" or "rapidapi"
gh secret set APIFY_API_TOKEN   # if using Apify
gh secret set RAPIDAPI_KEY      # if using RapidAPI
gh secret set GMAIL_EMAIL
gh secret set GMAIL_APP_PASSWORD
```

### 5. Boss MCP Configuration

Add to Claude Desktop MCP settings:

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

## Usage

### Local Testing

```bash
# Test run without storing data
python main.py --dry-run

# Full pipeline execution
python main.py

# Clean old content
python main.py --cleanup

# Test individual components
python -m scrapers.rss_scraper
python -m scrapers.twitter_scraper
python -m scrapers.gmail_scraper
```

### Boss Curation Workflow

Once Claude MCP is configured, use natural language queries:

```
Weekly Overview:
"Show me this week's summary stats and top 10 articles"

Theme-Based Searching:
"What are the best vendor lock-in stories from this week?"
"Show me articles about data strategy or infrastructure"

Content Selection:
"Select articles with IDs abc123, def456, ghi789 for newsletter"
"Make article abc123 the lead story with priority 1"

Newsletter Preparation:
"Show me all selected articles for this week's newsletter"
"Preview the newsletter content with selected articles"
```

## Content Sources

### RSS Feeds
- VentureBeat AI
- AI Business
- MIT Technology Review  
- TechCrunch AI
- The Register AI/ML
- Analytics India Magazine
- Harvard Business Review

### Twitter Accounts
- @AndrewYNg
- @karpathy
- @ylecun
- @sama
- @OpenAI
- @GoogleAI

### Gmail Newsletters
- Any email tagged with "newsletter" label
- Processed in last 24 hours
- Supports major newsletter platforms

## Content Evaluation

Articles are scored 0-100 based on alignment with "Don't panic. Prepare your data. Stay agnostic." philosophy:

- Business relevance for tech executives (30 points)
- Data strategy/vendor independence themes (25 points)
- Actionable insights vs pure research (20 points)
- Enterprise decision-making impact (15 points)
- Recency and relevance (10 points)

## Weekly Process

### Automated (Daily at 7 AM UTC)
- Scrape RSS feeds, Twitter, Gmail newsletters
- Score content with AI for relevance
- Organize by current week
- Store in Supabase with weekly cycling

### Boss Curation (Weekend)
1. **Monday Morning**: Check weekly stats and top articles
2. **During Week**: Monitor specific topics as needed
3. **Weekend Curation**: Select 3-5 best articles for newsletter
4. **Monthly Review**: Analyze source performance and trends

## File Structure

```
ai-newsletter-pipeline/
├── main.py                 # Orchestration and CLI
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── config/
│   └── settings.py        # Configuration management
├── scrapers/
│   ├── rss_scraper.py     # RSS feed processing
│   ├── twitter_scraper.py # Twitter API integration
│   └── gmail_scraper.py   # Newsletter email processing
├── database/
│   ├── supabase_client.py # Database operations
│   └── weekly_manager.py  # Week cycling logic
├── processors/
│   ├── content_processor.py # Cleaning and formatting
│   ├── deduplicator.py     # Duplicate detection
│   └── ai_evaluator.py     # OpenAI scoring
├── mcp/
│   ├── mcp_queries.py      # Pre-built queries
│   ├── curation_tools.py   # Article selection
│   └── analytics.py        # Performance tracking
├── utils/
│   ├── logger.py          # Logging setup
│   └── helpers.py         # Utility functions
└── .github/workflows/
    └── daily-scrape.yml   # CI/CD automation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details