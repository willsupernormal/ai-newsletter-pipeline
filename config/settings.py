"""
Configuration management using pydantic-settings
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Database Configuration
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase anon key")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service role key")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")
    
    # Twitter Configuration
    TWITTER_SERVICE: str = Field(default="apify", description="Twitter service: apify or rapidapi")
    APIFY_API_TOKEN: Optional[str] = Field(default=None, description="Apify API token")
    APIFY_ACTOR_ID: str = Field(default="apify/twitter-scraper", description="Apify actor ID")
    RAPIDAPI_KEY: Optional[str] = Field(default=None, description="RapidAPI key")
    RAPIDAPI_TWITTER_HOST: str = Field(default="twitter-api-service.rapidapi.com", description="RapidAPI Twitter host")
    
    # Gmail Configuration
    GMAIL_EMAIL: str = Field(..., description="Gmail address for newsletter scraping")
    GMAIL_APP_PASSWORD: str = Field(..., description="Gmail app password")
    GMAIL_IMAP_SERVER: str = Field(default="imap.gmail.com", description="Gmail IMAP server")
    GMAIL_IMAP_PORT: int = Field(default=993, description="Gmail IMAP port")
    
    # Pipeline Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    CONTENT_RETENTION_WEEKS: int = Field(default=4, description="How many weeks to retain content")
    MIN_RELEVANCE_SCORE: float = Field(default=50.0, description="Minimum relevance score to store")
    MAX_ARTICLES_PER_SOURCE: int = Field(default=50, description="Maximum articles per source per run")
    REQUEST_DELAY_SECONDS: float = Field(default=1.0, description="Delay between requests")
    
    # RSS Configuration
    RSS_REQUEST_TIMEOUT: int = Field(default=30, description="RSS request timeout in seconds")
    RSS_MAX_RETRIES: int = Field(default=3, description="Maximum RSS request retries")
    
    # Content Processing
    CONTENT_EXCERPT_LENGTH: int = Field(default=500, description="Maximum excerpt length")
    DUPLICATE_SIMILARITY_THRESHOLD: float = Field(default=0.85, description="Similarity threshold for duplicates")
    
    # Twitter Monitoring
    TWITTER_ACCOUNTS: str = Field(
        default="AndrewYNg,karpathy,ylecun,sama,OpenAI,GoogleAI",
        description="Comma-separated Twitter accounts to monitor"
    )
    
    # Newsletter Processing
    NEWSLETTER_LABEL: str = Field(default="newsletter", description="Gmail label for newsletters")
    PROCESS_HOURS_BACK: int = Field(default=24, description="Hours back to process emails")
    
    # Performance Settings
    MAX_CONCURRENT_REQUESTS: int = Field(default=10, description="Maximum concurrent requests")
    BATCH_SIZE: int = Field(default=100, description="Batch size for processing")
    
    @field_validator('TWITTER_SERVICE')
    @classmethod
    def validate_twitter_service(cls, v):
        if v not in ['apify', 'rapidapi']:
            raise ValueError('TWITTER_SERVICE must be "apify" or "rapidapi"')
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError('LOG_LEVEL must be a valid logging level')
        return v
    
    @property
    def twitter_accounts_list(self) -> List[str]:
        """Get Twitter accounts as a list"""
        return [account.strip() for account in self.TWITTER_ACCOUNTS.split(',') if account.strip()]
    
    @property
    def rss_feeds(self) -> List[dict]:
        """Get RSS feeds configuration"""
        return [
            {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/"},
            {"name": "AI Business", "url": "https://aibusiness.com/rss.xml"},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
            {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
            {"name": "The Register AI/ML", "url": "https://www.theregister.com/software/ai_ml/headlines.atom"},
            {"name": "Analytics India Magazine", "url": "https://analyticsindiamag.com/feed/"},
            {"name": "Harvard Business Review", "url": "https://feeds.hbr.org/harvardbusiness"},
            # Newsletter-style RSS feeds
            {"name": "The Batch (Andrew Ng)", "url": "https://www.deeplearning.ai/the-batch/feed/"},
            {"name": "Import AI", "url": "https://jack-clark.net/feed/"},
            {"name": "The Gradient", "url": "https://thegradient.pub/rss/"}
        ]
    
    @property
    def ai_scoring_prompt(self) -> str:
        """Get the AI scoring prompt template"""
        return """
You are evaluating AI news for business leaders with the philosophy: "Don't panic. Prepare your data. Stay agnostic."

ARTICLE: {title} - {content_excerpt}
SOURCE: {source_name}

Rate this article 0-100 based on:
1. Business relevance for tech executives (30 pts)
2. Data strategy/vendor independence themes (25 pts) 
3. Actionable insights vs pure research (20 pts)
4. Enterprise decision-making impact (15 pts)
5. Recency and relevance (10 pts)

PRIORITIZE:
- Vendor lock-in problems and solutions
- Data infrastructure strategies  
- Enterprise AI implementation realities
- Platform-agnostic approaches
- Business model disruptions

AVOID:
- Pure academic research
- Consumer AI products
- Vendor marketing disguised as news
- Technical papers without business implications

RESPOND WITH JSON:
{
  "relevance_score": 0-100,
  "business_impact_score": 0-100, 
  "key_themes": ["theme1", "theme2"],
  "reasoning": "Brief explanation of score"
}
"""
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": True
    }