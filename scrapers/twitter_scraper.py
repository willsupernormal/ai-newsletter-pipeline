"""
Twitter scraper using Apify service
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from apify_client import ApifyClient

from config.settings import Settings


class TwitterScraper:
    """Twitter scraper using Apify service"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.client = ApifyClient(settings.APIFY_API_TOKEN)
        
        if settings.TWITTER_SERVICE != "apify":
            self.logger.warning(f"Twitter service set to {settings.TWITTER_SERVICE}, but ApifyTwitterScraper requires 'apify'")
    
    def extract_twitter_metrics(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Twitter engagement metrics"""
        try:
            return {
                'retweets': tweet_data.get('retweetCount', 0),
                'likes': tweet_data.get('likeCount', 0),
                'replies': tweet_data.get('replyCount', 0),
                'quotes': tweet_data.get('quoteCount', 0),
                'views': tweet_data.get('viewCount', 0),
                'bookmarks': tweet_data.get('bookmarkCount', 0),
                'engagement_rate': self.calculate_engagement_rate(tweet_data),
                'user_followers': tweet_data.get('author', {}).get('followers', 0),
                'tweet_id': tweet_data.get('id'),
                'conversation_id': tweet_data.get('conversationId')
            }
        except Exception as e:
            self.logger.warning(f"Failed to extract Twitter metrics: {e}")
            return {}
    
    def calculate_engagement_rate(self, tweet_data: Dict[str, Any]) -> float:
        """Calculate engagement rate for a tweet"""
        try:
            likes = tweet_data.get('likeCount', 0)
            retweets = tweet_data.get('retweetCount', 0)
            replies = tweet_data.get('replyCount', 0)
            quotes = tweet_data.get('quoteCount', 0)
            views = tweet_data.get('viewCount', 0)
            
            total_engagement = likes + retweets + replies + quotes
            
            if views > 0:
                return round((total_engagement / views) * 100, 2)
            elif total_engagement > 0:
                # Fallback calculation using follower count
                followers = tweet_data.get('author', {}).get('followers', 0)
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
    
    async def scrape_user_tweets(self, username: str, max_tweets: int = 20) -> List[Dict[str, Any]]:
        """Scrape tweets from a specific user using Apify"""
        try:
            self.logger.info(f"Scraping tweets from @{username}")
            
            # Configure Apify actor input
            actor_input = {
                "handles": [username],
                "tweetsDesired": max_tweets,
                "addUserInfo": True,
                "includeSearchTerms": False,
                "onlyImage": False,
                "onlyQuote": False,
                "onlyTwitterBlue": False,
                "onlyVerified": False,
                "start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),  # Last 7 days
                "end": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Run the actor
            self.logger.debug(f"Running Apify actor with input: {actor_input}")
            run = self.client.actor(self.settings.APIFY_ACTOR_ID).call(run_input=actor_input)
            
            # Check if run was successful
            if run.get('status') != 'SUCCEEDED':
                self.logger.error(f"Apify actor run failed for @{username}: {run.get('status')}")
                return []
            
            # Get the results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
            
            self.logger.info(f"Retrieved {len(results)} raw results from @{username}")
            
            # Process tweets into our format
            processed_tweets = []
            for tweet_data in results:
                try:
                    # Skip retweets and replies for cleaner content
                    if tweet_data.get('isRetweet', False) or tweet_data.get('inReplyToUser'):
                        continue
                    
                    tweet_text = tweet_data.get('text', '').strip()
                    if not tweet_text:
                        continue
                    
                    # Skip tweets that are too short or likely spam
                    if len(tweet_text) < 50:
                        continue
                    
                    # Extract author info
                    author = tweet_data.get('author', {})
                    author_handle = author.get('userName', username)
                    author_name = author.get('name', username)
                    
                    # Parse creation date
                    created_at = None
                    if 'createdAt' in tweet_data:
                        try:
                            created_at = datetime.fromisoformat(tweet_data['createdAt'].replace('Z', '+00:00'))
                        except ValueError:
                            self.logger.debug(f"Could not parse date: {tweet_data.get('createdAt')}")
                    
                    # Clean content
                    clean_content = self.clean_tweet_content(tweet_text)
                    
                    # Extract metrics
                    twitter_metrics = self.extract_twitter_metrics(tweet_data)
                    
                    # Extract tags
                    tags = self.extract_tags_from_tweet(tweet_text, author_handle)
                    
                    # Build article structure
                    article = {
                        'title': f"@{author_handle}: {clean_content[:100]}{'...' if len(clean_content) > 100 else ''}",
                        'url': tweet_data.get('url', f"https://twitter.com/{author_handle}/status/{tweet_data.get('id', '')}"),
                        'content_excerpt': clean_content,
                        'source_type': 'twitter',
                        'source_name': f"@{author_handle}",
                        'published_at': created_at,
                        'tags': tags,
                        'twitter_metrics': twitter_metrics
                    }
                    
                    processed_tweets.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process tweet from @{username}: {e}")
                    continue
            
            self.logger.info(f"Processed {len(processed_tweets)} tweets from @{username}")
            return processed_tweets
            
        except Exception as e:
            self.logger.error(f"Error scraping @{username}: {e}")
            return []
    
    async def scrape_accounts(self) -> List[Dict[str, Any]]:
        """Scrape all configured Twitter accounts"""
        accounts = self.settings.twitter_accounts_list
        self.logger.info(f"Starting Twitter scraping for {len(accounts)} accounts")
        
        all_tweets = []
        
        # Process accounts sequentially to avoid rate limiting
        for account in accounts:
            try:
                # Calculate tweets per account based on total limit
                tweets_per_account = min(
                    self.settings.MAX_ARTICLES_PER_SOURCE // len(accounts),
                    30  # Max 30 tweets per account
                )
                
                tweets = await self.scrape_user_tweets(account, tweets_per_account)
                all_tweets.extend(tweets)
                
                # Add delay between accounts to be respectful to Apify
                if self.settings.REQUEST_DELAY_SECONDS > 0:
                    await asyncio.sleep(self.settings.REQUEST_DELAY_SECONDS * 2)  # Longer delay for Twitter
                
            except Exception as e:
                self.logger.error(f"Failed to scrape @{account}: {e}")
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