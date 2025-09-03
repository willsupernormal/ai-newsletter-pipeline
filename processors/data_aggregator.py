"""
Data aggregation system for RSS + Twitter content
Handles multi-source data collection and normalization
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config.settings import Settings
from scrapers.rss_scraper import RSScraper
from scrapers.twitter_scraper import TwitterScraper
from processors.content_processor import ContentProcessor
from processors.deduplicator import Deduplicator

@dataclass
class AggregatedContent:
    """Container for aggregated multi-source content"""
    articles: List[Dict[str, Any]]
    rss_count: int
    twitter_count: int
    total_count: int
    processing_time: float

class DataAggregator:
    """Aggregates content from RSS and Twitter sources"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.content_processor = ContentProcessor()
        self.deduplicator = Deduplicator()
        self.logger = logging.getLogger(__name__)
    
    async def collect_rss_content(self) -> List[Dict[str, Any]]:
        """Collect and process RSS content"""
        self.logger.info("Collecting RSS content")
        
        try:
            async with RSScraper(self.settings) as rss_scraper:
                articles = await rss_scraper.scrape_all_feeds()
            
            # Process articles
            processed_articles = []
            for article in articles:
                try:
                    processed = self.content_processor.process_article(article)
                    processed['source_type'] = 'rss'
                    processed_articles.append(processed)
                except Exception as e:
                    self.logger.error(f"Failed to process RSS article: {e}")
            
            self.logger.info(f"Collected {len(processed_articles)} RSS articles")
            return processed_articles
            
        except Exception as e:
            self.logger.error(f"RSS collection failed: {e}")
            return []
    
    async def collect_twitter_content(self) -> List[Dict[str, Any]]:
        """Collect and process Twitter content"""
        self.logger.info("Collecting Twitter content")
        
        try:
            twitter_scraper = TwitterScraper(self.settings)
            articles = await twitter_scraper.scrape_all_accounts()
            
            # Process articles
            processed_articles = []
            for article in articles:
                try:
                    processed = self.content_processor.process_article(article)
                    processed['source_type'] = 'twitter'
                    # Preserve Twitter-specific metrics
                    if 'twitter_metrics' in article:
                        processed['twitter_metrics'] = article['twitter_metrics']
                    processed_articles.append(processed)
                except Exception as e:
                    self.logger.error(f"Failed to process Twitter article: {e}")
            
            self.logger.info(f"Collected {len(processed_articles)} Twitter articles")
            return processed_articles
            
        except Exception as e:
            self.logger.error(f"Twitter collection failed: {e}")
            return []
    
    def _normalize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize articles from different sources for consistent processing"""
        normalized = []
        
        for article in articles:
            # Ensure all required fields exist
            normalized_article = {
                'title': article.get('title', ''),
                'content_excerpt': article.get('content_excerpt', ''),
                'url': article.get('url', ''),
                'source_name': article.get('source_name', ''),
                'source_type': article.get('source_type', 'unknown'),
                'published_date': article.get('published_date'),
                'tags': article.get('tags', []),
                'word_count': article.get('word_count', 0),
                'processed_at': article.get('processed_at', datetime.now().isoformat())
            }
            
            # Add source-specific fields
            if article.get('source_type') == 'twitter':
                normalized_article['twitter_metrics'] = article.get('twitter_metrics', {})
            
            # Add aggregation metadata
            normalized_article['aggregated_at'] = datetime.now().isoformat()
            
            normalized.append(normalized_article)
        
        return normalized
    
    async def aggregate_all_content(self) -> AggregatedContent:
        """Collect and aggregate content from all sources"""
        start_time = datetime.now()
        self.logger.info("Starting multi-source content aggregation")
        
        # Collect from all sources concurrently
        rss_task = self.collect_rss_content()
        twitter_task = self.collect_twitter_content()
        
        rss_articles, twitter_articles = await asyncio.gather(
            rss_task, twitter_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(rss_articles, Exception):
            self.logger.error(f"RSS collection failed: {rss_articles}")
            rss_articles = []
        if isinstance(twitter_articles, Exception):
            self.logger.error(f"Twitter collection failed: {twitter_articles}")
            twitter_articles = []
        
        # Combine all articles
        all_articles = rss_articles + twitter_articles
        
        # Normalize article format
        normalized_articles = self._normalize_articles(all_articles)
        
        # Remove duplicates across sources
        unique_articles = await self.deduplicator.remove_duplicates(normalized_articles)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = AggregatedContent(
            articles=unique_articles,
            rss_count=len(rss_articles),
            twitter_count=len(twitter_articles),
            total_count=len(unique_articles),
            processing_time=processing_time
        )
        
        self.logger.info(f"Aggregation complete: {result.rss_count} RSS + {result.twitter_count} Twitter = {result.total_count} unique articles in {processing_time:.1f}s")
        
        return result
    
    async def get_daily_content(self, target_date: Optional[date] = None) -> AggregatedContent:
        """Get aggregated content for a specific day"""
        if target_date is None:
            target_date = date.today()
        
        self.logger.info(f"Aggregating content for {target_date}")
        
        # For now, collect all recent content
        # In production, you might want to filter by date
        content = await self.aggregate_all_content()
        
        # Filter articles to target date (if published_date available)
        filtered_articles = []
        for article in content.articles:
            published_date = article.get('published_date')
            if published_date:
                try:
                    if isinstance(published_date, str):
                        pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00')).date()
                    else:
                        pub_date = published_date.date() if hasattr(published_date, 'date') else published_date
                    
                    # Include articles from target date and previous day (for timezone differences)
                    if pub_date >= target_date - timedelta(days=1):
                        filtered_articles.append(article)
                except:
                    # Include articles with unparseable dates
                    filtered_articles.append(article)
            else:
                # Include articles without dates
                filtered_articles.append(article)
        
        return AggregatedContent(
            articles=filtered_articles,
            rss_count=sum(1 for a in filtered_articles if a['source_type'] == 'rss'),
            twitter_count=sum(1 for a in filtered_articles if a['source_type'] == 'twitter'),
            total_count=len(filtered_articles),
            processing_time=content.processing_time
        )
