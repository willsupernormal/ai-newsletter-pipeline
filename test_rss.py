#!/usr/bin/env python3
"""Test RSS scraping functionality"""

import asyncio
import logging
from config.settings import Settings
from scrapers.rss_scraper import RSScraper

logging.basicConfig(level=logging.INFO)

async def test_rss():
    """Test RSS feed scraping"""
    settings = Settings()
    
    print("Testing RSS Scraper...")
    print(f"Found {len(settings.rss_feeds)} RSS feeds configured:")
    for feed in settings.rss_feeds:
        print(f"  - {feed['name']}: {feed['url']}")
    
    print("\nStarting RSS scraping test (fetching first feed only)...")
    
    # Test with just the first feed
    test_feed = settings.rss_feeds[0]
    
    async with RSScraper(settings) as scraper:
        # Scrape just one feed for testing
        articles = await scraper.scrape_single_feed(test_feed)
        
        print(f"\nResults:")
        print(f"  Articles scraped: {len(articles)}")
        
        if articles:
            print(f"\nFirst article:")
            article = articles[0]
            print(f"  Title: {article['title'][:100]}...")
            print(f"  URL: {article['url']}")
            print(f"  Source: {article['source_name']}")
            print(f"  Tags: {article.get('tags', [])}")
            print(f"  Content excerpt: {article['content_excerpt'][:200]}...")
        
        return articles

if __name__ == "__main__":
    articles = asyncio.run(test_rss())
    print(f"\n✓ RSS scraping test completed successfully with {len(articles)} articles")