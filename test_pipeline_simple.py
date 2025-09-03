#!/usr/bin/env python3
"""
Simple pipeline test focusing on RSS scraping and data processing
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_rss_pipeline():
    """Test RSS scraping with better error handling"""
    print("=== Simple RSS Pipeline Test ===\n")
    
    try:
        from config.settings import Settings
        from scrapers.rss_scraper import RSScraper
        from processors.content_processor import ContentProcessor
        from processors.deduplicator import Deduplicator
        
        settings = Settings()
        print("✓ Settings loaded")
        
        # Get RSS feeds from settings
        rss_feeds = settings.rss_feeds
        
        print(f"Testing with {len(rss_feeds)} RSS feeds...")
        
        # Initialize components
        content_processor = ContentProcessor()
        deduplicator = Deduplicator()
        
        print("✓ Processors initialized")
        
        # Test RSS scraping
        async with RSScraper(settings) as rss_scraper:
            print("Starting RSS scraping...")
            
            all_articles = []
            
            # Scrape each feed individually with error handling
            for feed in rss_feeds:
                try:
                    print(f"  Scraping: {feed['name']}")
                    articles = await rss_scraper.scrape_single_feed(feed)
                    all_articles.extend(articles)
                    print(f"    → {len(articles)} articles collected")
                    
                    # Add delay between feeds to avoid rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"    → Failed: {e}")
                    continue
            
            print(f"\nTotal articles collected: {len(all_articles)}")
            
            if all_articles:
                # Test content processing
                print("\nProcessing articles...")
                processed_articles = []
                
                for article in all_articles[:5]:  # Process first 5 articles
                    try:
                        processed = content_processor.process_article(article)
                        processed_articles.append(processed)
                    except Exception as e:
                        print(f"  Processing failed for article: {e}")
                
                print(f"✓ Processed {len(processed_articles)} articles")
                
                # Test deduplication
                print("Testing deduplication...")
                unique_articles = await deduplicator.remove_duplicates(processed_articles)
                print(f"✓ {len(unique_articles)} unique articles after deduplication")
                
                # Show sample results
                print("\n=== Sample Articles ===")
                for i, article in enumerate(unique_articles[:3]):
                    print(f"\n{i+1}. {article['title']}")
                    print(f"   Source: {article['source_name']}")
                    print(f"   URL: {article['url']}")
                    print(f"   Content: {article['content_excerpt'][:100]}...")
                    if 'tags' in article:
                        print(f"   Tags: {article['tags'][:5]}")
                
                return True
            else:
                print("⚠️  No articles collected - all feeds may be rate limited")
                return False
                
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the simple pipeline test"""
    success = await test_rss_pipeline()
    
    if success:
        print("\n🎉 Simple pipeline test completed successfully!")
        print("The core components are working. RSS scraping may be limited by rate limiting.")
    else:
        print("\n⚠️  Pipeline test had issues. Check the output above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
