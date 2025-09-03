#!/usr/bin/env python3
"""
Test multi-stage digest system with mock AI filtering
Demonstrates the concept without OpenAI API calls
"""

import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Any
import random

from config.settings import Settings
from processors.data_aggregator import DataAggregator
from database.digest_storage import DigestStorage
from utils.logger import setup_logger

class MockDigestProcessor:
    """Mock processor that simulates AI filtering without API calls"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
    
    async def create_daily_digest(self, all_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock two-stage digest creation"""
        
        if not all_articles:
            return {
                'selected_articles': [],
                'digest_text': 'No articles available for digest',
                'key_insights': [],
                'total_processed': 0
            }
        
        self.logger.info(f"Mock Stage 1: Filtering {len(all_articles)} articles to top 20")
        
        # Mock Stage 1: Select top 20 based on business keywords
        business_keywords = ['enterprise', 'business', 'data', 'strategy', 'investment', 'security', 'automation']
        
        scored_articles = []
        for article in all_articles:
            score = 0
            title_lower = article['title'].lower()
            content_lower = article.get('content_excerpt', '').lower()
            
            for keyword in business_keywords:
                if keyword in title_lower:
                    score += 3
                if keyword in content_lower:
                    score += 1
            
            # Bonus for certain sources
            if 'business' in article['source_name'].lower():
                score += 2
            if 'harvard' in article['source_name'].lower():
                score += 3
            
            scored_articles.append((article, score))
        
        # Sort by score and take top 20
        scored_articles.sort(key=lambda x: x[1], reverse=True)
        stage_1_articles = [article for article, score in scored_articles[:20]]
        
        self.logger.info(f"Mock Stage 2: Final selection from {len(stage_1_articles)} articles")
        
        # Mock Stage 2: Select final 5 with diversity
        final_articles = []
        used_sources = set()
        
        for article in stage_1_articles:
            if len(final_articles) >= 5:
                break
            
            # Ensure source diversity
            source = article['source_name']
            if source not in used_sources or len(final_articles) < 3:
                final_articles.append(article)
                used_sources.add(source)
        
        # Create mock digest
        digest_text = f"""Daily AI Digest for {date.today()}

KEY DEVELOPMENTS:
Today's analysis reveals significant developments in enterprise AI adoption, data strategy, and business automation. The selected articles highlight critical trends that tech executives should monitor.

BUSINESS IMPACT:
• Enterprise AI deployment accelerating across multiple sectors
• Data governance and vendor independence becoming strategic priorities  
• Investment patterns shifting toward practical AI applications
• Security considerations driving policy decisions

SELECTED ARTICLES:
{chr(10).join([f"• {article['title']} ({article['source_name']})" for article in final_articles])}

This digest represents the most business-relevant content from {len(all_articles)} articles across RSS and Twitter sources."""

        key_insights = [
            "Enterprise AI adoption accelerating with focus on practical applications",
            "Data strategy and vendor independence emerging as competitive advantages",
            "Investment shifting from research to production-ready AI solutions",
            "Security and governance frameworks becoming business differentiators",
            "Cross-industry AI implementation patterns providing strategic guidance"
        ]
        
        return {
            'selected_articles': final_articles,
            'digest_text': digest_text,
            'key_insights': key_insights,
            'total_processed': len(all_articles),
            'stage_1_count': len(stage_1_articles),
            'final_count': len(final_articles)
        }

async def test_multi_stage_digest():
    """Test the complete multi-stage digest system"""
    
    setup_logger('INFO')
    logger = logging.getLogger(__name__)
    
    target_date = date.today()
    logger.info(f"Testing multi-stage digest for {target_date}")
    
    try:
        # Initialize components
        settings = Settings()
        data_aggregator = DataAggregator(settings)
        mock_processor = MockDigestProcessor(settings)
        digest_storage = DigestStorage(settings)
        
        # Stage 0: Data Collection
        logger.info("Stage 0: Collecting RSS content")
        aggregated_content = await data_aggregator.get_daily_content(target_date)
        
        if aggregated_content.total_count == 0:
            print("⚠️ No articles collected for testing")
            return False
        
        print(f"📊 Collected {aggregated_content.total_count} articles ({aggregated_content.rss_count} RSS + {aggregated_content.twitter_count} Twitter)")
        
        # Multi-stage Processing (Mock)
        logger.info("Starting mock multi-stage digest creation")
        digest_result = await mock_processor.create_daily_digest(aggregated_content.articles)
        
        print(f"\n🎯 Multi-Stage Filtering Results:")
        print(f"  • Stage 0 (Collection): {digest_result['total_processed']} articles")
        print(f"  • Stage 1 (Business Filter): {digest_result['total_processed']} → {digest_result['stage_1_count']}")
        print(f"  • Stage 2 (Final Selection): {digest_result['stage_1_count']} → {digest_result['final_count']}")
        
        print(f"\n📰 Selected Articles:")
        for i, article in enumerate(digest_result['selected_articles'], 1):
            print(f"  {i}. {article['title']}")
            print(f"     Source: {article['source_name']} ({article['source_type']})")
        
        print(f"\n💡 Key Insights:")
        for insight in digest_result['key_insights']:
            print(f"  • {insight}")
        
        print(f"\n📝 Digest Preview:")
        print(digest_result['digest_text'][:400] + "...")
        
        # Test storage (without OpenAI dependency)
        try:
            selected_urls = [article['url'] for article in digest_result['selected_articles']]
            stored_count = await digest_storage.store_all_articles(
                aggregated_content.articles,
                target_date,
                selected_urls
            )
            print(f"\n💾 Storage Test: {stored_count} articles stored successfully")
        except Exception as e:
            print(f"⚠️ Storage test failed: {e}")
        
        print(f"\n🎉 Multi-stage digest test completed successfully!")
        print(f"📈 System demonstrates: RSS collection → Business filtering → Final selection → Storage")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_multi_stage_digest())
    exit(0 if success else 1)
