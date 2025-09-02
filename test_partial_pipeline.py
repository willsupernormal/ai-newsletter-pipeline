#!/usr/bin/env python3
"""Test partial pipeline - RSS + AI Evaluation + Database"""

import asyncio
import logging
from datetime import datetime
from config.settings import Settings
from database.weekly_manager import WeeklyManager
from scrapers.rss_scraper import RSScraper
from processors.content_processor import ContentProcessor
from processors.ai_evaluator import AIEvaluator
from processors.deduplicator import Deduplicator
from utils.logger import setup_logger

async def test_partial_pipeline():
    """Run a partial pipeline test with RSS feeds only"""
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("PARTIAL PIPELINE TEST - RSS + AI + Database")
    print("=" * 60)
    
    try:
        # Initialize components
        settings = Settings()
        weekly_manager = WeeklyManager(settings)
        content_processor = ContentProcessor()
        ai_evaluator = AIEvaluator(settings)
        deduplicator = Deduplicator()
        
        # Initialize current week
        current_week = await weekly_manager.initialize_current_week()
        print(f"\n✓ Initialized week: {current_week}")
        
        # Test with just MIT Technology Review feed (reliable)
        test_feed = {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"}
        
        print(f"\nScraping RSS feed: {test_feed['name']}...")
        async with RSScraper(settings) as scraper:
            articles = await scraper.scrape_single_feed(test_feed)
        
        if not articles:
            print("✗ No articles scraped")
            return
        
        print(f"✓ Scraped {len(articles)} articles")
        
        # Process only first 3 articles for testing
        test_articles = articles[:3]
        print(f"\nProcessing {len(test_articles)} articles for testing...")
        
        # Process content
        processed_articles = []
        for article in test_articles:
            try:
                processed = content_processor.process_article(article)
                processed_articles.append(processed)
            except Exception as e:
                logger.error(f"Failed to process article: {e}")
        
        print(f"✓ Processed {len(processed_articles)} articles")
        
        # Remove duplicates
        unique_articles = await deduplicator.remove_duplicates(processed_articles)
        print(f"✓ {len(unique_articles)} unique articles after deduplication")
        
        # AI evaluation
        print("\nEvaluating articles with AI...")
        evaluated_articles = []
        for i, article in enumerate(unique_articles, 1):
            try:
                print(f"  Evaluating article {i}/{len(unique_articles)}: {article['title'][:50]}...")
                evaluated = await ai_evaluator.evaluate_article(article)
                if evaluated['relevance_score'] >= settings.MIN_RELEVANCE_SCORE:
                    evaluated_articles.append(evaluated)
                    print(f"    → Score: {evaluated['relevance_score']}/100 ✓")
                else:
                    print(f"    → Score: {evaluated['relevance_score']}/100 (below threshold)")
            except Exception as e:
                logger.error(f"Failed to evaluate article: {e}")
        
        print(f"\n✓ {len(evaluated_articles)} articles meet relevance threshold")
        
        # Store in database
        if evaluated_articles:
            print(f"\nStoring {len(evaluated_articles)} articles in database...")
            stored_count = await weekly_manager.store_weekly_articles(evaluated_articles)
            print(f"✓ Successfully stored {stored_count} articles")
            
            # Update weekly stats
            await weekly_manager.update_weekly_stats()
            
            # Get and display summary
            summary = await weekly_manager.get_current_week_summary()
            print("\n" + "=" * 60)
            print("WEEKLY SUMMARY")
            print("=" * 60)
            print(f"Week Start: {summary['week_start']}")
            if summary['stats']:
                stats = summary['stats']
                print(f"Total Articles: {stats.get('total_articles', 0)}")
                print(f"Average Relevance: {stats.get('avg_relevance', 0):.1f}")
                print(f"RSS Articles: {stats.get('rss_count', 0)}")
        
        print("\n✓ Partial pipeline test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}", exc_info=True)
        print(f"\n✗ Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_partial_pipeline())