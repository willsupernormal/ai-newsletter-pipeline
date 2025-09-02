"""
Twitter AI content scraper using search instead of specific accounts
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any
from datetime import datetime
import re

from config.settings import Settings


class TwitterAISearchScraper:
    """Twitter scraper that searches for AI-related content"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.api_key = settings.RAPIDAPI_KEY
        self.api_host = settings.RAPIDAPI_TWITTER_HOST
        
        # AI-related search queries - focusing on specific accounts
        self.search_queries = [
            # Key AI thought leaders
            "from:AndrewYNg",
            "from:karpathy", 
            "from:ylecun",
            "from:sama",
            "from:GaryMarcus",
            "from:emollick",
            
            # AI companies and organizations
            "from:OpenAI",
            "from:GoogleAI", 
            "from:DeepMind",
            "from:AnthropicAI",
            "from:MetaAI",
            
            # Business/Enterprise AI
            "from:IBM OR from:Microsoft",
            "from:nvidia",
            
            # Also search for AI topics
            "artificial intelligence enterprise OR business AI -filter:replies",
            "data strategy OR vendor lock-in AI"
        ]
    
    async def search_tweets(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        """Search for tweets matching query"""
        url = f"https://{self.api_host}/search"
        headers = {
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": self.api_key
        }
        params = {
            "query": query,
            "type": "Latest",  # Get latest tweets
            "count": str(count)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.parse_search_results(data)
                    else:
                        self.logger.error(f"Search API error {response.status}")
                        return []
        except Exception as e:
            self.logger.error(f"Failed to search tweets: {e}")
            return []
    
    def parse_search_results(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse search results into article format"""
        articles = []
        
        try:
            if 'result' not in api_response:
                return []
            
            result = api_response['result']
            if 'timeline' not in result:
                return []
            
            timeline = result['timeline']
            if 'instructions' not in timeline:
                return []
            
            for instruction in timeline['instructions']:
                if 'entries' not in instruction:
                    continue
                
                for entry in instruction['entries']:
                    try:
                        article = self.parse_tweet_entry(entry)
                        if article:
                            articles.append(article)
                    except Exception as e:
                        self.logger.debug(f"Failed to parse tweet: {e}")
                        continue
            
            self.logger.info(f"Parsed {len(articles)} tweets from search")
            
        except Exception as e:
            self.logger.error(f"Error parsing search results: {e}")
        
        return articles
    
    def parse_tweet_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a single tweet entry"""
        if 'content' not in entry:
            return None
        
        content = entry['content']
        if 'itemContent' not in content:
            return None
        
        item = content['itemContent']
        if 'tweet_results' not in item:
            return None
        
        tweet_result = item['tweet_results'].get('result', {})
        if 'legacy' not in tweet_result:
            return None
        
        legacy = tweet_result['legacy']
        text = legacy.get('full_text', '')
        
        if not text:
            return None
        
        # Get user info
        username = 'unknown'
        user_name = 'Twitter User'
        if 'core' in tweet_result:
            user_result = tweet_result['core'].get('user_results', {}).get('result', {})
            if 'legacy' in user_result:
                user_legacy = user_result['legacy']
                username = user_legacy.get('screen_name', 'unknown')
                user_name = user_legacy.get('name', 'Twitter User')
        
        # Get tweet ID
        tweet_id = legacy.get('id_str', '')
        
        # Parse created_at
        created_at = datetime.now()
        if 'created_at' in legacy:
            try:
                created_at = datetime.strptime(
                    legacy['created_at'], 
                    '%a %b %d %H:%M:%S %z %Y'
                )
            except:
                pass
        
        # Clean text (remove URLs)
        clean_text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        clean_text = ' '.join(clean_text.split())
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags = ['twitter', 'ai']
        tags.extend([f'hashtag_{tag.lower()}' for tag in hashtags[:3]])
        
        # Create article
        article = {
            'title': f"@{username}: {clean_text[:80]}...",
            'url': f"https://twitter.com/{username}/status/{tweet_id}" if tweet_id else "https://twitter.com",
            'content_excerpt': clean_text,
            'source_type': 'twitter',
            'source_name': f"Twitter/@{username}",
            'published_at': created_at,
            'tags': tags[:10],
            'twitter_metrics': {
                'retweets': legacy.get('retweet_count', 0),
                'likes': legacy.get('favorite_count', 0),
                'replies': legacy.get('reply_count', 0),
                'quotes': legacy.get('quote_count', 0)
            }
        }
        
        return article
    
    async def scrape_accounts(self) -> List[Dict[str, Any]]:
        """Search for AI-related tweets"""
        self.logger.info("Starting Twitter AI content search")
        
        all_articles = []
        
        # Use first 3 queries for testing
        for query in self.search_queries[:3]:
            try:
                self.logger.info(f"Searching: {query[:50]}...")
                articles = await self.search_tweets(query, count=10)
                
                # Limit to 5 articles per search
                all_articles.extend(articles[:5])
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Search failed: {e}")
        
        self.logger.info(f"Twitter search completed: {len(all_articles)} tweets collected")
        return all_articles


# Make it compatible with the main pipeline
class TwitterScraper(TwitterAISearchScraper):
    """Alias for compatibility"""
    pass