#!/usr/bin/env python3
"""
RSS-only pipeline for testing real data collection to Supabase
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from config.settings import Settings
from database.weekly_manager import WeeklyManager
from scrapers.rss_scraper import RSScraper
from processors.content_processor import ContentProcessor
from processors.deduplicator import Deduplicator
from utils.logger import setup_logger

async def run_rss_pipeline():
    """Run RSS-only pipeline with database storage"""
    
    # Setup logging
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    logger.info("Starting RSS-only AI newsletter pipeline")
    
    try:
        # Initialize components
        settings = Settings()
        weekly_manager = WeeklyManager(settings)
        content_processor = ContentProcessor()
        deduplicator = Deduplicator()
        
        # Initialize current week
        current_week = await weekly_manager.initialize_current_week()
        logger.info(f"Processing content for week starting {current_week}")
        
        # Initialize RSS scraper only
        rss_scraper = RSScraper(settings)
        
        # Run RSS scraping
        logger.info("Starting RSS content scraping")
        
        async with rss_scraper:
            all_articles = await rss_scraper.scrape_all_feeds()
        
        if not all_articles:
            logger.warning("No articles collected from RSS feeds")
            return
        
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
        
        # Add week start date to all articles
        for article in unique_articles:
            article['week_start_date'] = current_week
            # Add basic scoring since we're not using AI evaluation
            article['relevance_score'] = 60.0  # Default score
            article['business_impact_score'] = 55.0
            article['key_themes'] = article.get('tags', [])[:5]
            article['reasoning'] = "RSS content without AI evaluation"
        
        # Store in database
        logger.info("Storing articles in database")
        stored_count = await weekly_manager.store_weekly_articles(unique_articles)
        logger.info(f"Successfully stored {stored_count} articles")
        
        # Update weekly cycle stats
        await weekly_manager.update_weekly_stats()
        
        logger.info("RSS pipeline execution completed successfully")
        
        # Print summary
        print(f"\n🎉 RSS Pipeline Results:")
        print(f"  Articles collected: {len(all_articles)}")
        print(f"  After processing: {len(processed_articles)}")
        print(f"  After deduplication: {len(unique_articles)}")
        print(f"  Stored in database: {stored_count}")
        print(f"  Week starting: {current_week}")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(run_rss_pipeline())
    exit(0 if success else 1)
