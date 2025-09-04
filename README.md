# AI Newsletter Pipeline

Automated content collection and AI-powered daily digest system for business AI newsletters. Built with async Python, Supabase, and Claude MCP integration.

## Features

- **Daily Automated Scraping**: RSS feeds, Twitter accounts, and Gmail newsletters
- **Multi-Stage AI Processing**: Two-stage OpenAI filtering for optimal content selection
- **Daily Digest Generation**: AI creates comprehensive daily summaries with key insights
- **Weekly Content Organization**: Boss sees current week's content with daily breakdowns
- **Claude MCP Integration**: Natural language database interaction for curation
- **Smart Duplicate Detection**: Advanced deduplication across all sources
- **GitHub Actions Automation**: Runs daily at 7 AM UTC
- **Source Performance Analytics**: Track which sources deliver best content
- **Enhanced Database Schema**: Optimized for MCP queries and boss interaction

## Architecture

```
Daily Pipeline (GitHub Actions 7 AM UTC)
├── Multi-Source Scraping
│   ├── RSS Feeds → Business AI sources
│   ├── Twitter Accounts → Key influencers  
│   └── Gmail Newsletter Tag → Parse "newsletter" tagged emails
├── Content Processing
│   ├── Deduplication → Remove duplicates across sources
│   ├── Content Cleaning → Extract and format text
│   └── Multi-Stage AI Filtering
│       ├── Stage 1: Relevance filtering (top 15 from all articles)
│       └── Stage 2: Final selection (top 5 with summaries)
└── Daily Digest Creation
    ├── AI-Generated Summary → Key themes and insights
    ├── Selected Articles → Top 5 with enhanced descriptions
    └── Database Storage → daily_digests table with article references

Boss Interaction (Anytime via Claude MCP)
├── Daily Digest Review → "Show me today's digest"
├── Weekly Overview → "What are this week's top themes?"
├── Targeted Queries → "Find vendor lock-in articles from this week"
├── Article Selection → "Mark articles 1,3,5 as newsletter-ready"
└── Performance Analysis → "Which sources performed best this week?"
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
# Enhanced AI digest pipeline (recommended)
python run_ai_digest_pipeline.py

# Show recent daily digests
python run_ai_digest_pipeline.py show

# Legacy weekly pipeline
python main.py --dry-run  # Test run without storing
python main.py           # Full pipeline execution
python main.py --cleanup # Clean old content

# RSS-only pipeline for testing
python run_rss_pipeline.py

# Simple pipeline without AI processing
python run_simple_pipeline.py

# Test individual components
python -m scrapers.rss_scraper
python -m scrapers.twitter_scraper
python -m scrapers.gmail_scraper
```

### Boss Interaction Workflow

Once Claude MCP is configured, use natural language queries:

```
Daily Digest Review:
"Show me today's daily digest"
"What were the key insights from yesterday's digest?"
"Show me the last 3 days of digests"

Weekly Overview:
"Show me this week's summary stats and top articles"
"What are the trending themes this week?"
"Which sources performed best this week?"

Theme-Based Searching:
"Find all vendor lock-in articles from this week"
"Show me data strategy articles with high relevance scores"
"What AI governance stories do we have?"

Content Selection:
"Mark articles with IDs abc123, def456 for newsletter"
"Set article abc123 as priority 1 lead story"
"Show me all articles selected for newsletter this week"

Analytics & Performance:
"Which content sources are delivering the best articles?"
"Show me relevance score trends over the past month"
"What topics are we covering most frequently?"
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

## Daily Process

### Automated Pipeline (Daily at 7 AM UTC)
1. **Content Scraping**: Collect from RSS feeds, Twitter, Gmail newsletters
2. **Multi-Stage AI Processing**:
   - Stage 1: Filter to top 15 most relevant articles
   - Stage 2: Select final 5 articles with enhanced summaries
3. **Daily Digest Creation**: AI generates comprehensive summary with key insights
4. **Database Storage**: Store in `daily_digests` table with article references
5. **Weekly Organization**: Articles organized by week for easy boss access

### Boss Interaction (Anytime via MCP)
1. **Daily Review**: Check morning digest for key developments
2. **Weekly Planning**: Review week's themes and top articles
3. **Newsletter Curation**: Select and prioritize articles for publication
4. **Performance Monitoring**: Track source quality and content trends
5. **Ad-hoc Queries**: Search for specific topics or themes as needed

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
│   ├── supabase_client.py    # Database operations
│   ├── supabase_simple.py    # Simplified client for basic ops
│   ├── digest_storage.py     # Daily digest storage and retrieval
│   ├── weekly_manager.py     # Week cycling logic
│   └── schema.sql           # Complete database schema with views
├── processors/
│   ├── content_processor.py  # Cleaning and formatting
│   ├── deduplicator.py      # Duplicate detection
│   ├── ai_evaluator.py      # OpenAI scoring (legacy)
│   ├── multi_stage_digest.py # Two-stage AI filtering system
│   ├── data_aggregator.py   # Multi-source content aggregation
│   └── theme_extractor.py   # Topic and theme analysis
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