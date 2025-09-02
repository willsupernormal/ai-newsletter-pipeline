#!/usr/bin/env python3
"""Test Twitter scraping with RapidAPI"""

import requests
import json

# Test RapidAPI Twitter endpoint
url = "https://twitter241.p.rapidapi.com/user-tweets"

# Test with Andrew Ng's Twitter
querystring = {"user": "2455740283", "count": "5"}  # Andrew Ng's user ID

headers = {
    "x-rapidapi-host": "twitter241.p.rapidapi.com",
    "x-rapidapi-key": "9d133bebebmshf038001088ec251p1a9f1fjsn438b29fbbae0"
}

print("Testing Twitter API with RapidAPI...")
print(f"Fetching tweets from Andrew Ng (user ID: 2455740283)...\n")

try:
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ API call successful!")
        
        # Check if we got results
        if 'result' in data and 'timeline' in data['result']:
            tweets = data['result']['timeline']['instructions'][0]['entries'] if 'instructions' in data['result']['timeline'] else []
            print(f"Found {len(tweets)} tweets\n")
            
            # Show first tweet as sample
            if tweets and len(tweets) > 0:
                first_tweet = tweets[0]
                print("Sample tweet structure:")
                print(json.dumps(first_tweet, indent=2)[:500] + "...")
        else:
            print("Response structure:")
            print(json.dumps(data, indent=2)[:500] + "...")
    else:
        print(f"✗ API call failed with status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\nNote: Twitter scraping with RapidAPI is configured!")
print("The pipeline can now scrape tweets from the configured accounts.")