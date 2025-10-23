#!/usr/bin/env python3
"""
Basic functionality test for AI Newsletter Pipeline
Tests core components without requiring external API keys
"""

import asyncio
import sys
import os
from datetime import datetime, date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that core modules can be imported"""
    print("Testing imports...")
    
    try:
        from config.settings import Settings
        print("✓ Settings module imported")
    except Exception as e:
        print(f"✗ Settings import failed: {e}")
        return False
    
    try:
        from processors.content_processor import ContentProcessor
        print("✓ ContentProcessor imported")
    except Exception as e:
        print(f"✗ ContentProcessor import failed: {e}")
        return False
    
    try:
        from processors.deduplicator import Deduplicator
        print("✓ Deduplicator imported")
    except Exception as e:
        print(f"✗ Deduplicator import failed: {e}")
        return False
    
    try:
        from utils.logger import setup_logger
        print("✓ Logger utilities imported")
    except Exception as e:
        print(f"✗ Logger import failed: {e}")
        return False
    
    return True

def test_settings():
    """Test settings configuration"""
    print("\nTesting settings configuration...")
    
    try:
        from config.settings import Settings
        
        # Test with environment variables if available
        settings = Settings()
        
        # Test RSS feeds configuration
        rss_feeds = settings.rss_feeds
        print(f"✓ RSS feeds configured: {len(rss_feeds)} feeds")
        
        # Test Twitter accounts
        twitter_accounts = settings.twitter_accounts_list
        print(f"✓ Twitter accounts configured: {len(twitter_accounts)} accounts")
        
        # Test AI prompt service (synchronous test)
        try:
            from services.prompt_service import get_prompt_service
            prompt_service = get_prompt_service(settings)
            # Test that service initializes correctly
            print("✓ AI prompt service initialized successfully")
        except Exception as e:
            print(f"✗ AI prompt service initialization failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False

def test_content_processor():
    """Test content processing functionality"""
    print("\nTesting content processor...")
    
    try:
        from processors.content_processor import ContentProcessor
        
        processor = ContentProcessor()
        
        # Test article processing
        test_article = {
            'title': 'Test AI Article: Enterprise Machine Learning Implementation',
            'content_excerpt': 'This is a test article about enterprise AI implementation. It discusses vendor lock-in issues and data strategy considerations for business leaders.',
            'source_name': 'Test Source',
            'source_type': 'rss',
            'url': 'https://example.com/test-article'
        }
        
        processed = processor.process_article(test_article)
        
        # Verify processing results
        assert 'processed_at' in processed
        assert 'word_count' in processed
        assert processed['word_count'] > 0
        
        print(f"✓ Article processed successfully")
        print(f"  - Word count: {processed['word_count']}")
        print(f"  - Processed at: {processed['processed_at']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Content processor test failed: {e}")
        return False

async def test_deduplicator():
    """Test deduplication functionality"""
    print("\nTesting deduplicator...")
    
    try:
        from processors.deduplicator import Deduplicator
        
        deduplicator = Deduplicator()
        
        # Test with duplicate articles
        articles = [
            {
                'title': 'AI Implementation in Enterprise',
                'content_excerpt': 'Article about AI implementation',
                'url': 'https://example.com/article1'
            },
            {
                'title': 'AI Implementation in Enterprise',  # Exact duplicate
                'content_excerpt': 'Article about AI implementation',
                'url': 'https://example.com/article1'
            },
            {
                'title': 'Machine Learning in Business',
                'content_excerpt': 'Different article about ML',
                'url': 'https://example.com/article2'
            }
        ]
        
        unique_articles = await deduplicator.remove_duplicates(articles)
        
        assert len(unique_articles) == 2  # Should remove 1 duplicate
        
        print(f"✓ Deduplication successful")
        print(f"  - Original articles: {len(articles)}")
        print(f"  - Unique articles: {len(unique_articles)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Deduplicator test failed: {e}")
        return False

def test_logger():
    """Test logging setup"""
    print("\nTesting logger setup...")
    
    try:
        from utils.logger import setup_logger
        import logging
        
        setup_logger('INFO')
        logger = logging.getLogger('test_logger')
        
        logger.info("Test log message")
        print("✓ Logger setup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Logger test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== AI Newsletter Pipeline - Basic Functionality Test ===\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Settings Test", test_settings),
        ("Content Processor Test", test_content_processor),
        ("Deduplicator Test", test_deduplicator),
        ("Logger Test", test_logger)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
                
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Basic functionality is working.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
