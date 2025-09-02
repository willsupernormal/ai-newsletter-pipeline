#!/usr/bin/env python3
"""Test a single RSS feed"""

import asyncio
import logging
from config.settings import Settings
from scrapers.rss_scraper import RSScraper

logging.basicConfig(level=logging.INFO)

async def test_feed():
    """Test MIT Technology Review feed which usually works"""
    settings = Settings()
    
    # Test MIT Technology Review feed (usually more reliable)
    test_feed = {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"}
    
    print(f"Testing feed: {test_feed['name']}")
    print(f"URL: {test_feed['url']}")
    print("\nFetching articles...")
    
    async with RSScraper(settings) as scraper:
        articles = await scraper.scrape_single_feed(test_feed)
        
        print(f"\n✓ Successfully scraped {len(articles)} articles")
        
        if articles:
            print("\nSample articles:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n{i}. {article['title'][:80]}...")
                print(f"   URL: {article['url']}")
                print(f"   Tags: {', '.join(article.get('tags', []))}")
                if article.get('published_at'):
                    print(f"   Published: {article['published_at']}")
        
        return articles

if __name__ == "__main__":
    articles = asyncio.run(test_feed())