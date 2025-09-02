#!/usr/bin/env python3
"""
AI Newsletter Pipeline - Main Orchestration
Automated content collection and weekly curation system
"""

import asyncio
import argparse
import logging
from datetime import datetime
from typing import Optional

from config.settings import Settings
from database.weekly_manager import WeeklyManager
from scrapers.rss_scraper import RSScraper
from scrapers.twitter_scraper import TwitterScraper
from scrapers.gmail_scraper import GmailScraper
from processors.content_processor import ContentProcessor
from processors.ai_evaluator import AIEvaluator
from processors.deduplicator import Deduplicator
from utils.logger import setup_logger


async def run_daily_pipeline(dry_run: bool = False) -> None:
    """Main daily pipeline execution"""
    logger = logging.getLogger(__name__)
    logger.info("Starting AI newsletter pipeline")
    
    try:
        # Initialize components
        settings = Settings()
        weekly_manager = WeeklyManager(settings)
        content_processor = ContentProcessor()
        ai_evaluator = AIEvaluator(settings)
        deduplicator = Deduplicator()
        
        # Initialize current week
        current_week = await weekly_manager.initialize_current_week()
        logger.info(f"Processing content for week starting {current_week}")
        
        # Initialize scrapers
        rss_scraper = RSScraper(settings)
        twitter_scraper = TwitterScraper(settings)
        gmail_scraper = GmailScraper(settings)
        
        all_articles = []
        
        # Run scrapers concurrently
        logger.info("Starting content scraping")
        scraping_tasks = [
            rss_scraper.scrape_all_feeds(),
            twitter_scraper.scrape_accounts(),
            gmail_scraper.scrape_newsletters()
        ]
        
        scraping_results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(scraping_results):
            scraper_name = ['RSS', 'Twitter', 'Gmail'][i]
            if isinstance(result, Exception):
                logger.error(f"{scraper_name} scraping failed: {result}")
            else:
                logger.info(f"{scraper_name} scraping completed: {len(result)} articles")
                all_articles.extend(result)
        
        if not all_articles:
            logger.warning("No articles collected from any source")
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
        
        # AI evaluation and scoring
        logger.info("Evaluating content with AI")
        evaluated_articles = []
        for article in unique_articles:
            try:
                evaluated = await ai_evaluator.evaluate_article(article)
                if evaluated['relevance_score'] >= settings.MIN_RELEVANCE_SCORE:
                    evaluated_articles.append(evaluated)
            except Exception as e:
                logger.error(f"Failed to evaluate article {article.get('title', 'Unknown')}: {e}")
        
        logger.info(f"Articles meeting relevance threshold: {len(evaluated_articles)}")
        
        # Store in database with weekly organization
        if not dry_run and evaluated_articles:
            logger.info("Storing articles in database")
            stored_count = await weekly_manager.store_weekly_articles(evaluated_articles)
            logger.info(f"Successfully stored {stored_count} articles")
            
            # Update weekly cycle stats
            await weekly_manager.update_weekly_stats()
        
        logger.info("Pipeline execution completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        raise


async def cleanup_old_content() -> None:
    """Clean up old content based on retention settings"""
    logger = logging.getLogger(__name__)
    settings = Settings()
    weekly_manager = WeeklyManager(settings)
    
    try:
        cleaned_count = await weekly_manager.cleanup_old_content()
        logger.info(f"Cleaned up {cleaned_count} old articles")
    except Exception as e:
        logger.error(f"Content cleanup failed: {e}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Newsletter Pipeline")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run pipeline without storing results')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old content')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(args.log_level)
    logger = logging.getLogger(__name__)
    
    if args.cleanup:
        logger.info("Starting content cleanup")
        asyncio.run(cleanup_old_content())
    else:
        logger.info(f"Starting pipeline (dry_run={args.dry_run})")
        asyncio.run(run_daily_pipeline(args.dry_run))


if __name__ == "__main__":
    main()