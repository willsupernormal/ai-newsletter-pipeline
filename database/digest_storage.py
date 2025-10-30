"""
Database storage for daily digests and multi-source content
"""

import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional, Tuple
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
    ) -> List[Dict[str, Any]]:
        """
        Store selected articles in digest_articles table with full AI enrichment
        
        Returns:
            articles_with_ids: List of articles with database IDs
        """
        
        try:
            articles_with_ids = []
            
            for i, article in enumerate(selected_articles):
                # Get corresponding AI analysis from article_summaries
                ai_data = article_summaries[i] if article_summaries and i < len(article_summaries) else {}
                
                # Prepare data for digest_articles table
                article_data = {
                    # Basic fields
                    'title': article['title'],
                    'url': article['url'],
                    'source_name': article['source_name'],
                    'source_type': article['source_type'],
                    'published_at': article.get('published_date'),
                    'scraped_at': datetime.now().isoformat(),
                    'digest_date': digest_date.isoformat() if hasattr(digest_date, 'isoformat') else str(digest_date),
                    
                    # Slack/Airtable tracking
                    'posted_to_slack': False,
                    'added_to_airtable': False,
                    
                    # AI-generated fields (from article_summaries JSON structure)
                    'detailed_summary': ai_data.get('detailed_summary', ''),
                    'business_impact': ai_data.get('business_impact', ''),  # Includes strategic context
                    'key_quotes': ai_data.get('key_quotes', []),
                    'specific_data': ai_data.get('specific_data', []),
                    'companies_mentioned': ai_data.get('companies_mentioned', [])
                }
                
                # Insert into digest_articles table (upsert to handle duplicates)
                response = self.db_client.client.table('digest_articles')\
                    .upsert(article_data, on_conflict='url,digest_date')\
                    .execute()
                
                if response.data:
                    article_id = str(response.data[0]['id'])
                    article_with_id = article.copy()
                    article_with_id['id'] = article_id
                    articles_with_ids.append(article_with_id)
                    
                    self.logger.info(f"✓ Stored digest article: {article['title'][:50]}...")
                else:
                    self.logger.error(f"Failed to store article: {article['title']}")
            
            self.logger.info(f"Stored {len(articles_with_ids)} articles in digest_articles table")
            return articles_with_ids
            
        except Exception as e:
            self.logger.error(f"Failed to store digest articles: {e}")
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
    
    async def mark_posted_to_slack(self, article_ids: List[str], message_ts: str = None):
        """Mark articles as posted to Slack"""
        try:
            for article_id in article_ids:
                update_data = {'posted_to_slack': True}
                if message_ts:
                    update_data['slack_message_ts'] = message_ts
                
                self.db_client.client.table('digest_articles')\
                    .update(update_data)\
                    .eq('id', article_id)\
                    .execute()
            
            self.logger.info(f"Marked {len(article_ids)} articles as posted to Slack")
        except Exception as e:
            self.logger.error(f"Failed to mark articles as posted: {e}")
    
    async def mark_added_to_airtable(self, article_id: str, airtable_record_id: str):
        """Mark article as added to Airtable"""
        try:
            self.db_client.client.table('digest_articles')\
                .update({
                    'added_to_airtable': True,
                    'airtable_record_id': airtable_record_id
                })\
                .eq('id', article_id)\
                .execute()
            
            self.logger.info(f"Marked article {article_id} as added to Airtable: {airtable_record_id}")
        except Exception as e:
            self.logger.error(f"Failed to mark article as added to Airtable: {e}")
    
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
