#!/usr/bin/env python3
"""Test Twitter API to find correct endpoints"""

import aiohttp
import asyncio
import json

async def test_search():
    """Test Twitter search by username"""
    
    api_key = "9d133bebebmshf038001088ec251p1a9f1fjsn438b29fbbae0"
    api_host = "twitter241.p.rapidapi.com"
    
    # Try searching for AI-related content instead
    print("Testing Twitter search for AI content...\n")
    
    url = f"https://{api_host}/search"
    headers = {
        "x-rapidapi-host": api_host,
        "x-rapidapi-key": api_key
    }
    
    # Search for AI-related tweets
    params = {
        "query": "artificial intelligence OR machine learning OR OpenAI OR GPT",
        "type": "Latest",
        "count": "10"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"Search API Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                
                # Parse results
                if 'result' in data:
                    tweets = []
                    result = data['result']
                    
                    # Navigate the response structure
                    if 'timeline' in result:
                        timeline = result['timeline']
                        if 'instructions' in timeline:
                            for instruction in timeline['instructions']:
                                if 'entries' in instruction:
                                    entries = instruction['entries']
                                    for entry in entries[:5]:  # First 5 tweets
                                        if 'content' in entry:
                                            content = entry['content']
                                            if 'itemContent' in content:
                                                item = content['itemContent']
                                                if 'tweet_results' in item:
                                                    tweet_result = item['tweet_results'].get('result', {})
                                                    if 'legacy' in tweet_result:
                                                        legacy = tweet_result['legacy']
                                                        text = legacy.get('full_text', '')
                                                        user = tweet_result.get('core', {}).get('user_results', {}).get('result', {}).get('legacy', {})
                                                        username = user.get('screen_name', 'unknown')
                                                        
                                                        if text:
                                                            print(f"@{username}:")
                                                            print(f"  {text[:100]}...")
                                                            print()
                                                            tweets.append({'user': username, 'text': text})
                    
                    print(f"✓ Found {len(tweets)} AI-related tweets")
                    return tweets
                else:
                    print("Response structure:")
                    print(json.dumps(data, indent=2)[:500])
            else:
                print(f"Error: {await response.text()}")
    
    return []

if __name__ == "__main__":
    tweets = asyncio.run(test_search())
    print(f"\n{'✓' if tweets else '✗'} Search test completed")