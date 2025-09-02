"""
AI-powered content evaluation using OpenAI
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import openai
from openai import AsyncOpenAI
import tiktoken

from config.settings import Settings


class AIEvaluator:
    """AI-powered content evaluation and scoring"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logging.getLogger(__name__)
        
        # Initialize tokenizer for the model
        try:
            self.encoding = tiktoken.encoding_for_model(settings.OPENAI_MODEL)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback estimation: ~4 chars per token
            return len(text) // 4
    
    def truncate_content_for_evaluation(self, title: str, content: str) -> str:
        """Truncate content to fit within token limits"""
        # Reserve tokens for prompt and response
        max_content_tokens = 2000  # Conservative limit
        
        combined_text = f"{title}\n\n{content}"
        
        if self.count_tokens(combined_text) <= max_content_tokens:
            return content
        
        # Truncate content while preserving the beginning (most important)
        target_chars = max_content_tokens * 4  # Rough estimation
        
        if len(content) > target_chars:
            # Try to cut at sentence boundary
            truncated = content[:target_chars]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')
            
            cut_point = max(last_period, last_newline)
            if cut_point > target_chars * 0.8:  # If we found a good cut point
                content = content[:cut_point + 1]
            else:
                content = content[:target_chars] + "..."
        
        return content
    
    async def evaluate_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate article using AI and return enhanced data"""
        try:
            title = article_data.get('title', '')
            content = article_data.get('content_excerpt', '')
            source_name = article_data.get('source_name', '')
            
            if not title or not content:
                self.logger.warning("Missing title or content for evaluation")
                return self.create_default_evaluation(article_data)
            
            # Truncate content if needed
            content = self.truncate_content_for_evaluation(title, content)
            
            # Create evaluation prompt
            prompt = self.settings.ai_scoring_prompt.format(
                title=title,
                content_excerpt=content,
                source_name=source_name
            )
            
            # Call OpenAI API
            evaluation_result = await self.call_openai_api(prompt)
            
            if evaluation_result:
                # Merge evaluation results with article data
                enhanced_article = article_data.copy()
                enhanced_article.update(evaluation_result)
                
                # Add evaluation metadata
                enhanced_article['evaluated_at'] = article_data.get('processed_at')
                enhanced_article['evaluation_model'] = self.settings.OPENAI_MODEL
                
                return enhanced_article
            else:
                return self.create_default_evaluation(article_data)
                
        except Exception as e:
            self.logger.error(f"Article evaluation failed: {e}")
            return self.create_default_evaluation(article_data)
    
    async def call_openai_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI API with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Calling OpenAI API (attempt {attempt + 1})")
                
                response = await self.client.chat.completions.create(
                    model=self.settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert content evaluator for business AI newsletters. "
                                     "Always respond with valid JSON matching the requested format."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.3,  # Low temperature for consistent scoring
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    result = json.loads(content)
                    return self.validate_and_clean_evaluation(result)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Invalid JSON response: {e}")
                    # Try to extract JSON from response
                    return self.extract_json_from_response(content)
                
            except openai.RateLimitError:
                wait_time = 2 ** attempt  # Exponential backoff
                self.logger.warning(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                continue
                
            except openai.APIError as e:
                self.logger.error(f"OpenAI API error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                break
                
            except Exception as e:
                self.logger.error(f"Unexpected error calling OpenAI: {e}")
                break
        
        return None
    
    def extract_json_from_response(self, response_content: str) -> Optional[Dict[str, Any]]:
        """Try to extract JSON from malformed response"""
        try:
            # Look for JSON-like content
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return self.validate_and_clean_evaluation(result)
                
        except Exception as e:
            self.logger.debug(f"Failed to extract JSON: {e}")
        
        return None
    
    def validate_and_clean_evaluation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean evaluation result"""
        validated = {}
        
        # Validate relevance score
        relevance_score = result.get('relevance_score', 0)
        try:
            relevance_score = float(relevance_score)
            relevance_score = max(0, min(100, relevance_score))  # Clamp to 0-100
        except (ValueError, TypeError):
            relevance_score = 50  # Default score
        
        validated['relevance_score'] = relevance_score
        
        # Validate business impact score
        business_impact_score = result.get('business_impact_score', relevance_score)
        try:
            business_impact_score = float(business_impact_score)
            business_impact_score = max(0, min(100, business_impact_score))
        except (ValueError, TypeError):
            business_impact_score = relevance_score  # Use relevance score as fallback
        
        validated['business_impact_score'] = business_impact_score
        
        # Validate key themes
        key_themes = result.get('key_themes', [])
        if isinstance(key_themes, list):
            # Clean and limit themes
            clean_themes = []
            for theme in key_themes[:10]:  # Limit to 10 themes
                if isinstance(theme, str) and theme.strip():
                    clean_themes.append(theme.strip().lower().replace(' ', '_'))
            validated['key_themes'] = clean_themes
        else:
            validated['key_themes'] = []
        
        # Validate reasoning
        reasoning = result.get('reasoning', '')
        if isinstance(reasoning, str):
            validated['reasoning'] = reasoning.strip()[:500]  # Limit length
        else:
            validated['reasoning'] = ""
        
        return validated
    
    def create_default_evaluation(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create default evaluation when AI evaluation fails"""
        enhanced_article = article_data.copy()
        
        # Basic heuristic scoring
        relevance_score = self.calculate_heuristic_score(article_data)
        
        enhanced_article.update({
            'relevance_score': relevance_score,
            'business_impact_score': relevance_score * 0.8,  # Conservative estimate
            'key_themes': article_data.get('tags', [])[:5],  # Use existing tags
            'reasoning': "Automatic scoring based on content analysis",
            'evaluation_model': 'heuristic'
        })
        
        return enhanced_article
    
    def calculate_heuristic_score(self, article_data: Dict[str, Any]) -> float:
        """Calculate relevance score using heuristics"""
        score = 50.0  # Base score
        
        title = article_data.get('title', '').lower()
        content = article_data.get('content_excerpt', '').lower()
        tags = [tag.lower() for tag in article_data.get('tags', [])]
        source_name = article_data.get('source_name', '').lower()
        
        combined_text = title + " " + content
        
        # High-value keywords (business impact)
        high_value_keywords = [
            'enterprise', 'platform', 'infrastructure', 'data strategy',
            'vendor lock-in', 'business model', 'roi', 'cost', 'efficiency',
            'automation', 'implementation', 'deployment', 'integration'
        ]
        
        for keyword in high_value_keywords:
            if keyword in combined_text:
                score += 8
        
        # AI/ML keywords
        ai_keywords = [
            'artificial intelligence', 'machine learning', 'ai', 'ml',
            'neural network', 'deep learning', 'llm', 'gpt'
        ]
        
        for keyword in ai_keywords:
            if keyword in combined_text:
                score += 5
        
        # Source quality adjustment
        high_quality_sources = [
            'harvard business review', 'mit technology review',
            'venturebeat', 'techcrunch'
        ]
        
        if any(source in source_name for source in high_quality_sources):
            score += 10
        
        # Content quality indicators
        if len(content) > 200:
            score += 5
        
        if article_data.get('word_count', 0) > 100:
            score += 5
        
        # Twitter engagement boost
        if article_data.get('source_type') == 'twitter':
            twitter_metrics = article_data.get('twitter_metrics', {})
            engagement_rate = twitter_metrics.get('engagement_rate', 0)
            
            if engagement_rate > 2.0:
                score += 15
            elif engagement_rate > 1.0:
                score += 10
            elif engagement_rate > 0.5:
                score += 5
        
        # Penalize low-quality content
        spam_indicators = [
            'click here', 'buy now', 'limited time', 'exclusive offer',
            'free trial', 'sign up now'
        ]
        
        for indicator in spam_indicators:
            if indicator in combined_text:
                score -= 10
        
        # Clamp score to valid range
        return max(0, min(100, score))
    
    async def batch_evaluate_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate multiple articles with rate limiting"""
        if not articles:
            return []
        
        self.logger.info(f"Starting AI evaluation for {len(articles)} articles")
        
        # Process articles with rate limiting
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent API calls
        
        async def evaluate_with_semaphore(article):
            async with semaphore:
                result = await self.evaluate_article(article)
                # Add small delay to respect rate limits
                await asyncio.sleep(0.2)
                return result
        
        # Create tasks for all articles
        tasks = [evaluate_with_semaphore(article) for article in articles]
        
        # Execute with progress tracking
        evaluated_articles = []
        completed = 0
        
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                evaluated_articles.append(result)
                completed += 1
                
                if completed % 10 == 0:
                    self.logger.info(f"Evaluated {completed}/{len(articles)} articles")
                    
            except Exception as e:
                self.logger.error(f"Failed to evaluate article: {e}")
                continue
        
        self.logger.info(f"AI evaluation completed: {len(evaluated_articles)} articles processed")
        return evaluated_articles
    
    def get_evaluation_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary statistics of evaluations"""
        if not articles:
            return {}
        
        relevance_scores = [a.get('relevance_score', 0) for a in articles]
        business_scores = [a.get('business_impact_score', 0) for a in articles]
        
        all_themes = []
        for article in articles:
            all_themes.extend(article.get('key_themes', []))
        
        # Count theme frequency
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_articles': len(articles),
            'avg_relevance_score': sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0,
            'avg_business_score': sum(business_scores) / len(business_scores) if business_scores else 0,
            'high_relevance_articles': len([s for s in relevance_scores if s >= 80]),
            'medium_relevance_articles': len([s for s in relevance_scores if 60 <= s < 80]),
            'low_relevance_articles': len([s for s in relevance_scores if s < 60]),
            'top_themes': [theme for theme, count in top_themes]
        }


# CLI testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_ai_evaluator():
        settings = Settings()
        
        if not settings.OPENAI_API_KEY:
            print("OPENAI_API_KEY not set in environment")
            return
        
        evaluator = AIEvaluator(settings)
        
        # Test article
        test_article = {
            'title': 'Enterprise AI Implementation: Avoiding Vendor Lock-in',
            'content_excerpt': 'Companies are increasingly adopting AI solutions but many fall into vendor lock-in traps. This article explores strategies for maintaining platform independence while implementing enterprise AI systems. Key considerations include data portability, API standardization, and multi-cloud architectures.',
            'source_name': 'Harvard Business Review',
            'source_type': 'rss',
            'tags': ['enterprise', 'ai', 'vendor_lock_in', 'data_strategy']
        }
        
        result = await evaluator.evaluate_article(test_article)
        
        print("AI Evaluation Result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    
    # Run test
    asyncio.run(test_ai_evaluator())