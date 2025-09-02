"""
Supabase client for database operations
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
import asyncpg
from supabase import create_client, Client

from config.settings import Settings


class SupabaseClient:
    """Async Supabase client wrapper for database operations"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        self._pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
    
    async def init_connection_pool(self) -> None:
        """Initialize async connection pool for direct database operations"""
        if self._pool is None:
            # Extract project reference from Supabase URL
            # URL format: https://xpxrbgttnjjcfwmnosyc.supabase.co
            import re
            match = re.match(r'https://([^.]+)\.supabase\.co', self.settings.SUPABASE_URL)
            if not match:
                raise ValueError(f"Invalid Supabase URL format: {self.settings.SUPABASE_URL}")
            
            project_ref = match.group(1)
            # Construct PostgreSQL connection URL
            # Format: postgresql://postgres.[project-ref]:[password]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
            db_url = f"postgresql://postgres.{project_ref}:{self.settings.SUPABASE_SERVICE_KEY}@aws-0-us-west-1.pooler.supabase.com:5432/postgres"
            
            try:
                self._pool = await asyncpg.create_pool(
                    db_url,
                    min_size=5,
                    max_size=20,
                    command_timeout=60
                )
                self.logger.info("Database connection pool initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize connection pool: {e}")
                raise
    
    def _extract_db_password(self) -> str:
        """Extract database password from service key"""
        # In production, you'd store this separately or use environment variables
        # For now, we'll use the service key as a fallback
        return self.settings.SUPABASE_SERVICE_KEY
    
    async def close_pool(self) -> None:
        """Close the connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    async def execute_query(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        if not self._pool:
            await self.init_connection_pool()
        
        async with self._pool.acquire() as conn:
            try:
                if params:
                    rows = await conn.fetch(query, *params)
                else:
                    rows = await conn.fetch(query)
                
                return [dict(row) for row in rows]
            except Exception as e:
                self.logger.error(f"Query execution failed: {e}")
                self.logger.error(f"Query: {query}")
                self.logger.error(f"Params: {params}")
                raise
    
    async def execute_command(self, command: str, params: List[Any] = None) -> int:
        """Execute INSERT/UPDATE/DELETE command and return affected rows"""
        if not self._pool:
            await self.init_connection_pool()
        
        async with self._pool.acquire() as conn:
            try:
                if params:
                    result = await conn.execute(command, *params)
                else:
                    result = await conn.execute(command)
                
                # Extract number from result string like "INSERT 0 5"
                return int(result.split()[-1])
            except Exception as e:
                self.logger.error(f"Command execution failed: {e}")
                self.logger.error(f"Command: {command}")
                self.logger.error(f"Params: {params}")
                raise
    
    async def insert_article(self, article_data: Dict[str, Any]) -> str:
        """Insert a single article and return its ID"""
        query = """
        INSERT INTO articles (
            title, url, content_excerpt, source_type, source_name,
            published_at, week_start_date, relevance_score, 
            business_impact_score, tags, twitter_metrics
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id
        """
        
        params = [
            article_data['title'],
            article_data.get('url'),
            article_data.get('content_excerpt'),
            article_data['source_type'],
            article_data['source_name'],
            article_data.get('published_at'),
            article_data['week_start_date'],
            article_data.get('relevance_score'),
            article_data.get('business_impact_score'),
            article_data.get('tags', []),
            article_data.get('twitter_metrics')
        ]
        
        result = await self.execute_query(query, params)
        return str(result[0]['id'])
    
    async def bulk_insert_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Insert multiple articles efficiently"""
        if not articles:
            return 0
        
        if not self._pool:
            await self.init_connection_pool()
        
        async with self._pool.acquire() as conn:
            try:
                # Prepare data for bulk insert
                records = []
                for article in articles:
                    records.append((
                        article['title'],
                        article.get('url'),
                        article.get('content_excerpt'),
                        article['source_type'],
                        article['source_name'],
                        article.get('published_at'),
                        article['week_start_date'],
                        article.get('relevance_score'),
                        article.get('business_impact_score'),
                        article.get('tags', []),
                        article.get('twitter_metrics')
                    ))
                
                query = """
                INSERT INTO articles (
                    title, url, content_excerpt, source_type, source_name,
                    published_at, week_start_date, relevance_score,
                    business_impact_score, tags, twitter_metrics
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (url) DO NOTHING
                """
                
                result = await conn.executemany(query, records)
                inserted_count = len(records) - result.count("INSERT 0 0")
                
                self.logger.info(f"Bulk inserted {inserted_count} articles")
                return inserted_count
                
            except Exception as e:
                self.logger.error(f"Bulk insert failed: {e}")
                raise
    
    async def get_articles_by_week(self, week_start: date, limit: int = 100) -> List[Dict[str, Any]]:
        """Get articles for a specific week"""
        query = """
        SELECT * FROM articles 
        WHERE week_start_date = $1 
        ORDER BY relevance_score DESC, scraped_at DESC 
        LIMIT $2
        """
        return await self.execute_query(query, [week_start, limit])
    
    async def get_current_week_articles(self, min_relevance: float = 50, limit: int = 100) -> List[Dict[str, Any]]:
        """Get current week articles above relevance threshold"""
        query = """
        SELECT * FROM current_week_articles 
        WHERE relevance_score >= $1 
        LIMIT $2
        """
        return await self.execute_query(query, [min_relevance, limit])
    
    async def search_articles_by_content(self, search_term: str, current_week_only: bool = True, limit: int = 20) -> List[Dict[str, Any]]:
        """Search articles by title and content"""
        if current_week_only:
            query = """
            SELECT * FROM articles 
            WHERE week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
              AND (title ILIKE $1 OR content_excerpt ILIKE $1)
            ORDER BY relevance_score DESC 
            LIMIT $2
            """
        else:
            query = """
            SELECT * FROM articles 
            WHERE (title ILIKE $1 OR content_excerpt ILIKE $1)
            ORDER BY scraped_at DESC, relevance_score DESC 
            LIMIT $2
            """
        
        search_pattern = f"%{search_term}%"
        return await self.execute_query(query, [search_pattern, limit])
    
    async def get_articles_by_tags(self, tags: List[str], current_week_only: bool = True, limit: int = 20) -> List[Dict[str, Any]]:
        """Get articles containing any of the specified tags"""
        if current_week_only:
            query = """
            SELECT * FROM articles 
            WHERE week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
              AND tags && $1
            ORDER BY relevance_score DESC 
            LIMIT $2
            """
        else:
            query = """
            SELECT * FROM articles 
            WHERE tags && $1
            ORDER BY scraped_at DESC, relevance_score DESC 
            LIMIT $2
            """
        
        return await self.execute_query(query, [tags, limit])
    
    async def get_articles_by_source_type(self, source_type: str, current_week_only: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
        """Get articles by source type"""
        if current_week_only:
            query = """
            SELECT * FROM articles 
            WHERE week_start_date = DATE_TRUNC('week', CURRENT_DATE)::DATE
              AND source_type = $1
            ORDER BY relevance_score DESC 
            LIMIT $2
            """
        else:
            query = """
            SELECT * FROM articles 
            WHERE source_type = $1
            ORDER BY scraped_at DESC, relevance_score DESC 
            LIMIT $2
            """
        
        return await self.execute_query(query, [source_type, limit])
    
    async def select_articles_for_newsletter(self, article_ids: List[str], priority_order: Optional[List[int]] = None, notes: Optional[List[str]] = None) -> int:
        """Mark articles as selected for newsletter"""
        if not self._pool:
            await self.init_connection_pool()
        
        updated_count = 0
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                for i, article_id in enumerate(article_ids):
                    priority = priority_order[i] if priority_order and i < len(priority_order) else None
                    note = notes[i] if notes and i < len(notes) else None
                    
                    query = """
                    UPDATE articles 
                    SET selected_for_newsletter = TRUE,
                        newsletter_priority = $2,
                        curator_notes = $3,
                        updated_at = NOW()
                    WHERE id = $1::uuid
                    """
                    
                    result = await conn.execute(query, article_id, priority, note)
                    if "UPDATE 1" in result:
                        updated_count += 1
        
        self.logger.info(f"Selected {updated_count} articles for newsletter")
        return updated_count
    
    async def get_selected_articles(self) -> List[Dict[str, Any]]:
        """Get articles selected for current week's newsletter"""
        query = """
        SELECT * FROM newsletter_articles
        """
        return await self.execute_query(query)
    
    async def get_weekly_stats(self, week_start: Optional[date] = None) -> Dict[str, Any]:
        """Get statistics for a specific week"""
        if week_start is None:
            query = """
            SELECT 
                COUNT(*) as total_articles,
                AVG(relevance_score) as avg_relevance,
                COUNT(*) FILTER (WHERE selected_for_newsletter = TRUE) as selected_count,
                COUNT(*) FILTER (WHERE source_type = 'rss') as rss_count,
                COUNT(*) FILTER (WHERE source_type = 'twitter') as twitter_count,
                COUNT(*) FILTER (WHERE source_type = 'gmail_newsletter') as newsletter_count
            FROM current_week_articles
            """
            params = []
        else:
            query = """
            SELECT 
                COUNT(*) as total_articles,
                AVG(relevance_score) as avg_relevance,
                COUNT(*) FILTER (WHERE selected_for_newsletter = TRUE) as selected_count,
                COUNT(*) FILTER (WHERE source_type = 'rss') as rss_count,
                COUNT(*) FILTER (WHERE source_type = 'twitter') as twitter_count,
                COUNT(*) FILTER (WHERE source_type = 'gmail_newsletter') as newsletter_count
            FROM articles
            WHERE week_start_date = $1
            """
            params = [week_start]
        
        result = await self.execute_query(query, params)
        return result[0] if result else {}
    
    async def update_source_performance(self, source_name: str, success: bool, avg_relevance: Optional[float] = None) -> None:
        """Update source performance metrics"""
        if success:
            update_field = "success_count = success_count + 1"
        else:
            update_field = "failure_count = failure_count + 1"
        
        query = f"""
        UPDATE content_sources 
        SET {update_field},
            last_processed = NOW(),
            average_relevance_score = COALESCE($2, average_relevance_score)
        WHERE name = $1
        """
        
        await self.execute_command(query, [source_name, avg_relevance])
    
    async def cleanup_old_articles(self, retention_weeks: int) -> int:
        """Remove articles older than retention period"""
        query = """
        DELETE FROM articles 
        WHERE week_start_date < CURRENT_DATE - INTERVAL '%s weeks'
        """ % retention_weeks
        
        return await self.execute_command(query)
    
    async def log_processing_run(self, process_type: str, status: str, 
                               articles_processed: int = 0, error_message: str = None, 
                               details: Dict[str, Any] = None) -> None:
        """Log a processing run"""
        query = """
        INSERT INTO processing_logs 
        (process_type, status, articles_processed, error_message, details, completed_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        completed_at = datetime.now() if status in ['completed', 'failed'] else None
        
        await self.execute_command(query, [
            process_type, status, articles_processed, 
            error_message, details, completed_at
        ])