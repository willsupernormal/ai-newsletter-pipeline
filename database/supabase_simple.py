"""
Simplified Supabase client using the official SDK
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from supabase import create_client, Client

from config.settings import Settings


class SimpleSupabaseClient:
    """Simplified Supabase client using the official SDK"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        self.logger = logging.getLogger(__name__)
    
    async def execute_query(self, table_name: str, operation: str = 'select', **kwargs) -> List[Dict[str, Any]]:
        """Execute a query using Supabase SDK"""
        try:
            table = self.client.table(table_name)
            
            if operation == 'select':
                query = table.select(kwargs.get('columns', '*'))
                
                # Add filters
                if 'eq' in kwargs:
                    for field, value in kwargs['eq'].items():
                        query = query.eq(field, value)
                if 'limit' in kwargs:
                    query = query.limit(kwargs['limit'])
                if 'order' in kwargs:
                    query = query.order(kwargs['order']['column'], 
                                      desc=kwargs['order'].get('desc', False))
                
                response = query.execute()
                return response.data if response.data else []
            
            return []
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    async def get_recent_articles(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get articles from the last N days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        response = self.client.table('articles').select('*').gte('scraped_at', cutoff_date).execute()
        return response.data
    
    async def get_article_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Get article by URL"""
        response = self.client.table('articles').select('*').eq('url', url).execute()
        return response.data[0] if response.data else None
    
    async def insert_article(self, article_data: Dict[str, Any]) -> str:
        """Insert a single article and return its ID"""
        try:
            response = self.client.table('articles').insert(article_data).execute()
            if response.data:
                return str(response.data[0]['id'])
            raise Exception("Insert returned no data")
        except Exception as e:
            self.logger.error(f"Failed to insert article: {e}")
            raise
    
    async def bulk_insert_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Insert multiple articles efficiently"""
        if not articles:
            return 0
        
        try:
            # Supabase SDK handles bulk inserts
            response = self.client.table('articles').upsert(
                articles, 
                on_conflict='url'  # Don't insert duplicates
            ).execute()
            
            inserted_count = len(response.data) if response.data else 0
            self.logger.info(f"Bulk inserted {inserted_count} articles")
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"Bulk insert failed: {e}")
            # Try inserting one by one as fallback
            inserted = 0
            for article in articles:
                try:
                    await self.insert_article(article)
                    inserted += 1
                except:
                    pass
            return inserted
    
    async def get_weekly_stats(self, week_start: Optional[date] = None) -> Dict[str, Any]:
        """Get statistics for a specific week"""
        try:
            if week_start:
                response = self.client.table('articles')\
                    .select('*')\
                    .eq('week_start_date', week_start.isoformat())\
                    .execute()
            else:
                # Current week
                from datetime import timedelta
                today = datetime.now().date()
                current_week = today - timedelta(days=today.weekday())
                response = self.client.table('articles')\
                    .select('*')\
                    .eq('week_start_date', current_week.isoformat())\
                    .execute()
            
            articles = response.data if response.data else []
            
            # Calculate stats
            total = len(articles)
            if total == 0:
                return {
                    'total_articles': 0,
                    'avg_relevance': 0,
                    'selected_count': 0,
                    'rss_count': 0,
                    'twitter_count': 0,
                    'newsletter_count': 0
                }
            
            relevance_scores = [a['relevance_score'] for a in articles if a.get('relevance_score')]
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
            
            return {
                'total_articles': total,
                'avg_relevance': avg_relevance,
                'selected_count': sum(1 for a in articles if a.get('selected_for_newsletter')),
                'rss_count': sum(1 for a in articles if a.get('source_type') == 'rss'),
                'twitter_count': sum(1 for a in articles if a.get('source_type') == 'twitter'),
                'newsletter_count': sum(1 for a in articles if a.get('source_type') == 'gmail_newsletter')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly stats: {e}")
            return {}