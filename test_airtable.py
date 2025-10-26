"""Test Airtable connection"""
import asyncio
from config.settings import Settings
from services.airtable_client import AirtableClient

async def test_airtable():
    """Test Airtable connection"""
    print("Testing Airtable connection...")
    
    try:
        settings = Settings()
        client = AirtableClient(settings)
        
        # Try to get recent articles (should be empty)
        articles = client.get_recent_articles(limit=5)
        print(f"✅ Connected successfully!")
        print(f"📊 Found {len(articles)} existing articles")
        
        # Try to create a test record
        test_article = {
            'title': 'Test Article - DELETE ME',
            'url': 'https://example.com/test',
            'source_name': 'VentureBeat',
            'stage': '📥 Saved',
            'priority': '🟡 Medium',
            'ai_summary_short': 'This is a test article to verify Airtable integration.',
            'supabase_id': 'test-123'
        }
        
        record_id = client.create_article_record(test_article)
        
        if record_id:
            print(f"✅ Test record created: {record_id}")
            print(f"🔗 Check your Airtable base - you should see 'Test Article - DELETE ME'")
            print(f"   You can delete it manually from Airtable")
        else:
            print("❌ Failed to create test record")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your AIRTABLE_API_KEY in .env")
        print("2. Check your AIRTABLE_BASE_ID in .env")
        print("3. Verify table name is exactly 'Content Pipeline'")
        print("4. Ensure all required fields exist in Airtable")

if __name__ == "__main__":
    asyncio.run(test_airtable())
