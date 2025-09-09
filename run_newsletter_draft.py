#!/usr/bin/env python3
"""
Newsletter Draft Runner - Generate weekly newsletter drafts
Usage: python run_newsletter_draft.py [--week YYYY-MM-DD]
"""

import asyncio
import logging
import sys
from datetime import datetime, date
from processors.newsletter_draft_processor import NewsletterDraftProcessor
from config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_newsletter_draft(target_week: date = None):
    """Generate newsletter draft for specified week"""
    
    logger.info("🗞️  Starting Newsletter Draft Generation")
    
    try:
        settings = Settings()
        processor = NewsletterDraftProcessor(settings)
        
        # Generate draft
        result = await processor.generate_weekly_newsletter_draft(target_week)
        
        if result['success']:
            print(f"\n✅ Newsletter Draft Generated Successfully!")
            print(f"📅 Week: {result['week_start']}")
            print(f"🆔 Draft ID: {result['draft_id']}")
            print(f"📊 Articles Processed: {result['articles_processed']}")
            print(f"📰 Headlines: {result['headlines_count']}")
            print(f"📖 Deep Dive: {'Yes' if result['has_deep_dive'] else 'No'}")
            print(f"💡 Operator Takeaways: {result['takeaways_count']}")
            
            print(f"\n🎯 Next Steps:")
            print(f"1. Review draft in Supabase newsletter_drafts table")
            print(f"2. Boss can edit via Claude MCP interface")
            print(f"3. Update status to 'approved' when ready")
            
        else:
            print(f"\n❌ Newsletter Draft Generation Failed")
            print(f"Error: {result['error']}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Newsletter draft generation failed: {e}")
        print(f"\n❌ Fatal Error: {e}")
        return False

def parse_week_arg(week_str: str) -> date:
    """Parse week argument (YYYY-MM-DD format)"""
    try:
        target_date = datetime.strptime(week_str, '%Y-%m-%d').date()
        # Get Monday of that week
        return target_date - timedelta(days=target_date.weekday())
    except ValueError:
        raise ValueError(f"Invalid date format: {week_str}. Use YYYY-MM-DD")

async def main():
    """Main function"""
    
    target_week = None
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--week' and len(sys.argv) > 2:
            try:
                from datetime import timedelta
                target_week = parse_week_arg(sys.argv[2])
                print(f"📅 Generating newsletter for week starting: {target_week}")
            except ValueError as e:
                print(f"❌ {e}")
                print("Usage: python run_newsletter_draft.py [--week YYYY-MM-DD]")
                return
        else:
            print("Usage: python run_newsletter_draft.py [--week YYYY-MM-DD]")
            return
    
    # Run newsletter draft generation
    success = await run_newsletter_draft(target_week)
    
    if success:
        print(f"\n🎉 Newsletter draft generation completed!")
    else:
        print(f"\n💥 Newsletter draft generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
