#!/usr/bin/env python3
"""
Test Twitter scraper with RapidAPI
"""

import asyncio
import logging
from config.settings import Settings
from scrapers.twitter_scraper import TwitterScraper

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_raw_api():
    """Test the raw RapidAPI call to debug response format"""
    import aiohttp
    import json
    
    url = "https://twitter241.p.rapidapi.com/user-tweets"
    params = {
        'user': '2455740283',
        'count': '20'
    }
    headers = {
        'x-rapidapi-host': 'twitter241.p.rapidapi.com',
        'x-rapidapi-key': '9d133bebebmshf038001088ec251p1a9f1fjsn438b29fbbae0'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            print(f"Status: {response.status}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status == 200:
                data = await response.json()
                print(f"Response keys: {list(data.keys())}")
                print(f"Full response: {json.dumps(data, indent=2)[:1000]}...")
                return data
            else:
                text = await response.text()
                print(f"Error response: {text}")
                return None

async def test_twitter_scraper():
    """Test the RapidAPI Twitter scraper"""
    
    print("=== Testing Raw API Call ===")
    raw_data = await test_raw_api()
    
    if not raw_data:
        return False
    
    print("\n=== Testing Twitter Scraper ===")
    
    # Create settings with RapidAPI key
    settings = Settings(
        SUPABASE_URL="dummy",
        SUPABASE_KEY="dummy", 
        SUPABASE_SERVICE_KEY="dummy",
        OPENAI_API_KEY="dummy",
        GMAIL_EMAIL="dummy",
        GMAIL_APP_PASSWORD="dummy",
        TWITTER_SERVICE="rapidapi",
        RAPIDAPI_KEY="9d133bebebmshf038001088ec251p1a9f1fjsn438b29fbbae0"
    )
    
    scraper = TwitterScraper(settings)
    
    # Test with Andrew Ng's user ID
    print("Testing Twitter scraper with Andrew Ng's user ID 216939636...")
    tweets = await scraper.scrape_user_tweets("216939636", max_tweets=5)
    
    print(f"\n✅ Retrieved {len(tweets)} tweets")
    
    for i, tweet in enumerate(tweets[:2]):
        print(f"\n--- Tweet {i+1} ---")
        print(f"Title: {tweet['title']}")
        print(f"URL: {tweet['url']}")
        print(f"Content: {tweet['content_excerpt'][:150]}...")
        print(f"Metrics: {tweet['twitter_metrics']}")
        print(f"Tags: {tweet['tags'][:5]}")  # Show first 5 tags
    
    return len(tweets) > 0

if __name__ == "__main__":
    success = asyncio.run(test_twitter_scraper())
    if success:
        print("\n🎉 Twitter scraper test PASSED!")
    else:
        print("\n❌ Twitter scraper test FAILED!")
