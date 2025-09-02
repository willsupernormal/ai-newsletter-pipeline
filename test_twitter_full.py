#!/usr/bin/env python3
"""Test Twitter scraping with RapidAPI"""

import asyncio
import logging
import json
from config.settings import Settings
from scrapers.twitter_rapidapi import TwitterRapidAPIScraper

logging.basicConfig(level=logging.INFO)

async def test_twitter():
    """Test Twitter scraping"""
    settings = Settings()
    
    print("=" * 60)
    print("TWITTER SCRAPING TEST")
    print("=" * 60)
    
    print(f"\nConfiguration:")
    print(f"  Service: {settings.TWITTER_SERVICE}")
    print(f"  API Host: {settings.RAPIDAPI_TWITTER_HOST}")
    print(f"  Accounts: {', '.join(settings.twitter_accounts_list)}")
    
    # Test with one account first
    scraper = TwitterRapidAPIScraper(settings)
    
    print("\n📱 Testing single account: @AndrewYNg")
    articles = await scraper.fetch_user_tweets('AndrewYNg', count=3)
    
    if articles:
        print(f"✓ Retrieved {len(articles)} tweets\n")
        
        for i, article in enumerate(articles[:2], 1):
            print(f"{i}. {article['title'][:60]}...")
            print(f"   Source: {article['source_name']}")
            print(f"   Tags: {', '.join(article['tags'][:3])}")
            if article.get('twitter_metrics'):
                metrics = article['twitter_metrics']
                print(f"   Engagement: {metrics.get('likes', 0)} likes, {metrics.get('retweets', 0)} RTs")
            print()
    else:
        print("✗ No tweets retrieved")
        print("\nTrying alternative approach...")
        
        # Test raw API call
        import aiohttp
        url = f"https://{settings.RAPIDAPI_TWITTER_HOST}/user-tweets"
        headers = {
            "x-rapidapi-host": settings.RAPIDAPI_TWITTER_HOST,
            "x-rapidapi-key": settings.RAPIDAPI_KEY
        }
        params = {"user": "2455740283", "count": "2"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                print(f"API Response Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("Response structure:")
                    print(json.dumps(data, indent=2)[:500] + "...")
                else:
                    print(f"Error: {await response.text()}")
    
    return articles

if __name__ == "__main__":
    articles = asyncio.run(test_twitter())
    print(f"\n{'✓' if articles else '✗'} Twitter test completed")