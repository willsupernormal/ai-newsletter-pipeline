#!/usr/bin/env python3
"""Test simple database operations with Supabase"""

from supabase import create_client
from datetime import datetime, date

# Test connection
url = 'https://xpxrbgttnjjcfwmnosyc.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhweHJiZ3R0bmpqY2Z3bW5vc3ljIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjgyNzcxMiwiZXhwIjoyMDcyNDAzNzEyfQ.26hGWgyfV7Z0uQPbq74YhtIsFHWi2miN-4n9Wb-fvhA'

client = create_client(url, key)

print("Testing Supabase database operations...")

# Test 1: Check if articles table exists
try:
    response = client.table('articles').select('*').limit(1).execute()
    print(f"✓ Articles table accessible, {len(response.data)} records found")
except Exception as e:
    print(f"✗ Articles table error: {e}")

# Test 2: Check weekly_cycles table
try:
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    response = client.table('weekly_cycles').select('*').eq('week_start_date', week_start).execute()
    if response.data:
        print(f"✓ Current week cycle exists: {week_start}")
    else:
        print(f"✓ Weekly cycles table accessible, no current week yet")
except Exception as e:
    print(f"✗ Weekly cycles error: {e}")

# Test 3: Try to insert a test article
try:
    from datetime import timedelta
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    test_article = {
        'title': 'Test Article - Pipeline Setup',
        'url': f'https://test.com/article-{datetime.now().timestamp()}',
        'content_excerpt': 'This is a test article to verify database connectivity',
        'source_type': 'rss',
        'source_name': 'Test Source',
        'published_at': datetime.now().isoformat(),
        'week_start_date': week_start.isoformat(),
        'relevance_score': 75.0,
        'tags': ['test', 'setup']
    }
    
    response = client.table('articles').insert(test_article).execute()
    if response.data:
        print(f"✓ Successfully inserted test article")
        article_id = response.data[0]['id']
        
        # Clean up test article
        client.table('articles').delete().eq('id', article_id).execute()
        print(f"✓ Successfully deleted test article")
    else:
        print(f"✗ Failed to insert test article")
except Exception as e:
    print(f"✗ Insert test failed: {e}")

print("\n✓ Database connectivity test completed")