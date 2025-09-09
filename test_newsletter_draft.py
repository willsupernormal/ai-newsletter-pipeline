#!/usr/bin/env python3
"""
Test script for newsletter draft generation
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from processors.newsletter_draft_processor import NewsletterDraftProcessor
from config.settings import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_newsletter_draft():
    """Test newsletter draft generation with current week data"""
    
    logger.info("=== Testing Newsletter Draft Generation ===")
    
    try:
        settings = Settings()
        processor = NewsletterDraftProcessor(settings)
        
        # Test getting current week
        current_week = processor.get_week_start()
        logger.info(f"Current week start: {current_week}")
        
        # Test getting weekly articles
        articles = await processor.get_weekly_articles(current_week)
        logger.info(f"Found {len(articles)} articles for current week")
        
        if not articles:
            logger.warning("No articles found - testing with mock data")
            # Could add mock data here if needed
            return
        
        # Show sample articles
        logger.info("Sample articles:")
        for i, article in enumerate(articles[:3]):
            logger.info(f"  {i+1}. {article['title']} ({article['source_name']})")
        
        # Test article scoring (just first 5 to avoid API costs)
        test_articles = articles[:5]
        logger.info(f"Testing scoring with {len(test_articles)} articles...")
        
        scored_articles = await processor.score_articles_for_newsletter(test_articles)
        logger.info(f"Scored {len(scored_articles)} articles")
        
        # Show scoring results
        for article in scored_articles:
            logger.info(f"Article: {article['title'][:50]}...")
            logger.info(f"  Relevance: {article.get('relevance_score', 0)}")
            logger.info(f"  Headline Potential: {article.get('headline_potential_score', 0)}")
            logger.info(f"  Deep Dive Potential: {article.get('deep_dive_potential_score', 0)}")
        
        # Test content selection
        logger.info("Testing newsletter content selection...")
        newsletter_content = await processor.select_newsletter_content(scored_articles)
        
        logger.info(f"Selected content:")
        logger.info(f"  Headlines: {len(newsletter_content.get('top_headlines', []))}")
        logger.info(f"  Deep Dive: {'Yes' if newsletter_content.get('deep_dive') else 'No'}")
        logger.info(f"  Operator Takeaways: {len(newsletter_content.get('operators_lens', []))}")
        logger.info(f"  Quick Hits: {len(newsletter_content.get('quick_hits', []))}")
        
        # Show selected headlines
        for i, headline in enumerate(newsletter_content.get('top_headlines', [])):
            logger.info(f"  Headline {i+1}: {headline.get('title', 'No title')}")
            logger.info(f"    Summary: {headline.get('summary', 'No summary')}")
        
        # Show deep dive
        deep_dive = newsletter_content.get('deep_dive')
        if deep_dive:
            logger.info(f"  Deep Dive: {deep_dive.get('title', 'No title')}")
            logger.info(f"    Content: {deep_dive.get('expanded_content', '')[:100]}...")
        
        logger.info("✅ Newsletter draft test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Newsletter draft test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run newsletter draft tests"""
    
    logger.info("Starting newsletter draft tests...")
    await test_newsletter_draft()
    logger.info("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
