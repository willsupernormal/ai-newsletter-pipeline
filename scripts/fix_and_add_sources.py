#!/usr/bin/env python3
"""
Fix blocked RSS sources and add new premium sources
This script:
1. Updates blocked sources with alternative URLs
2. Adds Enterprise AI sources
3. Adds Open Source AI sources
"""

import asyncio
from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient


# Alternative URLs for blocked sources
BLOCKED_SOURCE_FIXES = [
    {
        "old_name": "Microsoft AI blog",
        "new_name": "Microsoft AI Blog (DevBlogs)",
        "new_url": "https://devblogs.microsoft.com/ai/feed/",
        "reason": "Original blogs.microsoft.com blocked, using devblogs instead"
    },
    {
        "old_name": "Towards Data Science",
        "new_name": "Towards Data Science (Medium)",
        "new_url": "https://medium.com/feed/towards-data-science",
        "reason": "Using Medium feed endpoint instead of direct TDS"
    },
    # The Information requires paid access, we'll replace with similar source
    {
        "old_name": "The Information",
        "new_name": "Protocol (Tech Policy)",
        "new_url": "https://www.protocol.com/feeds/feed.rss",
        "reason": "The Information is paywalled, Protocol offers similar tech journalism"
    }
]


# New Enterprise AI sources
ENTERPRISE_AI_SOURCES = [
    {
        "name": "Gartner AI & Analytics",
        "url": "https://www.gartner.com/en/topics/artificial-intelligence/rss",
        "category": "Enterprise AI"
    },
    {
        "name": "McKinsey AI Insights",
        "url": "https://www.mckinsey.com/capabilities/quantumblack/how-we-help-clients/rss",
        "category": "Enterprise AI"
    },
    {
        "name": "Deloitte AI Institute",
        "url": "https://www2.deloitte.com/us/en/pages/deloitte-analytics/topics/artificial-intelligence.rss",
        "category": "Enterprise AI"
    },
    {
        "name": "IBM AI Blog",
        "url": "https://www.ibm.com/blogs/watson/feed/",
        "category": "Enterprise AI"
    },
    {
        "name": "Accenture AI",
        "url": "https://www.accenture.com/us-en/blogs/artificial-intelligence-blog/rss.xml",
        "category": "Enterprise AI"
    },
    {
        "name": "Google Cloud AI Blog",
        "url": "https://cloud.google.com/blog/products/ai-machine-learning/rss",
        "category": "Enterprise AI"
    },
    {
        "name": "AWS Machine Learning Blog",
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "category": "Enterprise AI"
    }
]


# New Open Source AI sources
OPEN_SOURCE_AI_SOURCES = [
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "Open Source AI"
    },
    {
        "name": "Papers with Code",
        "url": "https://paperswithcode.com/latest/rss",
        "category": "Open Source AI"
    },
    {
        "name": "PyTorch Blog",
        "url": "https://pytorch.org/blog/feed.xml",
        "category": "Open Source AI"
    },
    {
        "name": "TensorFlow Blog",
        "url": "https://blog.tensorflow.org/feeds/posts/default",
        "category": "Open Source AI"
    },
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "category": "Open Source AI"
    },
    {
        "name": "Anthropic News",
        "url": "https://www.anthropic.com/news/rss.xml",
        "category": "Open Source AI"
    },
    {
        "name": "LangChain Blog",
        "url": "https://blog.langchain.dev/rss/",
        "category": "Open Source AI"
    },
    {
        "name": "Stability AI Blog",
        "url": "https://stability.ai/blog/rss.xml",
        "category": "Open Source AI"
    },
    {
        "name": "Meta AI Research",
        "url": "https://ai.meta.com/blog/rss/",
        "category": "Open Source AI"
    },
    {
        "name": "Google AI Blog",
        "url": "https://ai.googleblog.com/feeds/posts/default",
        "category": "Open Source AI"
    }
]


async def disable_blocked_source(db_client, old_name: str):
    """Disable a blocked RSS source"""
    try:
        result = db_client.client.table('content_sources')\
            .update({'active': False})\
            .eq('name', old_name)\
            .eq('type', 'rss')\
            .execute()
        
        if result.data:
            print(f"  ✅ Disabled: {old_name}")
            return True
        else:
            print(f"  ⚠️  Not found: {old_name}")
            return False
    except Exception as e:
        print(f"  ❌ Error disabling {old_name}: {e}")
        return False


async def add_source(db_client, name: str, url: str, category: str = None):
    """Add a new RSS source"""
    try:
        # Check if source already exists
        existing = db_client.client.table('content_sources')\
            .select('*')\
            .eq('identifier', url)\
            .execute()
        
        if existing.data:
            print(f"  ⚠️  Already exists: {name}")
            return False
        
        # Insert new source
        data = {
            'name': name,
            'type': 'rss',
            'identifier': url,
            'active': True
        }
        
        # Note: category field not used (doesn't exist in DB schema)
        
        result = db_client.client.table('content_sources').insert(data).execute()
        
        if result.data:
            print(f"  ✅ Added: {name}")
            print(f"      URL: {url}")
            return True
        else:
            print(f"  ❌ Failed to add: {name}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error adding {name}: {e}")
        return False


async def fix_blocked_sources(db_client):
    """Fix blocked sources by replacing with alternatives"""
    print("\n" + "="*80)
    print("🔧 FIXING BLOCKED SOURCES")
    print("="*80)
    
    for fix in BLOCKED_SOURCE_FIXES:
        print(f"\n📌 {fix['old_name']} → {fix['new_name']}")
        print(f"   Reason: {fix['reason']}")
        
        # Disable old source
        await disable_blocked_source(db_client, fix['old_name'])
        
        # Add new source
        await add_source(db_client, fix['new_name'], fix['new_url'])


async def add_enterprise_sources(db_client):
    """Add Enterprise AI sources"""
    print("\n" + "="*80)
    print("🏢 ADDING ENTERPRISE AI SOURCES")
    print("="*80)
    
    added = 0
    for source in ENTERPRISE_AI_SOURCES:
        print(f"\n📌 {source['name']}")
        if await add_source(db_client, source['name'], source['url'], source['category']):
            added += 1
    
    print(f"\n✅ Added {added}/{len(ENTERPRISE_AI_SOURCES)} Enterprise AI sources")


async def add_open_source_sources(db_client):
    """Add Open Source AI sources"""
    print("\n" + "="*80)
    print("🔓 ADDING OPEN SOURCE AI SOURCES")
    print("="*80)
    
    added = 0
    for source in OPEN_SOURCE_AI_SOURCES:
        print(f"\n📌 {source['name']}")
        if await add_source(db_client, source['name'], source['url'], source['category']):
            added += 1
    
    print(f"\n✅ Added {added}/{len(OPEN_SOURCE_AI_SOURCES)} Open Source AI sources")


async def show_summary(db_client):
    """Show summary of all active sources"""
    print("\n" + "="*80)
    print("📊 SUMMARY OF ACTIVE RSS SOURCES")
    print("="*80)
    
    try:
        result = db_client.client.table('content_sources')\
            .select('*')\
            .eq('type', 'rss')\
            .eq('active', True)\
            .execute()
        
        sources = result.data
        print(f"\n✅ Total active RSS sources: {len(sources)}")
        
        print("\n📂 All Sources:")
        for source in sorted(sources, key=lambda x: x['name']):
            print(f"  • {source['name']}")
                
    except Exception as e:
        print(f"❌ Error getting summary: {e}")


async def main():
    """Main function"""
    print("\n" + "="*80)
    print("🚀 RSS SOURCE UPGRADE SCRIPT")
    print("="*80)
    print("\nThis script will:")
    print("  1. Fix 3 blocked premium sources (403 errors)")
    print("  2. Add 7 Enterprise AI sources")
    print("  3. Add 10 Open Source AI sources")
    print("\n" + "="*80)
    
    # Confirm
    response = input("\nProceed? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        return
    
    # Initialize
    settings = Settings()
    db_client = SimpleSupabaseClient(settings)
    
    # Execute fixes
    await fix_blocked_sources(db_client)
    await add_enterprise_sources(db_client)
    await add_open_source_sources(db_client)
    await show_summary(db_client)
    
    print("\n" + "="*80)
    print("✅ UPGRADE COMPLETE!")
    print("="*80)
    print("\n💡 Next steps:")
    print("  1. Run a test digest: python3 run_ai_digest_pipeline.py force")
    print("  2. Check for errors in the logs")
    print("  3. Verify new sources are working")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
