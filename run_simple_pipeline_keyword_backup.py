#!/usr/bin/env python3
"""
Simple RSS pipeline using Supabase SDK - works in GitHub Actions
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any

from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient
from scrapers.rss_scraper import RSScraper
from processors.content_processor import ContentProcessor
from processors.deduplicator import Deduplicator
from processors.theme_extractor import ThemeExtractor
from utils.logger import setup_logger

async def get_current_week_start() -> date:
    """Get the start of the current week (Monday)"""
    today = datetime.now().date()
    return today - timedelta(days=today.weekday())

async def run_simple_pipeline():
    """Run RSS pipeline with Supabase SDK"""
    
    # Setup logging
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    logger.info("Starting simple RSS pipeline with Supabase SDK")
    
    try:
        # Initialize components
        settings = Settings()
        db_client = SimpleSupabaseClient(settings)
        content_processor = ContentProcessor()
        deduplicator = Deduplicator()
        theme_extractor = ThemeExtractor()
        
        # Get current week
        current_week = await get_current_week_start()
        logger.info(f"Processing content for week starting {current_week}")
        
        # Run RSS scraping
        logger.info("Starting RSS content scraping")
        
        async with RSScraper(settings) as rss_scraper:
            all_articles = await rss_scraper.scrape_all_feeds()
        
        if not all_articles:
            logger.warning("No articles collected from RSS feeds")
            return False
        
        logger.info(f"Total articles collected: {len(all_articles)}")
        
        # Process and clean content
        logger.info("Processing content")
        processed_articles = []
        for article in all_articles:
            try:
                processed = content_processor.process_article(article)
                processed_articles.append(processed)
            except Exception as e:
                logger.error(f"Failed to process article {article.get('title', 'Unknown')}: {e}")
        
        # Remove duplicates
        logger.info("Removing duplicates")
        unique_articles = await deduplicator.remove_duplicates(processed_articles)
        logger.info(f"Articles after deduplication: {len(unique_articles)}")
        
        # Prepare articles for database with theme extraction
        db_articles = []
        for article in unique_articles:
            # Extract themes using rule-based approach (no API cost)
            key_themes = theme_extractor.extract_themes(
                article['title'],
                article.get('content_excerpt', ''),
                article.get('tags', [])
            )
            
            db_article = {
                'title': article['title'],
                'content_excerpt': article.get('content_excerpt', ''),
                'url': article['url'],
                'source_name': article['source_name'],
                'source_type': 'rss',
                'published_at': article.get('published_date'),
                'week_start_date': current_week.isoformat(),
                'tags': article.get('tags', []),
                'key_themes': key_themes,  # Rule-based themes
                'relevance_score': 60.0,  # Default score
                'business_impact_score': 55.0,
                'selected_for_newsletter': False,
                'scraped_at': datetime.now().isoformat()
            }
            db_articles.append(db_article)
        
        # Store in database
        logger.info("Storing articles in Supabase")
        stored_count = await db_client.bulk_insert_articles(db_articles)
        logger.info(f"Successfully stored {stored_count} articles")
        
        # Get and log weekly stats
        stats = await db_client.get_weekly_stats(current_week)
        logger.info(f"Weekly stats: {stats}")
        
        # Print summary
        print(f"\n🎉 Simple Pipeline Results:")
        print(f"  Articles collected: {len(all_articles)}")
        print(f"  After processing: {len(processed_articles)}")
        print(f"  After deduplication: {len(unique_articles)}")
        print(f"  Stored in database: {stored_count}")
        print(f"  Week starting: {current_week}")
        print(f"  Weekly stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(run_simple_pipeline())
    exit(0 if success else 1)
