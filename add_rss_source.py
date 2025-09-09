#!/usr/bin/env python3
"""
Add new RSS sources to the content_sources table
Usage: python add_rss_source.py "Source Name" "https://example.com/feed.xml"
"""

import sys
import asyncio
from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient

async def add_rss_source(name: str, url: str, active: bool = True):
    """Add a new RSS source to the content_sources table"""
    
    settings = Settings()
    db_client = SimpleSupabaseClient(settings)
    
    try:
        # Check if source already exists
        existing = db_client.client.table('content_sources')\
            .select('*')\
            .eq('name', name)\
            .eq('type', 'rss')\
            .execute()
        
        if existing.data:
            print(f"❌ RSS source '{name}' already exists")
            return False
        
        # Insert new RSS source
        result = db_client.client.table('content_sources').insert({
            'name': name,
            'type': 'rss',
            'identifier': url,
            'active': active
        }).execute()
        
        if result.data:
            print(f"✅ Successfully added RSS source: {name}")
            print(f"   URL: {url}")
            print(f"   Active: {active}")
            return True
        else:
            print(f"❌ Failed to add RSS source: {name}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding RSS source: {e}")
        return False

async def list_rss_sources():
    """List all RSS sources in the content_sources table"""
    
    settings = Settings()
    db_client = SimpleSupabaseClient(settings)
    
    try:
        result = db_client.client.table('content_sources')\
            .select('*')\
            .eq('type', 'rss')\
            .order('name')\
            .execute()
        
        if result.data:
            print(f"\n📰 RSS Sources ({len(result.data)} total):")
            print("-" * 80)
            for source in result.data:
                status = "🟢 Active" if source['active'] else "🔴 Inactive"
                last_processed = source.get('last_processed', 'Never')
                if last_processed and last_processed != 'Never':
                    last_processed = last_processed[:19].replace('T', ' ')
                
                print(f"{status} | {source['name']}")
                print(f"         URL: {source['identifier']}")
                print(f"         Last processed: {last_processed}")
                print(f"         Success/Failure: {source.get('success_count', 0)}/{source.get('failure_count', 0)}")
                print()
        else:
            print("📰 No RSS sources found")
            
    except Exception as e:
        print(f"❌ Error listing RSS sources: {e}")

async def toggle_rss_source(name: str, active: bool):
    """Enable or disable an RSS source"""
    
    settings = Settings()
    db_client = SimpleSupabaseClient(settings)
    
    try:
        result = db_client.client.table('content_sources')\
            .update({'active': active})\
            .eq('name', name)\
            .eq('type', 'rss')\
            .execute()
        
        if result.data:
            status = "enabled" if active else "disabled"
            print(f"✅ RSS source '{name}' {status}")
            return True
        else:
            print(f"❌ RSS source '{name}' not found")
            return False
            
    except Exception as e:
        print(f"❌ Error updating RSS source: {e}")
        return False

def print_usage():
    """Print usage instructions"""
    print("""
🔧 RSS Source Management Tool

Usage:
  python add_rss_source.py add "Source Name" "https://example.com/feed.xml"
  python add_rss_source.py list
  python add_rss_source.py enable "Source Name"
  python add_rss_source.py disable "Source Name"

Examples:
  python add_rss_source.py add "AI News" "https://ainews.com/feed.xml"
  python add_rss_source.py list
  python add_rss_source.py disable "Old Source"
""")

async def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) != 4:
            print("❌ Usage: python add_rss_source.py add \"Source Name\" \"https://example.com/feed.xml\"")
            return
        
        name = sys.argv[2]
        url = sys.argv[3]
        await add_rss_source(name, url)
        
    elif command == "list":
        await list_rss_sources()
        
    elif command == "enable":
        if len(sys.argv) != 3:
            print("❌ Usage: python add_rss_source.py enable \"Source Name\"")
            return
        
        name = sys.argv[2]
        await toggle_rss_source(name, True)
        
    elif command == "disable":
        if len(sys.argv) != 3:
            print("❌ Usage: python add_rss_source.py disable \"Source Name\"")
            return
        
        name = sys.argv[2]
        await toggle_rss_source(name, False)
        
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    asyncio.run(main())
