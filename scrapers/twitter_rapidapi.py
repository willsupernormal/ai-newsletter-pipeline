"""
Twitter scraper using RapidAPI
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

from config.settings import Settings


class TwitterRapidAPIScraper:
    """Twitter scraper using RapidAPI service"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.api_key = settings.RAPIDAPI_KEY
        self.api_host = settings.RAPIDAPI_TWITTER_HOST
        
        # Map Twitter usernames to user IDs (you'll need to add more)
        self.user_id_map = {
            'AndrewYNg': '2455740283',
            'karpathy': '33836629',
            'ylecun': '48008938',
            'sama': '1605',
            'OpenAI': '4398626122',
            'GoogleAI': '33838201'
        }
    
    async def fetch_user_tweets(self, username: str, count: int = 10) -> List[Dict[str, Any]]:
        """Fetch tweets from a specific user"""
        user_id = self.user_id_map.get(username)
        if not user_id:
            self.logger.warning(f"No user ID mapping for {username}")
            return []
        
        url = f"https://{self.api_host}/user-tweets"
        headers = {
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": self.api_key
        }
        params = {
            "user": user_id,
            "count": str(count)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self.parse_tweets(data, username)
                    else:
                        self.logger.error(f"RapidAPI error {response.status} for {username}")
                        return []
        except Exception as e:
            self.logger.error(f"Failed to fetch tweets for {username}: {e}")
            return []
    
    def parse_tweets(self, api_response: Dict[str, Any], username: str) -> List[Dict[str, Any]]:
        """Parse RapidAPI response into our article format"""
        articles = []
        
        try:
            # The response structure may vary, adjust as needed
            tweets = []
            
            # Try different response formats
            if 'result' in api_response:
                if 'timeline' in api_response['result']:
                    timeline = api_response['result']['timeline']
                    if 'instructions' in timeline:
                        for instruction in timeline['instructions']:
                            if 'entries' in instruction:
                                tweets = instruction['entries']
                    elif 'entries' in timeline:
                        tweets = timeline['entries']
            elif 'data' in api_response:
                tweets = api_response['data']
            elif isinstance(api_response, list):
                tweets = api_response
            
            # Process tweets
            for tweet in tweets[:10]:  # Limit to 10 tweets
                try:
                    article = self.tweet_to_article(tweet, username)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.logger.debug(f"Failed to parse tweet: {e}")
                    continue
            
            self.logger.info(f"Parsed {len(articles)} tweets from {username}")
            
        except Exception as e:
            self.logger.error(f"Error parsing tweets: {e}")
        
        return articles
    
    def tweet_to_article(self, tweet_data: Any, username: str) -> Dict[str, Any]:
        """Convert a tweet to article format"""
        try:
            # Extract text content (structure varies by API response)
            text = ""
            tweet_id = ""
            created_at = datetime.now()
            
            # Handle different tweet data structures
            if isinstance(tweet_data, dict):
                # Look for tweet content in various places
                if 'content' in tweet_data:
                    content = tweet_data['content']
                    if 'itemContent' in content:
                        item = content['itemContent']
                        if 'tweet_results' in item:
                            result = item['tweet_results'].get('result', {})
                            if 'legacy' in result:
                                legacy = result['legacy']
                                text = legacy.get('full_text', '')
                                tweet_id = legacy.get('id_str', '')
                                # Parse created_at
                                if 'created_at' in legacy:
                                    try:
                                        created_at = datetime.strptime(
                                            legacy['created_at'], 
                                            '%a %b %d %H:%M:%S %z %Y'
                                        )
                                    except:
                                        pass
                
                # Simpler structure
                if not text and 'text' in tweet_data:
                    text = tweet_data['text']
                if not text and 'full_text' in tweet_data:
                    text = tweet_data['full_text']
                if not tweet_id and 'id' in tweet_data:
                    tweet_id = str(tweet_data['id'])
            
            if not text:
                return None
            
            # Clean tweet text
            import re
            clean_text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            clean_text = ' '.join(clean_text.split())
            
            # Extract hashtags for tags
            hashtags = re.findall(r'#(\w+)', text)
            tags = ['twitter', f'author_{username.lower()}']
            tags.extend([f'hashtag_{tag.lower()}' for tag in hashtags[:5]])
            
            # Create article
            article = {
                'title': f"@{username}: {clean_text[:100]}...",
                'url': f"https://twitter.com/{username}/status/{tweet_id}" if tweet_id else f"https://twitter.com/{username}",
                'content_excerpt': clean_text,
                'source_type': 'twitter',
                'source_name': f"Twitter/@{username}",
                'published_at': created_at,
                'tags': tags[:10],  # Limit tags
                'twitter_metrics': self.extract_metrics(tweet_data)
            }
            
            return article
            
        except Exception as e:
            self.logger.debug(f"Failed to convert tweet to article: {e}")
            return None
    
    def extract_metrics(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract engagement metrics from tweet"""
        metrics = {}
        
        try:
            # Look for metrics in various places
            if 'legacy' in tweet_data:
                legacy = tweet_data['legacy']
                metrics = {
                    'retweets': legacy.get('retweet_count', 0),
                    'likes': legacy.get('favorite_count', 0),
                    'replies': legacy.get('reply_count', 0),
                    'quotes': legacy.get('quote_count', 0)
                }
            elif 'public_metrics' in tweet_data:
                pm = tweet_data['public_metrics']
                metrics = {
                    'retweets': pm.get('retweet_count', 0),
                    'likes': pm.get('like_count', 0),
                    'replies': pm.get('reply_count', 0),
                    'quotes': pm.get('quote_count', 0)
                }
        except:
            pass
        
        return metrics
    
    async def scrape_accounts(self) -> List[Dict[str, Any]]:
        """Scrape all configured Twitter accounts"""
        accounts = self.settings.twitter_accounts_list
        self.logger.info(f"Starting Twitter scraping for {len(accounts)} accounts")
        
        all_articles = []
        
        for account in accounts:
            try:
                self.logger.info(f"Scraping @{account}...")
                articles = await self.fetch_user_tweets(account, count=5)
                all_articles.extend(articles)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to scrape {account}: {e}")
        
        self.logger.info(f"Twitter scraping completed: {len(all_articles)} tweets collected")
        return all_articles


# Make it compatible with the main pipeline
class TwitterScraper(TwitterRapidAPIScraper):
    """Alias for compatibility"""
    pass