"""
Multi-stage AI digest processor for RSS + Twitter content
Two-stage LLM filtering: 100+ articles → 20 → 5 final selections
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple
import json
import openai
from openai import AsyncOpenAI
from collections import defaultdict

from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient
from services.prompt_service import get_prompt_service

class MultiStageDigestProcessor:
    """Two-stage AI filtering for daily digest creation with diversity controls"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.db_client = SimpleSupabaseClient(settings)
        self.prompt_service = get_prompt_service(settings)
    
    def _prepare_article_summary(self, article: Dict[str, Any]) -> str:
        """Create concise article summary for LLM processing"""
        return f"""
TITLE: {article['title']}
SOURCE: {article['source_name']} ({article['source_type']})
CONTENT: {article.get('content_excerpt', '')[:300]}...
URL: {article['url']}
TAGS: {', '.join(article.get('tags', []))}
{f"ENGAGEMENT: {article.get('twitter_metrics', {}).get('engagement_score', 'N/A')}" if article['source_type'] == 'twitter' else ""}
"""
    
    async def _get_recently_selected_articles(self, days_back: int = 7) -> set:
        """Get URLs of articles selected in recent digests to avoid recycling"""
        try:
            cutoff_date = (date.today() - timedelta(days=days_back)).isoformat()
            
            # Get recent digests with their selected article IDs
            response = self.db_client.client.table('daily_digests')\
                .select('selected_article_ids')\
                .gte('digest_date', cutoff_date)\
                .execute()
            
            if not response.data:
                return set()
            
            # Collect all selected article IDs
            selected_ids = []
            for digest in response.data:
                if digest.get('selected_article_ids'):
                    selected_ids.extend(digest['selected_article_ids'])
            
            if not selected_ids:
                return set()
            
            # Get URLs for these article IDs
            articles_response = self.db_client.client.table('articles')\
                .select('url')\
                .in_('id', selected_ids)\
                .execute()
            
            recently_selected_urls = set()
            if articles_response.data:
                recently_selected_urls = {article['url'] for article in articles_response.data}
            
            self.logger.info(f"Found {len(recently_selected_urls)} recently selected articles to exclude")
            return recently_selected_urls
            
        except Exception as e:
            self.logger.error(f"Failed to get recently selected articles: {e}")
            return set()
    
    def _apply_diversity_filtering(self, articles: List[Dict[str, Any]], recently_selected: set) -> List[Dict[str, Any]]:
        """Apply diversity and freshness filtering before AI selection"""
        
        # Remove recently selected articles
        fresh_articles = [a for a in articles if a['url'] not in recently_selected]
        self.logger.info(f"Filtered out {len(articles) - len(fresh_articles)} recently selected articles")
        
        # Group by source for diversity
        by_source = defaultdict(list)
        for article in fresh_articles:
            by_source[article['source_name']].append(article)
        
        # Apply source limits and recency weighting
        diverse_articles = []
        max_per_source = max(2, len(fresh_articles) // len(by_source)) if by_source else len(fresh_articles)
        
        for source_name, source_articles in by_source.items():
            # Sort by recency (published_date if available, otherwise scraped_at)
            def get_sort_key(article):
                pub_date = article.get('published_date')
                if pub_date:
                    try:
                        if isinstance(pub_date, str):
                            return datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                        return pub_date
                    except:
                        pass
                # Fallback to scraped_at or current time
                scraped = article.get('scraped_at', datetime.now())
                if isinstance(scraped, str):
                    try:
                        return datetime.fromisoformat(scraped.replace('Z', '+00:00'))
                    except:
                        return datetime.now()
                return scraped
            
            source_articles.sort(key=get_sort_key, reverse=True)
            
            # Take top articles from this source (respecting diversity limit)
            selected_from_source = source_articles[:max_per_source]
            diverse_articles.extend(selected_from_source)
            
            self.logger.debug(f"Selected {len(selected_from_source)} articles from {source_name}")
        
        self.logger.info(f"Applied diversity filtering: {len(fresh_articles)} -> {len(diverse_articles)} articles")
        return diverse_articles
    
    async def stage_1_filtering(self, all_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Stage 1: Filter articles with diversity controls, then AI selection to top 20"""
        
        self.logger.info(f"Stage 1: Starting with {len(all_articles)} articles")
        
        # Get recently selected articles to avoid recycling
        recently_selected = await self._get_recently_selected_articles(days_back=7)
        
        # Apply diversity and freshness filtering first
        diverse_articles = self._apply_diversity_filtering(all_articles, recently_selected)
        
        if not diverse_articles:
            self.logger.warning("No articles remaining after diversity filtering")
            return []
        
        self.logger.info(f"Stage 1: AI filtering {len(diverse_articles)} diverse articles to top 20")
        
        # Prepare article summaries for LLM
        article_summaries = []
        for i, article in enumerate(diverse_articles):
            summary = f"[{i}] {self._prepare_article_summary(article)}"
            article_summaries.append(summary)
        
        # Create batches to avoid token limits (process in chunks of 50)
        batch_size = 50
        selected_indices = []
        
        for batch_start in range(0, len(diverse_articles), batch_size):
            batch_end = min(batch_start + batch_size, len(diverse_articles))
            batch_articles = article_summaries[batch_start:batch_end]
            
            # Get stage 1 filtering prompt from database
            prompt = await self.prompt_service.get_formatted_prompt(
                'digest_stage1_filtering_prompt',
                article_count=len(batch_articles),
                articles=chr(10).join(batch_articles)
            )
            
            if not prompt:
                self.logger.error("Stage 1 filtering prompt not found in database")
                # Fallback: select first few articles from batch
                fallback_count = min(10, len(batch_articles))
                selected_indices.extend(range(batch_start, batch_start + fallback_count))
                continue
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Cost-effective for filtering
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )
                
                content = response.choices[0].message.content.strip()
                self.logger.debug(f"OpenAI response: {content}")
                
                # Try to extract JSON from response
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                result = json.loads(content)
                # Adjust indices for global array
                batch_selected = [idx + batch_start for idx in result["selected_indices"]]
                selected_indices.extend(batch_selected)
                
                self.logger.info(f"Batch {batch_start}-{batch_end}: Selected {len(batch_selected)} articles")
                
            except Exception as e:
                self.logger.error(f"Stage 1 filtering failed for batch {batch_start}: {e}")
                # Fallback: select first few articles from batch
                fallback_count = min(10, len(batch_articles))
                selected_indices.extend(range(batch_start, batch_start + fallback_count))
        
        # Return top 20 overall (limit in case we got more from multiple batches)
        # Filter out invalid indices and limit to 20
        valid_indices = [i for i in selected_indices if 0 <= i < len(diverse_articles)]
        final_selected = valid_indices[:20]
        selected_articles = [diverse_articles[i] for i in final_selected]
        
        self.logger.info(f"Stage 1 complete: Selected {len(selected_articles)} articles")
        return selected_articles
    
    async def stage_2_final_selection(self, filtered_articles: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], str, List[str]]:
        """Stage 2: Select final 5 articles and create comprehensive digest"""
        
        self.logger.info(f"Stage 2: Final selection from {len(filtered_articles)} articles")
        
        # Prepare detailed summaries for final selection
        detailed_summaries = []
        for i, article in enumerate(filtered_articles):
            summary = f"""
[{i}] TITLE: {article['title']}
SOURCE: {article['source_name']} ({article['source_type']})
FULL CONTENT: {article.get('content_excerpt', '')}
URL: {article['url']}
THEMES: {', '.join(article.get('key_themes', []))}
PUBLISHED: {article.get('published_date', 'Unknown')}
{f"TWITTER ENGAGEMENT: {article.get('twitter_metrics', {})}" if article['source_type'] == 'twitter' else ""}
"""
            detailed_summaries.append(summary)
        
        # Get stage 2 final selection prompt from database
        prompt = await self.prompt_service.get_formatted_prompt(
            'digest_stage2_final_selection_prompt',
            article_count=len(filtered_articles),
            articles=chr(10).join(detailed_summaries)
        )
        
        if not prompt:
            self.logger.error("Stage 2 final selection prompt not found in database")
            # Fallback: select first 5 articles
            fallback_articles = filtered_articles[:5]
            fallback_digest = f"Daily digest for {date.today()}: {len(fallback_articles)} articles selected (fallback mode - prompt not found)"
            return fallback_articles, fallback_digest, ["Fallback mode - manual review needed"], []
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Use better model for final analysis
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            self.logger.debug(f"Stage 2 OpenAI response: {content}")
            
            # Try to extract JSON from response
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            result = json.loads(content)
            
            # Extract selected articles
            selected_articles = [filtered_articles[i] for i in result["selected_indices"]]
            
            # Enhance article summaries with source and URL information
            enhanced_summaries = []
            for i, summary in enumerate(result.get('article_summaries', [])):
                if i < len(selected_articles):
                    article = selected_articles[i]
                    enhanced_summary = summary.copy()
                    enhanced_summary['source'] = f"{article['source_name']} ({article['source_type']})"
                    enhanced_summary['url'] = article['url']
                    enhanced_summaries.append(enhanced_summary)
            
            # Create comprehensive digest text
            digest_text = f"""
{result['daily_summary']}

KEY INSIGHTS:
{chr(10).join([f"• {insight}" for insight in result['key_insights']])}

SELECTED ARTICLES:
{chr(10).join([f"{i+1}. {article['title']} ({article['source_name']})" for i, article in enumerate(selected_articles)])}
"""
            
            # Extract detailed article summaries for Ben's newsletter writing
            article_summaries = result.get('article_summaries', [])
            
            self.logger.info(f"Stage 2 complete: Final {len(selected_articles)} articles selected with detailed summaries")
            return selected_articles, digest_text, result['key_insights'], enhanced_summaries
            
        except Exception as e:
            self.logger.error(f"Stage 2 final selection failed: {e}")
            # Fallback: select first 5 articles
            fallback_articles = filtered_articles[:5]
            fallback_digest = f"Daily digest for {date.today()}: {len(fallback_articles)} articles selected (fallback mode)"
            return fallback_articles, fallback_digest, ["Fallback mode - manual review needed"], []
    
    async def create_daily_digest(self, all_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Complete two-stage digest creation process"""
        
        if not all_articles:
            return {
                'selected_articles': [],
                'digest_text': 'No articles available for digest',
                'key_insights': [],
                'total_processed': 0
            }
        
        self.logger.info(f"Starting daily digest creation with {len(all_articles)} articles")
        
        # Stage 1: Initial filtering
        stage_1_articles = await self.stage_1_filtering(all_articles)
        
        # Stage 2: Final selection and digest creation
        final_articles, digest_text, key_insights, article_summaries = await self.stage_2_final_selection(stage_1_articles)
        
        return {
            'selected_articles': final_articles,
            'digest_text': digest_text,
            'key_insights': key_insights,
            'article_summaries': article_summaries,
            'total_processed': len(all_articles),
            'stage_1_count': len(stage_1_articles),
            'final_count': len(final_articles)
        }
