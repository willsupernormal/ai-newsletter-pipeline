"""
Async RSS feed scraper with rate limiting and error recovery
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import feedparser
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient


class RSScraper:
    """Async RSS feed scraper with robust error handling"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.db_client = SimpleSupabaseClient(settings)
        
        # Configure feedparser
        feedparser.USER_AGENT = "AI Newsletter Pipeline/1.0"
    
    async def get_rss_sources(self) -> List[Dict[str, Any]]:
        """Load active RSS sources from content_sources table"""
        try:
            response = self.db_client.client.table('content_sources').select('*').eq('type', 'rss').eq('active', True).execute()
            sources = response.data
            self.logger.info(f"Loaded {len(sources)} active RSS sources from database")
            return sources
        except Exception as e:
            self.logger.error(f"Failed to load RSS sources from database: {e}")
            return []
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.settings.RSS_REQUEST_TIMEOUT),
            connector=aiohttp.TCPConnector(limit=self.settings.MAX_CONCURRENT_REQUESTS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract text"""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            
            # Clean up whitespace
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            # Truncate to max length
            if len(text) > self.settings.CONTENT_EXCERPT_LENGTH:
                text = text[:self.settings.CONTENT_EXCERPT_LENGTH] + "..."
            
            return text
            
        except Exception as e:
            self.logger.warning(f"Failed to clean HTML content: {e}")
            return html_content[:self.settings.CONTENT_EXCERPT_LENGTH] + "..." if len(html_content) > self.settings.CONTENT_EXCERPT_LENGTH else html_content
    
    def extract_tags_from_content(self, title: str, content: str) -> List[str]:
        """Extract relevant tags from title and content"""
        tags = set()
        text = (title + " " + content).lower()
        
        # AI/ML related keywords
        ai_keywords = [
            "artificial intelligence", "machine learning", "deep learning", "ai", "ml",
            "neural network", "llm", "gpt", "chatgpt", "openai", "generative ai",
            "computer vision", "nlp", "natural language processing"
        ]
        
        # Business keywords
        business_keywords = [
            "vendor lock-in", "data strategy", "enterprise", "platform", "infrastructure",
            "cloud", "automation", "digital transformation", "roi", "cost", "security",
            "privacy", "compliance", "governance"
        ]
        
        # Technology keywords
        tech_keywords = [
            "api", "saas", "iaas", "paas", "kubernetes", "docker", "microservices",
            "database", "analytics", "big data", "edge computing", "iot"
        ]
        
        all_keywords = ai_keywords + business_keywords + tech_keywords
        
        for keyword in all_keywords:
            if keyword in text:
                tags.add(keyword.replace(" ", "_"))
        
        # Add source-specific tags
        if "venture" in text or "startup" in text or "funding" in text:
            tags.add("startup")
        
        if "research" in text or "study" in text or "paper" in text:
            tags.add("research")
        
        if "regulation" in text or "policy" in text or "government" in text:
            tags.add("regulation")
        
        return list(tags)[:10]  # Limit to 10 tags
    
    async def fetch_feed_content(self, feed_url: str) -> Optional[str]:
        """Fetch RSS feed content with retry logic"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        for attempt in range(self.settings.RSS_MAX_RETRIES):
            try:
                self.logger.debug(f"Fetching {feed_url} (attempt {attempt + 1})")
                
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        self.logger.debug(f"Successfully fetched {len(content)} chars from {feed_url}")
                        return content
                    else:
                        self.logger.warning(f"HTTP {response.status} for {feed_url}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout fetching {feed_url} (attempt {attempt + 1})")
            except aiohttp.ClientError as e:
                self.logger.warning(f"Client error fetching {feed_url}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error fetching {feed_url}: {e}")
            
            if attempt < self.settings.RSS_MAX_RETRIES - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def parse_feed_entries(self, feed_content: str, feed_name: str) -> List[Dict[str, Any]]:
        """Parse RSS feed entries into structured data"""
        try:
            parsed_feed = feedparser.parse(feed_content)
            
            if hasattr(parsed_feed, 'bozo') and parsed_feed.bozo:
                self.logger.warning(f"Feed parsing warning for {feed_name}: {parsed_feed.bozo_exception}")
            
            articles = []
            
            for entry in parsed_feed.entries[:self.settings.MAX_ARTICLES_PER_SOURCE]:
                try:
                    # Extract publication date
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                    
                    # Skip articles older than 7 days
                    if published_at and (datetime.now() - published_at).days > 7:
                        continue
                    
                    # Extract content
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value if isinstance(entry.content, list) else entry.content
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    # Clean content
                    clean_content = self.clean_html_content(content)
                    
                    # Extract title
                    title = getattr(entry, 'title', 'No Title').strip()
                    
                    # Get URL
                    url = getattr(entry, 'link', '').strip()
                    
                    if not title or not url:
                        self.logger.debug(f"Skipping entry with missing title or URL: {title[:50]}...")
                        continue
                    
                    # Extract tags
                    tags = self.extract_tags_from_content(title, clean_content)
                    
                    article = {
                        'title': title,
                        'url': url,
                        'content_excerpt': clean_content,
                        'source_type': 'rss',
                        'source_name': feed_name,
                        'published_at': published_at,
                        'tags': tags
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse entry from {feed_name}: {e}")
                    continue
            
            self.logger.info(f"Parsed {len(articles)} articles from {feed_name}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to parse feed {feed_name}: {e}")
            return []
    
    async def scrape_single_feed(self, feed_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape a single RSS feed"""
        feed_name = feed_config['name']
        feed_url = feed_config['url']
        
        try:
            self.logger.info(f"Scraping RSS feed: {feed_name}")
            
            # Fetch feed content
            feed_content = await self.fetch_feed_content(feed_url)
            
            if feed_content is None:
                self.logger.error(f"Failed to fetch content for {feed_name}")
                return []
            
            # Parse entries
            articles = self.parse_feed_entries(feed_content, feed_name)
            
            # Add rate limiting
            if self.settings.REQUEST_DELAY_SECONDS > 0:
                await asyncio.sleep(self.settings.REQUEST_DELAY_SECONDS)
            
            return articles
            
        except Exception as e:
            self.logger.error(f"Error scraping {feed_name}: {e}")
            return []
    
    async def scrape_all_feeds(self) -> List[Dict[str, Any]]:
        """Scrape all configured RSS feeds concurrently"""
        if not self.session:
            async with self:
                return await self._scrape_all_feeds_impl()
        else:
            return await self._scrape_all_feeds_impl()
    
    async def _scrape_all_feeds_impl(self) -> List[Dict[str, Any]]:
        """Internal implementation of scrape_all_feeds using dynamic sources"""
        # Load RSS sources from database
        sources = await self.get_rss_sources()
        
        if not sources:
            self.logger.warning("No active RSS sources found in database")
            return []
        
        self.logger.info(f"Starting RSS scraping for {len(sources)} feeds from database")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_REQUESTS)
        
        async def scrape_with_semaphore(source):
            async with semaphore:
                # Convert database source to feed config format
                feed_config = {
                    'name': source['name'],
                    'url': source['identifier'],
                    'source_id': source['id']
                }
                return await self.scrape_single_feed(feed_config)
        
        # Run all feeds concurrently
        tasks = [scrape_with_semaphore(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all articles
        all_articles = []
        successful_feeds = 0
        
        for i, result in enumerate(results):
            source = sources[i]
            feed_name = source['name']
            
            if isinstance(result, Exception):
                self.logger.error(f"Feed {feed_name} failed: {result}")
            else:
                articles = result
                all_articles.extend(articles)
                successful_feeds += 1
                self.logger.info(f"Feed {feed_name}: {len(articles)} articles")
        
        self.logger.info(f"RSS scraping completed: {successful_feeds}/{len(sources)} feeds successful, "
                        f"{len(all_articles)} total articles")
        
        # Update last_processed timestamp for successful sources
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                source = sources[i]
                try:
                    self.db_client.client.table('content_sources').update({
                        'last_processed': datetime.now().isoformat()
                    }).eq('id', source['id']).execute()
                except Exception as update_error:
                    self.logger.warning(f"Failed to update last_processed for source {source['name']}: {update_error}")
        
        return all_articles


# CLI testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_rss_scraper():
        settings = Settings()
        
        async with RSScraper(settings) as scraper:
            articles = await scraper.scrape_all_feeds()
            
            print(f"Total articles: {len(articles)}")
            for i, article in enumerate(articles[:3]):  # Show first 3
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article['title']}")
                print(f"Source: {article['source_name']}")
                print(f"URL: {article['url']}")
                print(f"Tags: {article['tags']}")
                print(f"Content: {article['content_excerpt'][:200]}...")
    
    # Run test
    asyncio.run(test_rss_scraper())