#!/usr/bin/env python3
"""Simplified pipeline test using Supabase SDK"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from supabase import create_client

from config.settings import Settings
from scrapers.rss_scraper import RSScraper
from processors.content_processor import ContentProcessor
from processors.ai_evaluator import AIEvaluator
from processors.deduplicator import Deduplicator
from utils.logger import setup_logger

async def test_simplified_pipeline():
    """Run a simplified pipeline test"""
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("SIMPLIFIED PIPELINE TEST")
    print("=" * 60)
    
    try:
        # Initialize components
        settings = Settings()
        
        # Initialize Supabase client
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        
        content_processor = ContentProcessor()
        ai_evaluator = AIEvaluator(settings)
        deduplicator = Deduplicator()
        
        # Get current week
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        print(f"\n✓ Current week: {week_start}")
        
        # Initialize week in database
        try:
            existing = supabase.table('weekly_cycles')\
                .select('*')\
                .eq('week_start_date', week_start.isoformat())\
                .execute()
            
            if not existing.data:
                supabase.table('weekly_cycles').insert({
                    'week_start_date': week_start.isoformat(),
                    'articles_collected': 0,
                    'articles_curated': 0
                }).execute()
                print(f"✓ Initialized new week cycle")
            else:
                print(f"✓ Week cycle already exists")
        except Exception as e:
            logger.warning(f"Could not initialize week cycle: {e}")
        
        # Test with MIT Technology Review feed
        test_feed = {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"}
        
        print(f"\nScraping RSS feed: {test_feed['name']}...")
        async with RSScraper(settings) as scraper:
            articles = await scraper.scrape_single_feed(test_feed)
        
        if not articles:
            print("✗ No articles scraped")
            return False
        
        print(f"✓ Scraped {len(articles)} articles")
        
        # Process only first 2 articles for testing
        test_articles = articles[:2]
        print(f"\nProcessing {len(test_articles)} articles...")
        
        # Process content
        processed_articles = []
        for article in test_articles:
            try:
                processed = content_processor.process_article(article)
                processed['week_start_date'] = week_start.isoformat()
                processed_articles.append(processed)
            except Exception as e:
                logger.error(f"Failed to process: {e}")
        
        print(f"✓ Processed {len(processed_articles)} articles")
        
        # AI evaluation
        print("\nEvaluating articles with AI...")
        evaluated_articles = []
        for i, article in enumerate(processed_articles, 1):
            try:
                print(f"  Evaluating {i}/{len(processed_articles)}: {article['title'][:50]}...")
                evaluated = await ai_evaluator.evaluate_article(article)
                evaluated['week_start_date'] = week_start.isoformat()
                
                if evaluated['relevance_score'] >= settings.MIN_RELEVANCE_SCORE:
                    evaluated_articles.append(evaluated)
                    print(f"    → Score: {evaluated['relevance_score']}/100 ✓")
                else:
                    print(f"    → Score: {evaluated['relevance_score']}/100 (below threshold)")
            except Exception as e:
                logger.error(f"Evaluation failed: {e}")
        
        print(f"\n✓ {len(evaluated_articles)} articles meet threshold")
        
        # Store in database
        if evaluated_articles:
            print(f"\nStoring articles in database...")
            
            for article in evaluated_articles:
                # Ensure all required fields and convert datetime objects
                article['scraped_at'] = datetime.now().isoformat()
                
                # Convert all datetime fields to ISO format strings
                for field in ['published_at', 'evaluated_at', 'processed_at']:
                    if field in article and article[field]:
                        if isinstance(article[field], (datetime, date)):
                            article[field] = article[field].isoformat()
                
                # Ensure week_start_date is a string
                if 'week_start_date' in article:
                    if isinstance(article['week_start_date'], (datetime, date)):
                        article['week_start_date'] = article['week_start_date'].isoformat()
                
                # Remove fields that don't exist in the database schema
                # Keep only the fields that exist in the schema
                allowed_fields = [
                    'title', 'url', 'content_excerpt', 'source_type', 'source_name',
                    'published_at', 'scraped_at', 'week_start_date', 'relevance_score',
                    'business_impact_score', 'tags', 'twitter_metrics',
                    'selected_for_newsletter', 'curator_notes', 'newsletter_priority'
                ]
                
                # Create a new dict with only allowed fields
                cleaned_article = {}
                for field in allowed_fields:
                    if field in article:
                        cleaned_article[field] = article[field]
                
                # Replace the article with the cleaned version
                evaluated_articles[evaluated_articles.index(article)] = cleaned_article
                
                # Ensure tags is a list (sometimes returned as key_themes)
                if 'key_themes' in article:
                    article['tags'] = article.get('key_themes', [])
                    del article['key_themes']
            
            # Debug: print fields being inserted
            print(f"\nFields to insert: {list(evaluated_articles[0].keys())}")
            
            try:
                # Use upsert to handle duplicates
                response = supabase.table('articles').upsert(
                    evaluated_articles,
                    on_conflict='url'
                ).execute()
                
                stored = len(response.data) if response.data else 0
                print(f"✓ Stored {stored} articles")
                
                # Update weekly stats
                if stored > 0:
                    stats = supabase.table('articles')\
                        .select('*')\
                        .eq('week_start_date', week_start.isoformat())\
                        .execute()
                    
                    total = len(stats.data) if stats.data else 0
                    
                    supabase.table('weekly_cycles')\
                        .update({'articles_collected': total})\
                        .eq('week_start_date', week_start.isoformat())\
                        .execute()
                    
                    print(f"✓ Updated weekly stats: {total} total articles")
                
            except Exception as e:
                logger.error(f"Database storage failed: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("✓ Pipeline test completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}", exc_info=True)
        print(f"\n✗ Pipeline test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simplified_pipeline())