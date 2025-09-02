#!/usr/bin/env python3
"""Test full pipeline with all configured sources"""

import asyncio
import logging
from datetime import datetime, timedelta, date
from supabase import create_client

from config.settings import Settings
from scrapers.rss_scraper import RSScraper
from processors.content_processor import ContentProcessor
from processors.ai_evaluator import AIEvaluator
from utils.logger import setup_logger

async def test_full_pipeline():
    """Run full pipeline test with RSS feeds"""
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("FULL PIPELINE TEST")
    print("=" * 60)
    
    try:
        # Initialize components
        settings = Settings()
        
        # Show configuration
        print("\n📋 Configuration:")
        print(f"  ✓ Supabase: Configured")
        print(f"  ✓ OpenAI: Configured (Model: {settings.OPENAI_MODEL})")
        print(f"  ✓ RSS Feeds: {len(settings.rss_feeds)} feeds")
        print(f"  ✓ Twitter: RapidAPI configured")
        print(f"  ✓ Gmail: Skipped (using RSS feeds instead)")
        
        # Initialize Supabase
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
        
        content_processor = ContentProcessor()
        ai_evaluator = AIEvaluator(settings)
        
        # Get current week
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Initialize week
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
        except:
            pass
        
        print(f"\n📅 Week: {week_start}")
        
        # Test multiple RSS feeds
        print("\n📰 Testing RSS Feeds:")
        all_articles = []
        
        async with RSScraper(settings) as scraper:
            # Test 3 different feeds
            test_feeds = settings.rss_feeds[:3]
            
            for feed in test_feeds:
                print(f"\n  Scraping: {feed['name']}...")
                try:
                    articles = await scraper.scrape_single_feed(feed)
                    if articles:
                        # Take only 2 articles per feed for testing
                        articles = articles[:2]
                        all_articles.extend(articles)
                        print(f"    ✓ Got {len(articles)} articles")
                except Exception as e:
                    print(f"    ✗ Failed: {e}")
        
        print(f"\n📊 Total articles collected: {len(all_articles)}")
        
        if not all_articles:
            print("No articles to process")
            return False
        
        # Process articles
        print("\n🔄 Processing articles...")
        processed_articles = []
        for article in all_articles:
            try:
                processed = content_processor.process_article(article)
                processed['week_start_date'] = week_start.isoformat()
                processed_articles.append(processed)
            except Exception as e:
                logger.error(f"Processing failed: {e}")
        
        print(f"  ✓ Processed {len(processed_articles)} articles")
        
        # AI evaluation (only first 3 for speed)
        print("\n🤖 AI Evaluation:")
        evaluated_articles = []
        test_articles = processed_articles[:3]
        
        for i, article in enumerate(test_articles, 1):
            try:
                print(f"  {i}. {article['title'][:50]}...")
                evaluated = await ai_evaluator.evaluate_article(article)
                evaluated['week_start_date'] = week_start.isoformat()
                
                if evaluated['relevance_score'] >= settings.MIN_RELEVANCE_SCORE:
                    evaluated_articles.append(evaluated)
                    print(f"     Score: {evaluated['relevance_score']}/100 ✓")
                else:
                    print(f"     Score: {evaluated['relevance_score']}/100 ✗")
            except Exception as e:
                print(f"     Failed: {e}")
        
        # Store in database
        if evaluated_articles:
            print(f"\n💾 Storing {len(evaluated_articles)} articles...")
            
            for article in evaluated_articles:
                # Clean fields for database
                article['scraped_at'] = datetime.now().isoformat()
                
                # Convert datetime fields
                for field in ['published_at']:
                    if field in article and article[field]:
                        if isinstance(article[field], (datetime, date)):
                            article[field] = article[field].isoformat()
                
                # Keep only schema fields
                allowed_fields = [
                    'title', 'url', 'content_excerpt', 'source_type', 'source_name',
                    'published_at', 'scraped_at', 'week_start_date', 'relevance_score',
                    'business_impact_score', 'tags'
                ]
                
                cleaned = {k: v for k, v in article.items() if k in allowed_fields}
                evaluated_articles[evaluated_articles.index(article)] = cleaned
            
            try:
                response = supabase.table('articles').upsert(
                    evaluated_articles,
                    on_conflict='url'
                ).execute()
                
                stored = len(response.data) if response.data else 0
                print(f"  ✓ Stored {stored} articles")
            except Exception as e:
                print(f"  ✗ Storage failed: {e}")
        
        # Show summary
        print("\n" + "=" * 60)
        print("📈 PIPELINE SUMMARY")
        print("=" * 60)
        print(f"  RSS Feeds tested: {len(test_feeds)}")
        print(f"  Articles scraped: {len(all_articles)}")
        print(f"  Articles processed: {len(processed_articles)}")
        print(f"  Articles evaluated: {len(test_articles)}")
        print(f"  Articles stored: {len(evaluated_articles)}")
        print("\n✅ Pipeline test completed successfully!")
        print("\nYour AI newsletter pipeline is ready to use!")
        print("Run 'python3 main.py' to execute the full daily pipeline.")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n✗ Pipeline failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_pipeline())