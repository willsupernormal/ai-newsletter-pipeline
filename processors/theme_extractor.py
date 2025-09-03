"""
Rule-based theme extraction for business AI content
No API costs - uses keyword matching and content analysis
"""

import re
from typing import List, Dict, Set
from collections import Counter

class ThemeExtractor:
    """Extract business themes from article content without AI"""
    
    def __init__(self):
        # Business-focused theme keywords
        self.theme_keywords = {
            'enterprise-ai': [
                'enterprise', 'corporate', 'business', 'organization', 'company',
                'deployment', 'implementation', 'adoption', 'transformation'
            ],
            'data-strategy': [
                'data', 'analytics', 'database', 'warehouse', 'pipeline',
                'governance', 'quality', 'management', 'strategy'
            ],
            'vendor-independence': [
                'open source', 'vendor lock', 'independence', 'portability',
                'multi-cloud', 'hybrid', 'agnostic', 'interoperability'
            ],
            'automation': [
                'automation', 'workflow', 'process', 'efficiency', 'productivity',
                'robotic', 'streamline', 'optimize'
            ],
            'machine-learning': [
                'machine learning', 'ml', 'model', 'training', 'inference',
                'neural network', 'deep learning', 'algorithm'
            ],
            'generative-ai': [
                'generative', 'gpt', 'llm', 'large language', 'chatbot',
                'text generation', 'content creation', 'prompt'
            ],
            'computer-vision': [
                'computer vision', 'image', 'video', 'visual', 'recognition',
                'detection', 'classification', 'opencv'
            ],
            'nlp': [
                'natural language', 'nlp', 'text processing', 'sentiment',
                'translation', 'speech', 'voice'
            ],
            'cloud-ai': [
                'aws', 'azure', 'google cloud', 'gcp', 'cloud', 'saas',
                'api', 'service', 'platform'
            ],
            'security': [
                'security', 'privacy', 'encryption', 'compliance', 'gdpr',
                'audit', 'risk', 'governance'
            ],
            'investment': [
                'funding', 'investment', 'valuation', 'ipo', 'acquisition',
                'merger', 'venture', 'capital', 'startup'
            ],
            'regulation': [
                'regulation', 'policy', 'government', 'law', 'compliance',
                'ethics', 'responsible', 'governance'
            ]
        }
        
        # Company/vendor keywords for vendor tracking
        self.vendor_keywords = {
            'microsoft', 'google', 'amazon', 'aws', 'azure', 'openai',
            'anthropic', 'meta', 'facebook', 'apple', 'nvidia', 'intel',
            'ibm', 'oracle', 'salesforce', 'adobe', 'databricks'
        }
    
    def extract_themes(self, title: str, content: str = "", tags: List[str] = None) -> List[str]:
        """Extract themes from article title and content"""
        
        # Combine text for analysis
        text = f"{title} {content}".lower()
        
        # Find matching themes
        found_themes = set()
        
        for theme, keywords in self.theme_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    found_themes.add(theme)
                    break  # One match per theme is enough
        
        # Add vendor mentions
        for vendor in self.vendor_keywords:
            if vendor.lower() in text:
                found_themes.add(f"vendor-{vendor}")
        
        # Include original RSS tags if they're meaningful
        if tags:
            for tag in tags:
                if tag and tag.lower() not in ['ai', 'artificial intelligence']:
                    found_themes.add(f"rss-{tag.lower()}")
        
        # Convert to sorted list (max 8 themes to keep focused)
        return sorted(list(found_themes))[:8]
    
    def get_theme_summary(self, articles: List[Dict]) -> Dict[str, int]:
        """Get theme frequency across articles"""
        theme_counter = Counter()
        
        for article in articles:
            themes = article.get('key_themes', [])
            theme_counter.update(themes)
        
        return dict(theme_counter.most_common(20))
