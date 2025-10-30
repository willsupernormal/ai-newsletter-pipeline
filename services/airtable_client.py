"""
Airtable integration for Content Pipeline
Handles creating and updating records in Airtable base
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from pyairtable import Api
from pyairtable.formulas import match

from config.settings import Settings


class AirtableClient:
    """Client for interacting with Airtable Content Pipeline"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        if not settings.AIRTABLE_API_KEY or not settings.AIRTABLE_BASE_ID:
            raise ValueError("Airtable credentials not configured")
        
        self.api = Api(settings.AIRTABLE_API_KEY)
        self.table = self.api.table(
            settings.AIRTABLE_BASE_ID,
            settings.AIRTABLE_TABLE_NAME
        )
    
    def create_article_record(self, article_data: Dict[str, Any]) -> Optional[str]:
        """
        Create new article record in Airtable
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            Record ID if successful, None otherwise
        """
        try:
            # Check if article already exists (by URL)
            existing = self.search_by_url(article_data.get('url'))
            if existing:
                self.logger.info(f"Article already exists in Airtable: {article_data.get('title')}")
                return existing['id']
            
            # Format data for Airtable
            fields = self._format_article_fields(article_data)
            
            # Create record
            record = self.table.create(fields)
            
            self.logger.info(f"✓ Created Airtable record: {record['id']} - {article_data.get('title')}")
            return record['id']
            
        except Exception as e:
            self.logger.error(f"Failed to create Airtable record: {e}")
            return None
    
    def update_article_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing article record
        
        Args:
            record_id: Airtable record ID
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.table.update(record_id, updates)
            self.logger.info(f"✓ Updated Airtable record: {record_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update Airtable record {record_id}: {e}")
            return False
    
    def search_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Search for article by URL
        
        Args:
            url: Article URL
            
        Returns:
            Record dict if found, None otherwise
        """
        try:
            formula = match({"Original URL": url})
            records = self.table.all(formula=formula)
            
            if records:
                return records[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to search Airtable by URL: {e}")
            return None
    
    def search_by_supabase_id(self, supabase_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for article by Supabase ID
        
        Args:
            supabase_id: Supabase article ID
            
        Returns:
            Record dict if found, None otherwise
        """
        try:
            formula = match({"Supabase ID": supabase_id})
            records = self.table.all(formula=formula)
            
            if records:
                return records[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to search Airtable by Supabase ID: {e}")
            return None
    
    def _format_article_fields(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format article data for Airtable fields
        
        Args:
            article_data: Raw article data
            
        Returns:
            Formatted fields dict
        """
        fields = {}
        
        # Basic fields
        if 'title' in article_data:
            fields['Title'] = article_data['title']
        
        if 'url' in article_data:
            fields['Original URL'] = article_data['url']
        
        if 'source_name' in article_data:
            fields['Source'] = article_data['source_name']
        
        # Stage (default to Saved)
        fields['Stage'] = article_data.get('stage', '📥 Saved')
        
        # Dates
        if 'digest_date' in article_data:
            if isinstance(article_data['digest_date'], (date, datetime)):
                fields['Digest Date'] = article_data['digest_date'].isoformat()
            else:
                fields['Digest Date'] = article_data['digest_date']
        
        # Theme and Content Type
        if 'primary_theme' in article_data and article_data['primary_theme']:
            fields['Theme'] = article_data['primary_theme']
        
        if 'content_type' in article_data and article_data['content_type']:
            fields['Content Type'] = article_data['content_type'].capitalize()
        
        # Priority (default to Medium)
        fields['Priority'] = article_data.get('priority', '🟡 Medium')
        
        # AI-generated analysis (from digest_articles table)
        if 'detailed_summary' in article_data and article_data['detailed_summary']:
            fields['Detailed Summary'] = article_data['detailed_summary']
        
        if 'business_impact' in article_data and article_data['business_impact']:
            fields['Business Impact'] = article_data['business_impact']
        
        if 'strategic_context' in article_data and article_data['strategic_context']:
            fields['Strategic Context'] = article_data['strategic_context']
        
        if 'key_quotes' in article_data:
            fields['Key Quotes'] = self._format_quotes(article_data['key_quotes'])
        
        if 'specific_data' in article_data:
            fields['Specific Data'] = self._format_metrics(article_data['specific_data'])
        
        if 'talking_points' in article_data and article_data['talking_points']:
            fields['Talking Points'] = '\n'.join(article_data['talking_points'])
        
        if 'newsletter_angles' in article_data and article_data['newsletter_angles']:
            fields['Newsletter Angles'] = '\n'.join(article_data['newsletter_angles'])
        
        if 'technical_details' in article_data and article_data['technical_details']:
            fields['Technical Details'] = '\n'.join(article_data['technical_details'])
        
        if 'companies_mentioned' in article_data and article_data['companies_mentioned']:
            fields['Companies Mentioned'] = ', '.join(article_data['companies_mentioned'])
        
        # Full article text (from scraping)
        if 'full_article_text' in article_data:
            fields['Full Article Text'] = article_data['full_article_text']
        
        if 'word_count' in article_data:
            fields['Word Count'] = article_data['word_count']
        
        if 'author' in article_data and article_data['author']:
            fields['Author'] = article_data['author']
        
        # Supabase ID for linking
        if 'supabase_id' in article_data:
            fields['Supabase ID'] = article_data['supabase_id']
        
        return fields
    
    def _format_metrics(self, metrics: List[Dict[str, Any]]) -> str:
        """Format metrics list as readable text"""
        if not metrics:
            return ""
        
        formatted = []
        for i, metric in enumerate(metrics, 1):
            metric_name = metric.get('metric', 'Metric')
            value = metric.get('value', 'N/A')
            context = metric.get('context', '')
            
            formatted.append(f"{i}. {metric_name}: {value}")
            if context:
                formatted.append(f"   Context: {context}")
        
        return "\n".join(formatted)
    
    def _format_quotes(self, quotes: List[Dict[str, Any]]) -> str:
        """Format quotes list as readable text"""
        if not quotes:
            return ""
        
        formatted = []
        for i, quote in enumerate(quotes, 1):
            quote_text = quote.get('quote', '')
            speaker = quote.get('speaker', '')
            context = quote.get('context', '')
            
            formatted.append(f"{i}. \"{quote_text}\"")
            if speaker:
                formatted.append(f"   - {speaker}")
            if context:
                formatted.append(f"   Context: {context}")
        
        return "\n".join(formatted)
    
    def get_recent_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent articles from Airtable
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of article records
        """
        try:
            records = self.table.all(
                max_records=limit,
                sort=["-Digest Date"]
            )
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get recent articles: {e}")
            return []
