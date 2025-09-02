"""
Weekly content management and cycling
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

from database.supabase_client import SupabaseClient
from config.settings import Settings


class WeeklyManager:
    """Manages weekly content cycles and organization"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db = SupabaseClient(settings)
        self.logger = logging.getLogger(__name__)
    
    def get_current_week_start(self) -> date:
        """Get the start of current week (Monday)"""
        today = datetime.now().date()
        return today - timedelta(days=today.weekday())
    
    def get_week_start_for_date(self, target_date: date) -> date:
        """Get week start for any date"""
        return target_date - timedelta(days=target_date.weekday())
    
    async def initialize_current_week(self) -> date:
        """Initialize current week cycle if it doesn't exist"""
        current_week_start = self.get_current_week_start()
        
        # Check if week already exists
        existing_week = await self.db.execute_query(
            "SELECT * FROM weekly_cycles WHERE week_start_date = $1",
            [current_week_start]
        )
        
        if not existing_week:
            # Create new week entry
            await self.db.execute_command(
                """
                INSERT INTO weekly_cycles (week_start_date, articles_collected, articles_curated)
                VALUES ($1, 0, 0)
                """,
                [current_week_start]
            )
            self.logger.info(f"Initialized new week cycle: {current_week_start}")
        
        return current_week_start
    
    def organize_article_by_week(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign article to appropriate week based on published date"""
        # Use published_at if available, otherwise use current time
        if 'published_at' in article_data and article_data['published_at']:
            if isinstance(article_data['published_at'], str):
                try:
                    published_date = datetime.fromisoformat(article_data['published_at'].replace('Z', '+00:00')).date()
                except ValueError:
                    published_date = datetime.now().date()
            elif isinstance(article_data['published_at'], datetime):
                published_date = article_data['published_at'].date()
            else:
                published_date = datetime.now().date()
        else:
            published_date = datetime.now().date()
        
        week_start = self.get_week_start_for_date(published_date)
        article_data['week_start_date'] = week_start
        
        return article_data
    
    async def store_weekly_articles(self, articles: List[Dict[str, Any]]) -> int:
        """Store articles with weekly organization"""
        if not articles:
            return 0
        
        # Organize articles by week
        organized_articles = []
        for article in articles:
            organized_article = self.organize_article_by_week(article)
            organized_articles.append(organized_article)
        
        # Bulk insert articles
        try:
            stored_count = await self.db.bulk_insert_articles(organized_articles)
            
            if stored_count > 0:
                # Update weekly cycle statistics
                await self.update_weekly_stats()
                
                self.logger.info(f"Stored {stored_count} articles with weekly organization")
            
            return stored_count
            
        except Exception as e:
            self.logger.error(f"Failed to store weekly articles: {e}")
            raise
    
    async def update_weekly_stats(self, week_start: Optional[date] = None) -> None:
        """Update statistics for a specific week"""
        if week_start is None:
            week_start = self.get_current_week_start()
        
        try:
            # Calculate week statistics
            stats_query = """
            SELECT 
                COUNT(*) as total_articles,
                AVG(relevance_score) as avg_relevance,
                COUNT(*) FILTER (WHERE selected_for_newsletter = TRUE) as curated_count,
                array_agg(DISTINCT unnest(tags)) FILTER (WHERE tags IS NOT NULL AND array_length(tags, 1) > 0) as all_themes
            FROM articles 
            WHERE week_start_date = $1
            """
            
            stats_result = await self.db.execute_query(stats_query, [week_start])
            
            if stats_result:
                stats = stats_result[0]
                
                # Get top themes (most frequent tags)
                all_themes = stats.get('all_themes') or []
                top_themes = []
                if all_themes:
                    # Count theme frequency
                    theme_counts = {}
                    for theme in all_themes:
                        if theme:  # Skip None/empty themes
                            theme_counts[theme] = theme_counts.get(theme, 0) + 1
                    
                    # Get top 5 themes
                    top_themes = sorted(theme_counts.keys(), 
                                      key=lambda x: theme_counts[x], 
                                      reverse=True)[:5]
                
                # Update weekly cycle record
                update_query = """
                UPDATE weekly_cycles 
                SET articles_collected = $2,
                    articles_curated = $3,
                    average_relevance_score = $4,
                    top_themes = $5,
                    updated_at = NOW()
                WHERE week_start_date = $1
                """
                
                await self.db.execute_command(update_query, [
                    week_start,
                    stats['total_articles'],
                    stats['curated_count'],
                    stats['avg_relevance'],
                    top_themes
                ])
                
                self.logger.info(f"Updated weekly stats for {week_start}: "
                               f"{stats['total_articles']} articles, "
                               f"avg relevance {stats['avg_relevance']:.1f}")
        
        except Exception as e:
            self.logger.error(f"Failed to update weekly stats: {e}")
            raise
    
    async def get_current_week_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of current week"""
        current_week = self.get_current_week_start()
        
        try:
            # Get basic weekly stats
            weekly_stats = await self.db.get_weekly_stats(current_week)
            
            # Get source breakdown
            source_breakdown = await self.db.execute_query("""
                SELECT 
                    source_type,
                    COUNT(*) as count,
                    AVG(relevance_score) as avg_relevance
                FROM articles 
                WHERE week_start_date = $1
                GROUP BY source_type
                ORDER BY count DESC
            """, [current_week])
            
            # Get top articles
            top_articles = await self.db.execute_query("""
                SELECT title, source_name, relevance_score, url
                FROM articles 
                WHERE week_start_date = $1
                ORDER BY relevance_score DESC
                LIMIT 5
            """, [current_week])
            
            # Get selected articles count
            selected_count = await self.db.execute_query("""
                SELECT COUNT(*) as count
                FROM articles 
                WHERE week_start_date = $1 AND selected_for_newsletter = TRUE
            """, [current_week])
            
            return {
                'week_start': current_week,
                'stats': weekly_stats,
                'source_breakdown': source_breakdown,
                'top_articles': top_articles,
                'selected_articles_count': selected_count[0]['count'] if selected_count else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly summary: {e}")
            raise
    
    async def get_weekly_comparison(self, weeks_back: int = 4) -> List[Dict[str, Any]]:
        """Compare recent weeks' performance"""
        try:
            query = """
            SELECT * FROM weekly_trends 
            LIMIT $1
            """
            
            return await self.db.execute_query(query, [weeks_back])
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly comparison: {e}")
            raise
    
    async def get_theme_trends(self, weeks_back: int = 4) -> Dict[str, List[str]]:
        """Get trending themes over recent weeks"""
        try:
            end_date = self.get_current_week_start()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            query = """
            SELECT week_start_date, top_themes
            FROM weekly_cycles 
            WHERE week_start_date >= $1 AND week_start_date <= $2
            ORDER BY week_start_date DESC
            """
            
            results = await self.db.execute_query(query, [start_date, end_date])
            
            theme_trends = {}
            for week_data in results:
                week_str = week_data['week_start_date'].strftime('%Y-%m-%d')
                theme_trends[week_str] = week_data['top_themes'] or []
            
            return theme_trends
            
        except Exception as e:
            self.logger.error(f"Failed to get theme trends: {e}")
            raise
    
    async def cleanup_old_content(self, retention_weeks: Optional[int] = None) -> int:
        """Clean up old content based on retention policy"""
        if retention_weeks is None:
            retention_weeks = self.settings.CONTENT_RETENTION_WEEKS
        
        try:
            # Clean up old articles
            deleted_articles = await self.db.cleanup_old_articles(retention_weeks)
            
            # Clean up old weekly cycles
            cutoff_date = self.get_current_week_start() - timedelta(weeks=retention_weeks)
            deleted_cycles = await self.db.execute_command("""
                DELETE FROM weekly_cycles 
                WHERE week_start_date < $1
            """, [cutoff_date])
            
            # Clean up old processing logs
            deleted_logs = await self.db.execute_command("""
                DELETE FROM processing_logs 
                WHERE started_at < $1
            """, [datetime.now() - timedelta(weeks=retention_weeks)])
            
            self.logger.info(f"Cleanup completed: {deleted_articles} articles, "
                           f"{deleted_cycles} weekly cycles, {deleted_logs} logs removed")
            
            return deleted_articles
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old content: {e}")
            raise
    
    async def get_source_performance_trends(self, weeks_back: int = 4) -> List[Dict[str, Any]]:
        """Analyze source performance over time"""
        try:
            end_date = self.get_current_week_start()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            query = """
            SELECT 
                cs.name,
                cs.type,
                cs.success_rate,
                cs.average_relevance_score,
                COUNT(a.id) as recent_articles,
                AVG(a.relevance_score) as recent_avg_relevance
            FROM source_performance cs
            LEFT JOIN articles a ON a.source_name = cs.name 
                AND a.week_start_date >= $1
            GROUP BY cs.name, cs.type, cs.success_rate, cs.average_relevance_score
            ORDER BY recent_avg_relevance DESC NULLS LAST
            """
            
            return await self.db.execute_query(query, [start_date])
            
        except Exception as e:
            self.logger.error(f"Failed to get source performance trends: {e}")
            raise
    
    async def archive_completed_week(self, week_start: date) -> bool:
        """Mark a week as archived/completed"""
        try:
            # Update weekly cycle to mark as completed
            await self.db.execute_command("""
                UPDATE weekly_cycles 
                SET updated_at = NOW()
                WHERE week_start_date = $1
            """, [week_start])
            
            # Log the archival
            await self.db.log_processing_run(
                process_type="week_archive",
                status="completed",
                details={"archived_week": week_start.isoformat()}
            )
            
            self.logger.info(f"Archived week {week_start}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to archive week {week_start}: {e}")
            return False