#!/usr/bin/env python3
"""
AI-powered daily digest pipeline
Multi-stage LLM filtering: RSS + Twitter → 100+ articles → 20 → 5 final selections
"""

import asyncio
import logging
from datetime import datetime, date
from typing import Dict, Any

from config.settings import Settings
from processors.data_aggregator import DataAggregator
from processors.multi_stage_digest import MultiStageDigestProcessor
from database.digest_storage import DigestStorage
from services.slack_notifier import SlackNotifier
from utils.logger import setup_logger

async def run_ai_digest_pipeline(target_date: date = None):
    """Run complete AI digest pipeline with multi-stage filtering"""
    
    # Setup logging
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    
    if target_date is None:
        target_date = date.today()
    
    logger.info(f"Starting AI digest pipeline for {target_date}")
    
    try:
        # Initialize components
        settings = Settings()
        data_aggregator = DataAggregator(settings)
        digest_processor = MultiStageDigestProcessor(settings)
        digest_storage = DigestStorage(settings)
        slack_notifier = SlackNotifier(
            webhook_url=settings.SLACK_WEBHOOK_URL,
            error_webhook_url=settings.SLACK_ERROR_WEBHOOK_URL,
            enabled=settings.SLACK_ENABLED
        )
        
        # Check if digest already exists for this date
        existing_digest = await digest_storage.get_daily_digest(target_date)
        if existing_digest:
            logger.info(f"Digest already exists for {target_date}")
            print(f"📰 Daily digest already exists for {target_date}")
            print(f"Summary: {existing_digest['summary_text'][:200]}...")
            return True
        
        # Stage 0: Data Collection & Aggregation
        logger.info("Stage 0: Collecting content from RSS + Twitter")
        aggregated_content = await data_aggregator.get_daily_content(target_date)
        
        if aggregated_content.total_count == 0:
            logger.warning("No articles collected - skipping digest creation")
            print("⚠️ No articles collected for digest")
            return False
        
        logger.info(f"Collected {aggregated_content.total_count} articles ({aggregated_content.rss_count} RSS + {aggregated_content.twitter_count} Twitter)")
        
        # Multi-stage AI Processing
        logger.info("Starting multi-stage AI digest creation")
        digest_result = await digest_processor.create_daily_digest(aggregated_content.articles)
        
        if not digest_result['selected_articles']:
            logger.warning("No articles selected by AI - skipping digest creation")
            print("⚠️ AI selected no articles for digest")
            return False
        
        # Store all articles (selected and non-selected)
        selected_urls = [article['url'] for article in digest_result['selected_articles']]
        await digest_storage.store_all_articles(
            aggregated_content.articles,
            target_date,
            selected_urls
        )
        
        # Store daily digest
        digest_id = await digest_storage.store_daily_digest(
            digest_date=datetime.strptime(target_date, '%Y-%m-%d').date(),
            summary_text=digest_result['digest_text'],
            key_insights=digest_result['key_insights'],
            selected_articles=digest_result['selected_articles'],
            total_processed=digest_result['total_processed'],
            ai_reasoning=f"Multi-stage filtering: {digest_result['total_processed']} → {digest_result['stage_1_count']} → {digest_result['final_count']}",
            article_summaries=digest_result.get('article_summaries', [])
        )
        
        # Success summary
        logger.info(f"Daily digest created successfully: {digest_id}")
        
        print(f"\n🎉 AI Daily Digest Created for {target_date}")
        print(f"📊 Processing Summary:")
        print(f"  • Total articles collected: {digest_result['total_processed']}")
        print(f"    - RSS articles: {aggregated_content.rss_count}")
        print(f"    - Twitter articles: {aggregated_content.twitter_count}")
        print(f"  • Stage 1 filtering: {digest_result['total_processed']} → {digest_result['stage_1_count']}")
        print(f"  • Stage 2 final selection: {digest_result['stage_1_count']} → {digest_result['final_count']}")
        print(f"  • Digest ID: {digest_id}")
        
        print(f"\n📰 Selected Articles:")
        for i, article in enumerate(digest_result['selected_articles'], 1):
            print(f"  {i}. {article['title']}")
            print(f"     Source: {article['source_name']} ({article['source_type']})")
        
        print(f"\n💡 Key Insights:")
        for insight in digest_result['key_insights']:
            print(f"  • {insight}")
        
        # Post to Slack
        if settings.SLACK_WEBHOOK_URL and settings.SLACK_ENABLED:
            logger.info("Posting digest to Slack...")
            slack_success = slack_notifier.post_digest(
                digest_date=target_date if isinstance(target_date, date) else datetime.strptime(target_date, '%Y-%m-%d').date(),
                summary_text=digest_result['digest_text'],
                key_insights=digest_result['key_insights'],
                selected_articles=digest_result['selected_articles'],
                total_processed=digest_result['total_processed'],
                rss_count=aggregated_content.rss_count,
                twitter_count=aggregated_content.twitter_count
            )
            
            if slack_success:
                logger.info("✅ Successfully posted digest to Slack")
                print("\n📱 Posted to Slack: #ai-daily-digest")
            else:
                logger.warning("⚠️ Failed to post digest to Slack (check logs)")
                print("\n⚠️ Slack posting failed (digest still saved to database)")
        else:
            logger.info("Slack posting disabled or not configured")
            print("\n📱 Slack posting: Disabled")
        
        return True
        
    except Exception as e:
        logger.error(f"AI digest pipeline failed: {e}", exc_info=True)
        print(f"❌ Pipeline failed: {e}")
        
        # Send error notification to Slack
        try:
            settings = Settings()
            slack_notifier = SlackNotifier(
                webhook_url=settings.SLACK_WEBHOOK_URL,
                error_webhook_url=settings.SLACK_ERROR_WEBHOOK_URL,
                enabled=settings.SLACK_ENABLED
            )
            
            slack_notifier.post_error_notification(
                error_message=f"Daily digest pipeline failed for {target_date}",
                error_details=str(e),
                pipeline_stage="AI Digest Pipeline"
            )
        except Exception as slack_error:
            logger.error(f"Failed to send error notification to Slack: {slack_error}")
        
        return False

async def show_recent_digests(days: int = 3):
    """Display recent daily digests"""
    settings = Settings()
    digest_storage = DigestStorage(settings)
    
    digests = await digest_storage.get_recent_digests(days)
    
    if not digests:
        print(f"No digests found in the last {days} days")
        return
    
    print(f"\n📚 Recent Daily Digests (last {days} days):")
    for digest in digests:
        print(f"\n📅 {digest['digest_date']}")
        print(f"📊 {len(digest['selected_article_ids'])} articles selected from {digest['total_articles_processed']} total")
        print(f"📝 {digest['summary_text'][:150]}...")
        
        # Show key insights
        if digest.get('key_insights'):
            print("💡 Key insights:")
            for insight in digest['key_insights'][:2]:  # Show first 2
                print(f"  • {insight}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        # Show recent digests
        asyncio.run(show_recent_digests())
    else:
        # Run digest pipeline
        success = asyncio.run(run_ai_digest_pipeline())
        exit(0 if success else 1)
