"""
Content deduplication using similarity analysis
"""

import logging
import hashlib
from typing import List, Dict, Any, Set, Tuple
import re
from difflib import SequenceMatcher
from urllib.parse import urlparse


class Deduplicator:
    """Content deduplication using multiple similarity methods"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(__name__)
    
    async def remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles using multiple methods"""
        if not articles:
            return []
        
        self.logger.info(f"Starting deduplication for {len(articles)} articles")
        
        # Step 1: Remove exact URL duplicates
        unique_by_url = self.remove_url_duplicates(articles)
        self.logger.info(f"After URL deduplication: {len(unique_by_url)} articles")
        
        # Step 2: Remove title duplicates
        unique_by_title = self.remove_title_duplicates(unique_by_url)
        self.logger.info(f"After title deduplication: {len(unique_by_title)} articles")
        
        # Step 3: Remove content similarity duplicates
        unique_by_content = self.remove_content_duplicates(unique_by_title)
        self.logger.info(f"After content deduplication: {len(unique_by_content)} articles")
        
        # Step 4: Handle cross-source duplicates (same story from different sources)
        final_unique = self.handle_cross_source_duplicates(unique_by_content)
        self.logger.info(f"Final unique articles: {len(final_unique)}")
        
        return final_unique
    
    def remove_url_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove articles with duplicate URLs"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '').strip()
            
            if not url:
                unique_articles.append(article)
                continue
            
            # Normalize URL for comparison
            normalized_url = self.normalize_url(url)
            
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_articles.append(article)
            else:
                self.logger.debug(f"Removed duplicate URL: {url}")
        
        return unique_articles
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Normalize domain (remove www, convert to lowercase)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Normalize path (remove trailing slash, convert to lowercase)
            path = parsed.path.rstrip('/').lower()
            
            # Ignore query parameters and fragments for duplicate detection
            normalized = f"{parsed.scheme}://{domain}{path}"
            
            return normalized
            
        except Exception:
            return url.lower().strip()
    
    def remove_title_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove articles with very similar titles"""
        unique_articles = []
        processed_titles = []
        
        for article in articles:
            title = article.get('title', '').strip()
            
            if not title:
                unique_articles.append(article)
                continue
            
            # Normalize title for comparison
            normalized_title = self.normalize_title(title)
            
            # Check similarity with existing titles
            is_duplicate = False
            for existing_title in processed_titles:
                similarity = self.calculate_text_similarity(normalized_title, existing_title)
                
                if similarity > 0.9:  # Very high threshold for titles
                    is_duplicate = True
                    self.logger.debug(f"Removed duplicate title: {title}")
                    break
            
            if not is_duplicate:
                processed_titles.append(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for comparison"""
        # Convert to lowercase
        normalized = title.lower()
        
        # Remove common prefixes/suffixes
        prefixes = ['breaking:', 'news:', 'update:', 'exclusive:', 'report:']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):].strip()
                break
        
        # Remove source suffixes (e.g., "| TechCrunch")
        normalized = re.sub(r'\s*[|•·]\s*[^|•·]*$', '', normalized)
        
        # Remove excessive punctuation
        normalized = re.sub(r'[!]{2,}', '!', normalized)
        normalized = re.sub(r'[?]{2,}', '?', normalized)
        
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized.strip()
    
    def remove_content_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove articles with similar content"""
        if len(articles) <= 1:
            return articles
        
        unique_articles = []
        content_hashes = set()
        processed_articles = []
        
        for current_article in articles:
            content = current_article.get('content_excerpt', '').strip()
            
            if not content:
                unique_articles.append(current_article)
                continue
            
            # Check content hash first (exact duplicates)
            content_hash = self.calculate_content_hash(content)
            if content_hash in content_hashes:
                self.logger.debug(f"Removed exact content duplicate: {current_article.get('title', '')[:50]}...")
                continue
            
            # Check similarity with existing articles
            is_duplicate = False
            for processed_article in processed_articles:
                similarity = self.calculate_content_similarity(current_article, processed_article)
                
                if similarity > self.similarity_threshold:
                    # Choose the better article (higher quality/relevance)
                    if self.should_replace_article(current_article, processed_article):
                        # Replace the processed article with current one
                        idx = processed_articles.index(processed_article)
                        processed_articles[idx] = current_article
                        # Update in unique_articles as well
                        for i, art in enumerate(unique_articles):
                            if art is processed_article:
                                unique_articles[i] = current_article
                                break
                    
                    is_duplicate = True
                    self.logger.debug(f"Merged similar articles: {current_article.get('title', '')[:50]}...")
                    break
            
            if not is_duplicate:
                content_hashes.add(content_hash)
                processed_articles.append(current_article)
                unique_articles.append(current_article)
        
        return unique_articles
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of normalized content"""
        # Normalize content for hashing
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        normalized = re.sub(r'[^\w\s]', '', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def calculate_content_similarity(self, article1: Dict[str, Any], article2: Dict[str, Any]) -> float:
        """Calculate similarity between two articles"""
        # Get content
        content1 = article1.get('content_excerpt', '')
        content2 = article2.get('content_excerpt', '')
        
        if not content1 or not content2:
            return 0.0
        
        # Calculate title similarity (weighted heavily)
        title1 = self.normalize_title(article1.get('title', ''))
        title2 = self.normalize_title(article2.get('title', ''))
        title_similarity = self.calculate_text_similarity(title1, title2)
        
        # Calculate content similarity
        content_similarity = self.calculate_text_similarity(content1, content2)
        
        # Combined similarity (title weighted more heavily)
        combined_similarity = (title_similarity * 0.6) + (content_similarity * 0.4)
        
        return combined_similarity
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Use sequence matcher
        similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        return similarity
    
    def should_replace_article(self, new_article: Dict[str, Any], existing_article: Dict[str, Any]) -> bool:
        """Determine if new article should replace existing duplicate"""
        # Prefer articles with higher relevance scores
        new_score = new_article.get('relevance_score', 0)
        existing_score = existing_article.get('relevance_score', 0)
        
        if new_score != existing_score:
            return new_score > existing_score
        
        # Prefer articles with more content
        new_length = len(new_article.get('content_excerpt', ''))
        existing_length = len(existing_article.get('content_excerpt', ''))
        
        if abs(new_length - existing_length) > 100:  # Significant difference
            return new_length > existing_length
        
        # Prefer certain source types
        source_priority = {'rss': 3, 'gmail_newsletter': 2, 'twitter': 1}
        new_priority = source_priority.get(new_article.get('source_type', ''), 0)
        existing_priority = source_priority.get(existing_article.get('source_type', ''), 0)
        
        if new_priority != existing_priority:
            return new_priority > existing_priority
        
        # Prefer more recent articles
        new_date = new_article.get('published_at')
        existing_date = existing_article.get('published_at')
        
        if new_date and existing_date:
            return new_date > existing_date
        
        # Default: keep existing
        return False
    
    def handle_cross_source_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle duplicates that appear across different sources"""
        if len(articles) <= 1:
            return articles
        
        # Group articles by normalized title
        title_groups = {}
        
        for article in articles:
            normalized_title = self.normalize_title(article.get('title', ''))
            title_key = self.create_title_key(normalized_title)
            
            if title_key not in title_groups:
                title_groups[title_key] = []
            title_groups[title_key].append(article)
        
        # Process each group
        final_articles = []
        
        for title_key, group in title_groups.items():
            if len(group) == 1:
                final_articles.append(group[0])
            else:
                # Multiple articles with similar titles
                best_article = self.select_best_from_group(group)
                final_articles.append(best_article)
                
                removed_count = len(group) - 1
                if removed_count > 0:
                    self.logger.debug(f"Merged {removed_count} cross-source duplicates for: {title_key[:50]}...")
        
        return final_articles
    
    def create_title_key(self, normalized_title: str) -> str:
        """Create a key for grouping similar titles"""
        # Remove common words and create a simplified key
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'shall', 'must'
        }
        
        # Extract meaningful words
        words = normalized_title.split()
        key_words = []
        
        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            if (len(clean_word) > 2 and 
                clean_word.lower() not in common_words and
                not clean_word.isdigit()):
                key_words.append(clean_word.lower())
        
        # Create key from first few meaningful words
        return ' '.join(key_words[:5])  # Use first 5 meaningful words
    
    def select_best_from_group(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best article from a group of similar articles"""
        if not articles:
            return None
        
        if len(articles) == 1:
            return articles[0]
        
        # Score each article
        scored_articles = []
        
        for article in articles:
            score = self.calculate_article_quality_score(article)
            scored_articles.append((score, article))
        
        # Sort by score (highest first)
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        
        best_article = scored_articles[0][1]
        
        # Merge information from other articles if beneficial
        merged_article = self.merge_article_information(best_article, articles)
        
        return merged_article
    
    def calculate_article_quality_score(self, article: Dict[str, Any]) -> float:
        """Calculate quality score for article selection"""
        score = 0.0
        
        # Relevance score (highest weight)
        relevance_score = article.get('relevance_score', 50)
        score += relevance_score * 0.4
        
        # Content length (more content generally better)
        content_length = len(article.get('content_excerpt', ''))
        if content_length > 500:
            score += 20
        elif content_length > 200:
            score += 10
        elif content_length > 100:
            score += 5
        
        # Source type preference
        source_type = article.get('source_type', '')
        if source_type == 'rss':
            score += 15
        elif source_type == 'gmail_newsletter':
            score += 10
        elif source_type == 'twitter':
            score += 5
        
        # Source quality
        source_name = article.get('source_name', '').lower()
        high_quality_sources = [
            'harvard business review', 'mit technology review',
            'venturebeat', 'techcrunch', 'the register'
        ]
        
        if any(quality_source in source_name for quality_source in high_quality_sources):
            score += 15
        
        # Recency (prefer more recent articles)
        published_at = article.get('published_at')
        if published_at:
            from datetime import datetime, timedelta
            age_days = (datetime.now() - published_at).days
            if age_days <= 1:
                score += 10
            elif age_days <= 3:
                score += 5
        
        return score
    
    def merge_article_information(self, best_article: Dict[str, Any], all_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge useful information from similar articles"""
        merged = best_article.copy()
        
        # Collect all tags
        all_tags = set(merged.get('tags', []))
        for article in all_articles:
            if article is not best_article:
                all_tags.update(article.get('tags', []))
        
        merged['tags'] = list(all_tags)[:20]  # Limit tags
        
        # If best article has short content, try to find longer version
        best_content_length = len(merged.get('content_excerpt', ''))
        
        for article in all_articles:
            if article is not best_article:
                article_content_length = len(article.get('content_excerpt', ''))
                
                if article_content_length > best_content_length * 1.5:  # Significantly longer
                    merged['content_excerpt'] = article['content_excerpt']
                    best_content_length = article_content_length
        
        return merged


# CLI testing
if __name__ == "__main__":
    deduplicator = Deduplicator()
    
    # Test articles with duplicates
    test_articles = [
        {
            'title': 'AI Breakthrough in Machine Learning',
            'content_excerpt': 'Researchers have made significant advances in machine learning technology...',
            'url': 'https://example.com/article1',
            'source_type': 'rss',
            'source_name': 'TechCrunch',
            'relevance_score': 85
        },
        {
            'title': 'Machine Learning AI Breakthrough',
            'content_excerpt': 'Scientists achieve breakthrough in artificial intelligence and machine learning...',
            'url': 'https://different.com/article2',
            'source_type': 'rss',
            'source_name': 'VentureBeat',
            'relevance_score': 80
        },
        {
            'title': 'Completely Different Article',
            'content_excerpt': 'This is about something totally different like blockchain technology...',
            'url': 'https://example.com/article3',
            'source_type': 'twitter',
            'source_name': '@somebody',
            'relevance_score': 70
        },
        {
            'title': 'AI Breakthrough in Machine Learning',  # Exact duplicate title
            'content_excerpt': 'Researchers have made significant advances in machine learning technology...',
            'url': 'https://example.com/article1',  # Same URL
            'source_type': 'rss',
            'source_name': 'TechCrunch',
            'relevance_score': 85
        }
    ]
    
    async def test():
        unique = await deduplicator.remove_duplicates(test_articles)
        print(f"Original: {len(test_articles)} articles")
        print(f"After deduplication: {len(unique)} articles")
        
        for i, article in enumerate(unique):
            print(f"\n{i+1}. {article['title']}")
            print(f"   Source: {article['source_name']}")
            print(f"   Score: {article['relevance_score']}")
    
    import asyncio
    asyncio.run(test())