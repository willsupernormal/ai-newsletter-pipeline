"""
Content processing and standardization
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlparse, urljoin
import html
import unicodedata


class ContentProcessor:
    """Processes and standardizes content from various sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and standardize article data"""
        try:
            processed = article_data.copy()
            
            # Clean and standardize title
            processed['title'] = self.clean_title(article_data.get('title', ''))
            
            # Clean and standardize content
            processed['content_excerpt'] = self.clean_content(article_data.get('content_excerpt', ''))
            
            # Validate and clean URL
            processed['url'] = self.clean_url(article_data.get('url', ''))
            
            # Standardize source name
            processed['source_name'] = self.standardize_source_name(article_data.get('source_name', ''))
            
            # Process publication date
            processed['published_at'] = self.standardize_date(article_data.get('published_at'))
            
            # Clean and validate tags
            processed['tags'] = self.clean_tags(article_data.get('tags', []))
            
            # Add processing metadata
            processed['processed_at'] = datetime.now()
            processed['content_length'] = len(processed['content_excerpt'])
            processed['word_count'] = self.count_words(processed['content_excerpt'])
            
            # Extract additional metadata
            processed.update(self.extract_metadata(processed))
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Failed to process article: {e}")
            return article_data
    
    def clean_title(self, title: str) -> str:
        """Clean and standardize article title"""
        if not title:
            return "Untitled"
        
        # Decode HTML entities
        title = html.unescape(title)
        
        # Normalize unicode characters
        title = unicodedata.normalize('NFKC', title)
        
        # Remove excessive whitespace
        title = ' '.join(title.split())
        
        # Remove common prefixes/suffixes
        title = re.sub(r'^(Breaking|BREAKING|News|NEWS|Update|UPDATE):\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\|\s*.*$', '', title)  # Remove "| Source Name" suffixes
        
        # Clean up punctuation
        title = re.sub(r'\s*[|•·]\s*$', '', title)
        
        # Limit length
        if len(title) > 200:
            title = title[:197] + "..."
        
        return title.strip()
    
    def clean_content(self, content: str) -> str:
        """Clean and standardize content excerpt"""
        if not content:
            return ""
        
        # Decode HTML entities
        content = html.unescape(content)
        
        # Normalize unicode
        content = unicodedata.normalize('NFKC', content)
        
        # Remove excessive whitespace and normalize line breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Max 2 consecutive newlines
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces/tabs to single space
        content = content.strip()
        
        # Remove common newsletter artifacts
        content = self.remove_newsletter_artifacts(content)
        
        # Remove tracking pixels and invisible content
        content = re.sub(r'<img[^>]*width=["\']1["\'][^>]*>', '', content)
        content = re.sub(r'<img[^>]*height=["\']1["\'][^>]*>', '', content)
        
        return content
    
    def remove_newsletter_artifacts(self, content: str) -> str:
        """Remove common newsletter artifacts and footers"""
        # Remove unsubscribe footers
        patterns = [
            r'unsubscribe.*?$',
            r'manage\s+your\s+preferences.*?$',
            r'you\s+received\s+this\s+email.*?$',
            r'sent\s+to\s+.*?@.*?$',
            r'update\s+your\s+email\s+preferences.*?$',
            r'view\s+in\s+browser.*?$',
            r'forward\s+to\s+a\s+friend.*?$'
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        return content.strip()
    
    def clean_url(self, url: str) -> str:
        """Clean and validate URL"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Remove tracking parameters
        tracking_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
            'fbclid', 'gclid', 'ref', 'source', 'campaign_id', 'mc_cid', 'mc_eid'
        ]
        
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            
            parsed = urlparse(url)
            
            if parsed.query:
                query_params = parse_qs(parsed.query)
                # Remove tracking parameters
                clean_params = {k: v for k, v in query_params.items() 
                              if k.lower() not in tracking_params}
                
                # Rebuild query string
                if clean_params:
                    clean_query = urlencode(clean_params, doseq=True)
                    parsed = parsed._replace(query=clean_query)
                else:
                    parsed = parsed._replace(query='')
            
            clean_url = urlunparse(parsed)
            
            # Basic validation
            if not clean_url.startswith(('http://', 'https://')):
                if clean_url.startswith('//'):
                    clean_url = 'https:' + clean_url
                elif not clean_url.startswith('mailto:'):
                    clean_url = 'https://' + clean_url
            
            return clean_url
            
        except Exception as e:
            self.logger.debug(f"URL cleaning failed for {url}: {e}")
            return url
    
    def standardize_source_name(self, source_name: str) -> str:
        """Standardize source name format"""
        if not source_name:
            return "Unknown Source"
        
        # Common standardizations
        standardizations = {
            'venturebeat': 'VentureBeat',
            'techcrunch': 'TechCrunch',
            'mit technology review': 'MIT Technology Review',
            'the register': 'The Register',
            'analytics india magazine': 'Analytics India Magazine',
            'harvard business review': 'Harvard Business Review',
            'ai business': 'AI Business'
        }
        
        source_lower = source_name.lower().strip()
        
        for key, standard_name in standardizations.items():
            if key in source_lower:
                return standard_name
        
        # Clean up source name
        source_name = source_name.strip()
        
        # Handle Twitter sources
        if source_name.startswith('@'):
            return source_name
        
        # Handle newsletter sources
        if 'newsletter' in source_name.lower():
            return source_name.title()
        
        # Default capitalization
        return ' '.join(word.capitalize() for word in source_name.split())
    
    def standardize_date(self, date_value: Any) -> Optional[datetime]:
        """Standardize publication date"""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            # Common date formats
            date_formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S GMT',
                '%d %b %Y %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
            
            # Try parsing with dateutil as fallback
            try:
                from dateutil import parser
                return parser.parse(date_value)
            except Exception:
                pass
        
        self.logger.debug(f"Could not parse date: {date_value}")
        return None
    
    def clean_tags(self, tags: List[str]) -> List[str]:
        """Clean and standardize tags"""
        if not tags:
            return []
        
        cleaned_tags = []
        seen_tags = set()
        
        for tag in tags:
            if not tag:
                continue
            
            # Clean tag
            clean_tag = tag.lower().strip()
            clean_tag = re.sub(r'[^\w\-_]', '_', clean_tag)  # Replace non-alphanumeric with underscore
            clean_tag = re.sub(r'_+', '_', clean_tag)  # Multiple underscores to single
            clean_tag = clean_tag.strip('_')  # Remove leading/trailing underscores
            
            if clean_tag and clean_tag not in seen_tags and len(clean_tag) > 1:
                cleaned_tags.append(clean_tag)
                seen_tags.add(clean_tag)
        
        return cleaned_tags[:20]  # Limit number of tags
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Split on whitespace and count non-empty tokens
        words = [word for word in text.split() if word.strip()]
        return len(words)
    
    def extract_metadata(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional metadata from article"""
        metadata = {}
        
        try:
            content = article_data.get('content_excerpt', '')
            title = article_data.get('title', '')
            
            # Calculate reading time (average 200 words per minute)
            word_count = article_data.get('word_count', 0)
            metadata['reading_time_minutes'] = max(1, round(word_count / 200))
            
            # Check content quality indicators
            metadata['has_quotes'] = '"' in content or '"' in content or '"' in content
            metadata['has_numbers'] = bool(re.search(r'\b\d+\b', content))
            metadata['has_links'] = 'http' in content
            metadata['title_word_count'] = len(title.split())
            
            # Content type indicators
            if any(word in content.lower() for word in ['study', 'research', 'paper', 'finding']):
                metadata['content_type'] = 'research'
            elif any(word in content.lower() for word in ['announces', 'launches', 'releases', 'unveils']):
                metadata['content_type'] = 'announcement'
            elif any(word in content.lower() for word in ['opinion', 'analysis', 'perspective', 'view']):
                metadata['content_type'] = 'analysis'
            else:
                metadata['content_type'] = 'news'
            
            # Urgency indicators
            urgency_words = ['breaking', 'urgent', 'alert', 'now', 'just', 'immediately']
            metadata['urgency_score'] = sum(1 for word in urgency_words if word in content.lower())
            
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata: {e}")
        
        return metadata
    
    def validate_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate article data and add quality scores"""
        validation = {
            'is_valid': True,
            'quality_score': 100,
            'issues': []
        }
        
        # Check required fields
        required_fields = ['title', 'source_type', 'source_name']
        for field in required_fields:
            if not article_data.get(field):
                validation['issues'].append(f"Missing {field}")
                validation['quality_score'] -= 20
        
        # Check title quality
        title = article_data.get('title', '')
        if len(title) < 10:
            validation['issues'].append("Title too short")
            validation['quality_score'] -= 15
        elif len(title) > 200:
            validation['issues'].append("Title too long")
            validation['quality_score'] -= 10
        
        # Check content quality
        content = article_data.get('content_excerpt', '')
        if len(content) < 50:
            validation['issues'].append("Content too short")
            validation['quality_score'] -= 25
        
        # Check URL validity
        url = article_data.get('url', '')
        if url and not url.startswith(('http://', 'https://', 'mailto:')):
            validation['issues'].append("Invalid URL format")
            validation['quality_score'] -= 10
        
        # Mark as invalid if quality score is too low
        if validation['quality_score'] < 40:
            validation['is_valid'] = False
        
        return validation
    
    def batch_process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple articles efficiently"""
        processed_articles = []
        
        for i, article in enumerate(articles):
            try:
                processed = self.process_article(article)
                validation = self.validate_article(processed)
                
                # Add validation results
                processed['validation'] = validation
                
                # Only include valid articles
                if validation['is_valid']:
                    processed_articles.append(processed)
                else:
                    self.logger.debug(f"Skipping invalid article {i}: {validation['issues']}")
                    
            except Exception as e:
                self.logger.error(f"Failed to process article {i}: {e}")
                continue
        
        self.logger.info(f"Processed {len(processed_articles)}/{len(articles)} articles successfully")
        return processed_articles


# CLI testing
if __name__ == "__main__":
    processor = ContentProcessor()
    
    # Test article
    test_article = {
        'title': '   Breaking: AI Breakthrough in Machine Learning   ',
        'content_excerpt': 'This is a test article about AI and machine learning advancements...',
        'url': 'https://example.com/article?utm_source=newsletter&utm_campaign=test',
        'source_type': 'rss',
        'source_name': 'techcrunch',
        'tags': ['ai', 'machine-learning', '', 'tech'],
        'published_at': '2024-01-15T10:30:00Z'
    }
    
    processed = processor.process_article(test_article)
    validation = processor.validate_article(processed)
    
    print("Processed Article:")
    for key, value in processed.items():
        print(f"  {key}: {value}")
    
    print(f"\nValidation: {validation}")