"""
Newsletter Draft Processor - Weekly newsletter generation for Sunday evenings
Implements executive-focused filtering, prioritization, and structured output
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json
from openai import AsyncOpenAI

from config.settings import Settings
from database.supabase_simple import SimpleSupabaseClient

class NewsletterDraftProcessor:
    """Processes weekly articles into structured newsletter drafts"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.db_client = SimpleSupabaseClient(settings)
    
    def get_week_start(self, target_date: date = None) -> date:
        """Get Monday of the current week"""
        if target_date is None:
            target_date = date.today()
        return target_date - timedelta(days=target_date.weekday())
    
    async def get_weekly_articles(self, week_start: date) -> List[Dict[str, Any]]:
        """Get all articles from the current week"""
        try:
            week_end = week_start + timedelta(days=7)
            
            response = self.db_client.client.table('articles')\
                .select('*')\
                .gte('scraped_at', week_start.isoformat())\
                .lt('scraped_at', week_end.isoformat())\
                .order('scraped_at', desc=True)\
                .execute()
            
            articles = response.data if response.data else []
            self.logger.info(f"Retrieved {len(articles)} articles for week starting {week_start}")
            return articles
            
        except Exception as e:
            self.logger.error(f"Failed to get weekly articles: {e}")
            return []
    
    async def score_articles_for_newsletter(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score articles based on newsletter criteria using AI"""
        
        if not articles:
            return []
        
        self.logger.info(f"Scoring {len(articles)} articles for newsletter criteria")
        
        # Prepare articles for AI scoring
        article_summaries = []
        for i, article in enumerate(articles):
            pub_date = article.get('published_at', article.get('scraped_at', ''))
            summary = f"""
[{i}] TITLE: {article['title']}
SOURCE: {article['source_name']} ({article['source_type']})
PUBLISHED: {pub_date}
CONTENT: {article.get('content_excerpt', '')[:400]}...
URL: {article['url']}
TAGS: {', '.join(article.get('tags', []))}
"""
            article_summaries.append(summary)
        
        # Process in batches to avoid token limits
        batch_size = 20
        scored_articles = []
        
        for batch_start in range(0, len(articles), batch_size):
            batch_end = min(batch_start + batch_size, len(articles))
            batch_articles = article_summaries[batch_start:batch_end]
            
            prompt = f"""
You are scoring articles for an executive AI newsletter focused on "Don't panic. Prepare your data. Stay agnostic."

SCORING CRITERIA (0-100 each):
1. RELEVANCE: AI-specific, high business impact for tech executives
2. TIMELINESS: Published within the week, addresses current trends
3. EVIDENCE QUALITY: Data, citations, case studies, concrete examples
4. INNOVATION: Operational consequences, not hype - real business implications

NEWSLETTER POTENTIAL:
- HEADLINE POTENTIAL: Suitable for 1-2 sentence executive summary
- DEEP DIVE POTENTIAL: Rich enough for 300-400 word analysis with implications

ARTICLES TO SCORE:
{chr(10).join(batch_articles)}

RESPOND WITH JSON:
{{
  "article_scores": [
    {{
      "article_index": 0,
      "relevance_score": 85,
      "timeliness_score": 90,
      "evidence_quality_score": 75,
      "innovation_score": 80,
      "headline_potential_score": 85,
      "deep_dive_potential_score": 90,
      "reasoning": "Brief explanation of scores"
    }}
  ]
}}

Score ALL {len(batch_articles)} articles. Focus on business value for executives, not technical details.
"""
            
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Cost-effective for scoring
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=3000
                )
                
                content = response.choices[0].message.content.strip()
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                result = json.loads(content)
                
                # Add scores to articles
                for score_data in result.get('article_scores', []):
                    article_idx = score_data['article_index'] + batch_start
                    if article_idx < len(articles):
                        article = articles[article_idx].copy()
                        article.update({
                            'relevance_score': score_data.get('relevance_score', 0),
                            'timeliness_score': score_data.get('timeliness_score', 0),
                            'evidence_quality_score': score_data.get('evidence_quality_score', 0),
                            'innovation_score': score_data.get('innovation_score', 0),
                            'headline_potential_score': score_data.get('headline_potential_score', 0),
                            'deep_dive_potential_score': score_data.get('deep_dive_potential_score', 0),
                            'scoring_reasoning': score_data.get('reasoning', '')
                        })
                        scored_articles.append(article)
                
                self.logger.info(f"Scored batch {batch_start}-{batch_end}: {len(result.get('article_scores', []))} articles")
                
            except Exception as e:
                self.logger.error(f"Failed to score batch {batch_start}: {e}")
                # Add articles with default scores
                for i in range(batch_start, batch_end):
                    if i < len(articles):
                        article = articles[i].copy()
                        article.update({
                            'relevance_score': 50,
                            'timeliness_score': 50,
                            'evidence_quality_score': 50,
                            'innovation_score': 50,
                            'headline_potential_score': 50,
                            'deep_dive_potential_score': 50,
                            'scoring_reasoning': 'Default scores due to processing error'
                        })
                        scored_articles.append(article)
        
        return scored_articles
    
    async def select_newsletter_content(self, scored_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select and structure content for newsletter sections"""
        
        if not scored_articles:
            return {
                'top_headlines': [],
                'deep_dive': None,
                'operators_lens': [],
                'quick_hits': []
            }
        
        # Sort articles by headline potential for top headlines
        headline_candidates = sorted(
            scored_articles, 
            key=lambda x: x.get('headline_potential_score', 0), 
            reverse=True
        )[:10]  # Top 10 for AI selection
        
        # Sort by deep dive potential for deep dive selection
        deep_dive_candidates = sorted(
            scored_articles,
            key=lambda x: x.get('deep_dive_potential_score', 0),
            reverse=True
        )[:5]  # Top 5 for AI selection
        
        self.logger.info(f"Selecting newsletter content from {len(headline_candidates)} headline and {len(deep_dive_candidates)} deep dive candidates")
        
        # Prepare content for AI selection
        headline_summaries = []
        for i, article in enumerate(headline_candidates):
            summary = f"""
[{i}] TITLE: {article['title']}
SOURCE: {article['source_name']}
SCORES: Relevance={article.get('relevance_score', 0)}, Innovation={article.get('innovation_score', 0)}
CONTENT: {article.get('content_excerpt', '')[:300]}...
"""
            headline_summaries.append(summary)
        
        deep_dive_summaries = []
        for i, article in enumerate(deep_dive_candidates):
            summary = f"""
[{i}] TITLE: {article['title']}
SOURCE: {article['source_name']}
SCORES: Deep Dive Potential={article.get('deep_dive_potential_score', 0)}, Evidence={article.get('evidence_quality_score', 0)}
CONTENT: {article.get('content_excerpt', '')[:500]}...
"""
            deep_dive_summaries.append(summary)
        
        prompt = f"""
You are creating a weekly AI newsletter for a tech executive. Select content following this structure:

NEWSLETTER REQUIREMENTS:
- Executive tone: snark-free, concise, no hype, subtle edge
- Focus: "Don't panic. Prepare your data. Stay agnostic."

HEADLINE CANDIDATES:
{chr(10).join(headline_summaries)}

DEEP DIVE CANDIDATES:
{chr(10).join(deep_dive_summaries)}

RESPOND WITH JSON:
{{
  "top_headlines": [
    {{
      "article_index": 0,
      "title": "Clean, executive-friendly title",
      "summary": "1-2 sentence neutral summary with business implications"
    }}
  ],
  "deep_dive": {{
    "article_index": 2,
    "title": "Deep dive article title",
    "expanded_content": "600-800 word comprehensive analysis that explores multiple dimensions of the topic. Include: 1) Context and background, 2) Current market dynamics, 3) Strategic implications for enterprise leaders, 4) Contrarian or alternative perspectives, 5) Connection to broader industry trends, 6) Actionable insights for decision-makers. Executive tone with analytical depth.",
    "key_implications": ["Strategic implication for enterprise planning", "Operational consideration for implementation", "Competitive advantage or risk factor", "Timeline and resource implications"],
    "related_perspectives": ["How this connects to broader AI/tech trends", "Alternative viewpoints or potential counterarguments", "Historical context or similar precedents"]
  }},
  "operators_lens": [
    "Takeaway 1: What this means for firms like yours",
    "Takeaway 2: Specific operational insight",
    "Takeaway 3: Strategic consideration"
  ],
  "quick_hits": [
    {{
      "type": "funding",
      "content": "Brief note on relevant funding/acquisition"
    }},
    {{
      "type": "regulation", 
      "content": "Brief regulatory update"
    }}
  ]
}}

SELECT:
- 3-5 top headlines (diverse sources, complementary topics)
- 1 deep dive article (rich content, strategic implications)
- 2-3 operator takeaways (actionable insights)
- 1-2 quick hits (optional, if relevant content exists)

Ensure executive focus, no technical jargon, business implications clear.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Better model for content selection
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                content = content.replace('```', '').strip()
            
            result = json.loads(content)
            
            # Map article indices back to actual articles
            newsletter_content = {
                'top_headlines': [],
                'deep_dive': None,
                'operators_lens': result.get('operators_lens', []),
                'quick_hits': result.get('quick_hits', [])
            }
            
            # Process headlines
            for headline in result.get('top_headlines', []):
                idx = headline.get('article_index')
                if idx is not None and idx < len(headline_candidates):
                    article = headline_candidates[idx]
                    newsletter_content['top_headlines'].append({
                        'article_id': article['id'],
                        'title': headline.get('title', article['title']),
                        'summary': headline.get('summary', ''),
                        'source': article['source_name'],
                        'url': article['url']
                    })
            
            # Process deep dive
            deep_dive_data = result.get('deep_dive')
            if deep_dive_data:
                idx = deep_dive_data.get('article_index')
                if idx is not None and idx < len(deep_dive_candidates):
                    article = deep_dive_candidates[idx]
                    newsletter_content['deep_dive'] = {
                        'article_id': article['id'],
                        'title': deep_dive_data.get('title', article['title']),
                        'expanded_content': deep_dive_data.get('expanded_content', ''),
                        'key_implications': deep_dive_data.get('key_implications', []),
                        'source': article['source_name'],
                        'url': article['url']
                    }
            
            self.logger.info(f"Selected {len(newsletter_content['top_headlines'])} headlines, "
                           f"{'1' if newsletter_content['deep_dive'] else '0'} deep dive, "
                           f"{len(newsletter_content['operators_lens'])} takeaways")
            
            return newsletter_content
            
        except Exception as e:
            self.logger.error(f"Failed to select newsletter content: {e}")
            # Fallback selection
            return {
                'top_headlines': [
                    {
                        'article_id': article['id'],
                        'title': article['title'],
                        'summary': 'Manual review needed - AI selection failed',
                        'source': article['source_name'],
                        'url': article['url']
                    }
                    for article in headline_candidates[:3]
                ],
                'deep_dive': {
                    'article_id': deep_dive_candidates[0]['id'],
                    'title': deep_dive_candidates[0]['title'],
                    'expanded_content': 'Manual expansion needed - AI processing failed',
                    'key_implications': ['Manual review required'],
                    'source': deep_dive_candidates[0]['source_name'],
                    'url': deep_dive_candidates[0]['url']
                } if deep_dive_candidates else None,
                'operators_lens': ['Manual review needed - AI processing failed'],
                'quick_hits': []
            }
    
    async def store_newsletter_draft(self, week_start: date, newsletter_content: Dict[str, Any], 
                                   total_articles: int, ai_reasoning: str = "") -> str:
        """Store newsletter draft in database"""
        try:
            draft_data = {
                'week_start_date': week_start.isoformat(),
                'status': 'draft',
                'top_headlines': newsletter_content.get('top_headlines', []),
                'deep_dive': newsletter_content.get('deep_dive'),
                'operators_lens': newsletter_content.get('operators_lens', []),
                'quick_hits': newsletter_content.get('quick_hits', []),
                'total_articles_considered': total_articles,
                'selection_criteria': {
                    'relevance_weight': 0.3,
                    'timeliness_weight': 0.25,
                    'evidence_quality_weight': 0.25,
                    'innovation_weight': 0.2
                },
                'ai_reasoning': ai_reasoning
            }
            
            # Check if draft already exists for this week
            existing = self.db_client.client.table('newsletter_drafts')\
                .select('id')\
                .eq('week_start_date', week_start.isoformat())\
                .execute()
            
            if existing.data:
                # Update existing draft
                result = self.db_client.client.table('newsletter_drafts')\
                    .update(draft_data)\
                    .eq('week_start_date', week_start.isoformat())\
                    .execute()
                draft_id = existing.data[0]['id']
                self.logger.info(f"Updated existing newsletter draft {draft_id}")
            else:
                # Create new draft
                result = self.db_client.client.table('newsletter_drafts')\
                    .insert(draft_data)\
                    .execute()
                draft_id = result.data[0]['id']
                self.logger.info(f"Created new newsletter draft {draft_id}")
            
            return draft_id
            
        except Exception as e:
            self.logger.error(f"Failed to store newsletter draft: {e}")
            raise
    
    async def generate_weekly_newsletter_draft(self, target_week: date = None) -> Dict[str, Any]:
        """Complete newsletter draft generation process"""
        
        if target_week is None:
            target_week = self.get_week_start()
        
        self.logger.info(f"Starting newsletter draft generation for week {target_week}")
        
        try:
            # Get weekly articles
            articles = await self.get_weekly_articles(target_week)
            
            if not articles:
                self.logger.warning(f"No articles found for week {target_week}")
                return {
                    'success': False,
                    'error': 'No articles found for the specified week',
                    'draft_id': None
                }
            
            # Score articles for newsletter criteria
            scored_articles = await self.score_articles_for_newsletter(articles)
            
            # Select and structure newsletter content
            newsletter_content = await self.select_newsletter_content(scored_articles)
            
            # Store draft in database
            draft_id = await self.store_newsletter_draft(
                target_week, 
                newsletter_content, 
                len(articles),
                f"Generated from {len(scored_articles)} scored articles"
            )
            
            self.logger.info(f"Newsletter draft generation completed: {draft_id}")
            
            return {
                'success': True,
                'draft_id': draft_id,
                'week_start': target_week.isoformat(),
                'articles_processed': len(articles),
                'headlines_count': len(newsletter_content.get('top_headlines', [])),
                'has_deep_dive': newsletter_content.get('deep_dive') is not None,
                'takeaways_count': len(newsletter_content.get('operators_lens', []))
            }
            
        except Exception as e:
            self.logger.error(f"Newsletter draft generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'draft_id': None
            }

# CLI testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_newsletter_processor():
        settings = Settings()
        processor = NewsletterDraftProcessor(settings)
        
        # Test with current week
        result = await processor.generate_weekly_newsletter_draft()
        
        print(f"Newsletter generation result: {result}")
        
        if result['success']:
            print(f"✅ Draft created: {result['draft_id']}")
            print(f"📊 Processed {result['articles_processed']} articles")
            print(f"📰 Generated {result['headlines_count']} headlines")
            print(f"📖 Deep dive: {'Yes' if result['has_deep_dive'] else 'No'}")
            print(f"💡 Takeaways: {result['takeaways_count']}")
        else:
            print(f"❌ Failed: {result['error']}")
    
    # Run test
    asyncio.run(test_newsletter_processor())
