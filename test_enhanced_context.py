#!/usr/bin/env python3
"""
Test enhanced context generation and Slack posting
"""
import asyncio
import logging
from datetime import date
from config.settings import Settings
from processors.multi_stage_digest import MultiStageDigestProcessor
from services.slack_notifier import SlackNotifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_enhanced_context():
    """Test the enhanced context generation with a sample article"""
    
    print("\n" + "="*70)
    print("🧪 Testing Enhanced Context Generation")
    print("="*70 + "\n")
    
    settings = Settings()
    processor = MultiStageDigestProcessor(settings)
    slack = SlackNotifier(
        webhook_url=settings.SLACK_WEBHOOK_URL,
        error_webhook_url=settings.SLACK_ERROR_WEBHOOK_URL,
        enabled=settings.SLACK_ENABLED
    )
    
    # Sample article for testing
    sample_articles = [
        {
            'title': 'Enterprise AI Governance: New Framework Released by Major Consulting Firms',
            'source_name': 'Harvard Business Review',
            'source_type': 'rss',
            'url': 'https://hbr.org/2025/10/enterprise-ai-governance',
            'content_excerpt': '''Major consulting firms have released a comprehensive governance framework 
            addressing compliance, ethics, and operational risks in AI deployment. The framework includes 
            risk assessment tools, implementation guidelines, and vendor evaluation criteria. Early adopters 
            report 40% reduction in compliance overhead. Research shows 73% of enterprises lack formal AI 
            governance, with average cost of governance failure at $2.3M. "Without proper governance, AI 
            becomes a liability rather than an asset," says Chief Risk Officer at Fortune 500 Financial Services.''',
            'relevance_score': 85.0
        }
    ]
    
    print("📝 Sample Article:")
    print(f"   Title: {sample_articles[0]['title']}")
    print(f"   Source: {sample_articles[0]['source_name']}")
    print(f"   Excerpt length: {len(sample_articles[0]['content_excerpt'])} chars")
    print()
    
    # Test Stage 2.5: Context Enrichment
    print("🔄 Running Stage 2.5: Context Enrichment...")
    print()
    
    try:
        enriched_articles = await processor.stage_2_5_context_enrichment(sample_articles)
        
        if not enriched_articles:
            print("❌ No enriched articles returned")
            return False
        
        article = enriched_articles[0]
        
        print("✅ Context Enrichment Complete!")
        print()
        print("-" * 70)
        print("📊 Enriched Context:")
        print("-" * 70)
        
        # Display enriched fields
        print(f"\n🎯 Primary Theme: {article.get('primary_theme', 'N/A')}")
        print(f"📑 Content Type: {article.get('content_type', 'N/A')}")
        
        print(f"\n📝 AI Summary (Short - 500 chars):")
        print(f"   {article.get('ai_summary_short', 'N/A')[:500]}")
        
        print(f"\n📝 AI Summary (Full):")
        summary = article.get('ai_summary', 'N/A')
        print(f"   {summary[:300]}..." if len(summary) > 300 else f"   {summary}")
        
        metrics = article.get('key_metrics', [])
        if metrics:
            print(f"\n📊 Key Metrics ({len(metrics)}):")
            for i, metric in enumerate(metrics, 1):
                print(f"   {i}. {metric.get('metric', 'N/A')}: {metric.get('value', 'N/A')}")
                print(f"      Context: {metric.get('context', 'N/A')}")
        else:
            print("\n📊 Key Metrics: None extracted")
        
        quotes = article.get('key_quotes', [])
        if quotes:
            print(f"\n💬 Key Quotes ({len(quotes)}):")
            for i, quote in enumerate(quotes, 1):
                print(f"   {i}. \"{quote.get('quote', 'N/A')}\"")
                print(f"      - {quote.get('speaker', 'N/A')}")
        else:
            print("\n💬 Key Quotes: None extracted")
        
        why_matters = article.get('why_it_matters', 'N/A')
        print(f"\n🎯 Why This Matters:")
        print(f"   {why_matters}")
        
        print("\n" + "=" * 70)
        print("📱 Testing Slack Message Formatting")
        print("=" * 70 + "\n")
        
        # Test Slack formatting
        success = slack.post_digest(
            digest_date=date.today(),
            summary_text="Test digest with enhanced context to verify formatting and display.",
            key_insights=[
                "Enhanced context includes comprehensive summaries",
                "Key metrics and quotes are extracted automatically",
                "Strategic implications provided for each article"
            ],
            selected_articles=enriched_articles,
            total_processed=1,
            rss_count=1,
            twitter_count=0
        )
        
        if success:
            print("✅ Slack message posted successfully!")
            print("   Check #ai-daily-digest channel in Slack")
            print()
            print("🎉 Test Complete - Enhanced Context Working!")
        else:
            print("❌ Failed to post to Slack")
            print("   Check webhook URL and network connection")
        
        return success
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_context())
    exit(0 if success else 1)
