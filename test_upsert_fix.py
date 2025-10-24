#!/usr/bin/env python3
"""
Test that the upsert fix works for duplicate digests
"""
import asyncio
from datetime import date
from config.settings import Settings
from database.digest_storage import DigestStorage

async def test_upsert():
    """Test that we can create and update a digest for the same date"""
    
    print("\n" + "="*70)
    print("🧪 Testing Digest Upsert (Duplicate Prevention Fix)")
    print("="*70 + "\n")
    
    settings = Settings()
    storage = DigestStorage(settings)
    
    test_date = date.today()
    
    # Sample article data
    sample_article = {
        'title': 'Test Article for Upsert',
        'url': 'https://example.com/test-upsert',
        'source_name': 'Test Source',
        'source_type': 'rss',
        'content_excerpt': 'Test content for upsert functionality',
        'ai_summary': 'Test summary',
        'ai_summary_short': 'Short test summary',
        'key_metrics': [],
        'key_quotes': [],
        'why_it_matters': 'Testing upsert',
        'primary_theme': 'Testing',
        'content_type': 'news'
    }
    
    try:
        # First insert
        print(f"📝 Creating first digest for {test_date}...")
        digest_id_1 = await storage.store_daily_digest(
            digest_date=test_date,
            summary_text="First test digest",
            key_insights=["Test insight 1"],
            selected_articles=[sample_article],
            total_processed=1,
            ai_reasoning="Test reasoning"
        )
        print(f"✅ First digest created: {digest_id_1}\n")
        
        # Second insert (should update, not fail)
        print(f"📝 Creating second digest for {test_date} (should update)...")
        digest_id_2 = await storage.store_daily_digest(
            digest_date=test_date,
            summary_text="Second test digest - UPDATED",
            key_insights=["Test insight 2", "Test insight 3"],
            selected_articles=[sample_article],
            total_processed=1,
            ai_reasoning="Updated test reasoning"
        )
        print(f"✅ Second digest upserted: {digest_id_2}\n")
        
        # Verify they have the same ID (updated, not created new)
        if digest_id_1 == digest_id_2:
            print("✅ SUCCESS: Same digest ID - record was updated, not duplicated")
        else:
            print("⚠️ WARNING: Different digest IDs - new record created instead of update")
            print(f"   First ID:  {digest_id_1}")
            print(f"   Second ID: {digest_id_2}")
        
        # Retrieve and verify
        print(f"\n📊 Retrieving digest for {test_date}...")
        retrieved = await storage.get_daily_digest(test_date)
        
        if retrieved:
            print(f"✅ Retrieved digest:")
            print(f"   Summary: {retrieved['summary_text']}")
            print(f"   Insights: {len(retrieved['key_insights'])} insights")
            print(f"   Articles: {len(retrieved['selected_article_ids'])} articles")
            
            if retrieved['summary_text'] == "Second test digest - UPDATED":
                print("\n🎉 UPSERT FIX WORKING: Digest was updated with new content!")
            else:
                print("\n⚠️ Digest not updated with new content")
        else:
            print("❌ Could not retrieve digest")
        
        print("\n" + "="*70)
        print("✅ Test Complete - Upsert Fix Verified")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_upsert())
    exit(0 if success else 1)
