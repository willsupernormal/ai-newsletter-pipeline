#!/usr/bin/env python3
"""
Test Slack integration with formatted messages
"""
import asyncio
from datetime import date
from services.slack_notifier import SlackNotifier
from config.settings import Settings

async def test_slack_integration():
    """Test Slack posting with sample digest"""
    
    print("🧪 Testing Slack Integration\n")
    
    # Initialize
    settings = Settings()
    slack = SlackNotifier(
        webhook_url=settings.SLACK_WEBHOOK_URL,
        error_webhook_url=settings.SLACK_ERROR_WEBHOOK_URL,
        enabled=settings.SLACK_ENABLED
    )
    
    print(f"✓ Slack enabled: {settings.SLACK_ENABLED}")
    print(f"✓ Main webhook configured: {settings.SLACK_WEBHOOK_URL[:50]}...")
    print(f"✓ Error webhook configured: {settings.SLACK_ERROR_WEBHOOK_URL[:50]}...")
    print()
    
    # Test 1: Post sample digest
    print("📱 Test 1: Posting sample daily digest...")
    
    sample_articles = [
        {
            'title': 'Enterprise AI Governance: New Framework Released',
            'source_name': 'Harvard Business Review',
            'summary': 'Major consulting firms release comprehensive governance framework addressing compliance, ethics, and operational risks in AI deployment. Framework includes risk assessment tools and implementation guidelines.',
            'url': 'https://hbr.org/2025/10/enterprise-ai-governance'
        },
        {
            'title': 'Data Infrastructure Strategies for AI at Scale',
            'source_name': 'MIT Technology Review',
            'summary': 'Analysis of successful enterprise data strategies that enable vendor-agnostic AI implementations. Focus on data preparation, quality management, and infrastructure flexibility.',
            'url': 'https://technologyreview.com/2025/10/data-infrastructure-ai'
        },
        {
            'title': 'Vendor Lock-in: The Hidden Cost of AI Platforms',
            'source_name': 'TechCrunch',
            'summary': 'Investigation reveals enterprises spending 40% more due to vendor lock-in. Case studies show benefits of platform-agnostic approaches and open standards.',
            'url': 'https://techcrunch.com/2025/10/vendor-lockin-ai'
        },
        {
            'title': 'AI Model Governance in Financial Services',
            'source_name': 'VentureBeat',
            'summary': 'New regulatory requirements drive adoption of comprehensive AI governance frameworks in banking. Focus on transparency, explainability, and risk management.',
            'url': 'https://venturebeat.com/2025/10/ai-governance-finance'
        },
        {
            'title': 'The ROI of Data Preparation in AI Projects',
            'source_name': 'Analytics India Magazine',
            'summary': 'Research shows 70% of AI project success depends on data quality. Organizations investing in data preparation see 3x higher ROI on AI initiatives.',
            'url': 'https://analyticsindiamag.com/2025/10/data-prep-roi'
        }
    ]
    
    success = slack.post_digest(
        digest_date=date.today(),
        summary_text="Today's AI landscape focuses on enterprise adoption challenges, with major developments in governance frameworks and data infrastructure strategies. Key theme: vendor-agnostic approaches gaining traction as organizations seek to avoid platform lock-in while maintaining flexibility.",
        key_insights=[
            'Enterprise AI governance frameworks gaining regulatory traction',
            'Data preparation remains critical bottleneck for AI success',
            'Vendor-agnostic approaches showing measurable ROI benefits'
        ],
        selected_articles=sample_articles,
        total_processed=87,
        rss_count=50,
        twitter_count=37
    )
    
    if success:
        print("✅ Sample digest posted successfully!")
        print("   Check #ai-daily-digest channel in Slack")
    else:
        print("❌ Failed to post digest")
    
    print()
    
    # Test 2: Post error notification
    print("📱 Test 2: Posting sample error notification...")
    
    error_success = slack.post_error_notification(
        error_message="Test error notification - Pipeline integration test",
        error_details="This is a test error to verify error notifications are working correctly. No actual error occurred.",
        pipeline_stage="Testing Phase"
    )
    
    if error_success:
        print("✅ Error notification posted successfully!")
        print("   Check #automation_errors channel in Slack")
    else:
        print("❌ Failed to post error notification")
    
    print()
    print("🎉 Slack integration test complete!")
    print()
    print("Next steps:")
    print("1. Check both Slack channels for messages")
    print("2. Verify formatting looks good")
    print("3. Run full pipeline: python3 run_ai_digest_pipeline.py")

if __name__ == "__main__":
    asyncio.run(test_slack_integration())
