"""
Database storage for daily digests and multi-source content
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

from database.supabase_simple import SimpleSupabaseClient
from config.settings import Settings

class DigestStorage:
    """Handles storage of daily digests and selected articles"""
    
    def __init__(self, settings: Settings):
        self.db_client = SimpleSupabaseClient(settings)
        self.logger = logging.getLogger(__name__)
    
    async def store_daily_digest(
        self, 
        digest_date: date,
        summary_text: str,
        key_insights: List[str],
        selected_articles: List[Dict[str, Any]],
        total_processed: int,
        ai_reasoning: str = "",
        article_summaries: List[Dict[str, Any]] = None
    ) -> str:
        """Store daily digest and return digest ID"""
        
        try:
            # First, store all articles (both selected and non-selected)
            article_ids = []
            for article in selected_articles:
                # Add digest metadata and convert datetime objects
                article_data = {
                    'title': article['title'],
                    'content_excerpt': article.get('content_excerpt', ''),
                    'url': article['url'],
                    'source_name': article['source_name'],
                    'source_type': article['source_type'],
                    'published_at': article.get('published_date'),
                    'week_start_date': self._get_week_start(digest_date).isoformat(),
                    'tags': article.get('tags', []),
                    'key_themes': article.get('key_themes', []),
                    'relevance_score': article.get('relevance_score', 60.0),
                    'business_impact_score': article.get('business_impact_score', 55.0),
                    'selected_for_digest': True,
                    'selected_for_newsletter': False,
                    'scraped_at': datetime.now().isoformat(),
                    
                    # Enhanced context fields (NEW)
                    'ai_summary': article.get('ai_summary', ''),
                    'ai_summary_short': article.get('ai_summary_short', ''),
                    'key_quotes': article.get('key_quotes', []),
                    'key_metrics': article.get('key_metrics', []),
                    'why_it_matters': article.get('why_it_matters', ''),
                    'primary_theme': article.get('primary_theme', ''),
                    'content_type': article.get('content_type', 'news')
                }
                
                # Add Twitter-specific fields if present
                if article.get('source_type') == 'twitter':
                    article_data['twitter_metrics'] = article.get('twitter_metrics', {})
                
                # Store article and get ID (use upsert to handle duplicates)
                try:
                    article_id = await self.db_client.insert_article(article_data)
                    article_ids.append(article_id)
                except Exception as e:
                    if 'duplicate key' in str(e):
                        # Article already exists, find its ID
                        existing = await self.db_client.get_article_by_url(article_data['url'])
                        if existing:
                            article_ids.append(existing['id'])
                            self.logger.debug(f"Using existing article ID for {article_data['url']}")
                        else:
                            self.logger.error(f"Could not find existing article for {article_data['url']}")
                            raise
                    else:
                        raise
            
            # Create digest record
            digest_date_str = digest_date.isoformat() if hasattr(digest_date, 'isoformat') else str(digest_date)
            digest_data = {
                'digest_date': digest_date_str,
                'summary_text': summary_text,
                'key_insights': key_insights,
                'selected_article_ids': article_ids,
                'total_articles_processed': total_processed,
                'ai_reasoning': ai_reasoning,
                'article_summaries': article_summaries or []
            }
            
            # Check if digest already exists for this date
            existing_digest = await self.get_daily_digest(digest_date)
            is_update = existing_digest is not None
            
            # Store digest (upsert: insert or update if exists)
            response = self.db_client.client.table('daily_digests')\
                .upsert(digest_data, on_conflict='digest_date')\
                .execute()
            
            if response.data:
                digest_id = str(response.data[0]['id'])
                
                # Update articles with digest reference
                for article_id in article_ids:
                    self.db_client.client.table('articles')\
                        .update({'daily_digest_id': digest_id})\
                        .eq('id', article_id)\
                        .execute()
                
                action = "Updated" if is_update else "Created"
                self.logger.info(f"{action} daily digest {digest_id} with {len(article_ids)} articles")
                return digest_id
            
            raise Exception("Insert returned no data")
            
        except Exception as e:
            self.logger.error(f"Failed to store daily digest: {e}")
            raise
    
    async def get_daily_digest(self, digest_date: date) -> Optional[Dict[str, Any]]:
        """Retrieve daily digest for a specific date"""
        try:
            response = self.db_client.client.table('daily_digests')\
                .select('*')\
                .eq('digest_date', digest_date.isoformat())\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get daily digest: {e}")
            return None
    
    async def get_digest_articles(self, digest_id: str) -> List[Dict[str, Any]]:
        """Get all articles associated with a digest"""
        try:
            response = self.db_client.client.table('articles')\
                .select('*')\
                .eq('daily_digest_id', digest_id)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            self.logger.error(f"Failed to get digest articles: {e}")
            return []
    
    async def store_all_articles(
        self, 
        articles: List[Dict[str, Any]], 
        digest_date: date,
        selected_article_urls: List[str] = None
    ) -> int:
        """Store all articles (selected and non-selected) for the day"""
        
        if not articles:
            return 0
        
        selected_urls = set(selected_article_urls or [])
        week_start = self._get_week_start(digest_date)
        
        # Prepare articles for storage
        db_articles = []
        for article in articles:
            db_article = {
                'title': article['title'],
                'content_excerpt': article.get('content_excerpt', ''),
                'url': article['url'],
                'source_name': article['source_name'],
                'source_type': article['source_type'],
                'published_at': article.get('published_date'),
                'week_start_date': week_start.isoformat(),
                'tags': article.get('tags', []),
                'key_themes': article.get('key_themes', []),
                'relevance_score': article.get('relevance_score', 50.0),
                'business_impact_score': article.get('business_impact_score', 50.0),
                'selected_for_digest': article['url'] in selected_urls,
                'selected_for_newsletter': False,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Add Twitter-specific fields
            if article.get('source_type') == 'twitter':
                db_article['twitter_metrics'] = article.get('twitter_metrics', {})
            
            db_articles.append(db_article)
        
        # Bulk insert
        stored_count = await self.db_client.bulk_insert_articles(db_articles)
        self.logger.info(f"Stored {stored_count} articles for {digest_date}")
        
        return stored_count
    
    def _get_week_start(self, target_date) -> date:
        """Get the Monday of the week containing the target date"""
        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date).date()
        elif isinstance(target_date, datetime):
            target_date = target_date.date()
        from datetime import timedelta
        return target_date - timedelta(days=target_date.weekday())
    
    async def get_recent_digests(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent daily digests"""
        try:
            from datetime import timedelta
            cutoff_date = (date.today() - timedelta(days=days)).isoformat()
            
            response = self.db_client.client.table('daily_digests')\
                .select('*')\
                .gte('digest_date', cutoff_date)\
                .order('digest_date', desc=True)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            self.logger.error(f"Failed to get recent digests: {e}")
            return []
