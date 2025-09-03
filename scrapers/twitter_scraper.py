"""
Twitter scraper using RapidAPI service
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
import json

from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient


class TwitterScraper:
    """Twitter scraper using RapidAPI service"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.db_client = SimpleSupabaseClient(settings)
        
        # RapidAPI configuration
        self.rapidapi_key = getattr(settings, 'RAPIDAPI_KEY', '9d133bebebmshf038001088ec251p1a9f1fjsn438b29fbbae0')
        self.rapidapi_host = 'twitter241.p.rapidapi.com'
        self.base_url = f'https://{self.rapidapi_host}'
        
        if settings.TWITTER_SERVICE != "rapidapi":
            self.logger.warning(f"Twitter service set to {settings.TWITTER_SERVICE}, using RapidAPI")
    
    async def get_twitter_sources(self) -> List[Dict[str, Any]]:
        """Load active Twitter sources from content_sources table"""
        try:
            response = self.db_client.client.table('content_sources').select('*').eq('type', 'twitter').eq('active', True).execute()
            sources = response.data
            self.logger.info(f"Loaded {len(sources)} active Twitter sources from database")
            return sources
        except Exception as e:
            self.logger.error(f"Failed to load Twitter sources from database: {e}")
            return []
    
    async def get_username_mapping(self) -> Dict[str, str]:
        """Load Twitter user ID to username mapping from twitter_users table"""
        try:
            response = self.db_client.client.table('twitter_users').select('user_id, username').execute()
            mapping = {user['user_id']: user['username'] for user in response.data}
            self.logger.info(f"Loaded username mapping for {len(mapping)} Twitter users")
            return mapping
        except Exception as e:
            self.logger.error(f"Failed to load username mapping: {e}")
            return {}
    
    def extract_twitter_metrics(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Twitter engagement metrics from RapidAPI format"""
        try:
            return {
                'retweets': tweet_data.get('retweet_count', 0),
                'likes': tweet_data.get('favorite_count', 0),
                'replies': tweet_data.get('reply_count', 0),
                'quotes': tweet_data.get('quote_count', 0),
                'views': tweet_data.get('view_count', 0),
                'bookmarks': tweet_data.get('bookmark_count', 0),
                'engagement_rate': self.calculate_engagement_rate(tweet_data),
                'user_followers': tweet_data.get('user', {}).get('followers_count', 0),
                'tweet_id': tweet_data.get('id_str', tweet_data.get('id')),
                'conversation_id': tweet_data.get('conversation_id')
            }
        except Exception as e:
            self.logger.warning(f"Failed to extract Twitter metrics: {e}")
            return {}
    
    def calculate_engagement_rate(self, tweet_data: Dict[str, Any]) -> float:
        """Calculate engagement rate for a tweet"""
        try:
            likes = tweet_data.get('favorite_count', 0)
            retweets = tweet_data.get('retweet_count', 0)
            replies = tweet_data.get('reply_count', 0)
            quotes = tweet_data.get('quote_count', 0)
            views = tweet_data.get('view_count', 0)
            
            total_engagement = likes + retweets + replies + quotes
            
            if views > 0:
                return round((total_engagement / views) * 100, 2)
            elif total_engagement > 0:
                # Fallback calculation using follower count
                followers = tweet_data.get('user', {}).get('followers_count', 0)
                if followers > 0:
                    return round((total_engagement / followers) * 100, 2)
            
            return 0.0
        except Exception:
            return 0.0
    
    def extract_tags_from_tweet(self, tweet_text: str, author_handle: str) -> List[str]:
        """Extract relevant tags from tweet content"""
        tags = set()
        text = tweet_text.lower()
        
        # AI/ML related keywords
        ai_keywords = [
            "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
            "neural network", "llm", "gpt", "chatgpt", "openai", "generative ai",
            "computer vision", "nlp", "natural language processing", "transformer",
            "prompt engineering", "fine-tuning", "rag", "embeddings"
        ]
        
        # Business/Enterprise keywords
        business_keywords = [
            "enterprise", "business", "startup", "funding", "investment", "vc",
            "saas", "platform", "api", "cloud", "aws", "azure", "gcp",
            "data", "analytics", "infrastructure", "security", "privacy"
        ]
        
        # Research/Technical keywords
        tech_keywords = [
            "research", "paper", "study", "breakthrough", "innovation",
            "open source", "github", "model", "dataset", "benchmark"
        ]
        
        all_keywords = ai_keywords + business_keywords + tech_keywords
        
        for keyword in all_keywords:
            if keyword in text:
                tags.add(keyword.replace(" ", "_"))
        
        # Add author-based tags
        tags.add(f"author_{author_handle.lower()}")
        
        # Extract hashtags
        import re
        hashtags = re.findall(r'#(\w+)', tweet_text)
        for hashtag in hashtags[:5]:  # Limit hashtags
            tags.add(f"hashtag_{hashtag.lower()}")
        
        return list(tags)[:15]  # Limit total tags
    
    def clean_tweet_content(self, tweet_text: str) -> str:
        """Clean and process tweet content"""
        if not tweet_text:
            return ""
        
        # Remove URLs
        import re
        tweet_text = re.sub(r'http\S+|www\S+|https\S+', '', tweet_text, flags=re.MULTILINE)
        
        # Clean up whitespace
        tweet_text = ' '.join(tweet_text.split())
        
        # Truncate if too long
        if len(tweet_text) > self.settings.CONTENT_EXCERPT_LENGTH:
            tweet_text = tweet_text[:self.settings.CONTENT_EXCERPT_LENGTH] + "..."
        
        return tweet_text.strip()
    
    def _extract_tweet_from_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract tweet data from timeline entry"""
        try:
            content = entry.get('content', {})
            if content.get('entryType') != 'TimelineTimelineItem':
                return None
            
            item_content = content.get('itemContent', {})
            if item_content.get('itemType') != 'TimelineTweet':
                return None
            
            tweet_results = item_content.get('tweet_results', {})
            result = tweet_results.get('result', {})
            
            if result.get('__typename') != 'Tweet':
                return None
            
            # Extract core tweet data
            legacy = result.get('legacy', {})
            core = result.get('core', {})
            user_results = core.get('user_results', {}).get('result', {})
            user_legacy = user_results.get('legacy', {})
            
            # Build simplified tweet structure
            tweet_data = {
                'id_str': result.get('rest_id'),
                'full_text': legacy.get('full_text', ''),
                'created_at': legacy.get('created_at', ''),
                'favorite_count': legacy.get('favorite_count', 0),
                'retweet_count': legacy.get('retweet_count', 0),
                'reply_count': legacy.get('reply_count', 0),
                'quote_count': legacy.get('quote_count', 0),
                'retweeted': legacy.get('retweeted', False),
                'in_reply_to_user_id': legacy.get('in_reply_to_user_id_str'),
                'user': {
                    'screen_name': user_legacy.get('screen_name', ''),
                    'name': user_legacy.get('name', ''),
                    'followers_count': user_legacy.get('followers_count', 0)
                }
            }
            
            return tweet_data
            
        except Exception as e:
            self.logger.debug(f"Failed to extract tweet from entry: {e}")
            return None
    
    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        """Get Twitter user ID by username using RapidAPI"""
        try:
            url = f"{self.base_url}/user-by-screen-name"
            params = {'username': username}
            headers = {
                'x-rapidapi-host': self.rapidapi_host,
                'x-rapidapi-key': self.rapidapi_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('result', {}).get('rest_id')
                    else:
                        self.logger.error(f"Failed to get user ID for @{username}: {response.status}")
                        return None
        except Exception as e:
            self.logger.error(f"Error getting user ID for @{username}: {e}")
            return None

    async def scrape_user_tweets(self, user_id: str, max_tweets: int = 20) -> List[Dict[str, Any]]:
        """Scrape tweets from a specific user using RapidAPI"""
        try:
            self.logger.info(f"Scraping tweets from user ID {user_id}")
            
            # Use user ID directly (no username lookup needed)
            
            # Make API request to get user tweets
            url = f"{self.base_url}/user-tweets"
            params = {
                'user': user_id,
                'count': min(max_tweets, 40)  # API limit
            }
            headers = {
                'x-rapidapi-host': self.rapidapi_host,
                'x-rapidapi-key': self.rapidapi_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status != 200:
                        self.logger.error(f"RapidAPI request failed for user ID {user_id}: {response.status}")
                        response_text = await response.text()
                        self.logger.debug(f"Response: {response_text}")
                        return []
                    
                    data = await response.json()
                    
            # Extract tweets from timeline structure
            timeline = data.get('result', {}).get('timeline', {})
            instructions = timeline.get('instructions', [])
            
            tweets_data = []
            for instruction in instructions:
                if instruction.get('type') == 'TimelinePinEntry':
                    # Pinned tweet
                    entry = instruction.get('entry', {})
                    if self._extract_tweet_from_entry(entry):
                        tweets_data.append(self._extract_tweet_from_entry(entry))
                elif instruction.get('type') == 'TimelineAddEntries':
                    # Regular timeline entries
                    entries = instruction.get('entries', [])
                    for entry in entries:
                        tweet_data = self._extract_tweet_from_entry(entry)
                        if tweet_data:
                            tweets_data.append(tweet_data)
            
            if not tweets_data:
                self.logger.warning(f"No tweets found for user ID {user_id}")
                return []
            
            self.logger.info(f"Retrieved {len(tweets_data)} raw tweets from user ID {user_id}")
            
            # Process tweets into our format
            processed_tweets = []
            for tweet_data in tweets_data:
                try:
                    # Skip retweets and replies for cleaner content
                    if tweet_data.get('retweeted', False) or tweet_data.get('in_reply_to_user_id'):
                        continue
                    
                    tweet_text = tweet_data.get('full_text', tweet_data.get('text', '')).strip()
                    if not tweet_text:
                        continue
                    
                    # Skip tweets that are too short
                    if len(tweet_text) < 50:
                        continue
                    
                    # Extract author info
                    user_info = tweet_data.get('user', {})
                    author_handle = user_info.get('screen_name', f'user_{user_id}')
                    author_name = user_info.get('name', f'User {user_id}')
                    
                    # Parse creation date
                    created_at = None
                    if 'created_at' in tweet_data:
                        try:
                            # Twitter date format: "Wed Oct 10 20:19:24 +0000 2018"
                            created_at = datetime.strptime(tweet_data['created_at'], '%a %b %d %H:%M:%S %z %Y')
                        except ValueError:
                            self.logger.debug(f"Could not parse date: {tweet_data.get('created_at')}")
                    
                    # Clean content
                    clean_content = self.clean_tweet_content(tweet_text)
                    
                    # Extract metrics
                    twitter_metrics = self.extract_twitter_metrics(tweet_data)
                    
                    # Extract tags
                    tags = self.extract_tags_from_tweet(tweet_text, author_handle)
                    
                    # Build article structure (username will be set later from database mapping)
                    article = {
                        'title': f"@{author_handle}: {clean_content[:100]}{'...' if len(clean_content) > 100 else ''}",
                        'url': f"https://twitter.com/{author_handle}/status/{tweet_data.get('id_str', tweet_data.get('id', ''))}",
                        'content_excerpt': clean_content,
                        'source_type': 'twitter',
                        'source_name': f"@{author_handle}",
                        'published_at': created_at,
                        'tags': tags,
                        'twitter_metrics': twitter_metrics,
                        'twitter_username': author_handle  # Will be updated with readable username later
                    }
                    
                    processed_tweets.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process tweet from user ID {user_id}: {e}")
                    continue
            
            self.logger.info(f"Processed {len(processed_tweets)} tweets from user ID {user_id}")
            return processed_tweets
            
        except Exception as e:
            self.logger.error(f"Error scraping user ID {user_id}: {e}")
            return []
    
    async def scrape_all_accounts(self) -> List[Dict[str, Any]]:
        """Main method called by data aggregator"""
        return await self.scrape_accounts()
    
    async def scrape_accounts(self) -> List[Dict[str, Any]]:
        """Scrape all configured Twitter accounts from database"""
        # Load Twitter sources from database
        sources = await self.get_twitter_sources()
        username_mapping = await self.get_username_mapping()
        
        if not sources:
            self.logger.warning("No active Twitter sources found in database")
            return []
        
        self.logger.info(f"Starting Twitter scraping for {len(sources)} accounts from database")
        
        all_tweets = []
        
        # Process accounts sequentially to avoid rate limiting
        for source in sources:
            user_id = source['identifier']
            source_name = source['name']
            
            try:
                # Calculate tweets per account based on total limit
                tweets_per_account = min(
                    self.settings.MAX_ARTICLES_PER_SOURCE // len(sources),
                    30  # Max 30 tweets per account
                )
                
                self.logger.info(f"Scraping {tweets_per_account} tweets from {source_name} (ID: {user_id})")
                tweets = await self.scrape_user_tweets(user_id, tweets_per_account)
                
                # Update each tweet with the correct username from mapping
                for tweet in tweets:
                    if user_id in username_mapping:
                        tweet['twitter_username'] = username_mapping[user_id]
                        tweet['source_name'] = f"@{username_mapping[user_id]}"
                        # Update title to use readable username
                        content = tweet['content_excerpt'][:100]
                        tweet['title'] = f"@{username_mapping[user_id]}: {content}{'...' if len(content) > 100 else ''}"
                
                all_tweets.extend(tweets)
                
                # Update last_processed timestamp for this source
                try:
                    self.db_client.client.table('content_sources').update({
                        'last_processed': datetime.now().isoformat()
                    }).eq('id', source['id']).execute()
                except Exception as update_error:
                    self.logger.warning(f"Failed to update last_processed for source {source_name}: {update_error}")
                
                # Add delay between accounts to avoid rate limiting
                if self.settings.REQUEST_DELAY_SECONDS > 0:
                    await asyncio.sleep(self.settings.REQUEST_DELAY_SECONDS * 2)
                
            except Exception as e:
                self.logger.error(f"Failed to scrape {source_name} (ID: {user_id}): {e}")
                continue
        
        # Sort tweets by engagement and relevance
        all_tweets.sort(key=lambda x: (
            x.get('twitter_metrics', {}).get('engagement_rate', 0),
            x.get('twitter_metrics', {}).get('likes', 0)
        ), reverse=True)
        
        # Limit total tweets
        if len(all_tweets) > self.settings.MAX_ARTICLES_PER_SOURCE:
            all_tweets = all_tweets[:self.settings.MAX_ARTICLES_PER_SOURCE]
        
        self.logger.info(f"Twitter scraping completed: {len(all_tweets)} tweets collected")
        return all_tweets
    
    def get_high_engagement_threshold(self, tweets: List[Dict[str, Any]]) -> float:
        """Calculate dynamic engagement threshold for filtering"""
        if not tweets:
            return 0.0
        
        engagement_rates = [
            tweet.get('twitter_metrics', {}).get('engagement_rate', 0)
            for tweet in tweets
        ]
        
        # Use 75th percentile as threshold
        engagement_rates.sort()
        if len(engagement_rates) >= 4:
            return engagement_rates[int(len(engagement_rates) * 0.75)]
        
        return 0.0
    
    def filter_high_quality_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter tweets based on engagement and quality metrics"""
        if not tweets:
            return []
        
        engagement_threshold = self.get_high_engagement_threshold(tweets)
        
        quality_tweets = []
        for tweet in tweets:
            metrics = tweet.get('twitter_metrics', {})
            
            # Check engagement rate
            if metrics.get('engagement_rate', 0) < engagement_threshold:
                continue
            
            # Check minimum interactions
            min_interactions = metrics.get('likes', 0) + metrics.get('retweets', 0)
            if min_interactions < 5:  # Minimum 5 interactions
                continue
            
            # Check content quality (avoid very short tweets)
            if len(tweet.get('content_excerpt', '')) < 100:
                continue
            
            quality_tweets.append(tweet)
        
        return quality_tweets


# CLI testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_twitter_scraper():
        settings = Settings()
        
        if not settings.APIFY_API_TOKEN:
            print("APIFY_API_TOKEN not set in environment")
            return
        
        scraper = TwitterScraper(settings)
        
        # Test single account
        tweets = await scraper.scrape_user_tweets("OpenAI", 5)
        
        print(f"Total tweets from OpenAI: {len(tweets)}")
        for i, tweet in enumerate(tweets[:2]):  # Show first 2
            print(f"\n--- Tweet {i+1} ---")
            print(f"Title: {tweet['title']}")
            print(f"URL: {tweet['url']}")
            print(f"Content: {tweet['content_excerpt'][:200]}...")
            print(f"Tags: {tweet['tags']}")
            print(f"Metrics: {tweet['twitter_metrics']}")
        
        # Test all accounts
        print("\n--- Testing all accounts ---")
        all_tweets = await scraper.scrape_accounts()
        print(f"Total tweets from all accounts: {len(all_tweets)}")
    
    # Run test
    asyncio.run(test_twitter_scraper())